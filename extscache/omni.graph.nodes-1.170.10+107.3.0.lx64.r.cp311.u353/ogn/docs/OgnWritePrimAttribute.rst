.. _omni_graph_nodes_WritePrimAttribute_3:

.. _omni_graph_nodes_WritePrimAttribute:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Write Prim Attribute
    :keywords: lang-en omnigraph node sceneGraph threadsafe WriteOnly nodes write-prim-attribute


Write Prim Attribute
====================

.. <description>

Given a path to a prim on the current USD stage and the name of an attribute on  that prim, sets the value of that attribute.  Does nothing if the given Prim or attribute can not be found.  If the attribute is found but it is not a compatible type, an error will be issued.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "Signal to the graph that this node is ready to be executed.", "None"
    "Layer Identifier (*inputs:layerIdentifier*)", "``token``", "Identifier of the USD layer to export data to. Identifier can be empty, ""<Session Layer>"", ""<Root Layer>"" or the identifier of a sublayer. If empty or invalid, data will be exported to the current layer. This is only used when ""Persist To USD"" is enabled.", ""
    "Attribute Name (*inputs:name*)", "``token``", "The name of the attribute to set on the specified prim", ""
    "Prim (*inputs:prim*)", "``target``", "The prim to be modified when 'usePath' is false", "None"
    "Prim Path (*inputs:primPath*)", "``token``", "The path of the prim to be modified when 'usePath' is true", ""
    "Persist To USD (*inputs:usdWriteBack*)", "``bool``", "Whether or not the value should be written back to USD, or kept a Fabric only value", "True"
    "Use Path (*inputs:usePath*)", "``bool``", "When true, the 'primPath' attribute is used as the path to the prim being read, otherwise it will read the connection at the 'prim' attribute", "False"
    "Value (*inputs:value*)", "``any``", "The new value to be written", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Signal to the graph that execution can continue downstream.", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Correctly Setup (*state:correctlySetup*)", "``bool``", "Whether or not the instance is properly setup", "False"
    "Dest Attrib (*state:destAttrib*)", "``uint64``", "A TokenC to the destination attrib", "None"
    "Dest Path (*state:destPath*)", "``uint64``", "A PathC to the destination prim", "None"
    "Dest Path Token (*state:destPathToken*)", "``uint64``", "The TokenC version of destPath'", "None"
    "Layer Identifier (*state:layerIdentifier*)", "``token``", "The prefetched layer identifier.", "None"
    "Resolved Layer Identifier (*state:resolvedLayerIdentifier*)", "``token``", "The prefetched full layer path.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.WritePrimAttribute"
    "Version", "3"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.nodes.WritePrimAttribute.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Write Prim Attribute"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnWritePrimAttributeDatabase"
    "Python Module", "omni.graph.nodes"

