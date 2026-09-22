.. _omni_sensors_nv_camera_CamDefaultEmbeddedLinesTask_1:

.. _omni_sensors_nv_camera_CamDefaultEmbeddedLinesTask:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam Default Embedded Lines Task
    :keywords: lang-en omnigraph node camera cam-default-embedded-lines-task


Cam Default Embedded Lines Task
===============================

.. <description>

Loads a preset of embedded line registers

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
    "Embed Frame ID (*inputs:embedFrameID*)", "``bool``", "boolean, whether frame ID shall be embedded into the embedded lines (overwrites camera type default)", "False"
    "Embed Frame ID Offset (*inputs:embedFrameIDOffset*)", "``int64``", "offset of the frame ID", "0"
    "Embed Timecode (*inputs:embedTimecode*)", "``bool``", "boolean, whether timecode shall be embedded into the embedded lines  (overwrites camera type default)", "False"
    "Embedded Bottom Lines (*inputs:embeddedBottomLines*)", "``int``", "number of embedded bottom lines", "0"
    "Embedded Data Filepath (*inputs:embeddedDataFilepath*)", "``token``", "File path to the embedded line data file", "/tmp/AR0231_daylight.raw"
    "Embedded Timecode Offset (*inputs:embeddedTimecodeOffset*)", "``int64``", "offset of the timecode in [us]", "0"
    "Embedded Top Lines (*inputs:embeddedTopLines*)", "``int``", "number of embedded top lines", "0"
    "External Time Of Sim Frame In (*inputs:externalTimeOfSimFrameIn*)", "``int64``", "externalTimeOfSimFrameIn input", "0"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Raw Encoding (*inputs:rawEncoding*)", "``token``", "Raw Encoding of the embedded registers RAW12, RAW16, RAW20, RAW24", "RAW12"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"
    "Timecode In (*inputs:timecodeIn*)", "``int64``", "timecode/timestamp input", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Dest (*outputs:dest*)", "``uint64``", "Destination Buffer", "None"
    "Embedded Dest (*outputs:embeddedDest*)", "``uint64``", "Embedded Data Lines Destination Buffer", "0"
    "gpuFoundationsOut (*outputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "None"
    "Hydra Time Out (*outputs:hydraTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0"
    "renderProductOut (*outputs:rp*)", "``uint64``", "Pointer to render product for this view", "None"
    "Sim Time Out (*outputs:simTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.camera.CamDefaultEmbeddedLinesTask"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamDefaultEmbeddedLinesTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

