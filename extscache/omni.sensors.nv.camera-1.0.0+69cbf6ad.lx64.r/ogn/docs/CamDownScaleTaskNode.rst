.. _omni_sensors_nv_camera_CamDownScaleTaskNode_1:

.. _omni_sensors_nv_camera_CamDownScaleTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam Down Scale Task Node
    :keywords: lang-en omnigraph node camera cam-down-scale-task-node


Cam Down Scale Task Node
========================

.. <description>

Scales down the camera image by a factor of 2^n

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Depth Precision (*inputs:depthPrecision*)", "``token``", "In case the downsampled data are depthmaps, they could be provided as FLOAT16 or FLOAT32", "FLOAT32"
    "Down Sample Factor (*inputs:downSampleFactor*)", "``uint64``", "Downsample Factor defined as 2^value ", "1"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Dest (*outputs:dest*)", "``uint64``", "Destination Buffer", "None"
    "gpuFoundationsOut (*outputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "None"
    "Hydra Time Out (*outputs:hydraTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"
    "renderProductOut (*outputs:rp*)", "``uint64``", "Pointer to render product for this view", "None"
    "Sim Time Out (*outputs:simTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.camera.CamDownScaleTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamDownScaleTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

