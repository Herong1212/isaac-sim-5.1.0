import os

from pxr import Plug

pluginsRoot = os.path.join(os.path.dirname(__file__), '../../../plugins')
animSchemaPath = pluginsRoot + '/animationSchema/resources'
omniSkelSchemaPath = pluginsRoot + '/omniSkelSchema/resources'
retargetingSchemaPath = pluginsRoot + '/retargetingSchema/resources'

Plug.Registry().RegisterPlugins(animSchemaPath)
Plug.Registry().RegisterPlugins(omniSkelSchemaPath)
Plug.Registry().RegisterPlugins(retargetingSchemaPath)
