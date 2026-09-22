import os

from pxr import Plug

pluginsRoot = os.path.join(os.path.dirname(__file__), '../../../plugins')
geospatialSchemaPath = pluginsRoot + '/omniGeospatial/resources'

Plug.Registry().RegisterPlugins(geospatialSchemaPath)