.. _omni_graph_nodes_GetPrimRelationship_3:

.. _omni_graph_nodes_GetPrimRelationship:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Prim Relationship
    :keywords: lang-en omnigraph node sceneGraph threadsafe ReadOnly nodes get-prim-relationship


Get Prim Relationship
=====================

.. <description>

DEPRECATED - Use ReadPrimRelationship!

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Relationship Name (*inputs:name*)", "``token``", "Name of the relationship property", ""
    "Prim Path (*inputs:path*)", "``token``", "Path of the prim with the relationship property", "None"
    "Prim (*inputs:prim*)", "``target``", "The prim with the relationship", "None"
    "Use Path (*inputs:usePath*)", "``bool``", "When true, the 'path' attribute is used, otherwise it will read the connection at the 'prim' attribute.", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Paths (*outputs:paths*)", "``token[]``", "The prim paths for the given relationship", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetPrimRelationship"
    "Version", "3"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "Get Prim Relationship"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnGetPrimRelationshipDatabase"
    "Python Module", "omni.graph.nodes"

