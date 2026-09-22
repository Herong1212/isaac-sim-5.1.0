.. _omni_graph_nodes_ReadPrimRelationship_1:

.. _omni_graph_nodes_ReadPrimRelationship:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Prim Relationship
    :keywords: lang-en omnigraph node sceneGraph threadsafe ReadOnly nodes read-prim-relationship


Read Prim Relationship
======================

.. <description>

Reads the target(s) of a relationship on a given prim

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Relationship Name (*inputs:name*)", "``token``", "The name of the relationship to read", ""
    "Prim (*inputs:prim*)", "``target``", "The prim with the named relationship to read", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*outputs:value*)", "``target``", "The relationship target(s)", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Correctly Setup (*state:correctlySetup*)", "``bool``", "Whether or not the instance is properly setup", "False"
    "Name (*state:name*)", "``token``", "The prefetched relationship name", "None"
    "Prim (*state:prim*)", "``target``", "The currently prefetched prim", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadPrimRelationship"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "usd"
    "uiName", "Read Prim Relationship"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnReadPrimRelationshipDatabase"
    "Python Module", "omni.graph.nodes"

