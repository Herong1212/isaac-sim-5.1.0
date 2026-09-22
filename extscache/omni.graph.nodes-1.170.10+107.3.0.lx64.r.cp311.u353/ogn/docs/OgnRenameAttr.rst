.. _omni_graph_nodes_RenameAttribute_1:

.. _omni_graph_nodes_RenameAttribute:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Rename Attributes In Bundles
    :keywords: lang-en omnigraph node bundle nodes rename-attribute


Rename Attributes In Bundles
============================

.. <description>

Changes the names of attributes from an input bundle for the corresponding output bundle. Attributes whose names are not in the 'inputAttrNames' list will be copied from the input bundle to the output bundle without changing the name.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Original Attribute Bundle (*inputs:data*)", "``bundle``", "Collection of attributes to be renamed", "None"
    "Attributes To Rename (*inputs:inputAttrNames*)", "``token``", "Comma or space separated text, listing the names of attributes in the input data to be renamed", ""
    "New Attribute Names (*inputs:outputAttrNames*)", "``token``", "Comma or space separated text, listing the new names for the attributes listed in inputAttrNames", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle Of Renamed Attributes (*outputs:data*)", "``bundle``", "Final bundle of attributes, with attributes renamed based on inputAttrNames and outputAttrNames", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.RenameAttribute"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Rename Attributes In Bundles"
    "Categories", "bundle"
    "Generated Class Name", "OgnRenameAttrDatabase"
    "Python Module", "omni.graph.nodes"

