.. _omni_sensors_nv_radar_VizTranscoderRadar_1:

.. _omni_sensors_nv_radar_VizTranscoderRadar:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Viz Transcoder Radar
    :keywords: lang-en omnigraph node radar viz-transcoder-radar


Viz Transcoder Radar
====================

.. <description>

Receives Radar data and prepares a buffer for it from the buffer manager, and passes it to output

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.radar<ext_omni_sensors_nv_radar>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Color Code (*inputs:colorCode*)", "``int``", "0 - constant, 1 - range, 2 - doppler, 3 - azimuth, 4 - elevation, 5 - rcs, 6 - semantic, 7 - material, 8 - instance", "4"
    "Cuda Stream In (*inputs:cudaStreamIn*)", "``uint64``", "Cuda Stream Input", "0"
    "Hydra Time (*inputs:hydraTime*)", "``double``", "hydra timestamp input as double in [ns]", "0.0"
    "In (*inputs:in*)", "``uint64``", "Source Buffer", "0"
    "Last Node (*inputs:lastNode*)", "``bool``", "true if the viz transcoder is last node in pipeline and needs to signal async work termination", "False"
    "Max Num Scans (*inputs:maxNumScans*)", "``int``", "max number of scans to accumulate", "2"
    "Meta (*inputs:meta*)", "``uint64``", "Source Meta Buffer", "0"
    "Send Data Id (*inputs:sendDataId*)", "``int``", "Send data buffer id to distinguish data on receiver side", "0"
    "Sensor Mount6 Dpose (*inputs:sensorMount6Dpose*)", "``float[]``", "sensor mounting pose in vehicle coordinates as (x, y, z, roll, pitch, yaw)", "[]"
    "Sim Time (*inputs:simTime*)", "``double``", "simTime timestamp input as double in [ns]", "0.0"
    "Target PID (*inputs:targetPID*)", "``uint64``", "Target process ID to send data stream to", "0"
    "Vline Scale (*inputs:vlineScale*)", "``float``", "scale of velocity lines", "1.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.radar.VizTranscoderRadar"
    "Version", "1"
    "Extension", "omni.sensors.nv.radar"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "VizTranscoderRadarDatabase"
    "Python Module", "omni.sensors.nv.radar"

