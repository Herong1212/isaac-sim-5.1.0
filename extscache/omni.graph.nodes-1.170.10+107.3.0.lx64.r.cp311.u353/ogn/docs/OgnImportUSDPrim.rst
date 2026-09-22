.. _omni_graph_ImportUSDPrim_1:

.. _omni_graph_ImportUSDPrim:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: import USD prim data
    :keywords: lang-en omnigraph node graph import-u-s-d-prim


import USD prim data
====================

.. <description>

Imports data from a USD prim into attributes in an output bundle This node is deprecated, Use ReadPrim nodes instead

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Apply Skel Binding (*inputs:applySkelBinding*)", "``bool``", "If the input USD prim is a Mesh, and has SkelBindingAPI schema applied, compute skinned points and normals.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Apply Transform (*inputs:applyTransform*)", "``bool``", "If importAttributes is true, apply the transform necessary to transform any transforming attributes into the space of this node.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Attributes To Import (*inputs:attrNamesToImport*)", "``token``", "Comma or space separated text, listing the names of attributes in the input data to be imported  or empty to import all attributes.", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "Compute Bounding Box (*inputs:computeBoundingBox*)", "``bool``", "Compute and store local bounding box of a prim and its children.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Import Attributes (*inputs:importAttributes*)", "``bool``", "Import attribute data from the USD prim.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Import Path (*inputs:importPath*)", "``bool``", "Record the input USD prim's path into the output bundle in an attribute named ""primPath"".", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Import Primvar Metadata (*inputs:importPrimvarMetadata*)", "``bool``", "Import metadata like the interpolation type for primvars, and store it as attributes in the output bundle.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Import Time (*inputs:importTime*)", "``bool``", "Record the usdTimecode above into the output bundle in an attribute named ""primTime"".", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Import Transform (*inputs:importTransform*)", "``bool``", "Record the transform required to take any attributes of the input USD prim  into the space of this node, i.e. the world transform of the input prim times the  inverse world transform of this node, into the output bundle in an attribute named ""transform"".", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Import Type (*inputs:importType*)", "``bool``", "Deprecated, prim type is always imported", "True"
    "", "Metadata", "*hidden* = true", ""
    "", "Metadata", "*displayGroup* = parameters", ""
    "Attributes To Rename (*inputs:inputAttrNames*)", "``token``", "Comma or space separated text, listing the names of attributes in the input data to be renamed", ""
    "Keep Prims Separate (*inputs:keepPrimsSeparate*)", "``bool``", "Prefix output attribute names with ""prim"" followed by a unique number and a colon,  to keep the attributes for separate input prims separate.  The prim paths will  be in the ""primPaths"" token array attribute.", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "New Attribute Names (*inputs:outputAttrNames*)", "``token``", "Comma or space separated text, listing the new names for the attributes listed in inputAttrNames", ""
    "Prim (*inputs:prim*)", "``bundle``", "The USD prim from which to import data.", "None"
    "Rename Attributes (*inputs:renameAttributes*)", "``bool``", "If true, attributes listed in ""inputAttrNames"" will be imported to attributes with the names specified in ""outputAttrNames"".", "False"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Time Varying Attributes (*inputs:timeVaryingAttributes*)", "``bool``", "Check whether the USD attributes are time-varying and if so, import their data at the time ""usdTimecode"".", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Usd Timecode (*inputs:usdTimecode*)", "``double``", "The time at which to evaluate the transform of the USD prim.", "0"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Output (*outputs:output*)", "``bundle``", "Output bundle containing all of the imported data.", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Apply Skel Binding (*state:prevApplySkelBinding*)", "``bool``", "Value of ""applySkelBinding"" input from previous run", "None"
    "Prev Apply Transform (*state:prevApplyTransform*)", "``bool``", "Value of ""applyTransform"" input from previous run", "None"
    "Prev Attr Names To Import (*state:prevAttrNamesToImport*)", "``token``", "Value of ""attrNamesToImport"" input from previous run", "None"
    "Prev Compute Bounding Box (*state:prevComputeBoundingBox*)", "``bool``", "Value of ""computeBoundingBox"" input from previous run", "None"
    "Prev Import Attributes (*state:prevImportAttributes*)", "``bool``", "Value of ""importAttributes"" input from previous run", "None"
    "Prev Import Path (*state:prevImportPath*)", "``bool``", "Value of ""importPath"" input from previous run", "None"
    "Prev Import Primvar Metadata (*state:prevImportPrimvarMetadata*)", "``bool``", "Value of ""importPrimvarMetadata"" input from previous run", "None"
    "Prev Import Time (*state:prevImportTime*)", "``bool``", "Value of ""importTime"" input from previous run", "None"
    "Prev Import Transform (*state:prevImportTransform*)", "``bool``", "Value of ""importTransform"" input from previous run", "None"
    "Prev Import Type (*state:prevImportType*)", "``bool``", "Value of ""importType"" input from previous run", "None"
    "Prev Input Attr Names (*state:prevInputAttrNames*)", "``token``", "Value of ""inputAttrNames"" input from previous run", "None"
    "Prev Inv Node Transform (*state:prevInvNodeTransform*)", "``matrixd[4]``", "Inverse transform of the node prim from the previous run.", "None"
    "Prev Keep Prims Separate (*state:prevKeepPrimsSeparate*)", "``bool``", "Value of ""keepPrimsSeparate"" input from previous run", "None"
    "Prev Only Import Specified (*state:prevOnlyImportSpecified*)", "``bool``", "Value of ""onlyImportSpecified"" input from previous run", "None"
    "Prev Output Attr Names (*state:prevOutputAttrNames*)", "``token``", "Value of ""outputAttrNames"" input from previous run", "None"
    "Prev Paths (*state:prevPaths*)", "``token[]``", "Array of paths from the previous run.", "None"
    "Prev Rename Attributes (*state:prevRenameAttributes*)", "``bool``", "Value of ""renameAttributes"" input from previous run", "None"
    "Prev Time Varying Attributes (*state:prevTimeVaryingAttributes*)", "``bool``", "Value of ""timeVaryingAttributes"" input from previous run", "None"
    "Prev Transforms (*state:prevTransforms*)", "``matrixd[4][]``", "Array of transforms from the previous run.", "None"
    "Prev Usd Timecode (*state:prevUsdTimecode*)", "``double``", "Value of ""usdTimecode"" input from previous run", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.ImportUSDPrim"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Icon", "ogn/icons/omni.graph.ImportUSDPrim.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "hidden", "true"
    "uiName", "import USD prim data"
    "Generated Class Name", "OgnImportUSDPrimDatabase"
    "Python Module", "omni.graph.nodes"

