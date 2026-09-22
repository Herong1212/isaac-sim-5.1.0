.. _omni_sensors_nv_camera_CamFileWriterTaskNode_1:

.. _omni_sensors_nv_camera_CamFileWriterTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam File Writer Task Node
    :keywords: lang-en omnigraph node camera cam-file-writer-task-node


Cam File Writer Task Node
=========================

.. <description>

Writes a camera raw file

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bin Header (*inputs:binHeader*)", "``token``", "A binary header which shall be added to the output file", "/tmp/headertest.raw"
    "Each Frame One File (*inputs:eachFrameOneFile*)", "``bool``", "indicates whether all frames shall be stored as a separate file", "False"
    "Filename (*inputs:filename*)", "``token``", "File path to the video raw file", "/tmp/test.raw"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Only Last Frame (*inputs:onlyLastFrame*)", "``bool``", "Save only the most recent frame. Only works when combined with the 'eachFrameOneFile' option.", "False"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"
    "Use Header (*inputs:useHeader*)", "``bool``", "indicates whether an header shall be added to the file", "False"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.camera.CamFileWriterTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamFileWriterTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

