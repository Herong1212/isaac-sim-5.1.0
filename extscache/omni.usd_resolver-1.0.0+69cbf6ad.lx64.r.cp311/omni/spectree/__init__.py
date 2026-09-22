__all__ = []

import os
from pxr import Plug

pluginsRoot = os.path.join(os.path.dirname(__file__), '../../plugins/omni_usd_live/resources')

Plug.Registry().RegisterPlugins(pluginsRoot)
