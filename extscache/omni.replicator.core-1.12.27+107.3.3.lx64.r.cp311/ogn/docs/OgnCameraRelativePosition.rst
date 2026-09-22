.. _omni_replicator_core_OgnCameraRelativePosition_1:

.. _omni_replicator_core_OgnCameraRelativePosition:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Camera Relative Position
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-camera-relative-position


Camera Relative Position
========================

.. <description>

Convert camera relative position to world position.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Camera Prim (*inputs:cameraPrim*)", "``target``", "Prims will be positioned relative to this camera", "None"
    "Distance (*inputs:distance*)", "``float[]``", "Distance from the prim(s) to the camera", "[]"
    "Exec In (*inputs:execIn*)", "``execution``", "exec", "None"
    "Height (*inputs:height*)", "``int``", "Height of the render product", "0"
    "Horizontal Location (*inputs:horizontalLocation*)", "``float[]``", "Horizontal location in the camera frame, which is in the range of [-1, 1]", "[]"
    "Num Samples (*inputs:numSamples*)", "``int``", "Number of samples", "0"
    "Vertical Location (*inputs:verticalLocation*)", "``float[]``", "Vertical location in the camera frame, which is in the range of [-1, 1]", "[]"
    "Width (*inputs:width*)", "``int``", "Width of the render product", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "exec", "None"
    "Samples (*outputs:samples*)", "``double[3][]``", "New positions of each prim in the world space", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnCameraRelativePosition"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Camera Relative Position"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnCameraRelativePositionDatabase"
    "Python Module", "omni.replicator.core"

