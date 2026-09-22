.. _omni_sensors_nv_camera_ColorCorrectionTaskNode_1:

.. _omni_sensors_nv_camera_ColorCorrectionTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Color Correction Task Node
    :keywords: lang-en omnigraph node camera color-correction-task-node


Color Correction Task Node
==========================

.. <description>

Corrects the color mapping of a camera image.

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bb (*inputs:Bb*)", "``float``", "Blue_blue", "1.0"
    "Bg (*inputs:Bg*)", "``float``", "Blue_green", "0.0"
    "Br (*inputs:Br*)", "``float``", "Blue_red", "0.0"
    "Gb (*inputs:Gb*)", "``float``", "Green_blue", "0.0"
    "Gg (*inputs:Gg*)", "``float``", "Green_green", "1.0"
    "Gr (*inputs:Gr*)", "``float``", "Green_red", "0.0"
    "Rb (*inputs:Rb*)", "``float``", "Red_blue", "0.0"
    "Rg (*inputs:Rg*)", "``float``", "Red_green", "0.0"
    "Rr (*inputs:Rr*)", "``float``", "Red_red", "1.0"
    "Apply Saturation (*inputs:applySaturation*)", "``bool``", "indicates whether black and fullwell shall be applied", "False"
    "Black (*inputs:black*)", "``float``", "Black floor level", "0.0"
    "Fullwell Black (*inputs:fullwell_black*)", "``float``", "maximal allowed value of the input array until it saturates", "1.0"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Output Float16 (*inputs:output_float16*)", "``bool``", "indicates whether the output should be float16", "False"
    "Red Blue Swap (*inputs:redBlueSwap*)", "``bool``", "indicates whether the first and the third component shall be swapped", "False"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"
    "Use Interactive Mode (*inputs:useInteractiveMode*)", "``bool``", "the CCM could be changed after the intialization (Linux only), uses cuda managed memory, only for sensor setup. Don't use in simulation scenarios", "False"
    "White Balance (*inputs:whiteBalance*)", "``float[3]``", "white balance correction of the light source", "[1.0, 1.0, 1.0]"


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

    "Unique ID", "omni.sensors.nv.camera.ColorCorrectionTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamColorCorrectionTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

