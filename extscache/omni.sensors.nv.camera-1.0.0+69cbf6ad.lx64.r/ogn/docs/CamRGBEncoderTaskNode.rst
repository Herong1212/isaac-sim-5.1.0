.. _omni_sensors_nv_camera_CamRGBEncoderTaskNode_1:

.. _omni_sensors_nv_camera_CamRGBEncoderTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam RGB Encoder Task Node
    :keywords: lang-en omnigraph node camera cam-r-g-b-encoder-task-node


Cam RGB Encoder Task Node
=========================

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

    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0.0"
    "Rgb Data Type (*inputs:rgbDataType*)", "``token``", "Data type of the RGB: Could be UINT8 or FLOAT16 ", "UINT8"
    "Rgb Semantic (*inputs:rgbSemantic*)", "``token``", "Data type of the RGB: Could be INTERLEAVED or PLANAR", "INTERLEAVED"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0.0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "output buffer (*outputs:dest*)", "``uint64``", "Destination Buffer", "None"
    "gpuFoundationsOut (*outputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "None"
    "Hydra Time Out (*outputs:hydraTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"
    "renderProductOut (*outputs:rp*)", "``uint64``", "Pointer to render product for this view", "None"
    "Sim Time Out (*outputs:simTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.camera.CamRGBEncoderTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamRGBEncoderTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

