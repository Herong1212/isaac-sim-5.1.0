.. _omni_sensors_nv_camera_CamPhotonEstimationTaskNode_1:

.. _omni_sensors_nv_camera_CamPhotonEstimationTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam Photon Estimation Task Node
    :keywords: lang-en omnigraph node camera cam-photon-estimation-task-node


Cam Photon Estimation Task Node
===============================

.. <description>

Translates the camera image to a RGB image for SiL FastPath.

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Blue Correction (*inputs:blueCorrection*)", "``float[3]``", "Red Correction Matrix (R,G,B)", "[0.0, 0.0, 0.0]"
    "Corrections Multiplier (*inputs:correctionsMultiplier*)", "``float``", "multiplier to applied to all values for values which are missing in the preceding chain (e.g. fstops etc)", "0.3298769777"
    "Exposure Time (*inputs:exposureTime*)", "``float``", "exposure time in [s]", "0.011"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Green Correction (*inputs:greenCorrection*)", "``float[3]``", "Red Correction Matrix (R,G,B)", "[0.0, 0.0, 0.0]"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0.0"
    "Illuminant Standard (*inputs:illuminantStandard*)", "``token``", "Defines the illlumination standard", "D65"
    "Max Illumination (*inputs:maxIllumination*)", "``float``", "maximal illumintation in the scene", "3000.0"
    "Max Value QE Curve (*inputs:maxValueQECurve*)", "``float``", "The maximal value in the quantum efficiency curve", "2.1"
    "Pixel Size (*inputs:pixelSize*)", "``float``", "PixelSize in [um]", "2.1"
    "Red Correction (*inputs:redCorrection*)", "``float[3]``", "Red Correction Matrix (R,G,B)", "[0.0, 0.0, 0.0]"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0.0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Dest (*outputs:dest*)", "``uint64``", "Destination Buffer", "0"
    "gpuFoundationsOut (*outputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "None"
    "Hydra Time Out (*outputs:hydraTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"
    "renderProductOut (*outputs:rp*)", "``uint64``", "Pointer to render product for this view", "None"
    "Sim Time Out (*outputs:simTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.camera.CamPhotonEstimationTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamPhotonEstimationTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

