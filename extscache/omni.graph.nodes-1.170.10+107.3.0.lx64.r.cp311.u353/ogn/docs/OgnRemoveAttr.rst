.. _omni_graph_nodes_RemoveAttribute_2:

.. _omni_graph_nodes_RemoveAttribute:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Remove Attributes From Bundles
    :keywords: lang-en omnigraph node bundle nodes remove-attribute


Remove Attributes From Bundles
==============================

.. <description>

Copies all attributes from an input bundle to the output bundle, except for any specified to be removed.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Allow Remove Prim Internal (*inputs:allowRemovePrimInternal*)", "``bool``", "When on, then primitive internal attributes can be removed('sourcePrimPath' etc...)", "False"
    "Attributes To Remove (*inputs:attrNamesToRemove*)", "``token``", "A list of wildcard patterns used to match the attribute names that are to be removed from the output bundle  Supported syntax of wildcard pattern:     '*' - match an arbitrary number of any characters     '?' - match any single character     '^' - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['points', 'faceVertexCount', 'faceVertexIndices', 'size']     '*' - match any     '* ^points' - match any, but exclude 'points'     '* ^face*' - match any, but exclude 'faceVertexCount' and 'faceVertexIndices'", ""
    "Original Bundle (*inputs:data*)", "``bundle``", "Collection of attributes to be partially copied to the output", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle After Removal (*outputs:data*)", "``bundle``", "Final bundle of attributes, with the attributes specified by attrNamesToRemove omitted", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.RemoveAttribute"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Remove Attributes From Bundles"
    "Categories", "bundle"
    "Generated Class Name", "OgnRemoveAttrDatabase"
    "Python Module", "omni.graph.nodes"

