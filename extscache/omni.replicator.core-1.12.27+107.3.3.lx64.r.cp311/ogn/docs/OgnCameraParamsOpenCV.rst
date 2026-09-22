.. _omni_replicator_core_CameraParamsOpenCV_1:

.. _omni_replicator_core_CameraParamsOpenCV:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Camera Params Open CV
    :keywords: lang-en omnigraph node Replicator core camera-params-open-c-v


Camera Params Open CV
=====================

.. <description>

Temporary node to read OpenCVFx and OpenCVFy from fabric while kit has not been updated.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Gpu (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations.", "0"
    "Render Product Path (*inputs:renderProductPath*)", "``token``", "RenderProduct prim path", ""
    "Render Results (*inputs:renderResults*)", "``uint64``", "Render results", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Camera Open CV Fx (*outputs:cameraOpenCVFx*)", "``float``", "Camera OpenCV fx", "None"
    "Camera Open CV Fy (*outputs:cameraOpenCVFy*)", "``float``", "Camera OpenCV fy", "None"
    "Received (*outputs:exec*)", "``execution``", "Executes for each newFrame event received", "None"
    "Is Pinhole Open CV (*outputs:isPinholeOpenCV*)", "``bool``", "Is pinhole openCV camera", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.CameraParamsOpenCV"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""CameraParamsOpenCV""]"
    "Categories", "Replicator"
    "__categoryDescriptions", "Replicator,Annotators"
    "Generated Class Name", "OgnCameraParamsOpenCVDatabase"
    "Python Module", "omni.replicator.core"

