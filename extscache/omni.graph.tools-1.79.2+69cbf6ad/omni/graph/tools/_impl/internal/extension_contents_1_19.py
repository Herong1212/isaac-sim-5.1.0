"""Implementation of the OmniGraph extension contents management class for code generator version 1.19 and above.
TODO: This requires integration into the build system and should be done as part of the performance improvements
      for node registration https://nvidia-omniverse.atlassian.net/browse/OM-70723
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType

from .extension_contents_base import ExtensionContentsBase
from .logging_utils import LOG


# ==============================================================================================================
class ExtensionContentsV119(ExtensionContentsBase):
    """Variation of the ExtensionContents class that handles the case of node types that were generated in version
    1.18 of omni.graph.tools or earlier, where the module path contains the generated ogn/ directory and has all of
    the nodes defined in its subdirectories.
    """

    def __init__(self, ext_id: str, module: ModuleType, ext_path: str | Path):
        super().__init__(ext_id, module, ext_path)
        _ = LOG.disabled or LOG.info(
            "Creating new style extension manager for %s in module %s at %s", ext_id, module, ext_path
        )

    # --------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        return f"V1.19 {super().__str__()}"

    # --------------------------------------------------------------------------------------------------------------
    def scan_for_nodes(self):
        pass

    # --------------------------------------------------------------------------------------------------------------
    def ensure_files_up_to_date(self):
        pass

    # --------------------------------------------------------------------------------------------------------------
    def do_python_imports(self):
        return (None, None)
