.. _omni_syntheticdata_SdTestRenderProductCamera_1:

.. _omni_syntheticdata_SdTestRenderProductCamera:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Test Render Product Camera
    :keywords: lang-en omnigraph node graph:simulation,graph:postRender,graph:action,internal:test syntheticdata sd-test-render-product-camera


Sd Test Render Product Camera
=============================

.. <description>

Synthetic Data node to test the renderProduct camera pipeline

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Camera Aperture Offset (*inputs:cameraApertureOffset*)", "``float[2]``", "Camera horizontal and vertical aperture offset", "[0.0, 0.0]"
    "Camera Aperture Size (*inputs:cameraApertureSize*)", "``float[2]``", "Camera horizontal and vertical aperture", "[0.0, 0.0]"
    "Camera F Stop (*inputs:cameraFStop*)", "``float``", "Camera fStop", "0.0"
    "Camera Fisheye Params (*inputs:cameraFisheyeParams*)", "``float[]``", "Camera fisheye projection parameters", "[]"
    "Camera Focal Length (*inputs:cameraFocalLength*)", "``float``", "Camera focal length", "0.0"
    "Camera Focus Distance (*inputs:cameraFocusDistance*)", "``float``", "Camera focus distance", "0.0"
    "Camera Model (*inputs:cameraModel*)", "``int``", "Camera model (pinhole or fisheye models)", "0"
    "Camera Near Far (*inputs:cameraNearFar*)", "``float[2]``", "Camera near/far clipping range", "[0.0, 0.0]"
    "Camera Projection (*inputs:cameraProjection*)", "``matrixd[4]``", "Camera projection matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Camera View Transform (*inputs:cameraViewTransform*)", "``matrixd[4]``", "Camera view matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*inputs:height*)", "``uint``", "Height of the frame", "0"
    "Meters Per Scene Unit (*inputs:metersPerSceneUnit*)", "``float``", "Scene units to meters scale", "0.0"
    "Render Product Camera Path (*inputs:renderProductCameraPath*)", "``token``", "RenderProduct camera prim path", ""
    "Render Product Resolution (*inputs:renderProductResolution*)", "``int[2]``", "RenderProduct resolution", "[0, 0]"
    "Render Results (*inputs:renderResults*)", "``uint64``", "OnDemand connection : pointer to render product results", "0"
    "renderProduct (*inputs:rp*)", "``uint64``", "PostRender connection : pointer to render product for this view", "0"
    "Stage (*inputs:stage*)", "``token``", "Stage in {simulation, postrender, ondemand}", ""
    "Trace Error (*inputs:traceError*)", "``bool``", "If true print an error message when the frame numbers are out-of-sync", "False"
    "Width (*inputs:width*)", "``uint``", "Width of the frame", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Test (*outputs:test*)", "``bool``", "Test value : false if failed", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdTestRenderProductCamera"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "__tokens", "[""simulation"", ""postRender"", ""onDemand""]"
    "Categories", "graph:simulation,graph:postRender,graph:action,internal:test"
    "Generated Class Name", "OgnSdTestRenderProductCameraDatabase"
    "Python Module", "omni.syntheticdata"

