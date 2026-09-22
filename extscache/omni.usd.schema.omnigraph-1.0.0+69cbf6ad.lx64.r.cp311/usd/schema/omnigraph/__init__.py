import os
from pxr import Plug

pluginsRoot = os.path.join(os.path.dirname(__file__), '../../../plugins')
omniGraphSchemaPath = pluginsRoot + '/omniGraphSchema/resources'

Plug.Registry().RegisterPlugins(omniGraphSchemaPath)
