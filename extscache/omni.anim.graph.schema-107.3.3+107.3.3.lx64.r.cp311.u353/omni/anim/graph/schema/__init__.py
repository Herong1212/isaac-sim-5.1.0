import os

from pxr import Plug

pluginsRoot = os.path.join(os.path.dirname(__file__), '../../../../plugins')
schemaPath = pluginsRoot + '/AnimGraphSchema/resources'

Plug.Registry().RegisterPlugins(schemaPath)