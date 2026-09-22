.. _omni_sensors_nv_lidar_TranscoderLidar_1:

.. _omni_sensors_nv_lidar_TranscoderLidar:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Transcoder Lidar
    :keywords: lang-en omnigraph node lidar transcoder-lidar


Transcoder Lidar
================

.. <description>

Transcodes RTSensor buffer to Lidar packets

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.lidar<ext_omni_sensors_nv_lidar>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Stream (*inputs:cudaStream*)", "``uint64``", "Cuda Stream Input", "0"
    "Decoder Path (*inputs:decoderPath*)", "``string``", "Optional, decoder path for file dumping", ""
    "Dump Packets (*inputs:dumpPackets*)", "``bool``", "Dump packets as dwBinFile", "False"
    "Encoder Type (*inputs:encoderType*)", "``int``", "Encoder Type -- needed if there are different versions of the sensor (e.g., NCD)", "7"
    "File Name (*inputs:fileName*)", "``string``", "File name of the packets", "lidar.h5"
    "Group Name (*inputs:groupName*)", "``string``", "Sensor name to be put inside hdf5 file", "Lidar"
    "Return Type (*inputs:returnType*)", "``int``", "Desired return type (0 - First, 1 - last, 2 - Strongest, 3 - MultipleReturns", "3"
    "Sensor Profile Name (*inputs:sensorProfileName*)", "``string``", "Filename of the sensor profile - has to be the same as in lidar model", "GENERIC"
    "Sim Time (*inputs:simTime*)", "``double``", "Simulation time given from PostProcessEntryNode", "0"
    "Src (*inputs:src*)", "``uint64``", "RtSensor buffer id", "0"
    "Src Meta (*inputs:srcMeta*)", "``uint64``", "Lidar Meta Data", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.lidar.TranscoderLidar"
    "Version", "1"
    "Extension", "omni.sensors.nv.lidar"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "TranscoderLidarDatabase"
    "Python Module", "omni.sensors.nv.lidar"

