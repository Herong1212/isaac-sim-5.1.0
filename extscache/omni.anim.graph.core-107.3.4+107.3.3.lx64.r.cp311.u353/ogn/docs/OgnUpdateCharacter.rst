.. _omni_anim_graph_UpdateCharacter_1:

.. _omni_anim_graph_UpdateCharacter:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Update Animation Graph
    :keywords: lang-en omnigraph node animation graph update-character


Update Animation Graph
======================

.. <description>

Allow manual updating processing of an animation graph on a character.

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.graph.core<ext_omni_anim_graph_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Delta Time (*inputs:deltaTime*)", "``float``", "The delta time for update.", "0"
    "Exec In (*inputs:execIn*)", "``execution``", "Input execution state", "None"
    "Skel Root Path (*inputs:skelRootPath*)", "``token``", "The prim path of a UsdSkelRoot to which has a AnimationGraph applied and assigned to it.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution", "None"
    "Pose (*outputs:pose*)", "``bundle``", "The character ouput pose.", "None"
    "", "Metadata", "*attrs* = ""{'uiName': 'Root Translation (World Space)', 'type': 'float[3]', 'description': 'The character root translation in world space.'}"",""{'uiName': 'Root Rotation (World Space)', 'type': 'quatf[4]', 'description': 'The character root rotation (quaternion) in world space.'}"",""{'uiName': 'Skeleton Delta Translation (Skeleton Space)', 'type': 'float[3]', 'description': 'The character skeleton displacement(delta) translation in skeleton space.'}"",""{'uiName': 'Skeleton Delta Rotation (Skeleton Space)', 'type': 'quatf[4]', 'description': 'The character skeleton displacement(delta) rotation(quaternion) in skeleton space.'}"",""{'uiName': 'Joint Translations (Local Space)', 'type': 'float[3][]', 'description': 'The character joint positions in local space, based on the referenced skeleton.'}"",""{'uiName': 'Joint Rotations (Local Space)', 'type': 'quatf[4][]', 'description': 'The character joint rotations (quaternion) in local space, based on the referenced skeleton.'}""", ""


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Force Output To Inherent SkelAnimation (*state:forceOutputToInherentSkelAnimation*)", "``bool``", "if true, forces output to inherent SkelAnimation output.", "False"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.anim.graph.UpdateCharacter"
    "Version", "1"
    "Extension", "omni.anim.graph.core"
    "Icon", "ogn/icons/omni.anim.graph.UpdateCharacter.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Update Animation Graph"
    "__tokens", "[""rootTranslation"", ""rootRotation"", ""skeletonDeltaTranslation"", ""skeletonDeltaRotation"", ""jointTranslations"", ""jointRotations""]"
    "Categories", "animation"
    "__categoryDescriptions", "animation,Nodes dealing with Animation"
    "Generated Class Name", "OgnUpdateCharacterDatabase"
    "Python Module", "omni.anim.graph.core"

