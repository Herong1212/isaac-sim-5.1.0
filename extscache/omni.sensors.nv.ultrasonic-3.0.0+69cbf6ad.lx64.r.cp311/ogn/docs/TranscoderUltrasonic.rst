.. _omni_sensors_nv_ultrasonic_TranscoderUltrasonic_1:

.. _omni_sensors_nv_ultrasonic_TranscoderUltrasonic:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Transcoder Ultrasonic
    :keywords: lang-en omnigraph node ultrasonic transcoder-ultrasonic


Transcoder Ultrasonic
=====================

.. <description>

Transcodes RTSensor buffer data to sensor specific formats and transmits it via udp

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.ultrasonic<ext_omni_sensors_nv_ultrasonic>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Stream (*inputs:cudaStream*)", "``uint64``", "Cuda Stream Input", "0"
    "Dump Packets (*inputs:dumpPackets*)", "``bool``", "Dump packets as dwBinFile", "False"
    "File Format (*inputs:fileFormat*)", "``string``", "File format to dump", "bin"
    "File Name (*inputs:fileName*)", "``string``", "File name of the packets", "uss.h5"
    "Format (*inputs:format*)", "``string``", "Output format", ""
    "Hydra Time (*inputs:hydraTime*)", "``double``", "hydra timestamp input as double in [ns]", "0.0"
    "Interface IP (*inputs:interfaceIP*)", "``string``", "local interface to use", "127.0.0.1"
    "Meta (*inputs:meta*)", "``uint64``", "Source Meta Data", "0"
    "Remote IP (*inputs:remoteIP*)", "``string``", "Remote IP of UDP channel", "127.0.0.1"
    "Remote Port (*inputs:remotePort*)", "``int``", "Remote port of UDP channel", "12001"
    "Signal Scaler (*inputs:signalScaler*)", "``float``", "Signal scaling parameter", "1.0"
    "Sim Time (*inputs:simTime*)", "``double``", "simTime timestamp input as double in [ns]", "0.0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"
    "Timestamp Mode (*inputs:timestampMode*)", "``string``", "mode for the sent timestamp", "VENDOR"
    "Vendor (*inputs:vendor*)", "``string``", "USS model vendor", "generic"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.ultrasonic.TranscoderUltrasonic"
    "Version", "1"
    "Extension", "omni.sensors.nv.ultrasonic"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "TranscoderUltrasonicDatabase"
    "Python Module", "omni.sensors.nv.ultrasonic"

