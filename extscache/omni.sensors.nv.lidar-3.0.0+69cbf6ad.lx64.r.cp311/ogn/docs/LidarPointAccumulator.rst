.. _omni_sensors_nv_lidar_LidarPointAccumulator_1:

.. _omni_sensors_nv_lidar_LidarPointAccumulator:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Lidar Point Accumulator
    :keywords: lang-en omnigraph node lidar lidar-point-accumulator


Lidar Point Accumulator
=======================

.. <description>

Gets pointcloud and writes it to csv file

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.lidar<ext_omni_sensors_nv_lidar>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Color Code (*inputs:colorCode*)", "``int``", "0 - constant, 1 - intensity, 2 - height, 3 - range, 4 - objectId, 5 - echoId, 6 - materialId", "1"
    "Cuda Stream (*inputs:cudaStream*)", "``uint64``", "Cuda Stream Input", "0"
    "Desired Coords Type (*inputs:desiredCoordsType*)", "``token``", "Desired output coords type", "CARTESIAN"
    "", "Metadata", "*allowedTokens* = CARTESIAN,SPHERICAL", ""
    "Export Byte Points (*inputs:exportBytePoints*)", "``bool``", "Export lidar points", "False"
    "Output On GPU (*inputs:outputOnGPU*)", "``bool``", "Output on GPU", "False"
    "Publish Viz Points (*inputs:publishVizPoints*)", "``bool``", "Export viz points", "True"
    "Send Data Id (*inputs:sendDataId*)", "``int``", "Send data id to distinguish point clouds on the receiver side", "0"
    "Sensor Mount6 D Pose (*inputs:sensorMount6DPose*)", "``float[]``", "[x,y,z,r,p,y]", "[]"
    "Src (*inputs:src*)", "``uint64``", "Input buffer", "0"
    "Src Meta (*inputs:srcMeta*)", "``uint64``", "Input meta data buffer", "0"
    "Target PID (*inputs:targetPID*)", "``uint64``", "Target process ID to send data stream to", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Stream (*outputs:cudaStream*)", "``uint64``", "Cuda Stream Input", "0"
    "Dest (*outputs:dest*)", "``uint64``", "Output buffer of accumulated GenericModelOutput", "0"
    "New Data (*outputs:newData*)", "``bool``", "True if new data is published", "False"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.lidar.LidarPointAccumulator"
    "Version", "1"
    "Extension", "omni.sensors.nv.lidar"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "LidarPointAccumulatorDatabase"
    "Python Module", "omni.sensors.nv.lidar"

