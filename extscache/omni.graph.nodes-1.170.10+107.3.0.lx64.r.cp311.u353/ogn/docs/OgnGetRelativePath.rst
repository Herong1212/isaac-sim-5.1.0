.. _omni_graph_nodes_GetRelativePath_1:

.. _omni_graph_nodes_GetRelativePath:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Relative Path
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes get-relative-path


Get Relative Path
=================

.. <description>

Generates a path token relative to anchor from path.(ex. (/World, /World/Cube) -> /Cube)

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Anchor (*inputs:anchor*)", "``token``", "Path token to compute relative to (ex. /World)", ""
    "Path (*inputs:path*)", "``['token', 'token[]']``", "Path token to convert to a relative path (ex. /World/Cube)", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Relative Path (*outputs:relativePath*)", "``['token', 'token[]']``", "Relative path token (ex. /Cube)", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Anchor (*state:anchor*)", "``token``", "Snapshot of previously seen rootPath", "None"
    "Path (*state:path*)", "``token``", "Snapshot of previously seen path", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetRelativePath"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Relative Path"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnGetRelativePathDatabase"
    "Python Module", "omni.graph.nodes"

