.. _omni_sensors_nv_radar_TranscoderRadar_1:

.. _omni_sensors_nv_radar_TranscoderRadar:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Transcoder Radar
    :keywords: lang-en omnigraph node radar transcoder-radar


Transcoder Radar
================

.. <description>

Transcodes RTSensor buffer data to sensor specific formats and dumps in file

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.radar<ext_omni_sensors_nv_radar>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Stream (*inputs:cudaStream*)", "``uint64``", "Cuda Stream Input", "0"
    "Decoder Path (*inputs:decoderPath*)", "``string``", "decoder path id", "/usr/local/driveworks/bin/libsample_radar_plugin_new.so"
    "Device (*inputs:device*)", "``string``", "device id", "CONTINENTAL_ARS430"
    "Dump Packets (*inputs:dumpPackets*)", "``bool``", "Dump packets as dwBinFile", "False"
    "Event I Ds (*inputs:eventIDs*)", "``int[]``", "Event IDs from SOME/IP Header 1. Only for NCD transcoders.", "[]"
    "Event Types (*inputs:eventTypes*)", "``int[]``", "Event Types of their respective Event ID from SOME/IP Header 1. Only for NCD transcoders.", "[]"
    "File Name (*inputs:fileName*)", "``string``", "File name of the dwBinFile", ""
    "Format (*inputs:format*)", "``string``", "format used for sent data", "RDI_1_0_8_V2"
    "Interface IP (*inputs:interfaceIP*)", "``string``", "local interface to use", "127.0.0.1"
    "Message Types (*inputs:messageTypes*)", "``int[]``", "message Types of their respective Event ID from SOME/IP Header 1. Only for NCD transcoders.", "[]"
    "Meta (*inputs:meta*)", "``uint64``", "Source Meta Data", "0"
    "Remote IP (*inputs:remoteIP*)", "``string``", "Remote IP of UDP channel", "239.0.0.1"
    "Remote Port (*inputs:remotePort*)", "``int``", "Remote port of UDP channel", "10001"
    "Service ID (*inputs:serviceID*)", "``uint64``", "Service ID and Method ID from SOME/IP Header 1. Only for NCD transcoders.", "2726985729"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.radar.TranscoderRadar"
    "Version", "1"
    "Extension", "omni.sensors.nv.radar"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "TranscoderRadarDatabase"
    "Python Module", "omni.sensors.nv.radar"

