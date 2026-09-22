import os

from pxr import Plug

pluginsRoot = os.path.join(os.path.dirname(__file__), '../../../plugins')
semanticSchemaPath = pluginsRoot + '/semantics/resources'

Plug.Registry().RegisterPlugins(semanticSchemaPath)
