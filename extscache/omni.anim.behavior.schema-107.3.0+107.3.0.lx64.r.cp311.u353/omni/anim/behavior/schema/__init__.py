import os

from pxr import Plug

pluginsRoot = os.path.join(os.path.dirname(__file__), '../../../../plugins')
schemaPath = pluginsRoot + '/BehaviorSchema/resources'

Plug.Registry().RegisterPlugins(schemaPath)