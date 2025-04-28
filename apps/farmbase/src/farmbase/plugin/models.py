import logging
from typing import Any, List, Optional

from pydantic import Field, SecretStr, field_validator
from pydantic.json import pydantic_encoder
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import StringEncryptedType, TSVectorType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from farmbase.config import FARMBASE_ENCRYPTION_KEY
from farmbase.database.core import Base
from farmbase.models import FarmbaseBase, Pagination, PrimaryKey, ProjectMixin
from farmbase.plugins.base import plugins
from farmbase.project.models import ProjectRead
from farmbase.validators import must_not_be_blank

logger = logging.getLogger(__name__)


def show_secrets_encoder(obj):
    if isinstance(obj, SecretStr):
        return obj.get_secret_value()
    else:
        return pydantic_encoder(obj)


class Plugin(Base):
    __table_args__ = {"schema": "farmbase_core"}
    id = Column(Integer, primary_key=True)
    title = Column(String)
    slug = Column(String, unique=True)
    description = Column(String)
    version = Column(String)
    author = Column(String)
    author_url = Column(String)
    type = Column(String)
    multiple = Column(Boolean)

    search_vector = Column(
        TSVectorType(
            "title",
            "slug",
            "type",
            "description",
            weights={"title": "A", "slug": "B", "type": "C", "description": "C"},
        )
    )

    @property
    def configuration_schema(self):
        """Renders the plugin's schema to JSON Schema."""
        try:
            plugin = plugins.get(self.slug)
            return plugin.configuration_schema.schema()
        except Exception as e:
            logger.warning(f"Error trying to load configuration_schema for plugin with slug {self.slug}: {e}")
            return None


# SQLAlchemy Model
class PluginEvent(Base):
    __table_args__ = {"schema": "farmbase_core"}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    slug = Column(String, unique=True)
    description = Column(String)
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
    plugin = relationship(Plugin, foreign_keys=[plugin_id])

    search_vector = Column(
        TSVectorType(
            "name",
            "slug",
            "description",
            weights={"name": "A", "slug": "B", "description": "C"},
        )
    )


class PluginInstance(Base, ProjectMixin):
    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean)
    _configuration = Column(StringEncryptedType(key=str(FARMBASE_ENCRYPTION_KEY), engine=AesEngine, padding="pkcs5"))
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
    plugin = relationship(Plugin, backref="instances")

    # this is some magic that allows us to use the plugin search vectors
    # against our plugin instances
    search_vector = association_proxy("plugin", "search_vector")

    @property
    def instance(self):
        """Fetches a plugin instance that matches this record."""
        try:
            plugin = plugins.get(self.plugin.slug)
            plugin.configuration = self.configuration
            plugin.project_id = self.project_id
            return plugin
        except Exception as e:
            logger.warning(f"Error trying to load plugin with slug {self.slug}: {e}")
            return self.plugin

    @property
    def broken(self):
        try:
            plugins.get(self.plugin.slug)
            return False
        except Exception:
            return True

    @property
    def configuration_schema(self):
        """Renders the plugin's schema to JSON Schema."""
        try:
            plugin = plugins.get(self.plugin.slug)
            return plugin.configuration_schema.schema()
        except Exception as e:
            logger.warning(f"Error trying to load plugin {self.plugin.title} {self.plugin.description} with error {e}")
            return None

    @hybrid_property
    def configuration(self):
        """Property that correctly returns a plugins configuration object."""
        try:
            if self._configuration:
                plugin = plugins.get(self.plugin.slug)
                return plugin.configuration_schema.parse_raw(self._configuration)
        except Exception as e:
            logger.warning(f"Error trying to load plugin {self.plugin.title} {self.plugin.description} with error {e}")
            return None

    @configuration.setter
    def configuration(self, configuration):
        """Property that correctly sets a plugins configuration object."""
        if configuration:
            plugin = plugins.get(self.plugin.slug)
            config_object = plugin.configuration_schema.parse_obj(configuration)
            self._configuration = config_object.json(encoder=show_secrets_encoder)


# Pydantic models...
class PluginBase(FarmbaseBase):
    pass


class PluginRead(PluginBase):
    id: PrimaryKey
    title: str
    slug: str
    author: str
    author_url: str
    type: str
    multiple: bool
    configuration_schema: Any
    description: Optional[str] = Field(None, nullable=True)


class PluginEventBase(FarmbaseBase):
    name: str
    slug: str
    plugin: PluginRead
    description: Optional[str] = Field(None, nullable=True)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Any):
        return must_not_be_blank(v)


class PluginEventRead(PluginEventBase):
    id: PrimaryKey


class PluginEventCreate(PluginEventBase):
    pass


class PluginEventPagination(Pagination):
    items: List[PluginEventRead] = []


class PluginInstanceRead(PluginBase):
    id: PrimaryKey
    enabled: Optional[bool]
    configuration: Optional[dict]
    configuration_schema: Any
    plugin: PluginRead
    project: Optional[ProjectRead]
    broken: Optional[bool]


class PluginInstanceReadMinimal(PluginBase):
    id: PrimaryKey
    enabled: Optional[bool]
    configuration_schema: Any
    plugin: PluginRead
    project: Optional[ProjectRead]
    broken: Optional[bool]


class PluginInstanceCreate(PluginBase):
    enabled: Optional[bool]
    configuration: Optional[dict]
    plugin: PluginRead
    project: ProjectRead


class PluginInstanceUpdate(PluginBase):
    id: PrimaryKey = None
    enabled: Optional[bool]
    configuration: Optional[dict]


class KeyValue(FarmbaseBase):
    key: str
    value: str | List[str] | dict


class PluginMetadata(FarmbaseBase):
    slug: str
    metadata: List[KeyValue] = []


class PluginPagination(Pagination):
    items: List[PluginRead] = []


class PluginInstancePagination(Pagination):
    items: List[PluginInstanceReadMinimal] = []
