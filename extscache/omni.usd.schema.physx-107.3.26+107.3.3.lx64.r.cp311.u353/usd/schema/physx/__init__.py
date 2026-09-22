import os

from pxr import Plug

pluginsRoot = os.path.join(os.path.dirname(__file__), '../../../plugins')

physxSchemaPath = pluginsRoot + '/PhysxSchema/resources'
Plug.Registry().RegisterPlugins(physxSchemaPath)

physxSchemaAdditionPath = pluginsRoot + "/PhysxSchemaAddition/resources"
Plug.Registry().RegisterPlugins(physxSchemaAdditionPath)
omniUsdPhysicsDeformablePath = pluginsRoot + "/OmniUsdPhysicsDeformableSchema/resources"
Plug.Registry().RegisterPlugins(omniUsdPhysicsDeformablePath)
