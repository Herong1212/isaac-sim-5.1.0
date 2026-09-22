.. _ext_omni_sensors_nv_radar:

Omniverse Radar Extension
==========================

Introduction
------------

The Radar Sensor extension consists of models and OmniGraph nodes for various post-processing functions (e.g., transcoding
Radar data into vendor-specific formats).

Currently, the extension supports one model:

- WpmDmatApproxRadar

This model has its own parameterization and at least one post-processing OmniGraph definition that specifies the processing pipeline nodes
with default parameters.

Multiple post-processing OmniGraphs can exist for the same Radar model, each with unique parameter values and/or different node configurations.

"WpmDmatApprox" stands for "Wave Propagation Model Detection Matrix Approximation". It uses the Wave Propagation Model (WPM) to ensure high fidelity while maintaining real-time capability.
Key features include:

- Multiple bounces
- Support for different materials and improved radiometry
- Antenna gain patterns
- Multiple scan configurations (e.g. near and far scan) per Radar instance

**Example Radar Prim**

This is an example of how to define a Radar sensor in USD:

.. code-block:: usda

    def OmniRadar "generic_radar" (
        doc = """Defines an instance of a radar that uses WPM DMAT approximation model"""
        prepend apiSchemas = ["OmniSensorGenericRadarWpmDmatAPI", "OmniSensorGenericRadarWpmDmatScanCfgAPI:s002"]
    )
    {
        # Global radar parameters from OmniSensorGenericRadarWpmDmatAPI
        float omni:sensor:tickRate = 20.0
        token omni:sensor:WpmDmat:auxOutputType = "NONE"
        token omni:sensor:WpmDmat:elementsCoordsType = "SPHERICAL"
        token omni:sensor:WpmDmat:outputFrameOfReference = "SENSOR"
        float[] omni:sensor:WpmDmat:customFrameOfReferenceTrafo = [0,0,0,0,0,0]
        float omni:sensor:WpmDmat:wavelengthmm = 3.9
        uint omni:sensor:WpmDmat:tracetreedepth = 4
        uint omni:sensor:WpmDmat:instancetimeoffsetusec = 5000
        token omni:sensor:WpmDmat:cfarmode = "2D"
        token omni:sensor:WpmDmat:antennagainmode = "COSINEFALLOFF"

        # First scan configuration (short range, wide angle)
        token omni:sensor:WpmDmat:scan:s001:elevMode = "NO_EL"
        float omni:sensor:WpmDmat:scan:s001:maxRangeM = 50
        float omni:sensor:WpmDmat:scan:s001:maxAzAngDeg = 75
        float omni:sensor:WpmDmat:scan:s001:maxElAngDeg = 20
        float omni:sensor:WpmDmat:scan:s001:raysPerDeg = 8.0
        uint omni:sensor:WpmDmat:scan:s001:timeOffsetUsec = 0
        float omni:sensor:WpmDmat:scan:s001:powerFactor = 1.0
        bool omni:sensor:WpmDmat:scan:s001:binsFromSpec = true
        bool omni:sensor:WpmDmat:scan:s001:enAngAliasing = false
        bool omni:sensor:WpmDmat:scan:s001:detValFromBinIdx = false
        float omni:sensor:WpmDmat:scan:s001:rangeResM = 0.4
        float omni:sensor:WpmDmat:scan:s001:velResMps = 0.147
        float omni:sensor:WpmDmat:scan:s001:boreAzResDeg = 1.3
        float omni:sensor:WpmDmat:scan:s001:boreElResDeg = 5.0
        uint omni:sensor:WpmDmat:scan:s001:rBins = 112
        uint omni:sensor:WpmDmat:scan:s001:vBins = 160
        uint omni:sensor:WpmDmat:scan:s001:azBins = 12
        uint omni:sensor:WpmDmat:scan:s001:elBins = 2
        uint omni:sensor:WpmDmat:scan:s001:cfarRnT = 1
        uint omni:sensor:WpmDmat:scan:s001:cfarRnG = 0
        uint omni:sensor:WpmDmat:scan:s001:cfarVnT = 1
        uint omni:sensor:WpmDmat:scan:s001:cfarVnG = 0
        uint omni:sensor:WpmDmat:scan:s001:cfarAznT = 1
        uint omni:sensor:WpmDmat:scan:s001:cfarAznG = 0
        uint omni:sensor:WpmDmat:scan:s001:cfarElnT = 1
        uint omni:sensor:WpmDmat:scan:s001:cfarElnG = 0
        float omni:sensor:WpmDmat:scan:s001:cfarMinVal = 7e-17
        float omni:sensor:WpmDmat:scan:s001:cfarOffset = 1.0
        float omni:sensor:WpmDmat:scan:s001:cfarNoiseMean = 0.0
        float omni:sensor:WpmDmat:scan:s001:cfarNoiseSDev = 0.0
        float[] omni:sensor:WpmDmat:scan:s001:maxVelMpsSequence = [50.0, 55.0]
        float[] omni:sensor:WpmDmat:scan:s001:rcsTuningCoefficients = [-12, 150, 0.0]
        float omni:sensor:WpmDmat:scan:s001:azimuthRadNoiseMean = 0.0
        float omni:sensor:WpmDmat:scan:s001:azimuthRadNoiseSDev = 0.0
        float omni:sensor:WpmDmat:scan:s001:elevationRadNoiseMean = 0.0
        float omni:sensor:WpmDmat:scan:s001:elevationRadNoiseSDev = 0.0
        float omni:sensor:WpmDmat:scan:s001:velocityNoiseMean = 0.0
        float omni:sensor:WpmDmat:scan:s001:velocityNoiseSDev = 0.0
        float omni:sensor:WpmDmat:scan:s001:rangeNoiseMean = 0.0
        float omni:sensor:WpmDmat:scan:s001:rangeNoiseSDev = 0.0
        float omni:sensor:WpmDmat:scan:s001:exponentialDecayFactor = 1.0

        # Second scan configuration (long range, narrow angle)
        token omni:sensor:WpmDmat:scan:s002:elevMode = "POS_EL"
        float omni:sensor:WpmDmat:scan:s002:maxRangeM = 300
        float omni:sensor:WpmDmat:scan:s002:maxAzAngDeg = 9
        float omni:sensor:WpmDmat:scan:s002:maxElAngDeg = 7
        # Define more parameters for s002 analogously to s001...

        def RenderProduct "RenderedOutputs"
        {
            uniform int2 resolution = (1280, 720)
            rel camera = <../../generic_radar>
            rel orderedVars = [
                <SupportedOutputs/RtxSensorCpu>,
                <SupportedOutputs/RtxSensorGpu>,
                <SupportedOutputs/RtxSensorGmo>,
                <SupportedOutputs/RtxSensorMetadata>,
            ]

            def Scope "SupportedOutputs"
            {
                def RenderVar "RtxSensorCpu"
                {
                    uniform string sourceName = "RtxSensorCpu"
                }
                def RenderVar "RtxSensorGpu"
                {
                    uniform string sourceName = "RtxSensorGpu"
                }
                def RenderVar "RtxSensorGmo"
                {
                    uniform string sourceName = "GenericModelOutput"
                }
                def RenderVar "RtxSensorMetadata"
                {
                    string sourceName = "RtxSensorMetadata"
                }
            }
        }
    }

.. _setting-radar-attributes:

Setting Radar attributes
------------------------

There are many attributes specific to OmniRadar prims that must be set to configure sensor behavior.
The Radar sensor simulation supports multiple scan patterns, allowing a Radar to
behave differently, e.g. in a near range and a far range scan. Usually,
a configuration is supplied with the goal of bringing the simulated
sensor's behavior as close to the real sensor as possible.

| In the Radar sensor's prim, parameters of the Radar can be set by
| prepending them with ``<parameterType> omni:sensor:WpmDmat:<parameterName> = <value>``
|
| For example
| ``uint omni:sensor:WpmDmat:TraceTreeDepth = 4``

.. _sensor-level-parameters:

Sensor-Level Parameters
^^^^^^^^^^^^^^^^^^^^^^^

To build a custom parameterization, there are some parameters that are
set once for each sensor and are the same across all of the sensor's
scan patterns:

.. table::
    :widths: auto

    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | Attribute                   | Description                                                                                              | Unit   | Allowed Values            |
    +=============================+==========================================================================================================+========+===========================+
    | WaveLengthMm                | Wavelength of the Radar                                                                                  | mm     | 3.9                       |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | TraceTreeDepth              | Depth of the ray tree build while traversing the scene. A bigger depth allows for realistic effects      | -      | Positive integer          |
    |                             | like multi bounce, while a shallower depth will increase performance                                     |        |                           |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | InstanceTimeOffsetUsec      | Time offset of this Radar instance to simulate continuous firing in a group of Radars                    | μs     | Any float                 |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | CfarMode                    | 2D: Only range and velocity dimensions are considered for CFAR processing                                | -      | "2D", "4D"                |
    |                             | 4D: Range, velocity, azimuth, and elevation dimensions are considered for CFAR processing                |        |                           |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | AntennaGainMode             | Antenna gain profile                                                                                     | -      | "COSINEFALLOFF","CONSTANT"|
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | NumScans                    | The number of scan patterns that the sensor supports. If a number of two is given,                       | -      | Positive integer          |
    |                             | the following parameters need to be repeated for each scan pattern, as described below.                  |        |                           |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+

The following parameters have to be set per scan, where the total number
of scans is determined by the ``omni:sensor:WpmDmat:NumScans`` value.

| The parameters that describe a scan are defined in the following way:
| ``<parameterType> omni:sensor:WpmDmat:scan<Idx>:<parameterName> = <value>``
| For example
| ``float omni:sensor:WpmDmat:scan1:RaysPerDeg = 10.0``

.. warning:: The scan index starts at 1, not at 0.

General Scan Parameters
^^^^^^^^^^^^^^^^^^^^^^^

The following parameters are provided once for each scan and influence
the general behavior of a Radar sensor. ``RaysPerDeg`` influences how many
rays the sensor shoots per degree and together with the parameters that
determine the sensor's field-of-view (FoV), the total number of rays is calculated.
Changing this value increases fidelity but decreases performance.

.. table::
    :widths: auto


    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+-----------------------------+
    | Attribute                   | Description                                                                                              | Unit   | Allowed Values              |
    +=============================+==========================================================================================================+========+=============================+
    | RaysPerDeg                  | Ray density. The total number of rays is depended on ``MaxAzAngDeg`` and ``MaxElAngDeg`` as well         | -      | Positive integer            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+-----------------------------+
    | TimeOffsetUsec              | time offset of the scan from the frame time to simulate non-equidistant scans                            | μs     | Any float                   |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+-----------------------------+
    | PowerFactor                 | Total output power of Radar                                                                              | W      | Positive float              |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+-----------------------------+
    | EnAngAliasing               | Enable angular aliasing                                                                                  | -      | true, false                 |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+-----------------------------+
    | DetValFromBinIdx            | If true, detection value derived from bin index; if false, more accurate inside cell                     | -      | true, false                 |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+-----------------------------+
    | ElevMode                    | Elevation mode; FULL_EL:pos neg elevation  POS_EL:only pos elevation  NO_EL: elevation=0                 | -      | "FULL_EL", "POS_EL", "NO_EL"|
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+-----------------------------+


Range and Angle Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^

These values are set per scan and determine the detection range of the
sensor as well as the FoV. These values are usually found in a Radar
sensor's spec sheet and can easily be set to approach the behavior of a
given real sensor.

.. table::
    :widths: auto

    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | Attribute                   | Description                                                                                              | Unit   | Allowed Values            |
    +=============================+==========================================================================================================+========+===========================+
    | MaxRangeM                   | Maximum detection range of the scan                                                                      | m      | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | MaxAzAngDeg                 | Maximum azimuth angle, FOV is 2x this value                                                              | deg    | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | MaxElAngDeg                 | Maximum elevation angle, FOV is 2x this value                                                            | deg    | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | RangeResM                   | Range resolution, only if ``BinsFromSpec`` is ``true``                                                   | m      | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | VelResMps                   | Velocity resolution, only if ``BinsFromSpec`` is ``true``                                                | m/s    | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | BoreAzResDeg                | Azimuth resolution at bore sight, only if ``BinsFromSpec`` is ``true``                                   | deg    | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | BoreElResDeg                | Elevation resolution at bore sight, only if ``BinsFromSpec`` is ``true``                                 | deg    | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+


Bin Parameters
^^^^^^^^^^^^^^^

These values are set per scan as well. The number of bins that the Radar
sensor uses to bin the returns can either be calculated by the sensor
from the values in the previous table or explicit values can be given to
the sensor. If ``BinsFromSpec`` is ``true``, the values for ``RBins``,
``VBins``, ``AzBins`` and ``ElBins`` will be ignored.

.. table::
    :widths: auto

    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | Attribute                   | Description                                                                                              | Unit   | Allowed Values            |
    +=============================+==========================================================================================================+========+===========================+
    | BinsFromSpec                | Flag to determine if bins are derived from resolution parameters                                         | -      | true, false               |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | RBins                       | Number of range bins of this scan. Only if ``BinsFromSpec`` is ``false``.                                | -      | Positive integer          |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | VBins                       | Number of velocity bins of this scan. Only if ``BinsFromSpec`` is ``false``.                             | -      | Positive integer          |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | AzBins                      | Number of azimuth bins of this scan. Only if ``BinsFromSpec`` is ``false``.                              | -      | Positive integer          |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | ElBins                      | Number of elevation bins of this scan. Only if ``BinsFromSpec`` is ``false``.                            | -      | Positive integer          |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+


CFAR (Constant False Alarm Rate) Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Cfar-parameters are set per scan. A Cfar-Implementation is used to
filter all returns that the sensor received for only the ones that are
targets of interest.

.. table::
    :widths: auto

    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | Attribute                   | Description                                                                                              | Unit   | Allowed Values            |
    +=============================+==========================================================================================================+========+===========================+
    | CfarRnT                     | CFAR number of range test cells                                                                          | -      | Positive integer          |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | CfarRnG                     | CFAR number of range guard cells                                                                         | -      | Positive integer          |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | CfarVnT                     | CFAR number of velocity test cells                                                                       | -      | Positive integer          |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | CfarVnG                     | CFAR number of velocity guard cells                                                                      | -      | Positive integer          |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | CfarAznT                    | CFAR number of azimuth test cells                                                                        | -      | Positive integer          |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | CfarAznG                    | CFAR number of azimuth guard cells                                                                       | -      | Positive integer          |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | CfarElnT                    | CFAR number of elevation test cells                                                                      | -      | Positive integer          |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | CfarElnG                    | CFAR number of elevation guard cells                                                                     | -      | Positive integer          |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | CfarMinVal                  | CFAR minimum value for detection, cells below are discarded                                              | -      | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | CfarOffset                  | Multiplied with raw CFAR noise level. Set to 1 if no scaling of noise is desired                         | -      | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | CfarNoiseMean               | Mean noise level used in CFAR                                                                            | -      | Any float                 |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | CfarNoiseSDev               | Standard deviation of noise in CFAR                                                                      | -      | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+


Noise Parameters
^^^^^^^^^^^^^^^^

The noise parameters are set per scan. The Noise parameters category
defines the characteristics of the noise affecting the Radar sensor's
measurements. These parameters help simulate real-world imperfections
and variability in the sensor's readings.

.. table::
    :widths: auto

    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | Attribute                   | Description                                                                                              | Unit   | Allowed Values            |
    +=============================+==========================================================================================================+========+===========================+
    | AzimuthRadNoiseMean         | Mean noise added to azimuth radial measurements                                                          | rad    | Any float                 |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | AzimuthRadNoiseSDev         | Standard deviation of azimuth radial noise at boresight                                                  | rad    | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | ElevationRadNoiseMean       | Mean noise added to elevation radial measurements                                                        | rad    | Any float                 |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | ElevationRadNoiseSDev       | Standard deviation of elevation radial noise at boresight                                                | rad    | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | VelocityNoiseMean           | Mean noise added to velocity measurements                                                                | m/s    | Any float                 |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | VelocityNoiseSDev           | Standard deviation of noise added to velocity measurements                                               | m/s    | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | RangeNoiseMean              | Mean noise added to range measurements                                                                   | m      | Any float                 |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | RangeNoiseSDev              | Standard deviation of noise added to range measurements                                                  | m      | Positive float            |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+

Sequence and Coefficient Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The sequence parameters are set per scan. The ``RcsTuningCoefficients`` array
is especially useful for tuning a Radar simulation to behave as similar as
possible to the real Radar.

.. table::
    :widths: auto

    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | Attribute                   | Description                                                                                              | Unit   | Allowed Values            |
    +=============================+==========================================================================================================+========+===========================+
    | MaxVelMpsSequence           | An array representing the maximum unambiguous velocity sequence of the scan, expressed in meters per     | m/s    | Array of floats           |
    |                             | second. This parameter models the varying maximum velocity that the Radar can unambiguously measure      |        |                           |
    |                             | over different time intervals.                                                                           |        |                           |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+
    | RcsTuningCoefficients       | The ``RcsTuningCoefficients`` are a list of parameters that influence the computation of the RCS.        | -      | Array of 3 floats         |
    |                             | ``RcsTuningCoefficients[0]`` is a threshold value and only returns with a RCS [dBsm] >                   |        |                           |
    |                             | ``RcsTuningCoefficients[0]`` will be accepted. ``RcsTuningCoefficients[1]`` is a scaling parameter       |        |                           |
    |                             | that's multiplied with the RCS before it is converted to dBsm. ``RcsTuningCoefficients[2]`` is a         |        |                           |
    |                             | scaling parameter that is multiplied with normalized noise that is added to the RCS after conversion     |        |                           |
    |                             | to dBsm. A value 0 will therefore not add any noise.                                                     |        |                           |
    +-----------------------------+----------------------------------------------------------------------------------------------------------+--------+---------------------------+


Radar Point Cloud
-----------------

The Radar extension uses the ``GenericModelOutput`` format. Refer to the documentation for more information on ``GenericModelOutput``.
