.. _omni_sensors_nv_camera_CamTextureReadTaskNode_1:

.. _omni_sensors_nv_camera_CamTextureReadTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam Texture Read Task Node
    :keywords: lang-en omnigraph node camera cam-texture-read-task-node


Cam Texture Read Task Node
==========================

.. <description>

Translates data from a render node to the camera pipeline

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Render Product/Arbitrary Output Variable (AOV) (*inputs:aov*)", "``token``", "AOV used as source (LDR, HDR, DEPTH)", "LDR"
    "degreesX (*inputs:degreesX*)", "``float``", "Degrees to tilt on the X axis", "0.0"
    "degreesY (*inputs:degreesY*)", "``float``", "Degrees to tilt on the Y axis", "0.0"
    "degreesZ (*inputs:degreesZ*)", "``float``", "Degrees to tilt on the Z axis", "0.0"
    "disparityBaselineMM (*inputs:disparityBaselineMM*)", "``float``", "Baseline distance between depth imagers in millimeters.", "55.0"
    "disparityFarthestDistanceError (*inputs:disparityFarthestDistanceError*)", "``float``", "Percent error in depth measurement at the farthest sensor range.", "0.14"
    "disparityFarthestRangeMM (*inputs:disparityFarthestRangeMM*)", "``float``", "Maximum visible distance for the depth sensor in millimeters.", "4000.0"
    "disparityHorizontalFovDeg (*inputs:disparityHorizontalFovDeg*)", "``float``", "Horizontal field of view in degrees.", "65.0"
    "disparityNearestDistanceError (*inputs:disparityNearestDistanceError*)", "``float``", "Percent error in depth measurement at the nearest sensor range.", "0.02"
    "disparityNearestRangeMM (*inputs:disparityNearestRangeMM*)", "``float``", "Minimum visible distance for the depth sensor in millimeters.", "300.0"
    "enableSyntheticDisparitySim (*inputs:enableSyntheticDisparitySim*)", "``bool``", "Enable disparity simulation when reading synthetic depth buffer.", "False"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Hydra Time (*inputs:hydraTime*)", "``double``", "hydra timestamp input as double in [s]", "0.0"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time (*inputs:simTime*)", "``double``", "simTime timestamp input as double in [s]", "0.0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Dest (*outputs:dest*)", "``uint64``", "Destination Buffer", "None"
    "gpuFoundationsOut (*outputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "None"
    "Hydra Time Out (*outputs:hydraTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"
    "renderProductOut (*outputs:rp*)", "``uint64``", "Pointer to render product for this view", "None"
    "Sim Time Out (*outputs:simTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.camera.CamTextureReadTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamTextureReadTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

