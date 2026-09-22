.. _omni_graph_nodes_CopyAttribute_1:

.. _omni_graph_nodes_CopyAttribute:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Copy Attributes From Bundles
    :keywords: lang-en omnigraph node bundle nodes copy-attribute


Copy Attributes From Bundles
============================

.. <description>

Copies all attributes from one input bundle and specified attributes from a second input bundle to the output bundle.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Full Bundle To Copy (*inputs:fullData*)", "``bundle``", "Collection of attributes to fully copy to the output", "None"
    "Extracted Names For Partial Copy (*inputs:inputAttrNames*)", "``token``", "Comma or space separated text, listing the names of attributes to copy from partialData", ""
    "New Names For Partial Copy (*inputs:outputAttrNames*)", "``token``", "Comma or space separated text, listing the new names of attributes copied from partialData", ""
    "Partial Bundle To Copy (*inputs:partialData*)", "``bundle``", "Collection of attributes from which to select named attributes", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle Of Copied Attributes (*outputs:data*)", "``bundle``", "Collection of attributes consisting of all attributes from input 'fullData' and selected inputs from input 'partialData'", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.CopyAttribute"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Copy Attributes From Bundles"
    "Categories", "bundle"
    "Generated Class Name", "OgnCopyAttrDatabase"
    "Python Module", "omni.graph.nodes"

