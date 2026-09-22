.. _omni_genproc_core_ScatterPointsModifier_1:

.. _omni_genproc_core_ScatterPointsModifier:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: scatter points modifier
    :keywords: lang-en omnigraph node core scatter-points-modifier


scatter points modifier
=======================

.. <description>

Post-modifier node for scatter points.

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Active (*inputs:active*)", "``bool``", "Is the Scatter Points Group node currently active?", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Bundle (*inputs:bundle*)", "``bundle``", "input bundle of points data", "None"
    "Ids (*inputs:ids*)", "``int[]``", "Ids of points to be modified", "[]"
    "Normals (*inputs:normals*)", "``float[3][]``", "Normals of points to be modified", "[]"
    "Object Indices (*inputs:objectIndices*)", "``int[]``", "Object Indices of points to be modified", "[]"
    "Positions (*inputs:positions*)", "``float[3][]``", "Positions of points to be modified", "[]"
    "Rotations (*inputs:rotations*)", "``float[3][]``", "Rotations of points to be modified", "[]"
    "Scales (*inputs:scales*)", "``float[3][]``", "Scales of points to be modified", "[]"
    "Tangents (*inputs:tangents*)", "``float[3][]``", "Tangents of points to be modified", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*outputs:bundle*)", "``bundle``", "output bundle of points data", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Active (*state:prevActive*)", "``bool``", "Previous active value for recompute test", "None"
    "Prev Ids (*state:prevIds*)", "``int[]``", "Previous ids of points to be modified", "[]"
    "Prev Normals (*state:prevNormals*)", "``float[3][]``", "Previous normals of points to be modified", "[]"
    "Prev Object Indices (*state:prevObjectIndices*)", "``int[]``", "Previous object indices of points to be modified", "[]"
    "Prev Positions (*state:prevPositions*)", "``float[3][]``", "Previous positions of points to be modified", "[]"
    "Prev Rotations (*state:prevRotations*)", "``float[3][]``", "Previous rotations of points to be modified", "[]"
    "Prev Scales (*state:prevScales*)", "``float[3][]``", "Previous scales of points to be modified", "[]"
    "Prev Tangents (*state:prevTangents*)", "``float[3][]``", "Previous tangents of points to be modified", "[]"
    "Remapped Ids From (*state:remappedIdsFrom*)", "``int[]``", "Remapped ids from", "None"
    "Remapped Ids To (*state:remappedIdsTo*)", "``int[]``", "Remapped ids to", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.ScatterPointsModifier"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "scatter points modifier"
    "__tokens", "{""points"": ""points"", ""rotations"": ""rotations"", ""scales"": ""scales"", ""tangents"": ""tangents"", ""normals"": ""normals"", ""objectIndices"": ""objectIndices""}"
    "Generated Class Name", "OgnScatterPointsModifierDatabase"
    "Python Module", "omni.genproc.core"

