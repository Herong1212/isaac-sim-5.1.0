"""Temporary measure for backwards compatibility to import bindings from old module structure.

The generated PyBind libraries used to be in omni/graph/core/bindings/. They were moved to
omni/graph/core to correspond to the example extension structure for Python imports. All this
file does is make the old import "import omni.graph.core.bindings._omni_graph_core" work the
same as the new one "import omni.graph.core._omni_graph_core"
"""

import omni.graph.core._omni_graph_core as bindings

_omni_graph_core = bindings
