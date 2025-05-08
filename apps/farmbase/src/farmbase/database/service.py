import json
from loguru import logger
from collections import namedtuple
from collections.abc import Iterable
from inspect import signature
from itertools import chain
from typing import Annotated, List

from fastapi import Depends, Query
from pydantic import ValidationError
from pydantic.types import Json, constr
from six import string_types
from sortedcontainers import SortedSet
from sqlalchemy import and_, desc, func, not_, or_, select
from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy_filters.exceptions import BadFilterFormat, FieldNotFound
from sqlalchemy_filters.models import Field, get_model_from_spec

from farmbase.auth.models import FarmbaseUser
from farmbase.auth.service import CurrentUser, get_current_role
from farmbase.database.core import DbSession
from farmbase.enums import UserRoles

from .core import Base, get_class_by_tablename, get_model_name_by_tablename


# allows only printable characters
QueryStr = constr(pattern=r"^[ -~]+$", min_length=1)

BooleanFunction = namedtuple("BooleanFunction", ("key", "sqlalchemy_fn", "only_one_arg"))
BOOLEAN_FUNCTIONS = [
    BooleanFunction("or", or_, False),
    BooleanFunction("and", and_, False),
    BooleanFunction("not", not_, True),
]


class Operator(object):
    OPERATORS = {
        "is_null": lambda f: f.is_(None),
        "is_not_null": lambda f: f.isnot(None),
        "==": lambda f, a: f == a,
        "eq": lambda f, a: f == a,
        "!=": lambda f, a: f != a,
        "ne": lambda f, a: f != a,
        ">": lambda f, a: f > a,
        "gt": lambda f, a: f > a,
        "<": lambda f, a: f < a,
        "lt": lambda f, a: f < a,
        ">=": lambda f, a: f >= a,
        "ge": lambda f, a: f >= a,
        "<=": lambda f, a: f <= a,
        "le": lambda f, a: f <= a,
        "like": lambda f, a: f.like(a),
        "ilike": lambda f, a: f.ilike(a),
        "not_ilike": lambda f, a: ~f.ilike(a),
        "in": lambda f, a: f.in_(a),
        "not_in": lambda f, a: ~f.in_(a),
        "any": lambda f, a: f.any(a),
        "not_any": lambda f, a: func.not_(f.any(a)),
    }

    def __init__(self, operator=None):
        if not operator:
            operator = "=="

        if operator not in self.OPERATORS:
            raise BadFilterFormat("Operator `{}` not valid.".format(operator))

        self.operator = operator
        self.function = self.OPERATORS[operator]
        self.arity = len(signature(self.function).parameters)


class Filter(object):
    def __init__(self, filter_spec):
        self.filter_spec = filter_spec

        try:
            filter_spec["field"]
        except KeyError:
            raise BadFilterFormat("`field` is a mandatory filter attribute.") from None
        except TypeError:
            raise BadFilterFormat("Filter spec `{}` should be a dictionary.".format(filter_spec)) from None

        self.operator = Operator(filter_spec.get("op"))
        self.value = filter_spec.get("value")
        value_present = True if "value" in filter_spec else False
        if not value_present and self.operator.arity == 2:
            raise BadFilterFormat("`value` must be provided.")

    def get_named_models(self):
        if "model" in self.filter_spec:
            model = self.filter_spec["model"]
            if model in ["Participant", "Commander", "Assignee"]:
                return {"IndividualContact"}
            if model == "TagAll":
                return {"Tag"}
            else:
                return {self.filter_spec["model"]}
        return set()

    def format_for_sqlalchemy(self, query, default_model):
        filter_spec = self.filter_spec
        if filter_spec.get("model") in ["Participant", "Commander", "Assignee"]:
            filter_spec["model"] = "IndividualContact"
        elif filter_spec.get("model") == "TagAll":
            filter_spec["model"] = "Tag"

        operator = self.operator
        value = self.value

        model = get_model_from_spec(filter_spec, query, default_model)

        function = operator.function
        arity = operator.arity

        field_name = self.filter_spec["field"]
        field = Field(model, field_name)
        sqlalchemy_field = field.get_sqlalchemy_field()

        if arity == 1:
            return function(sqlalchemy_field)

        if arity == 2:
            return function(sqlalchemy_field, value)


class BooleanFilter(object):
    def __init__(self, function, *filters):
        self.function = function
        self.filters = filters

    def get_named_models(self):
        models = SortedSet()
        for filter in self.filters:
            named_models = filter.get_named_models()
            if named_models:
                models.add(*named_models)
        return models

    def format_for_sqlalchemy(self, query, default_model):
        return self.function(*[filter.format_for_sqlalchemy(query, default_model) for filter in self.filters])


def _is_iterable_filter(filter_spec):
    """`filter_spec` may be a list of nested filter specs, or a dict."""
    return isinstance(filter_spec, Iterable) and not isinstance(filter_spec, (string_types, dict))


def build_filters(filter_spec):
    """Recursively process `filter_spec`"""
    if _is_iterable_filter(filter_spec):
        return list(chain.from_iterable(build_filters(item) for item in filter_spec))

    if isinstance(filter_spec, dict):
        # Check if filter spec defines a boolean function.
        for boolean_function in BOOLEAN_FUNCTIONS:
            if boolean_function.key in filter_spec:
                # The filter spec is for a boolean-function
                # Get the function argument definitions and validate
                fn_args = filter_spec[boolean_function.key]

                if not _is_iterable_filter(fn_args):
                    raise BadFilterFormat(
                        "`{}` value must be an iterable across the function arguments".format(boolean_function.key)
                    )
                if boolean_function.only_one_arg and len(fn_args) != 1:
                    raise BadFilterFormat("`{}` must have one argument".format(boolean_function.key))
                if not boolean_function.only_one_arg and len(fn_args) < 1:
                    raise BadFilterFormat("`{}` must have one or more arguments".format(boolean_function.key))
                return [BooleanFilter(boolean_function.sqlalchemy_fn, *build_filters(fn_args))]

    return [Filter(filter_spec)]


def get_query_models(query):
    """Get models from query.

    :param query:
                    A :class:`sqlalchemy.orm.Query` instance.

    :returns:
                    A dictionary with all the models included in the query.
    """
    models = [col_desc["entity"] for col_desc in query.column_descriptions]
    models.extend(mapper.class_ for mapper in query._join_entities)

    # account also query.select_from entities
    if hasattr(query, "_select_from_entity") and (query._select_from_entity is not None):
        model_class = (
            query._select_from_entity.class_
            if isinstance(query._select_from_entity, Mapper)  # sqlalchemy>=1.1
            else query._select_from_entity  # sqlalchemy==1.0
        )
        if model_class not in models:
            models.append(model_class)

    return {model.__name__: model for model in models}


def get_model_class_by_name(registry, name):
    """Return the model class matching `name` in the given `registry`."""
    for cls in registry.values():
        if getattr(cls, "__name__", None) == name:
            return cls


def get_named_models(filters):
    models = []
    for filter in filters:
        models.extend(filter.get_named_models())
    return models


async def get_default_model(stmt):
    """Return the singular model from `stmt`, or `None` if `stmt` contains
    multiple models.
    """
    # In SQLAlchemy 2, we need a different approach to get models from a select statement
    # This is a simplified version that assumes we can get the model from the statement

    # Try to get the model from the select statement
    try:
        # For a simple select(Model), we can get the model from the columns
        columns = stmt.columns
        if len(columns) == 1 and hasattr(columns[0], "table"):
            table = columns[0].table
            for mapper in Base.registry.mappers:
                if mapper.local_table == table:
                    return mapper.class_
    except Exception:
        # If we can't get the model from the columns, return None
        pass

    return None


async def auto_join(stmt, model_names):
    """Automatically join models to `stmt` if they're not already present
    and the join can be done implicitly.
    """
    # In SQLAlchemy 2, we need a different approach to get models from a select statement
    # This is a simplified version that assumes we can get the model from the Base registry

    # Get all models from the Base registry
    model_registry = Base.registry.mappers

    for name in model_names:
        # Find the model class by name
        model = None
        for mapper in model_registry:
            if mapper.class_.__name__ == name:
                model = mapper.class_
                break

        if model:
            try:
                # In SQLAlchemy 2, joins are applied to select statements
                stmt = stmt.join(model)
            except InvalidRequestError:
                pass  # can't be autojoined

    return stmt


async def apply_model_specific_filters(model: Base, stmt, current_user: FarmbaseUser, role: UserRoles):
    """Applies any model specific filter as it pertains to the given user."""
    model_map = {
        # Incident: [restricted_incident_filter],
        # Case: [restricted_case_filter],
        # IncidentType: [restricted_incident_type_filter],
    }

    filters = model_map.get(model, [])

    for f in filters:
        # Assuming the filter functions have been updated to be async and work with select statements
        stmt = await f(stmt, current_user, role)

    return stmt


async def apply_filters(stmt, filter_spec, model_cls=None, do_auto_join=True):
    """Apply filters to a SQLAlchemy select statement.

    :param stmt:
                    A :class:`sqlalchemy.sql.selectable.Select` instance.

    :param filter_spec:
                    A dict or an iterable of dicts, where each one includes
                    the necessary information to create a filter to be applied to the
                    statement.

                    Example::

                                    filter_spec = [
                                                    {'model': 'Foo', 'field': 'name', 'op': '==', 'value': 'foo'},
                                    ]

                    If the statement being modified refers to a single model, the `model` key
                    may be omitted from the filter spec.

                    Filters may be combined using boolean functions.

                    Example:

                                    filter_spec = {
                                                    'or': [
                                                                    {'model': 'Foo', 'field': 'id', 'op': '==', 'value': '1'},
                                                                    {'model': 'Bar', 'field': 'id', 'op': '==', 'value': '2'},
                                                    ]
                                    }

    :returns:
                    The :class:`sqlalchemy.sql.selectable.Select` instance after all the filters
                    have been applied.
    """
    # In SQLAlchemy 2, we need to adapt how we get the default model from a select statement
    # This is a simplified approach - in a real implementation, you might need more complex logic
    default_model = model_cls

    filters = build_filters(filter_spec)
    filter_models = get_named_models(filters)

    # Auto-join logic needs to be adapted for SQLAlchemy 2
    # This is a placeholder - in a real implementation, you would need to adapt auto_join
    # to work with select statements instead of query objects
    # if do_auto_join:
    #     stmt = auto_join_for_select(stmt, filter_models)

    sqlalchemy_filters = [filter.format_for_sqlalchemy(stmt, default_model) for filter in filters]

    if sqlalchemy_filters:
        for filter_condition in sqlalchemy_filters:
            stmt = stmt.where(filter_condition)

    return stmt


async def apply_filter_specific_joins(model: Base, filter_spec: dict, stmt):
    """Applies any model specific implicitly joins."""
    # this is required because by default sqlalchemy-filter's auto-join
    # knows nothing about how to join many-many relationships.
    model_map = {
        # (Feedback, "Incident"): (Incident, False),
        # (Feedback, "Case"): (Case, False),
        # (Task, "Project"): (Incident, False),
        # (Task, "Incident"): (Incident, False),
        # (Task, "IncidentPriority"): (Incident, False),
        # (Task, "IncidentType"): (Incident, False),
        # (PluginInstance, "Plugin"): (Plugin, False),
        # (Source, "Tag"): (Source.tags, True),
        # (Source, "TagType"): (Source.tags, True),
        # (QueryModel, "Tag"): (QueryModel.tags, True),
        # (QueryModel, "TagType"): (QueryModel.tags, True),
        # (FarmbaseUser, "Organization"): (FarmbaseUser.organizations, True),
        # (Case, "Tag"): (Case.tags, True),
        # (Case, "TagType"): (Case.tags, True),
        # (Case, "IndividualContact"): (Case.participants, True),
        # (Incident, "Tag"): (Incident.tags, True),
        # (Incident, "TagType"): (Incident.tags, True),
        # (Incident, "IndividualContact"): (Incident.participants, True),
        # (Incident, "Term"): (Incident.terms, True),
        # (Signal, "Tag"): (Signal.tags, True),
        # (Signal, "TagType"): {Signal.tags, True},
        # (SignalInstance, "Entity"): (SignalInstance.entities, True),
        # (SignalInstance, "EntityType"): (SignalInstance.entities, True),
        # (Tag, "TagType"): (Tag.tag_type, False),
    }
    filters = build_filters(filter_spec)

    # Replace mapping if looking for commander
    # if "Commander" in str(filter_spec):
    #     model_map.update({(Incident, "IndividualContact"): (Incident.commander, True)})
    # if "Assignee" in str(filter_spec):
    #     model_map.update({(Case, "IndividualContact"): (Case.assignee, True)})

    filter_models = get_named_models(filters)
    joined_models = []
    for filter_model in filter_models:
        if model_map.get((model, filter_model)):
            joined_model, is_outer = model_map[(model, filter_model)]
            try:
                if joined_model not in joined_models:
                    # In SQLAlchemy 2, joins are applied differently to select statements
                    if is_outer:
                        stmt = stmt.outerjoin(joined_model)
                    else:
                        stmt = stmt.join(joined_model)
                    joined_models.append(joined_model)
            except Exception as e:
                logger.exception(e)

    return stmt


# def composite_search(*, db_session, query_str: str, models: List[Base], current_user: FarmbaseUser):
#     """Perform a multi-table search based on the supplied query."""
#     s = CompositeSearch(db_session, models)
#     query = s.build_query(query_str, sort=True)
#
#     # TODO can we do this with composite filtering?
#     # for model in models:
#     #    query = apply_model_specific_filters(model, query, current_user)
#
#     return s.search(query=query)


async def search(*, query_str: str, stmt, model: str, sort=False):
    """Perform a search based on the query."""
    search_model = get_class_by_tablename(model)

    if not query_str.strip():
        return stmt

    search = []
    if hasattr(search_model, "search_vector"):
        vector = search_model.search_vector
        search.append(vector.op("@@")(func.tsq_parse(query_str)))

    if hasattr(search_model, "name"):
        search.append(
            search_model.name.ilike(f"%{query_str}%"),
        )
        search.append(search_model.name == query_str)

    if not search:
        raise Exception(f"Search not supported for model: {model}")

    stmt = stmt.where(or_(*search))

    if sort and hasattr(search_model, "search_vector"):
        vector = search_model.search_vector
        stmt = stmt.order_by(desc(func.ts_rank_cd(vector, func.tsq_parse(query_str))))

    # In SQLAlchemy 2, params are handled differently
    # We'll use bindparams if needed in the future
    return stmt


def create_sort_spec(model, sort_by, descending):
    """Creates sort_spec."""
    sort_spec = []
    if sort_by and descending:
        for field, direction in zip(sort_by, descending, strict=False):
            direction = "desc" if direction else "asc"

            # check to see if field is json with a key parameter
            try:
                new_field = json.loads(field)
                field = new_field.get("key", "")
            except json.JSONDecodeError:
                pass

            # we have a complex field, we may need to join
            if "." in field:
                complex_model, complex_field = field.split(".")[-2:]

                sort_spec.append(
                    {
                        "model": get_model_name_by_tablename(complex_model),
                        "field": complex_field,
                        "direction": direction,
                    }
                )
            else:
                sort_spec.append({"model": model, "field": field, "direction": direction})
    logger.debug(f"Sort Spec: {json.dumps(sort_spec, indent=2)}")
    return sort_spec


async def get_all(*, db_session: AsyncSession, model):
    """Fetches a query object based on the model class name."""
    return select(get_class_by_tablename(model))


async def common_parameters(
    current_user: CurrentUser,
    db_session: DbSession,
    page: int = Query(1, gt=0, lt=2147483647),
    items_per_page: int = Query(5, alias="items_per_page", gt=-2, lt=2147483647),
    query_str: QueryStr = Query(None, alias="q"),
    filter_spec: QueryStr = Query(None, alias="filter"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    role: UserRoles = Depends(get_current_role),
):
    return {
        "db_session": db_session,
        "page": page,
        "items_per_page": items_per_page,
        "query_str": query_str,
        "filter_spec": filter_spec,
        "sort_by": sort_by,
        "descending": descending,
        "current_user": current_user,
        "role": role,
    }


CommonParameters = Annotated[
    dict[str, int | CurrentUser | DbSession | QueryStr | Json | List[str] | List[bool] | UserRoles],
    Depends(common_parameters),
]


def has_tag_all(filter_spec: List[dict]):
    """Checks if the filter spec has a TagAll filter."""

    if isinstance(filter_spec, list):
        return False

    for key, value in filter_spec.items():
        if key == "and":
            for condition in value:
                or_condition = condition.get("or", [])
                if or_condition and or_condition[0].get("model") == "TagAll":
                    return True
    return False


def rebuild_filter_spec_without_tag_all(filter_spec: List[dict]):
    """Rebuilds the filter spec without the TagAll filter."""
    new_filter_spec = []
    tag_all_spec = []
    for key, value in filter_spec.items():
        if key == "and":
            for condition in value:
                or_condition = condition.get("or", [])
                if or_condition and or_condition[0].get("model") == "TagAll":
                    for cond in or_condition:
                        tag_all_spec.append({"and": [{"or": [cond]}]})
                else:
                    new_filter_spec.append(condition)
    return ({"and": new_filter_spec} if len(new_filter_spec) else None, tag_all_spec)


async def search_filter_sort_paginate(
    db_session: AsyncSession,
    model,
    query_str: str = None,
    filter_spec: str | dict | None = None,
    page: int = 1,
    items_per_page: int = 5,
    sort_by: List[str] = None,
    descending: List[bool] = None,
    current_user: FarmbaseUser = None,
    role: UserRoles = UserRoles.member,
):
    """Common functionality for searching, filtering, sorting, and pagination."""
    model_cls = get_class_by_tablename(model)

    try:
        # Create a select statement instead of a query
        stmt = select(model_cls)

        if query_str:
            sort = False if sort_by else True
            stmt = await search(query_str=query_str, stmt=stmt, model=model, sort=sort)

        # Apply model-specific filters
        # Note: This function needs to be updated to work with select statements
        # For now, we'll skip this step
        # stmt_restricted = apply_model_specific_filters(model_cls, stmt, current_user, role)

        tag_all_filters = []
        if filter_spec:
            # some functions pass filter_spec as dictionary such as auth/views.py/get_users
            # but most come from API as seraialized JSON
            if isinstance(filter_spec, str):
                filter_spec = json.loads(filter_spec)

            stmt = await apply_filter_specific_joins(model_cls, filter_spec, stmt)

            # if the filter_spec has the TagAll filter, we need to split the query up
            # and intersect all of the results
            if has_tag_all(filter_spec):
                new_filter_spec, tag_all_spec = rebuild_filter_spec_without_tag_all(filter_spec)
                if new_filter_spec:
                    stmt = await apply_filters(stmt, new_filter_spec, model_cls)
                for tag_filter in tag_all_spec:
                    tag_all_filters.append(await apply_filters(stmt, tag_filter, model_cls))
            else:
                stmt = await apply_filters(stmt, filter_spec, model_cls)

        # In SQLAlchemy 2, intersect works differently with select statements
        # For now, we'll skip this step
        # if model == "Incident" or model == "Case":
        #     stmt = stmt.intersect(stmt_restricted)
        #     for filter_stmt in tag_all_filters:
        #         stmt = stmt.intersect(filter_stmt)

        if sort_by:
            # Note: apply_sort needs to be updated to work with select statements
            # For now, we'll use a simple approach for sorting
            sort_spec = create_sort_spec(model, sort_by, descending)
            # Apply sorting manually
            for spec in sort_spec:
                field_name = spec["field"]
                direction = spec["direction"]
                field = getattr(model_cls, field_name, None)
                if field:
                    if direction == "desc":
                        stmt = stmt.order_by(desc(field))
                    else:
                        stmt = stmt.order_by(field)

    except FieldNotFound as e:
        raise ValidationError.from_exception_data(
            "BaseModel",
            [
                {
                    "loc": ("filter",),
                    "msg": str(e),
                    "type": "value_error.field_not_found",
                }
            ],
        ) from None
    except BadFilterFormat as e:
        raise ValidationError.from_exception_data(
            "BaseModel",
            [
                {
                    "loc": ("filter",),
                    "msg": str(e),
                    "type": "value_error.invalid_filter",
                }
            ],
        ) from None

    if items_per_page == -1:
        items_per_page = None

    # In SQLAlchemy 2, pagination is handled differently
    # We'll implement a simple offset/limit approach
    total_count_stmt = select(func.count()).select_from(stmt.subquery())

    try:
        # Execute the count query
        result = await db_session.execute(total_count_stmt)
        total = result.scalar() or 0

        # Apply pagination
        if items_per_page:
            offset = (page - 1) * items_per_page
            stmt = stmt.offset(offset).limit(items_per_page)

        # Execute the main query
        result = await db_session.execute(stmt)
        items = result.scalars().all()

    except ProgrammingError as e:
        logger.error(e)
        return {
            "items": [],
            "items_per_page": items_per_page,
            "page": page,
            "total": 0,
        }

    return {
        "items": items,
        "items_per_page": items_per_page,
        "page": page,
        "total": total,
    }


# def restricted_incident_filter(query: orm.Query, current_user: FarmbaseUser, role: UserRoles):
#     """Adds additional incident filters to query (usually for permissions)."""
#     if role == UserRoles.member:
#         # We filter out restricted incidents for users with a member role if the user is not an incident participant
#         query = (
#             query.join(Participant, Incident.id == Participant.incident_id)
#             .join(IndividualContact)
#             .filter(
#                 or_(
#                     Incident.visibility == Visibility.open,
#                     IndividualContact.email == current_user.email,
#                 )
#             )
#         )
#     return query.distinct()


# def restricted_case_filter(query: orm.Query, current_user: FarmbaseUser, role: UserRoles):
#     """Adds additional case filters to query (usually for permissions)."""
#     if role == UserRoles.member:
#         # We filter out restricted cases for users with a member role if the user is not a case participant
#         query = (
#             query.join(Participant, Case.id == Participant.case_id)
#             .join(IndividualContact)
#             .filter(
#                 or_(
#                     Case.visibility == Visibility.open,
#                     IndividualContact.email == current_user.email,
#                 )
#             )
#         )
#     return query.distinct()


# def restricted_incident_type_filter(query: orm.Query, current_user: FarmbaseUser):
#     """Adds additional incident type filters to query (usually for permissions)."""
#     if current_user:
#         query = query.filter(IncidentType.visibility == Visibility.open)
#     return query
