.. _omni_sensors_nv_camera_CamResizeImageTaskNode_1:

.. _omni_sensors_nv_camera_CamResizeImageTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam Resize Image Task Node
    :keywords: lang-en omnigraph node camera cam-resize-image-task-node


Cam Resize Image Task Node
==========================

.. <description>

Resizes an RGBA image

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
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Interpolation Method (*inputs:interpolationMethod*)", "``token``", "Method applied to do Interpolation: NEAREST_NEIGHBOUR, LINEAR, CUBIC, SUPERSAMPLING or LANCZOS ", "LANCZOS"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"
    "Src Sub Region Height (*inputs:srcSubRegionHeight*)", "``uint64``", "Height of the subRegion of the source", "1"
    "Src Sub Region Min X (*inputs:srcSubRegionMinX*)", "``uint64``", "The left upper corner coordinate in x", "0"
    "Src Sub Region Min Y (*inputs:srcSubRegionMinY*)", "``uint64``", "The left upper corner coordinate in y", "0"
    "Src Sub Region Width (*inputs:srcSubRegionWidth*)", "``uint64``", "Width of the subRegion of the source", "1"
    "Target Height (*inputs:targetHeight*)", "``uint64``", "width of the target image", "1"
    "Target Width (*inputs:targetWidth*)", "``uint64``", "width of the target image", "1"
    "Use Sub Region (*inputs:useSubRegion*)", "``bool``", "Indicates whether a subRegion (ROI) shall be extracted instead of the whole image", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Dest (*outputs:dest*)", "``uint64``", "Destination Buffer", "None"
    "gpuFoundationsOut (*outputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "None"
    "Hydra Time Out (*outputs:hydraTimeOut*)", "``double``", "timecode/timestamp output in [s]", "0.0"
    "renderProductOut (*outputs:rp*)", "``uint64``", "Pointer to render product for this view", "None"
    "Sim Time Out (*outputs:simTimeOut*)", "``double``", "timecode/timestamp output in [s]", "0.0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.camera.CamResizeImageTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamResizeImageTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

