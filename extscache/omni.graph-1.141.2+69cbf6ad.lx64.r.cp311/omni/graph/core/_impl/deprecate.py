r"""This module has moved to omni.graph.tools.deprecate. This file is only here for backward compatibility.
  _____   ______  _____   _____   ______  _____         _______  ______  _____
 |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
 | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
 | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
 | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
 |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/
"""

from omni.graph.tools import DeprecatedClass  # noqa
from omni.graph.tools import DeprecatedImport  # noqa
from omni.graph.tools import DeprecateMessage  # noqa
from omni.graph.tools import RenamedClass  # noqa
from omni.graph.tools import deprecated_function  # noqa

DeprecateMessage.deprecated("omni.graph.core.deprecate is deprecated. Use omni.graph.tools.deprecate instead.")
