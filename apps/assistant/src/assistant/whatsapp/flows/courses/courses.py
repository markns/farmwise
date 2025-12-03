import abc
import importlib
import inspect
import pkgutil
from urllib.parse import quote_plus

from loguru import logger
from pywa.types import FlowActionType, FlowButton, FlowCategory, FlowJSON
from pywa_async import WhatsApp

from assistant.schema import CourseData, Section, SectionList, SectionRow
from assistant.settings import settings


class FlowCourse(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    def endpoint(self) -> str:
        return f"/flows/{quote_plus(self.name.lower())}"

    @property
    @abc.abstractmethod
    def category(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        pass

    @abc.abstractmethod
    def flow_json(self) -> FlowJSON:
        pass

    def flow_button(self) -> FlowButton:
        return FlowButton(
            title="Start course",
            flow_action_type=FlowActionType.NAVIGATE,
            flow_action_screen="LESSON_ONE",
            flow_name=self.name,
        )


def load_courses(package_name="assistant.whatsapp.flows.courses", base_class=FlowCourse) -> list[FlowCourse]:
    """Load all subclasses of base_class from package."""
    package = importlib.import_module(package_name)
    courses = []

    # walk_packages recursively iterates through all subpackages
    for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__, prefix=package.__name__ + "."):
        try:
            module = importlib.import_module(modname)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, base_class) and obj is not base_class:
                    courses.append(obj())
        except ImportError as e:
            logger.error(f"Warning: Could not import {modname}: {e}")
            continue

    return courses


def get_courses_section_list():
    courses = load_courses()
    # Group courses by category
    category_map = {}
    for course in courses:
        category = course.category
        category_map.setdefault(category, []).append(course)

    sections = []
    for category, course_list in category_map.items():
        # Sort courses alphabetically by name
        sorted_courses = sorted(course_list, key=lambda c: c.name)
        rows = [
            SectionRow(
                title=course.name,
                callback_data=CourseData(title=course.name, name=course.name),
            )
            for course in sorted_courses
        ]
        sections.append(Section(title=category, rows=rows))

    courses_section_list = SectionList(button_title="Select course", sections=sections)
    return courses_section_list


async def create_or_update_flows(wa: WhatsApp):
    flows = await wa.get_flows()
    flow_id_map = {flow.name: flow.id for flow in flows}
    for course in load_courses():
        if course.name not in flow_id_map:
            logger.info(f"Creating flow: {course.name} {settings.WHATSAPP_CALLBACK_URL}{course.endpoint}")
            await wa.create_flow(
                name=course.name,
                categories=[FlowCategory.OTHER],
                endpoint_uri=f"{settings.WHATSAPP_CALLBACK_URL}{course.endpoint}",
                publish=True,
                flow_json=course.flow_json(),
            )
            # await flow.update_metadata(endpoint_uri=f"{settings.WHATSAPP_CALLBACK_URL}{course.endpoint}")
        else:
            logger.info(f"Updating flow: {course.name} {settings.WHATSAPP_CALLBACK_URL}{course.endpoint}")
            flow = await wa.get_flow(flow_id=flow_id_map[course.name])
            flow_assets = await flow.get_assets()
            # logger.info(flow_assets)
            for asset in flow_assets:
                if asset.type == "FLOW_JSON":
                    asset.url
                    # todo: diff with existing and only update if changed? How to handle versioning/ published?

            new_json = course.flow_json()

            res = await flow.update_json(flow_json=new_json)

            await flow.update_metadata(endpoint_uri=f"{settings.WHATSAPP_CALLBACK_URL}{course.endpoint}")

            if not res:
                logger.error("Validation errors:")
                for error in res.validation_errors:
                    logger.error(error)
