.. _omni_sensors_nv_camera_VizTranscoderCamera_1:

.. _omni_sensors_nv_camera_VizTranscoderCamera:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Viz Transcoder Camera
    :keywords: lang-en omnigraph node camera viz-transcoder-camera


Viz Transcoder Camera
=====================

.. <description>

Camera to Visualizer Sink Node

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Channel Name (*inputs:channelName*)", "``token``", "sink channel name", ""
    "Frame Id (*inputs:frameId*)", "``int64``", "Frame identifier", "0"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0.0"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Send Data Id (*inputs:sendDataId*)", "``int``", "Send data id to distinguish point clouds on the receiver side", "100"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0.0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.camera.VizTranscoderCamera"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "VizTranscoderCameraDatabase"
    "Python Module", "omni.sensors.nv.camera"

