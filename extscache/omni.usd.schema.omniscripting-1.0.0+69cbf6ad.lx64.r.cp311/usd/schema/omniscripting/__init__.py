import os
from pxr import Plug

pluginsRoot = os.path.join(os.path.dirname(__file__), '../../../plugins')
omniScriptingSchemaPath = pluginsRoot + '/omniScriptingSchema/resources'

Plug.Registry().RegisterPlugins(omniScriptingSchemaPath)
