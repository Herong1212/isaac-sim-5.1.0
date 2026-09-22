.. _omni_graph_nodes_ReadOmniGraphValue_1:

.. _omni_graph_nodes_ReadOmniGraphValue:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read OmniGraph Value
    :keywords: lang-en omnigraph node sceneGraph ReadOnly threadsafe nodes read-omni-graph-value


Read OmniGraph Value
====================

.. <description>

Imports a data value from the Fabric cache that is located at the given path and attribute name. This is for data that is not already present in OmniGraph as that data can be accessed through a direct connection to the underlying OmniGraph node.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Name (*inputs:name*)", "``token``", "The name of the attribute to be queried", ""
    "Path (*inputs:path*)", "``path``", "The path to the Fabric data bucket in which the attribute being queried lives.", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*outputs:value*)", "``any``", "The attribute value", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadOmniGraphValue"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Read OmniGraph Value"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnReadOmniGraphValueDatabase"
    "Python Module", "omni.graph.nodes"

