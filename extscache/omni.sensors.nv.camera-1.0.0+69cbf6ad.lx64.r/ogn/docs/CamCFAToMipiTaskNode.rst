.. _omni_sensors_nv_camera_CamCFAToMipiTaskNode_1:

.. _omni_sensors_nv_camera_CamCFAToMipiTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam CFA To Mipi Task Node
    :keywords: lang-en omnigraph node camera cam-c-f-a-to-mipi-task-node


Cam CFA To Mipi Task Node
=========================

.. <description>

Muxes CFA and Embedded Lines into one image for the transcoder

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Embedded Line Encoder (*inputs:EmbeddedLineEncoder*)", "``token``", "Encoder for the embedded Lines : Values: NONE, IMX390_DEFAULT, IMX728_DEFAULT, IMX623_DEFAULT, AR820_DEFAULT, defaults to NONE", "NONE"
    "Raw Encoding (*inputs:RawEncoding*)", "``token``", "Raw Encoding of the embedded registers RAW12, RAW16, RAW20, RAW24, defaults to RAW12", "RAW12"
    "Embedded Src (*inputs:embeddedSrc*)", "``uint64``", "Embedded Data Lines Src Buffer", "0"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
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

    "Unique ID", "omni.sensors.nv.camera.CamCFAToMipiTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamCFAToMipiTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

