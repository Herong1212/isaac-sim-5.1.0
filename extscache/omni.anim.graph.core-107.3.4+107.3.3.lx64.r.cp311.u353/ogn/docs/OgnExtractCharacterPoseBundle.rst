.. _omni_anim_graph_ExtractCharacterPoseBundle_1:

.. _omni_anim_graph_ExtractCharacterPoseBundle:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Extract Animation Graph Pose Bundle
    :keywords: lang-en omnigraph node animation graph extract-character-pose-bundle


Extract Animation Graph Pose Bundle
===================================

.. <description>

Extracts the pose as a bundle after the animation graph has executed.

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.graph.core<ext_omni_anim_graph_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Pose (*inputs:pose*)", "``bundle``", "The character input pose.", "None"
    "", "Metadata", "*attrs* = ""{'uiName': 'Root Translation (World Space)', 'type': 'float[3]', 'description': 'The character root translation in world space.'}"",""{'uiName': 'Root Rotation (World Space)', 'type': 'quatf[4]', 'description': 'The character root rotation (quaternion) in world space.'}"",""{'uiName': 'Skeleton Delta Translation (Skeleton Space)', 'type': 'float[3]', 'description': 'The character skeleton displacement(delta) translation in skeleton space.'}"",""{'uiName': 'Skeleton Rotation Displacement (Skeleton Space)', 'type': 'quatf[4]', 'description': 'The character skeleton displacement(delta) rotation(quaternion) in skeleton space.'}"",""{'uiName': 'Joint Translations (Local Space)', 'type': 'float[3][]', 'description': 'The character joint positions in local space, based on the referenced skeleton.'}"",""{'uiName': 'Joint Rotations (Local Space)', 'type': 'quatf[4][]', 'description': 'The character joint rotations (quaternion) in local space, based on the referenced skeleton.'}""", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Joint Rotations (Local Space) (*outputs:jointRotations*)", "``quatf[4][]``", "The character joint rotations (quaternion) in local space, based on the referenced skeleton.", "None"
    "Joint Translations (Local Space) (*outputs:jointTranslations*)", "``float[3][]``", "The character joint positions in local space, based on the referenced skeleton.", "None"
    "Root Rotation (World Space) (*outputs:rootRotation*)", "``quatf[4]``", "The character root rotation (quaternion) in world space.", "None"
    "Root Translation (World Space) (*outputs:rootTranslation*)", "``float[3]``", "The character root translation in world space.", "None"
    "Skeleton Delta Rotation (Skeleton Space) (*outputs:skeletonDeltaRotation*)", "``quatf[4]``", "The character skeleton displacement(delta) rotation(quaternion) in skeleton space.", "None"
    "Skeleton Delta Translation (Skeleton Space) (*outputs:skeletonDeltaTranslation*)", "``float[3]``", "The character skeleton displacement(delta) translation in skeleton space.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.anim.graph.ExtractCharacterPoseBundle"
    "Version", "1"
    "Extension", "omni.anim.graph.core"
    "Icon", "ogn/icons/omni.anim.graph.ExtractCharacterPoseBundle.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Extract Animation Graph Pose Bundle"
    "__tokens", "[""rootTranslation"", ""rootRotation"", ""skeletonDeltaTranslation"", ""skeletonDeltaRotation"", ""jointTranslations"", ""jointRotations""]"
    "Categories", "animation"
    "__categoryDescriptions", "animation,Nodes dealing with Animation"
    "Generated Class Name", "OgnExtractCharacterPoseBundleDatabase"
    "Python Module", "omni.anim.graph.core"

