.. _omni_graph_nodes_AppendTargetPaths_1:

.. _omni_graph_nodes_AppendTargetPaths:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Append Target Paths
    :keywords: lang-en omnigraph node sceneGraph threadsafe nodes append-target-paths


Append Target Paths
===================

.. <description>

Generates new targets by appending relative paths. Array inputs will be appended element-wise.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Input0 (*inputs:input0*)", "``['string', 'token', 'token[]']``", "The relative path to append. Must not start or end with /. (ex. Cube, Xform/Cube).", "None"
    "Root Targets (*inputs:rootTargets*)", "``target``", "The targets to append relative paths to.  If empty uses the stage root.", "None"
    "", "Metadata", "*allowMultiInputs* = 1", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Targets (*outputs:targets*)", "``target``", "The new target with paths appended. (ex. /World/Cube)", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.AppendTargetPaths"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Append Target Paths"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnAppendTargetPathsDatabase"
    "Python Module", "omni.graph.nodes"

