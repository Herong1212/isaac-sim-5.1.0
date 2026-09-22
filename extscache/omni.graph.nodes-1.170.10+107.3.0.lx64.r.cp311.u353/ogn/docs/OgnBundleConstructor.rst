.. _omni_graph_nodes_BundleConstructor_1:

.. _omni_graph_nodes_BundleConstructor:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Bundle Constructor
    :keywords: lang-en omnigraph node bundle nodes bundle-constructor


Bundle Constructor
==================

.. <description>

This node creates a bundle mirroring all of the dynamic input attributes that have been added to it. If no dynamic attributes exist then the bundle will be empty. See the 'InsertAttribute' node for something that can construct a bundle from existing connected attributes.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Constructed Bundle (*outputs:bundle*)", "``bundle``", "The bundle consisting of copies of all of the dynamic input attributes.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.BundleConstructor"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.nodes.BundleConstructor.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Bundle Constructor"
    "Categories", "bundle"
    "Generated Class Name", "OgnBundleConstructorDatabase"
    "Python Module", "omni.graph.nodes"

