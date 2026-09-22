.. _omni_graph_nodes_AttributeType_1:

.. _omni_graph_nodes_AttributeType:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Extract Attribute Type Information
    :keywords: lang-en omnigraph node bundle threadsafe nodes attribute-type


Extract Attribute Type Information
==================================

.. <description>

Queries information about the type of a specified attribute in an input bundle

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute To Query (*inputs:attrName*)", "``token``", "The name of the attribute to be queried", "input"
    "Bundle To Examine (*inputs:data*)", "``bundle``", "Bundle of attributes to examine", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute Array Depth (*outputs:arrayDepth*)", "``int``", "Zero for a single value, one for an array, two for an array of arrays. Set to -1 if the named attribute was not in the bundle.", "None"
    "Attribute Base Type (*outputs:baseType*)", "``int``", "An integer representing the type of the individual components. Set to -1 if the named attribute was not in the bundle.", "None"
    "Attribute Component Count (*outputs:componentCount*)", "``int``", "Number of components in each tuple, e.g. one for float, three for point3f, 16 for matrix4d. Set to -1 if the named attribute was not in the bundle.", "None"
    "Full Attribute Type (*outputs:fullType*)", "``int``", "A single int representing the full type information. Set to -1 if the named attribute was not in the bundle.", "None"
    "Attribute Role (*outputs:role*)", "``int``", "An integer representing semantic meaning of the type, e.g. point3f vs. normal3f vs. vector3f vs. float3. Set to -1 if the named attribute was not in the bundle.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.AttributeType"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Extract Attribute Type Information"
    "Categories", "bundle"
    "Generated Class Name", "OgnAttrTypeDatabase"
    "Python Module", "omni.graph.nodes"

