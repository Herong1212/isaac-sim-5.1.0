.. _omni_graph_nodes_InsertAttribute_1:

.. _omni_graph_nodes_InsertAttribute:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Insert Attribute
    :keywords: lang-en omnigraph node bundle nodes insert-attribute


Insert Attribute
================

.. <description>

Copies all attributes from an input bundle to the output bundle, as well as copying an additional 'attrToInsert' attribute from the node itself with a specified name.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute To Insert (*inputs:attrToInsert*)", "``any``", "The the attribute to be copied from the node to the output bundle", "None"
    "Original Bundle (*inputs:data*)", "``bundle``", "Initial bundle of attributes", "None"
    "Attribute Name (*inputs:outputAttrName*)", "``token``", "The name of the new output attribute in the bundle", "attr0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle With Inserted Attribute (*outputs:data*)", "``bundle``", "Bundle of input attributes with the new one inserted with the specified name", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.InsertAttribute"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Insert Attribute"
    "Categories", "bundle"
    "Generated Class Name", "OgnInsertAttrDatabase"
    "Python Module", "omni.graph.nodes"

