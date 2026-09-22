.. _omni_sensors_nv_camera_CamCfa2x2BilinearDemosaicingTaskNode_1:

.. _omni_sensors_nv_camera_CamCfa2x2BilinearDemosaicingTaskNode:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Cam Cfa2x2 Bilinear Demosaicing Task Node
    :keywords: lang-en omnigraph node camera cam-cfa2x2-bilinear-demosaicing-task-node


Cam Cfa2x2 Bilinear Demosaicing Task Node
=========================================

.. <description>

Translates a 2x2 CFA image into RGBA via simple bilinear demosaicing - This task doesn't cut the dynamic range if the content is more than 16 bits

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.camera<ext_omni_sensors_nv_camera>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "After Demosaicing Correction (*inputs:afterDemosaicingCorrection*)", "``float[3]``", "RGB gain correction after demosaicing has been applied", "[1.0, 1.0, 1.0]"
    "Blue (*inputs:blue*)", "``float[4]``", "RGBA Blue Components from CFA_CF00 CFA_CF01, CFA_CF10, CFA_CF11", "[0.0, 0.0, 0.0, 1.0]"
    "Embedded Src (*inputs:embeddedSrc*)", "``uint64``", "Embedded Data Lines Source Buffer", "0"
    "Flip Horizontal (*inputs:flipHorizontal*)", "``bool``", "horizonal mirroring", "False"
    "Flip Vertical (*inputs:flipVertical*)", "``bool``", "vertical mirroring", "False"
    "gpuFoundations (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Green (*inputs:green*)", "``float[4]``", "RGBA Blue Components from CFA_CF00 CFA_CF01, CFA_CF10, CFA_CF11", "[0.0, 1.0, 1.0, 0.0]"
    "Hydra Time In (*inputs:hydraTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Maximal Value (*inputs:maximalValue*)", "``uint64``", "the maximal value of the internal processing (20bits : 1048575) (passthrough : 1) (default for 24 bits: 16777215)", "16777215"
    "Output Data Type Format (*inputs:outputDataTypeFormat*)", "``token``", "Data Type of the output format: [FLOAT32, UINT32]", "UINT32"
    "Red (*inputs:red*)", "``float[4]``", "RGBA Blue Components from CFA_CF00 CFA_CF01, CFA_CF10, CFA_CF11", "[1.0, 0.0, 0.0, 0.0]"
    "renderProduct (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"
    "Sim Time In (*inputs:simTimeIn*)", "``double``", "timecode/timestamp input in [ns]", "0"
    "Src (*inputs:src*)", "``uint64``", "Source Buffer", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Dest (*outputs:dest*)", "``uint64``", "Destination Buffer", "0"
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

    "Unique ID", "omni.sensors.nv.camera.CamCfa2x2BilinearDemosaicingTaskNode"
    "Version", "1"
    "Extension", "omni.sensors.nv.camera"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "CamCfa2x2BilinearDemosaicingTaskNodeDatabase"
    "Python Module", "omni.sensors.nv.camera"

