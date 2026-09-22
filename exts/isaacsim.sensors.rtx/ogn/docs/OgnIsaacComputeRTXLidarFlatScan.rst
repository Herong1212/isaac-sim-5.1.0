.. _isaacsim_sensors_rtx_IsaacComputeRTXLidarFlatScan_3:

.. _isaacsim_sensors_rtx_IsaacComputeRTXLidarFlatScan:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Compute RTX Lidar Flat Scan
    :keywords: lang-en omnigraph node isaacRtxSensor rtx isaac-compute-r-t-x-lidar-flat-scan


Isaac Compute RTX Lidar Flat Scan
=================================

.. <description>

Extracts depth and intensity values from returns of accumulated scan of 2D RTX Lidar.

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.sensors.rtx<ext_isaacsim_sensors_rtx>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Azimuth Buffer Size (*inputs:azimuthBufferSize*)", "``uint64``", "size", "0"
    "", "Metadata", "*hidden* = true", ""
    "Azimuth Data Type (*inputs:azimuthDataType*)", "``float``", "type", "4"
    "", "Metadata", "*hidden* = true", ""
    "azimuth (*inputs:azimuthPtr*)", "``uint64``", "azimuth in rad [-pi,pi]", "0"
    "Buffer Size (*inputs:bufferSize*)", "``uint64``", "DEPRECATED - Size (in bytes) of the buffer (0 if the input is a texture)", "0"
    "Cuda Device Index (*inputs:cudaDeviceIndex*)", "``int``", "Index of the device on which data was originally generated.", "-1"
    "Data Pointer (*inputs:dataPtr*)", "``uint64``", "DEPRECATED - Pointer to Lidar render result.", "0"
    "Distance Buffer Size (*inputs:distanceBufferSize*)", "``uint64``", "size", "0"
    "", "Metadata", "*hidden* = true", ""
    "Distance Data Type (*inputs:distanceDataType*)", "``float``", "type", "4"
    "", "Metadata", "*hidden* = true", ""
    "distance (*inputs:distancePtr*)", "``uint64``", "range in m", "0"
    "Exec (*inputs:exec*)", "``execution``", "The input execution port", "None"
    "Intensity Buffer Size (*inputs:intensityBufferSize*)", "``uint64``", "size", "0"
    "", "Metadata", "*hidden* = true", ""
    "Intensity Data Type (*inputs:intensityDataType*)", "``float``", "type", "4"
    "", "Metadata", "*hidden* = true", ""
    "intensity (*inputs:intensityPtr*)", "``uint64``", "intensity [0,1]", "0"
    "Metadata Pointer (*inputs:metaDataPtr*)", "``uint64``", "Pointer to Lidar metadata.", "0"
    "Render Product Path (*inputs:renderProductPath*)", "``token``", "Used to retrieve Lidar configuration.", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Azimuth Range (*outputs:azimuthRange*)", "``float[2]``", "The azimuth range [min, max] (deg).", "[0.0, 0.0]"
    "Depth Range (*outputs:depthRange*)", "``float[2]``", "Range for sensor to detect a hit [min, max] (m)", "[0, 0]"
    "Exec (*outputs:exec*)", "``execution``", "Output execution triggers when lidar sensor has accumulated a full scan.", "None"
    "Horizontal Fov (*outputs:horizontalFov*)", "``float``", "Horizontal Field of View (deg)", "0"
    "Horizontal Resolution (*outputs:horizontalResolution*)", "``float``", "Increment between horizontal rays (deg)", "0"
    "Intensities Data (*outputs:intensitiesData*)", "``uchar[]``", "Intensity measurements from full scan, ordered by increasing azimuth", "[]"
    "Linear Depth Data (*outputs:linearDepthData*)", "``float[]``", "Linear depth measurements from full scan, ordered by increasing azimuth (m)", "[]"
    "Num Cols (*outputs:numCols*)", "``int``", "Number of columns in buffers", "0"
    "Num Rows (*outputs:numRows*)", "``int``", "Number of rows in buffers", "1"
    "Rotation Rate (*outputs:rotationRate*)", "``float``", "Rotation rate of sensor in Hz", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.sensors.rtx.IsaacComputeRTXLidarFlatScan"
    "Version", "3"
    "Extension", "isaacsim.sensors.rtx"
    "Icon", "ogn/icons/isaacsim.sensors.rtx.IsaacComputeRTXLidarFlatScan.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "categories", "Sensor"
    "keywords", "rtx,lidar,sensor"
    "tooltip", "Extracts depth and intensity values from returns of accumulated scan of 2D RTX Lidar."
    "display_name", "Compute RTX Lidar Flat Scan"
    "Categories", "isaacRtxSensor"
    "Generated Class Name", "OgnIsaacComputeRTXLidarFlatScanDatabase"
    "Python Module", "isaacsim.sensors.rtx"

