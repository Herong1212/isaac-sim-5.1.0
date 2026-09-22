.. _omni_sensors_nv_camera_CamYCbCrEncoderTaskNode_1:

.. _omni_sensors_nv_camera_CamYCbCrEncoderTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam Y Cb Cr Encoder Task Node
    :keywords: lang-en omnigraph node camera cam-y-cb-cr-encoder-task-node


Cam Y Cb Cr Encoder Task Node
=============================

.. <description>

Translates the camera rgba image to a YCbCr image for SiL FastPath.

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cb Coefficents B (*inputs:CbCoefficentsB*)", "``float``", "B component weight to calc Cb for custom YcbCr calculation", "0.0"
    "Cb Coefficents G (*inputs:CbCoefficentsG*)", "``float``", "G component weight to calc Cb for custom YcbCr calculation", "0.0"
    "Cb Coefficents R (*inputs:CbCoefficentsR*)", "``float``", "R component weight to calc Cb for custom YcbCr calculation", "0.0"
    "Cr Coefficents B (*inputs:CrCoefficentsB*)", "``float``", "B component weight to calc Cr for custom YcbCr calculation", "0.0"
    "Cr Coefficents G (*inputs:CrCoefficentsG*)", "``float``", "G component weight to calc Cr for custom YcbCr calculation", "0.0"
    "Cr Coefficents R (*inputs:CrCoefficentsR*)", "``float``", "R component weight to calc Cr for custom YcbCr calculation", "0.0"
    "Y Cb Cr Encoding Format (*inputs:YCbCrEncodingFormat*)", "``token``", "Format of the YCbCr: Could be YUV444,YUV422 or YUV420 ", "YUV420"
    "Y Cb Cr Encoding Standard (*inputs:YCbCrEncodingStandard*)", "``token``", "Standard of the RGB->YCbCr transcoding: Could be BT.601, BT.709, BT.2020, JPEG or custom ", "JPEG"
    "Y Coefficents B (*inputs:YCoefficentsB*)", "``float``", "B component weight to calc Y for custom YcbCr calculation", "0.0"
    "Y Coefficents G (*inputs:YCoefficentsG*)", "``float``", "G component weight to calc Y for custom YcbCr calculation", "0.0"
    "Y Coefficents R (*inputs:YCoefficentsR*)", "``float``", "R component weight to calc Y for custom YcbCr calculation", "0.0"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0.0"
    "Offset Cb (*inputs:offsetCb*)", "``float``", "Cb offset for custom YcbCr calculation", "0.0"
    "Offset Cr (*inputs:offsetCr*)", "``float``", "Cr offset for custom YcbCr calculation", "0.0"
    "Offset Y (*inputs:offsetY*)", "``float``", "Y offset for custom YcbCr calculation", "0.0"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0.0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"
    "Yuv Data Type (*inputs:yuvDataType*)", "``token``", "YUV output data type UINT8 or FLOAT16", "UINT8"


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

    "Unique ID", "omni.sensors.nv.camera.CamYCbCrEncoderTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamYCbCrEncoderTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

