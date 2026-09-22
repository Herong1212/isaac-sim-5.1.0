.. _omni_graph_ExportUSDPrim_1:

.. _omni_graph_ExportUSDPrim:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: export USD prim data
    :keywords: lang-en omnigraph node WriteOnly graph export-u-s-d-prim


export USD prim data
====================

.. <description>

Exports data from an input bundle into a USD prim This node is deprecated, Use WritePrim nodes instead

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Apply Transform (*inputs:applyTransform*)", "``bool``", "If true, apply the transform necessary to transform any transforming attributes from the space of the node into the space of the specified prim.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Attributes To Export (*inputs:attrNamesToExport*)", "``token``", "Comma or space separated text, listing the names of attributes in the input data to be exported  or empty to import all attributes.", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "Bundle (*inputs:bundle*)", "``bundle``", "The bundle from which data should be exported.", "None"
    "Attributes To Exclude (*inputs:excludedAttrNames*)", "``token``", "Attributes to be excluded from being exported", ""
    "Export to Root Layer (*inputs:exportToRootLayer*)", "``bool``", "If true, prims are exported in the root layer, otherwise the layer specified by ""layerName"" is used.", "True"
    "Attributes To Rename (*inputs:inputAttrNames*)", "``token``", "Comma or space separated text, listing the names of attributes in the input data to be renamed", ""
    "Layer Name (*inputs:layerName*)", "``token``", "Identifier of the layer to export to if ""exportToRootLayer"" is false, or leave this blank to export to the session layer", ""
    "Only Export To Existing (*inputs:onlyExportToExisting*)", "``bool``", "If true, only attributes that already exist in the specified output prim will have data transferred to them from the input bundle.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "New Attribute Names (*inputs:outputAttrNames*)", "``token``", "Comma or space separated text, listing the new names for the attributes listed in inputAttrNames", ""
    "Prim Path From Bundle (*inputs:primPathFromBundle*)", "``bool``", "When true, if there is a ""primPath"" token attribute inside the bundle, that will be the path of the USD prim to write to,  else the ""outputs:prim"" attribute below will be used for the USD prim path.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Export to Root Layer (*inputs:removeMissingAttrs*)", "``bool``", "If true, any attributes on the USD prim(s) being written to, that aren't in the input data,  will be removed from the USD prim(s).", "False"
    "Rename Attributes (*inputs:renameAttributes*)", "``bool``", "If true, attributes listed in ""inputAttrNames"" will be exported to attributes with the names specified in ""outputAttrNames"".  Note: to avoid potential issues with redundant attributes being created while typing, keep this off until after  specifying all input and output attribute names.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Time Varying Attributes (*inputs:timeVaryingAttributes*)", "``bool``", "Check whether the USD attributes should be time-varying and if so, export their data to a time sample at the time ""usdTimecode"".", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Usd Timecode (*inputs:usdTimecode*)", "``double``", "The time at which to evaluate the transform of the USD prim for applyTransform.", "0"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim (*outputs:prim*)", "``bundle``", "The USD prim(s) to which data should be exported if primPathFromBundle is false or if the bundle doesn't have a ""primPath"" token attribute.   Note: this is really an input, since the node just receives the path to the prim.  The node does not contain the prim.", "None"
    "", "Metadata", "*hidden* = true", ""


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Apply Transform (*state:prevApplyTransform*)", "``bool``", "Value of ""applyTransform"" input from previous run", "None"
    "Prev Attr Names To Export (*state:prevAttrNamesToExport*)", "``token``", "Value of ""attrNamesToExport"" input from previous run", "None"
    "Prev Bundle Dirty ID (*state:prevBundleDirtyID*)", "``uint64``", "Dirty ID of input bundle from previous run", "None"
    "Prev Excluded Attr Names (*state:prevExcludedAttrNames*)", "``token``", "Value of ""excludedAttrNames"" input from previous run", "None"
    "Prev Export To Root Layer (*state:prevExportToRootLayer*)", "``bool``", "Value of ""exportToRootLayer"" input from previous run", "None"
    "Prev Input Attr Names (*state:prevInputAttrNames*)", "``token``", "Value of ""inputAttrNames"" input from previous run", "None"
    "Prev Layer Name (*state:prevLayerName*)", "``token``", "Value of ""layerName"" input from previous run", "None"
    "Prev Only Export To Existing (*state:prevOnlyExportToExisting*)", "``bool``", "Value of ""onlyExportToExisting"" input from previous run", "None"
    "Prev Output Attr Names (*state:prevOutputAttrNames*)", "``token``", "Value of ""outputAttrNames"" input from previous run", "None"
    "Prev Prim Dirty I Ds (*state:prevPrimDirtyIDs*)", "``uint64[]``", "Dirty IDs of input prims from previous run", "None"
    "Prev Prim Path From Bundle (*state:prevPrimPathFromBundle*)", "``bool``", "Value of ""primPathFromBundle"" input from previous run", "None"
    "Prev Remove Missing Attrs (*state:prevRemoveMissingAttrs*)", "``bool``", "Value of ""removeMissingAttrs"" input from previous run", "None"
    "Prev Rename Attributes (*state:prevRenameAttributes*)", "``bool``", "Value of ""renameAttributes"" input from previous run", "None"
    "Prev Time Varying Attributes (*state:prevTimeVaryingAttributes*)", "``bool``", "Value of ""timeVaryingAttributes"" input from previous run", "None"
    "Prev Usd Timecode (*state:prevUsdTimecode*)", "``double``", "Value of ""usdTimecode"" input from previous run", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ExportUSDPrim"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.ExportUSDPrim.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "export USD prim data"
    "hidden", "true"
    "__tokens", "{""primPath"": ""primPath"", ""primType"": ""primType"", ""primTime"": ""primTime"", ""primCount"": ""primCount"", ""transform"": ""transform""}"
    "Generated Class Name", "OgnExportUSDPrimDatabase"
    "Python Module", "omni.graph.nodes"

