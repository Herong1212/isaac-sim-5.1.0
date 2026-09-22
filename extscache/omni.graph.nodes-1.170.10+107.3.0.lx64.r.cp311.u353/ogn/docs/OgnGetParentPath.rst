.. _omni_graph_nodes_GetParentPath_1:

.. _omni_graph_nodes_GetParentPath:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Parent Path
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes get-parent-path


Get Parent Path
===============

.. <description>

Generates a parent path token from another path token. (ex. /World/Cube -> /World)

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Path (*inputs:path*)", "``['token', 'token[]']``", "One or more path tokens to compute a parent path from. (ex. /World/Cube)", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Parent Path (*outputs:parentPath*)", "``['token', 'token[]']``", "Parent path token (ex. /World)", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Path (*state:path*)", "``token``", "Snapshot of previously seen path", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetParentPath"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Parent Path"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnGetParentPathDatabase"
    "Python Module", "omni.graph.nodes"

