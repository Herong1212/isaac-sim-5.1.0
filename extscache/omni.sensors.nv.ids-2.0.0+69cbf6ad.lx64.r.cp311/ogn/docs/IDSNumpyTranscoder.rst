.. _omni_sensors_nv_ids_IDSNumpyTranscoder_1:

.. _omni_sensors_nv_ids_IDSNumpyTranscoder:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: IDS Numpy Transcoder
    :keywords: lang-en omnigraph node ids i-d-s-numpy-transcoder


IDS Numpy Transcoder
====================

.. <description>

Receives Radar data and prepares a buffer for it from the buffer manager, and passes it to output

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.ids<ext_omni_sensors_nv_ids>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Stream In (*inputs:cudaStreamIn*)", "``uint64``", "Cuda Stream Input", "0"
    "File Name (*inputs:fileName*)", "``string``", "File name in which data is going to be stored", ""
    "In (*inputs:in*)", "``uint64``", "Source Buffer", "0"
    "Meta Data In (*inputs:metaDataIn*)", "``uint64``", "Source Buffer", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.ids.IDSNumpyTranscoder"
    "Version", "1"
    "Extension", "omni.sensors.nv.ids"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "IDSNumpyTranscoderDatabase"
    "Python Module", "omni.sensors.nv.ids"

