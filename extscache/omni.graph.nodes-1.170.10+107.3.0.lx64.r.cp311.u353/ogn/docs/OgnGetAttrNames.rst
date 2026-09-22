.. _omni_graph_nodes_GetAttributeNames_1:

.. _omni_graph_nodes_GetAttributeNames:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Attribute Names From Bundle
    :keywords: lang-en omnigraph node bundle threadsafe nodes get-attribute-names


Get Attribute Names From Bundle
===============================

.. <description>

Retrieves the names of all of the attributes contained in the input bundle, optionally sorted.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle To Examine (*inputs:data*)", "``bundle``", "Collection of attributes from which to extract names", "None"
    "Sort Output (*inputs:sort*)", "``bool``", "If true, the names will be output in sorted order (default, for consistency). If false, the order is not be guaranteed to be consistent between systems or over time, so do not rely on the order downstream in this case.", "True"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute Names (*outputs:output*)", "``token[]``", "Names of all of the attributes contained in the input bundle", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.GetAttributeNames"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Attribute Names From Bundle"
    "Categories", "bundle"
    "Generated Class Name", "OgnGetAttrNamesDatabase"
    "Python Module", "omni.graph.nodes"

