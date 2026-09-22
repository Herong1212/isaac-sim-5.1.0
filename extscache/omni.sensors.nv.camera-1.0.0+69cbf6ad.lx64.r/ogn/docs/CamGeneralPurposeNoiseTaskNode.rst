.. _omni_sensors_nv_camera_CamGeneralPurposeNoiseTask_1:

.. _omni_sensors_nv_camera_CamGeneralPurposeNoiseTask:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam General Purpose Noise Task
    :keywords: lang-en omnigraph node camera cam-general-purpose-noise-task


Cam General Purpose Noise Task
==============================

.. <description>

Adds dynamic noise to the image (photon shot noise and dark shot noise).

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Dark Shot Noise Gain (*inputs:darkShotNoiseGain*)", "``float``", "gain of the dark shot noise", "1.0"
    "Dark Shot Noise Sigma (*inputs:darkShotNoiseSigma*)", "``float``", "standard deviation (sigma) of the dark shot noise", "1.0"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Hdr Combination Data (*inputs:hdrCombinationData*)", "``float[2][]``", "Array of (border value of HDR region end, applied HDR gain), describes the gains of the noise in the different HDR regions", "[]"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Dest (*outputs:dest*)", "``uint64``", "Destination Buffer", "0"
    "gpuFoundationsOut (*outputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "None"
    "Hydra Time Out (*outputs:hydraTimeOut*)", "``double``", "timecode/timestamp output in [s]", "0.0"
    "renderProductOut (*outputs:rp*)", "``uint64``", "Pointer to render product for this view", "None"
    "Sim Time Out (*outputs:simTimeOut*)", "``double``", "timecode/timestamp output in [s]", "0.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.camera.CamGeneralPurposeNoiseTask"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamGeneralPurposeNoiseTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

