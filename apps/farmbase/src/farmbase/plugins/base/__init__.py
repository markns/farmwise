from __future__ import absolute_import, print_function

from farmbase.plugins.base.manager import PluginManager
from farmbase.plugins.base.v1 import *  # noqa

plugins = PluginManager()
register = plugins.register
unregister = plugins.unregister
