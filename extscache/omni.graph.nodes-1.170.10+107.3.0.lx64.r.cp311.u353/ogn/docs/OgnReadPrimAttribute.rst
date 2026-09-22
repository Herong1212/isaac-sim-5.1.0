.. _omni_graph_nodes_ReadPrimAttribute_3:

.. _omni_graph_nodes_ReadPrimAttribute:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read Prim Attribute
    :keywords: lang-en omnigraph node sceneGraph threadsafe ReadOnly nodes read-prim-attribute


Read Prim Attribute
===================

.. <description>

Given a path to a prim on the current USD stage and the name of an attribute on that prim, gets the value of that attribute, at the global timeline value.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Attribute Name (*inputs:name*)", "``token``", "The name of the attribute to get on the specified prim.", ""
    "Prim (*inputs:prim*)", "``target``", "The prim to be read from when ""Use Path"" is false.", "None"
    "Prim Path (*inputs:primPath*)", "``token``", "The path of the prim to be modified when ""Use Path"" is true.", "None"
    "Time (*inputs:usdTimecode*)", "``timecode``", "The time at which to evaluate the transform of the USD prim attribute. A value of ""nan"" indicates that the default USD time stamp should be used.", "NaN"
    "Use Path (*inputs:usePath*)", "``bool``", "When true, the ""Prim Path"" attribute is used as the path to the prim being read, otherwise it will read the connection at the ""Prim"" attribute.", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*outputs:value*)", "``any``", "The attribute value", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Correctly Setup (*state:correctlySetup*)", "``bool``", "Whether or not the instance is properly setup", "False"
    "Import Path (*state:importPath*)", "``uint64``", "Path at which data has been imported", "None"
    "Reimport At Time (*state:reimportAtTime*)", "``bool``", "Internal flag that's used to help decide if the source attribute at the specified time needs to be reimported.", "None"
    "Src Attrib (*state:srcAttrib*)", "``uint64``", "A TokenC to the source attribute", "None"
    "Src Path (*state:srcPath*)", "``uint64``", "A PathC to the source prim", "None"
    "Src Path As Token (*state:srcPathAsToken*)", "``uint64``", "A TokenC to the source prim", "None"
    "Time (*state:time*)", "``double``", "The timecode at which we have imported the value", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ReadPrimAttribute"
    "Version", "3"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.nodes.ReadPrimAttribute.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "usd"
    "uiName", "Read Prim Attribute"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnReadPrimAttributeDatabase"
    "Python Module", "omni.graph.nodes"

