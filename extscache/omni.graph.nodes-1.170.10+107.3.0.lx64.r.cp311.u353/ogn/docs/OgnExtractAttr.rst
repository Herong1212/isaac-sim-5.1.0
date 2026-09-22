.. _omni_graph_nodes_ExtractAttribute_1:

.. _omni_graph_nodes_ExtractAttribute:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Extract Attribute
    :keywords: lang-en omnigraph node bundle threadsafe nodes extract-attribute


Extract Attribute
=================

.. <description>

Copies a single attribute from an input bundle to an output attribute directly on the node if it exists in the input bundle and matches the type of the output attribute

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute To Extract (*inputs:attrName*)", "``token``", "Name of the attribute to look for in the bundle", "points"
    "Bundle For Extraction (*inputs:data*)", "``bundle``", "Collection of attributes from which the named attribute is to be extracted", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Extracted Attribute (*outputs:output*)", "``any``", "The single attribute extracted from the input bundle", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ExtractAttribute"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Extract Attribute"
    "Categories", "bundle"
    "Generated Class Name", "OgnExtractAttrDatabase"
    "Python Module", "omni.graph.nodes"

