.. _omni_sensors_nv_camera_CamEtHdrNoiseTask_1:

.. _omni_sensors_nv_camera_CamEtHdrNoiseTask:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam Et Hdr Noise Task
    :keywords: lang-en omnigraph node camera cam-et-hdr-noise-task


Cam Et Hdr Noise Task
=====================

.. <description>

Adds Dark Noise (spatital and temporal) to the image.

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Hdr Combination Data (*inputs:hdrCombinationData*)", "``float[3][]``", "Array of (gain, exposure time, max linear value) of the HDR regions", "[]"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Realtime (*inputs:realtime*)", "``bool``", "determines how the random values are generated (true= random per image (not yet implemented), false = random per pixel", "False"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Spatial Noise File Exposure Time (*inputs:spatialNoiseFileExposureTime*)", "``float``", "The exposure time in [s] ", "0.33"
    "Spatial Noise File Gain (*inputs:spatialNoiseFileGain*)", "``float``", "The total gain applied of the noise file", "1.0"
    "Spatial Noise File Pedestal (*inputs:spatialNoiseFilePedestal*)", "``uint64``", "The pedestal used", "0"
    "Spatial Noise Filename (*inputs:spatialNoiseFilename*)", "``token``", "File path to a UINT16 spatial noise file", "/temp/noise_ar0820.raw"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"
    "Standard Deviation Dark Shot Noise (*inputs:standardDeviationDarkShotNoise*)", "``float``", "The temporal standard deviation of dark shot noise (0.0 to disable dark shot noise) ", "0.0"


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

    "Unique ID", "omni.sensors.nv.camera.CamEtHdrNoiseTask"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamEtHdrNoiseTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

