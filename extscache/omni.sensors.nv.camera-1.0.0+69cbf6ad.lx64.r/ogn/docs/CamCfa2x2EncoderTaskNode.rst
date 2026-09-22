.. _omni_sensors_nv_camera_CamCfa2x2EncoderTaskNode_1:

.. _omni_sensors_nv_camera_CamCfa2x2EncoderTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam Cfa2x2 Encoder Task Node
    :keywords: lang-en omnigraph node camera cam-cfa2x2-encoder-task-node


Cam Cfa2x2 Encoder Task Node
============================

.. <description>

Translates the camera rgba image to a CFA image

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "CFA CF00 (*inputs:CFA_CF00*)", "``float[3]``", "Top Left Pixel of 2x2 Color Filter Array", "[0.0, 0.0, 0.0]"
    "CFA CF01 (*inputs:CFA_CF01*)", "``float[3]``", "Top Right Pixel of 2x2 Color Filter Array", "[0.0, 0.0, 0.0]"
    "CFA CF10 (*inputs:CFA_CF10*)", "``float[3]``", "Bottom Left Pixel of 2x2 Color Filter Array", "[0.0, 0.0, 0.0]"
    "CFA CF11 (*inputs:CFA_CF11*)", "``float[3]``", "Bottom Right Pixel of 2x2 Color Filter Array", "[0.0, 0.0, 0.0]"
    "Cfa Semantic (*inputs:cfaSemantic*)", "``token``", "Semantic of the Color Filter array: RGGB, GRBG, BGGR, RCCB, CRBC, BCCR, RCCC, CCCR or CRCC", "RGGB"
    "Embedded Src (*inputs:embeddedSrc*)", "``uint64``", "Embedded Data Lines Source Buffer", "0"
    "Flip Horizontal (*inputs:flipHorizontal*)", "``bool``", "horizonal mirroring", "False"
    "Flip Vertical (*inputs:flipVertical*)", "``bool``", "vertical mirroring", "False"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Maximal Value (*inputs:maximalValue*)", "``uint64``", "the maximal value of the internal processing (20bits : 1048575) (passthrough : 1) (default for 24 bits: 16777215)", "16777215"
    "Output Data Type Format (*inputs:outputDataTypeFormat*)", "``token``", "Data Type of the output format: [FLOAT32, UINT32]", "UINT32"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Dest (*outputs:dest*)", "``uint64``", "Destination Buffer", "0"
    "Embedded Dest (*outputs:embeddedDest*)", "``uint64``", "Embedded Data Lines Destination Buffer", "0"
    "gpuFoundationsOut (*outputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "None"
    "Hydra Time Out (*outputs:hydraTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"
    "renderProductOut (*outputs:rp*)", "``uint64``", "Pointer to render product for this view", "None"
    "Sim Time Out (*outputs:simTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.camera.CamCfa2x2EncoderTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamCfa2x2EncoderTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

