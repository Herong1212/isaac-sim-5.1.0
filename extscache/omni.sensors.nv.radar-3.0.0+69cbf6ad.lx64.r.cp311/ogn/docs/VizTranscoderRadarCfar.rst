.. _omni_sensors_nv_radar_VizTranscoderRadarCfar_1:

.. _omni_sensors_nv_radar_VizTranscoderRadarCfar:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Viz Transcoder Radar Cfar
    :keywords: lang-en omnigraph node radar viz-transcoder-radar-cfar


Viz Transcoder Radar Cfar
=========================

.. <description>

Receives Radar cfar and sends it for visualization

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.radar<ext_omni_sensors_nv_radar>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Color Code (*inputs:colorCode*)", "``int``", "0 - constant, 1 - HSV", "1"
    "Cuda Stream In (*inputs:cudaStreamIn*)", "``uint64``", "Cuda Stream Input", "0"
    "In (*inputs:in*)", "``uint64``", "Source Buffer", "0"
    "Max Val (*inputs:maxVal*)", "``float``", "max Cfar value", "1.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.radar.VizTranscoderRadarCfar"
    "Version", "1"
    "Extension", "omni.sensors.nv.radar"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "VizTranscoderRadarCfarDatabase"
    "Python Module", "omni.sensors.nv.radar"

