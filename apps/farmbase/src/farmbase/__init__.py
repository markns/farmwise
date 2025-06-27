import os
import os.path
import sys
from subprocess import check_output

from loguru import logger

from .agronomy.models import (
    Crop,
    CropCycle,
    CropCycleStage,
    Event,
    Pathogen,
    PathogenImage,
)
from .commodity.models import Commodity
from .contact.models import Contact
from .farm.activity.models import ActivityProduct, ActivityType, FarmActivity
from .farm.field.models import BoundaryDefinitionActivity, Field, FieldGroup, FieldGroupMember
from .farm.harvest.models import HarvestLoad, StorageLocation
from .farm.models import Farm, FarmContact
from .farm.note.models import Note
from .farm.planting.models import Planting
from .farm.platform.models import Platform
from .geospatial.models import Region, Subregion
from .market.models import Market, MarketPrice
from .message.models import Message
from .organization.models import Organization
from .plugin.models import Plugin, PluginEvent, PluginInstance
from .products.models import Manufacturer, Product
from .runresult.models import RunResult

try:
    VERSION = __import__("pkg_resources").get_distribution("farmbase").version
except Exception:
    VERSION = "unknown"

# fix is in the works see: https://github.com/mpdavis/python-jose/pull/207
import warnings

warnings.filterwarnings("ignore", message="int_from_bytes is deprecated")

if os.environ.get("LOG_MODULE_IMPORTS", False):

    class CustomMetaPathFinder:
        def find_spec(self, fullname, path, target=None):
            logger.info(f"Attempting to find spec for: {fullname}")
            # Let the default finders handle the actual module location
            return None

    class CustomPathHook:
        def __init__(self, path):
            self.path = path

        def find_spec(self, fullname, path, target=None):
            logger.info(f"Attempting to find spec in path hook for: {fullname} in {self.path}")
            # Allow default finders to handle the actual module location
            return None

    # Add the custom finder to the meta_path
    sys.meta_path.insert(0, CustomMetaPathFinder())


def _get_git_revision(path):
    if not os.path.exists(os.path.join(path, ".git")):
        return None
    try:
        revision = check_output(["git", "rev-parse", "HEAD"], cwd=path, env=os.environ)
    except Exception:
        # binary didn't exist, wasn't on path, etc
        return None
    return revision.decode("utf-8").strip()


def get_revision():
    """
    :returns: Revision number of this branch/checkout, if available. None if
        no revision number can be determined.
    """
    if "FARMBASE_BUILD" in os.environ:
        return os.environ["FARMBASE_BUILD"]
    package_dir = os.path.dirname(__file__)
    checkout_dir = os.path.normpath(os.path.join(package_dir, os.pardir, os.pardir))
    path = os.path.join(checkout_dir)
    if os.path.exists(path):
        return _get_git_revision(path)
    return None


def get_version():
    if __build__:
        return f"{__version__}.{__build__}"
    return __version__


def is_docker():
    # One of these environment variables are guaranteed to exist
    # from our official docker images.
    # FARMBASE_VERSION is from a tagged release, and FARMBASE_BUILD is from a
    # a git based image.
    return "FARMBASE_VERSION" in os.environ or "FARMBASE_BUILD" in os.environ


__version__ = VERSION
__build__ = get_revision()

# By defining __all__, you are telling Python and PyCharm
# what 'from farmbase.models import *' should import.
# PyCharm sees this and marks the imports above as "used".
__all__ = [
    "Farm",
    "FarmContact",
    "Note",
    "FieldGroup",
    "Field",
    "FieldGroupMember",
    "BoundaryDefinitionActivity",
    "StorageLocation",
    "HarvestLoad",
    "ActivityType",
    "FarmActivity",
    "ActivityProduct",
    "Planting",
    "Platform",
    "Commodity",
    "Plugin",
    "PluginEvent",
    "PluginInstance",
    "Contact",
    "Message",
    "Manufacturer",
    "Product",
    "Agent",
    "Organization",
    "Region",
    "Subregion",
    "Market",
    "MarketPrice",
    "Crop",
    "Pathogen",
    "PathogenImage",
    "Event",
    "CropCycle",
    "CropCycleStage",
]
