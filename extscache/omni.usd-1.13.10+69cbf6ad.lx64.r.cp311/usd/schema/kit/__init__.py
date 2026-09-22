__all__ = []

import os
import importlib

from pxr import Plug

module_carb_tokens = importlib.import_module('carb.tokens')

pluginsRoot = os.path.join(
   os.path.normpath(module_carb_tokens.get_tokens_interface().resolve("${omni.usd.core}")), "bin"
)
kitSchemaPath = pluginsRoot + '/usd/omniKit/resources'

Plug.Registry().RegisterPlugins(kitSchemaPath)
