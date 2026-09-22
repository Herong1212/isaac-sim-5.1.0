.. _omni_sensors_nv_camera_CamCompandingTaskNode_1:

.. _omni_sensors_nv_camera_CamCompandingTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam Companding Task Node
    :keywords: lang-en omnigraph node camera cam-companding-task-node


Cam Companding Task Node
========================

.. <description>

Does the companding and translates the pixels into the right value range

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Alignment (*inputs:Alignment*)", "``uint``", "alignment of the MSB of the companding, LSB starts with 0", "11"
    "Linear Compand Coeff (*inputs:LinearCompandCoeff*)", "``float[2][]``", "Array of companding parameters", "[]"
    "Post Pedestal (*inputs:PostPedestal*)", "``uint``", "Add a post companding pedestal", "0"
    "Pre Pedestal (*inputs:PrePedestal*)", "``uint``", "Add a pedestal before applying the companding", "0"
    "Embedded Src (*inputs:embeddedSrc*)", "``uint64``", "Embedded Data Lines Source Buffer", "0"
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
    "Embedded Dest (*outputs:embeddedDest*)", "``uint64``", "Embedded Data Lines Destination Buffer", "0"
    "gpuFoundationsOut (*outputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "None"
    "Hydra Time Out (*outputs:hydraTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"
    "renderProductOut (*outputs:rp*)", "``uint64``", "Pointer to render product for this view", "None"
    "Sim Time Out (*outputs:simTimeOut*)", "``double``", "timecode/timestamp output in [ns]", "0.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.camera.CamCompandingTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamCompandingTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

