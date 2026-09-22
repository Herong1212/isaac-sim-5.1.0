.. _ext_omni_sensors_nv_ultrasonic:

Omniverse Ultrasonic Extension
==============================

Introduction
^^^^^^^^^^^^

In Omniverse the Ultrasonic Sensor (USS) extension consists of the WPM-based simulation plugin and a sample material plugin.

Plugins
^^^^^^^

WpmUltrasonicPlugin
-------------------

**Introduction**

This is a generic USS simulation using WPM. Configuration options are available in the sensor group config file (JSON format).

**Plugin Name**

omni.sensors.nv.ultrasonic.wpm_ultrasonic.plugin

**Parameters & Attributes**

Attributes are specified through a sensor group config JSON file, which can be found in "data/sensors/ultrasonic" in "omni.sensors/common" extension. The desired sensor profile
is set via the USDA attribute "custom token rtxsensor:modelConfig" (see :ref:`Example in USDA<UltrasonicExampleUsda>`).

**Available Parameterizations**

+------------------+------------------------------------------------------------+
|  USS Model       |     Params File name                                       |
+==================+============================================================+
|  Example         |     Example.json                                           |
+------------------+------------------------------------------------------------+

.. only:: mercedes

    +-------------------------------------------------+----------------------------------------------+
    |  Valeo USV10 car variant 222                    |    Valeo_USV_222.json                        |
    +-------------------------------------------------+----------------------------------------------+
    |  Valeo USV10 car variant 222 HD version         |    Valeo_USV_222_HQ.json                     |
    +-------------------------------------------------+----------------------------------------------+
    |  Valeo USV10 car variant 222 (directivity table)|    Valeo_USV_222_table.json                  |
    +-------------------------------------------------+----------------------------------------------+
    |  Valeo USV10 car variant 223                    |    Valeo_USV_223_new.json                    |
    +-------------------------------------------------+----------------------------------------------+
    |  Valeo USV10 car variant 223 HD version         |    Valeo_USV_223_HQ_new.json                 |
    +-------------------------------------------------+----------------------------------------------+
    |  Valeo USV10 car variant 174 (directivity table)|    Valeo_USV_174_table.json                  |
    +-------------------------------------------------+----------------------------------------------+

Users can create custom parameterization files but they have to be placed in the common extension under (omni.sensors.nv.common/data/)
the parameterization name is then the file name. This JSON file can be read with the ProfileReader utility plugin. The parameterization file should be in JSON format and have the following structure:

.. _UltrasonicExampleJson:

::

    {
        "class": "sensor",
        "type": "ultrasonic",
        "name": Sensor name (e.g. "Example"),
        "driveWorksId": Sensor ID in DriveWorks (currently unused),
        "profile":
        {
            "AzSpanDeg": width of the field in which rays are shot,
            "ElSpanDeg": height of the field in which rays are shot,
            "RaysPerDeg": ray density per degree,
            "TraceTreeDepth": how many times the rays are reflected,
            "MembraneDiameter": membrane diameter in meters,
            "CenterFrequency": signal center frequency in Hz,
            "Bandwidth": signal bandwidth in Hz,
            "PulseDuration": duration of pulse in seconds,
            "PulsePower": dimensionless pulse power (spread out across rays),
            "SampleDuration": time sampling of the waveform in seconds,
            "CloseRange": distance at which additonal amplification is applied,
            "CloseRangeDecay": distance beyond which the close range amplification starts decaying,
            "CloseIndirectAmplBase": base amplification for indirect signal ways in close range,
            "CloseDirectAmplBase": base amplification for direct signal ways in close range,
            "CloseIndirectAmpl": scaling of the gain function for indirect signal ways in close range,
            "CloseDirectAmpl": scaling of the gain function for direct signal ways in close range,
            "NoiseMin": dimensionless minimum amplitude of noise,
            "NoiseMax": dimensionless maximum amplitude of noise,

            "SensorMounts":[
                [[ x1,  y1,  z1], [   roll1, pitch1 (negative up),    yaw1]],
                [[ x2,  y2,  z2], [   roll2, pitch2 (negative up),    yaw2]],
                [[ x3,  y3,  z3], [   roll3, pitch3 (negative up),    yaw3]],
                ....
            ],

            "RxGroups":[
                [0,1],
                [0,1,2],
                ...
            ],

            "FiringSequnce": [
                [
                [ time_offset1,  TxSensor1,  RxGroup1, channel1], [ time_offset2,  TxSensor2,  RxGroup2, channel2], ...
                ],
                [
                [ time_offset1,  TxSensor1,  RxGroup1, channel1], [ time_offset2,  TxSensor2,  RxGroup2, channel2], ...
                ],
                ...
            ],

            "SignalMode": "Chirp or AM",

            "GainCoeffs": [
                polynomial gain function coefficients
            ],

            "DirectivityCoeffs": [
                polynomial directivity function coefficients
            ]

            the latter can be replaced with a directivity table

            "DirectivityTable": {
                "sensor_id": {
                    "horizontal": [
                        [angle1, gain1],
                        [angle2, gain2],
                        ...
                    ],
                    "vertical": [
                        [angle1, gain1],
                        [angle2, gain2],
                        ...
                    ]
                },
                ...
        }
    }

**Example in USDA**

.. _UltrasonicExampleUsda:

.. code-block:: none

    def Camera "Ultrasonic_group"
    {
        custom token action:camera:name = "Ultrasonic_group"
        custom token cameraSensorType = "radar"
        custom token rtxsensor:sensorModelConfig = "Example"
        custom string sensorModelPluginName = "omni.sensors.nv.ultrasonic.wpm_ultrasonic.plugin"
        token visibility = "invisible"
        double3 xformOp:rotateYXZ = (85.65653228759767, -3.7055966501766535e-11, 177.71578979492222)
        double3 xformOp:scale = (1.0000000000000007, 1.0000000000000004, 1)
        double3 xformOp:translate = (-305.4795491922145, -212.8579889951991, 1.7645552181863593)
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
    }

**Data Structure**

USS outputs data organized in signal ways. A signal way is a sequence of samples that are sent from the transmitting sensor to the receiving sensor on a specific channel.
Each frame contains a certain amount of signal ways (specific to a model and a firing sequence).

USS can write output as a Generic Model Output (GMO) or in a vendor-specific format. USS outputs a Generic Model Output in the same format as the other sensors. The output is a binary buffer containing the USS data. Each 'frame' corresponds to the cumulative result of the whole sensor firing sequence.

The auxiliary data of the GMO (USSAuxiliaryData) structure is as follows:

+----------------------+-------------------+------------------------------------------------+
|      Field Name      | Type              | Description                                    |
+======================+===================+================================================+
|  numSgws             | uint32_t          | Number of signal ways                          |
+----------------------+-------------------+------------------------------------------------+
|  numSamplesPerSgw    | uint32_t          | Number of samples in each signal way           |
+----------------------+-------------------+------------------------------------------------+

The BasicElements structure of the GMO with USS data should be interpreted as follows:

+----------------------+-------------------+------------------------------------------------+
|      Field Name      | Type              | Description                                    |
+======================+===================+================================================+
|  timeOffsetNs        | int32_t           | Time offset of the signal way in the firing    |
|                      |                   | sequence (step 1)                              |
+----------------------+-------------------+------------------------------------------------+
|  x                   | float             | Transmitting sensor ID (step 1)                |
+----------------------+-------------------+------------------------------------------------+
|  y                   | float             | Receiving sensor ID (step 1)                   |
+----------------------+-------------------+------------------------------------------------+
|  z                   | float             | Channel ID  (step 1)                           |
+----------------------+-------------------+------------------------------------------------+
|  scalar              | float             | Value in sample                                |
+----------------------+-------------------+------------------------------------------------+

A sample parser of such generic dump format can be found in: ``source/extensions/omni.drivesim.sensors.nv.ultrasonic/python/generic_uss_parser.py``

USS Data Converter Plugin
-------------------------

**Introduction**

This is a data converter plugin implementing the conversion of the binary model output into an ultrasonic output object.

**Plugin Name**

omni.sensors.nv.ultrasonic.data_converter.plugin

**Usage**

Using this plugin is quite straighforward and can be illustrated via the following code snippet:

.. code-block:: none

    void* modelOutputBinaryBuffer = getBufferSomehow();
    ProviderCycle convertedBuffer = carb::getCachedInterface<omni::sensors::ultrasonic::IUltrasonicCycleConverter>()->
                                                        convertBuffer(modelOutputBinaryBuffer);

Omnigraph Nodes
^^^^^^^^^^^^^^^

Curently there is only one node in the USS extension. A transcoder which encodes the USS data into a desired format and writes it into file.

TranscoderUltrasonic
--------------------

**Introduction**

The Transcoder node encodes the US data stream into a specified format and writes it into a file.

**Omnigraph Node Name**

omni.sensors.nv.ultrasonic.TranscoderUltrasonic

**Parameters & Attributes**

+------------------+------------------------------------------------------------+----------+-------------+--------------------+-------+
|Parameter Name    |Description                                                 |Value Type|Value Range  |Default Value       |Example|
+==================+============================================================+==========+=============+====================+=======+
|signalScaler      |Scaling factor aplied to signals (amplification)            |float     |             | 1.0                |       |
+------------------+------------------------------------------------------------+----------+-------------+--------------------+-------+
|timestampMode     |Mode for the sent timestamp                                 |string    |             | VENDOR             |       |
+------------------+------------------------------------------------------------+----------+-------------+--------------------+-------+
|dumpPackets       |Dump packets into a file                                    |bool      |             | false              |       |
+------------------+------------------------------------------------------------+----------+-------------+--------------------+-------+
|vendor            |Vendor of the sensor model                                  |token     |"generic",   | "generic"          |       |
+------------------+------------------------------------------------------------+----------+-------------+--------------------+-------+
|fileFormat        |File format to dump                                         |string    |"bin", "pcap"| "bin"              |       |
+------------------+------------------------------------------------------------+----------+-------------+--------------------+-------+
|fileName          |Name of the file to write binary dumps into                 |string    |             | ""                 |       |
+------------------+------------------------------------------------------------+----------+-------------+--------------------+-------+
|format            |Packet format                                               |string    |             | ""                 |       |
+------------------+------------------------------------------------------------+----------+-------------+--------------------+-------+

USS Encoder Plugin
------------------

**Introduction**

This plugin contains packet encoders for USS data (generic and vendor-specific).