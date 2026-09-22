.. _omni_sensors_nv_ids_IDSVizTranscoder_1:

.. _omni_sensors_nv_ids_IDSVizTranscoder:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: IDS Viz Transcoder
    :keywords: lang-en omnigraph node ids i-d-s-viz-transcoder


IDS Viz Transcoder
==================

.. <description>

Receives Radar data and prepares a buffer for it from the buffer manager, and passes it to output

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.ids<ext_omni_sensors_nv_ids>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Color Code (*inputs:colorCode*)", "``int``", "0 - range, 1 - intensity", "0"
    "Cuda Stream In (*inputs:cudaStreamIn*)", "``uint64``", "Cuda Stream Input", "0"
    "Data Id (*inputs:dataId*)", "``int``", "Unique data id for visualizer", "0"
    "In (*inputs:in*)", "``uint64``", "Source Buffer", "0"
    "Meta Data In (*inputs:metaDataIn*)", "``uint64``", "Source Buffer", "0"
    "Sensor Mount6 D Pose (*inputs:sensorMount6DPose*)", "``float[]``", "sensor mounting pose in vehicle coordinates as (x, y, z, roll, pitch, yaw)", "[]"
    "Sensor Name (*inputs:sensorName*)", "``string``", "Name of the sensor", "ids"
    "Target PID (*inputs:targetPID*)", "``uint64``", "Target process ID to send data stream to", "0"
    "Viz Points (*inputs:vizPoints*)", "``bool``", "Publishes Points", "True"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.ids.IDSVizTranscoder"
    "Version", "1"
    "Extension", "omni.sensors.nv.ids"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "IDSVizTranscoderDatabase"
    "Python Module", "omni.sensors.nv.ids"

