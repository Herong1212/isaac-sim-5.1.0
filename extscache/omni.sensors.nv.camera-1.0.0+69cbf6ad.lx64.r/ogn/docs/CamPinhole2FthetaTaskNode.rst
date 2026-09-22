.. _omni_sensors_nv_camera_CamPinhole2FthetaTaskNode_1:

.. _omni_sensors_nv_camera_CamPinhole2FthetaTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam Pinhole2 Ftheta Task Node
    :keywords: lang-en omnigraph node camera cam-pinhole2-ftheta-task-node


Cam Pinhole2 Ftheta Task Node
=============================

.. <description>

Projects the data from a pinhole via the ftheta 5th order polynomial

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Lens Dist Center X (*inputs:LensDistCenterX*)", "``float``", "Distortion Center X Axis", "0.0"
    "Lens Dist Center Y (*inputs:LensDistCenterY*)", "``float``", "Distortion Center Y Axis", "0.0"
    "Lens Distortion P0 (*inputs:LensDistortionP0*)", "``float``", "Distortion Coefficent offset (In DW calibration always 0.0)", "0.0"
    "Lens Distortion P1 (*inputs:LensDistortionP1*)", "``float``", "Distortion Coefficent linear", "0.0"
    "Lens Distortion P2 (*inputs:LensDistortionP2*)", "``float``", "Distortion Coefficent square", "0.0"
    "Lens Distortion P3 (*inputs:LensDistortionP3*)", "``float``", "Distortion Coefficent cubic", "0.0"
    "Lens Distortion P4 (*inputs:LensDistortionP4*)", "``float``", "Distortion Coefficent power 4", "0.0"
    "Lens Distortion P5 (*inputs:LensDistortionP5*)", "``float``", "Distortion Coefficent power 5", "0.0"
    "Src FOV (*inputs:SrcFOV*)", "``uint``", "Field of View which is projected to the image plane", "0"
    "Render Product/Arbitrary Output Variable (AOV) (*inputs:aov*)", "``token``", "AOV used as source (LDR, HDR, DEPTH)", "LDR"
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

    "Unique ID", "omni.sensors.nv.camera.CamPinhole2FthetaTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamPinhole2FthetaTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

