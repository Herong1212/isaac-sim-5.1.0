.. _omni_graph_nodes_AppendPath_1:

.. _omni_graph_nodes_AppendPath:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Append Path
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes append-path


Append Path
===========

.. <description>

Generates a path token by appending the given relative path token to the given root or prim path token

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Path (*inputs:path*)", "``['token', 'token[]']``", "The path token(s) to be appended to. Must be a base or prim path (ex. /World)", "None"
    "Suffix (*inputs:suffix*)", "``token``", "The prim or prim-property path to append (ex. Cube or Cube.attr)", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Path (*outputs:path*)", "``['token', 'token[]']``", "The new path token(s) (ex. /World/Cube or /World/Cube.attr)", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Path (*state:path*)", "``token``", "Snapshot of previously seen path", "None"
    "Suffix (*state:suffix*)", "``token``", "Snapshot of previously seen suffix", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.AppendPath"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "paths"
    "uiName", "Append Path"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnAppendPathDatabase"
    "Python Module", "omni.graph.nodes"

