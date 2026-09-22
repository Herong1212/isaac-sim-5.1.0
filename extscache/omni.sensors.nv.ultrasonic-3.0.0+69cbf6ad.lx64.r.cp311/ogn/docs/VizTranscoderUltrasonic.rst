.. _omni_sensors_nv_ultrasonic_VizTranscoderUltrasonic_1:

.. _omni_sensors_nv_ultrasonic_VizTranscoderUltrasonic:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Viz Transcoder Ultrasonic
    :keywords: lang-en omnigraph node ultrasonic viz-transcoder-ultrasonic


Viz Transcoder Ultrasonic
=========================

.. <description>

Receives Radar data and prepares a buffer for it from the buffer manager, and passes it to output

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.ultrasonic<ext_omni_sensors_nv_ultrasonic>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Average Period (*inputs:averagePeriod*)", "``int``", "number of frames to average signal over", "4"
    "Cuda Stream In (*inputs:cudaStreamIn*)", "``uint64``", "Cuda Stream Input", "0"
    "Hydra Time (*inputs:hydraTime*)", "``double``", "hydra timestamp input as double in [ns]", "0.0"
    "In (*inputs:in*)", "``uint64``", "Source Buffer", "0"
    "Meta (*inputs:meta*)", "``uint64``", "Meta Source Buffer", "0"
    "Send Data Id (*inputs:sendDataId*)", "``int``", "Send data buffer id to distinguish data on receiver side", "0"
    "Sim Time (*inputs:simTime*)", "``double``", "simTime timestamp input as double in [ns]", "0.0"
    "Target PID (*inputs:targetPID*)", "``uint64``", "Target process ID to send data stream to", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.ultrasonic.VizTranscoderUltrasonic"
    "Version", "1"
    "Extension", "omni.sensors.nv.ultrasonic"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "VizTranscoderUltrasonicDatabase"
    "Python Module", "omni.sensors.nv.ultrasonic"

