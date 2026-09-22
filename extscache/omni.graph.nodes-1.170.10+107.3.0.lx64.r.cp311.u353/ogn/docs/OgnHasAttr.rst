.. _omni_graph_nodes_HasAttribute_1:

.. _omni_graph_nodes_HasAttribute:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Has Attribute
    :keywords: lang-en omnigraph node bundle threadsafe nodes has-attribute


Has Attribute
=============

.. <description>

Inspect an input bundle for a named attribute, setting output to true if it exists

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute To Find (*inputs:attrName*)", "``token``", "Name of the attribute to look for in the bundle", "points"
    "Bundle To Check (*inputs:data*)", "``bundle``", "Collection of attributes that may contain the named attribute", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Is Attribute In Bundle (*outputs:output*)", "``bool``", "True if the named attribute was found in the bundle", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.HasAttribute"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Has Attribute"
    "Categories", "bundle"
    "Generated Class Name", "OgnHasAttrDatabase"
    "Python Module", "omni.graph.nodes"

