import inspect
import sys
from pprint import pprint
from typing import Annotated, Any, Callable, Dict, Type, get_origin

from docstring_parser import parse
from pydantic import BaseModel, create_model
from pydantic.fields import Field, FieldInfo
from pydantic_core import PydanticUndefined
from typing_extensions import TypeGuard


def normalize_for_openai(obj: dict):
    if isinstance(obj, dict):
        # Create a new dict to avoid mutating while iterating
        new_obj = {}
        for k, v in obj.items():
            if k in ("minItems", "maxItems"):
                continue
            elif k == "prefixItems":
                # Assumes all prefixItems are the same type
                first_type = v[0].get("type", "number")
                new_obj["items"] = {"type": first_type}
            else:
                new_obj[k] = normalize_for_openai(v)
        return new_obj
    elif isinstance(obj, list):
        return [normalize_for_openai(i) for i in obj]
    else:
        return obj


def get_tool_defs(functions: list[Callable], case_insensitive: bool = False, strict: bool = False) -> list[dict]:
    result = []
    for function in functions:
        fun_schema = get_function_schema(function, case_insensitive, strict)
        fun_schema = normalize_for_openai(fun_schema)
        result.append(fun_schema)
    return result


def parameters_basemodel_from_function(function: Callable, param_docs) -> Type[BaseModel]:
    fields = {}
    parameters = inspect.signature(function).parameters

    # Get the global namespace, handling both functions and methods
    if inspect.ismethod(function):
        # For methods, get the class's module globals
        function_globals = sys.modules[function.__module__].__dict__
    else:
        # For regular functions, use __globals__ if available
        function_globals = getattr(function, "__globals__", {})

    for name, parameter in parameters.items():
        description = param_docs[name].description if name in param_docs else None
        type_ = parameter.annotation
        if type_ is inspect._empty:
            raise ValueError(f"Parameter '{name}' has no type annotation")

        # Handle both Annotated types and Pydantic Fields
        if get_origin(type_) is Annotated:
            if type_.__metadata__:
                description = type_.__metadata__[0]
            type_ = type_.__args__[0]
        if isinstance(type_, str):
            # this happens in postponed annotation evaluation, we need to try to resolve the type
            # if the type is not in the global namespace, we will get a NameError
            type_ = eval(type_, function_globals)

        # Check if the default is a Pydantic Field
        if isinstance(parameter.default, FieldInfo):
            # Reuse the existing Field
            field = parameter.default
            # Only update description if it was set by Annotated
            if description is not None:
                field.description = description
            fields[name] = (type_, field)
        else:
            default = PydanticUndefined if parameter.default is inspect.Parameter.empty else parameter.default
            fields[name] = (type_, Field(default, description=description))

    return create_model(f"{function.__name__}_ParameterModel", **fields)


def _recursive_purge_titles(d: Dict[str, Any]) -> None:
    """Remove a titles from a schema recursively"""
    if isinstance(d, dict):
        for key in list(d.keys()):
            if key == "title" and "type" in d.keys():
                del d[key]
            else:
                _recursive_purge_titles(d[key])


def get_name(func: Callable, case_insensitive: bool = False) -> str:
    schema_name = func.__name__

    if case_insensitive:
        schema_name = schema_name.lower()
    return schema_name


def get_function_schema(function: Callable, case_insensitive: bool = False, strict: bool = False) -> dict:
    if not hasattr(function, "__doc__") and not function.__doc__:
        raise ValueError(f"Function {function.__name__} has no docstring")

    docstring = parse(function.__doc__)
    param_docs = {p.arg_name: p for p in docstring.params}

    schema_name = function.__name__
    if case_insensitive:
        schema_name = schema_name.lower()

    function_schema: dict[str, Any] = {
        "type": "function",
        "name": schema_name,
        "description": docstring.description,
    }
    model = parameters_basemodel_from_function(function, param_docs)
    model_json_schema = model.model_json_schema()
    if strict:
        model_json_schema = to_strict_json_schema(model_json_schema)
        function_schema["strict"] = True
    else:
        _recursive_purge_titles(model_json_schema)
    function_schema["parameters"] = model_json_schema

    return function_schema


def to_strict_json_schema(schema: dict) -> dict[str, Any]:
    return _ensure_strict_json_schema(schema, path=())


def _ensure_strict_json_schema(
    json_schema: dict,
    path: tuple[str, ...],
) -> dict[str, Any]:
    """Mutates the given JSON schema to ensure it conforms to the `strict` standard
    that the API expects.
    """
    if not is_dict(json_schema):
        raise TypeError(f"Expected {json_schema} to be a dictionary; path={path}")

    typ = json_schema.get("type")
    if typ == "object" and "additionalProperties" not in json_schema:
        json_schema["additionalProperties"] = False

    # object types
    # { 'type': 'object', 'properties': { 'a':  {...} } }
    properties = json_schema.get("properties")
    if is_dict(properties):
        json_schema["required"] = [prop for prop in properties.keys()]
        json_schema["properties"] = {
            key: _ensure_strict_json_schema(prop_schema, path=(*path, "properties", key))
            for key, prop_schema in properties.items()
        }

    # arrays
    # { 'type': 'array', 'items': {...} }
    items = json_schema.get("items")
    if is_dict(items):
        json_schema["items"] = _ensure_strict_json_schema(items, path=(*path, "items"))

    # unions
    any_of = json_schema.get("anyOf")
    if isinstance(any_of, list):
        json_schema["anyOf"] = [
            _ensure_strict_json_schema(variant, path=(*path, "anyOf", str(i))) for i, variant in enumerate(any_of)
        ]

    # intersections
    all_of = json_schema.get("allOf")
    if isinstance(all_of, list):
        json_schema["allOf"] = [
            _ensure_strict_json_schema(entry, path=(*path, "anyOf", str(i))) for i, entry in enumerate(all_of)
        ]

    defs = json_schema.get("$defs")
    if is_dict(defs):
        for def_name, def_schema in defs.items():
            _ensure_strict_json_schema(def_schema, path=(*path, "$defs", def_name))

    return json_schema


def is_dict(obj: object) -> TypeGuard[dict[str, object]]:
    # just pretend that we know there are only `str` keys
    # as that check is not worth the performance cost
    return isinstance(obj, dict)


#######################################
#
# Examples

if __name__ == "__main__":

    class User(BaseModel):
        name: str
        age: int

    class ExampleClass:
        def simple_method(self, count: int, size: float | None, user: User):
            """simple method does something"""
            pass

    example_object = ExampleClass()

    from farmbase_agent_toolkit.api import FarmbaseAPI

    farmbase = FarmbaseAPI(secret_key="dsffd", context=None)

    pprint(get_tool_defs([farmbase.create_farm], strict=True))
