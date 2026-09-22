.. _omni_syntheticdata_SdRenderProductCamera_2:

.. _omni_syntheticdata_SdRenderProductCamera:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Render Product Camera
    :keywords: lang-en omnigraph node graph:postRender,graph:action syntheticdata sd-render-product-camera


Sd Render Product Camera
========================

.. <description>

Synthetic Data node to expose the camera data

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


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

    "Camera Aperture Offset (*outputs:cameraApertureOffset*)", "``float[2]``", "Camera horizontal and vertical aperture offset", "None"
    "Camera Aperture Size (*outputs:cameraApertureSize*)", "``float[2]``", "Camera horizontal and vertical aperture", "None"
    "Camera F Stop (*outputs:cameraFStop*)", "``float``", "Camera fStop", "None"
    "Camera Fisheye Params (*outputs:cameraFisheyeParams*)", "``float[]``", "Camera fisheye projection parameters", "None"
    "Camera Focal Length (*outputs:cameraFocalLength*)", "``float``", "Camera focal length", "None"
    "Camera Focus Distance (*outputs:cameraFocusDistance*)", "``float``", "Camera focus distance", "None"
    "Camera Model (*outputs:cameraModel*)", "``int``", "Camera model (pinhole or fisheye models)", "None"
    "Camera Near Far (*outputs:cameraNearFar*)", "``float[2]``", "Camera near/far clipping range", "None"
    "Camera Projection (*outputs:cameraProjection*)", "``matrixd[4]``", "Camera projection matrix", "None"
    "Camera View Transform (*outputs:cameraViewTransform*)", "``matrixd[4]``", "Camera view matrix", "None"
    "Received (*outputs:exec*)", "``execution``", "Executes for each newFrame event received", "None"
    "Meters Per Scene Unit (*outputs:metersPerSceneUnit*)", "``float``", "Scene units to meters scale", "None"
    "Render Product Resolution (*outputs:renderProductResolution*)", "``int[2]``", "RenderProduct resolution", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdRenderProductCamera"
    "Version", "2"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""RenderProductCameraSD""]"
    "Categories", "graph:postRender,graph:action"
    "Generated Class Name", "OgnSdRenderProductCameraDatabase"
    "Python Module", "omni.syntheticdata"

