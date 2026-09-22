.. _omni_graph_nodes_ExtractPrim_1:

.. _omni_graph_nodes_ExtractPrim:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Extract Prim
    :keywords: lang-en omnigraph node bundle nodes extract-prim


Extract Prim
============

.. <description>

Extract a child bundle that contains a primitive with requested path/prim. This node is designed to work with Multiple Primitives in a Bundle. It searches for a child bundle in the input bundle, with 'sourcePrimPath' that matches 'inputs:prim' or 'inputs:primPath'. The found child bundle will be provided to 'outputs_primBundle', or invalid, bundle otherwise.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim (*inputs:prim*)", "``target``", "The prim to be extracted from Multiple Primitives in Bundle.", "None"
    "Prim Path (*inputs:primPath*)", "``path``", "The path of the prim to be extracted from Multiple Primitives in Bundle.", ""
    "Prims Bundle (*inputs:prims*)", "``bundle``", "The Multiple Primitives in Bundle to extract from.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim Bundle (*outputs:primBundle*)", "``bundle``", "The extracted Single Primitive in Bundle", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ExtractPrim"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Extract Prim"
    "Categories", "bundle"
    "Generated Class Name", "OgnExtractPrimDatabase"
    "Python Module", "omni.graph.nodes"

