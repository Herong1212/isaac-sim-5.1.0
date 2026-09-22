.. _omni_sensors_nv_camera_CamFileReaderTaskNode_1:

.. _omni_sensors_nv_camera_CamFileReaderTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam File Reader Task Node
    :keywords: lang-en omnigraph node camera cam-file-reader-task-node


Cam File Reader Task Node
=========================

.. <description>

Reads a camera raw file

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "AOV Trigger (*inputs:AOVTrigger*)", "``token``", "The renderproduct which triggers the reader", "LDR"
    "File Data Type (*inputs:fileDataType*)", "``token``", "Data type of the RGB: Could be UINT8, UINT16, UINT32, FLOAT16 or FLOAT32", "UINT8"
    "Filename (*inputs:filename*)", "``token``", "File path to the video raw file", "/tmp/new.raw"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Height (*inputs:height*)", "``int``", "Image Height", "1208"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0.0"
    "Loop (*inputs:loop*)", "``bool``", "Indicates whether the input file shall be loop infinitely", "False"
    "Pixel Pattern (*inputs:pixelPattern*)", "``token``", "Pixel pattern of the input file: RGBA or CFA", "RGBA"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0.0"
    "Skip Back (*inputs:skipBack*)", "``uint64``", "Bytes to skip after each frame", "0"
    "Skip Front (*inputs:skipFront*)", "``uint64``", "Bytes to skip before each frame", "0"
    "Start (*inputs:start*)", "``bool``", "start", "False"
    "Width (*inputs:width*)", "``int``", "Image Width", "1920"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Dest (*outputs:dest*)", "``uint64``", "Destination Buffer", "None"
    "gpuFoundationsOut (*outputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "None"
    "Hydra Time Out (*outputs:hydraTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"
    "renderProductOut (*outputs:rp*)", "``uint64``", "Pointer to render product for this view", "None"
    "Sim Time Out (*outputs:simTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.camera.CamFileReaderTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamFileReaderTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

