.. _omni_graph_nodes_BundleInspector_4:

.. _omni_graph_nodes_BundleInspector:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Bundle Inspector
    :keywords: lang-en omnigraph node bundle nodes bundle-inspector


Bundle Inspector
================

.. <description>

This node creates independent outputs containing information about the contents of a bundle. It can be used for testing or debugging what is inside a bundle as it flows through the graph. The bundle is inspected recursively, so any bundles inside of the main bundle will have their contents added to the output as well. The bundle contents can be printed when the node executes, and it passes the input straight through unchanged, so you can insert this node between two nodes to inspect the data flowing through the graph.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle To Analyze (*inputs:bundle*)", "``bundle``", "The bundle to be inspected.", "None"
    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Inspect Depth (*inputs:inspectDepth*)", "``int``", "The depth that the inspector is going to traverse and print. For example, 0 means just attributes on the input bundles. 1 means its immediate children. -1 means the entire recursive contents of the bundle.", "1"
    "Print Contents (*inputs:print*)", "``bool``", "If true then the contents of 'Bundle To Analyze' will print when the node executes.", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Array Depths (*outputs:arrayDepths*)", "``int[]``", "List of the array depths of attributes present in the bundle.", "None"
    "Attribute Count (*outputs:attributeCount*)", "``uint64``", "Number of attributes present in the bundle. Every output that is an array type should have this number of elements in it.", "None"
    "Bundle Passthrough (*outputs:bundle*)", "``bundle``", "The input 'Bundle', passed through unchanged.", "None"
    "Child Count (*outputs:childCount*)", "``uint64``", "Number of child bundles present in the bundle.", "None"
    "Attribute Count (*outputs:count*)", "``uint64``", "Deprecated - Use 'Attribute Count' instead.", "None"
    "", "Metadata", "*hidden* = true", ""
    "Attribute Names (*outputs:names*)", "``token[]``", "List of the names of attributes present in the bundle.", "None"
    "Attribute Roles (*outputs:roles*)", "``token[]``", "List of the names of the roles of attributes present in the bundle.", "None"
    "Tuple Counts (*outputs:tupleCounts*)", "``int[]``", "List of the tuple counts of attributes present in the bundle.", "None"
    "Attribute Base Types (*outputs:types*)", "``token[]``", "List of the types of attributes present in the bundle.", "None"
    "Attribute Values (*outputs:values*)", "``token[]``", "List of the bundled attribute values, converted to token format.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.BundleInspector"
    "Version", "4"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.nodes.BundleInspector.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Bundle Inspector"
    "Categories", "bundle"
    "Generated Class Name", "OgnBundleInspectorDatabase"
    "Python Module", "omni.graph.nodes"

