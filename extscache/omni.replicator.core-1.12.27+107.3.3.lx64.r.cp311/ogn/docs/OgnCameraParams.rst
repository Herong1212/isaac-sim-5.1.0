.. _omni_replicator_core_CameraParams_1:

.. _omni_replicator_core_CameraParams:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Camera Params
    :keywords: lang-en omnigraph node Replicator:Annotators compute-on-request core camera-params


Camera Params
=============

.. <description>

This node exposes camera parameters.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


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
    "Camera Open CV Fx (*inputs:cameraOpenCVFx*)", "``float``", "Camera OpenCV fx", "0.0"
    "Camera Open CV Fy (*inputs:cameraOpenCVFy*)", "``float``", "Camera OpenCV fy", "0.0"
    "Camera Projection (*inputs:cameraProjection*)", "``matrixd[4]``", "Camera projection matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Camera View Transform (*inputs:cameraViewTransform*)", "``matrixd[4]``", "Camera view matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Is Pinhole Open CV (*inputs:isPinholeOpenCV*)", "``bool``", "Is pinhole openCV camera", "False"
    "Meters Per Scene Unit (*inputs:metersPerSceneUnit*)", "``float``", "Scene units to meters scale", "0.0"
    "Render Product Resolution (*inputs:renderProductResolution*)", "``int[2]``", "RenderProduct resolution", "[0, 0]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Camera Aperture (*outputs:cameraAperture*)", "``float[2]``", "Camera horizontal and vertical aperture", "None"
    "Camera Aperture Offset (*outputs:cameraApertureOffset*)", "``float[2]``", "Camera horizontal and vertical aperture offset", "None"
    "Camera F Stop (*outputs:cameraFStop*)", "``float``", "Camera fStop", "None"
    "Camera Fisheye Lens P (*outputs:cameraFisheyeLensP*)", "``float[]``", "Distortion coefficients to calculate tangential distortion. Special parameters for rad tan thin prism.", "None"
    "Camera Fisheye Lens S (*outputs:cameraFisheyeLensS*)", "``float[]``", "Distortion coefficients to calculate thin prism distortion. Special parameters for rad tan thin prism.", "None"
    "Camera Fisheye Max FOV (*outputs:cameraFisheyeMaxFOV*)", "``float``", "Camera fisheye maximum field of view", "None"
    "Camera Fisheye Nominal Height (*outputs:cameraFisheyeNominalHeight*)", "``int``", "Camera fisheye nominal height", "None"
    "Camera Fisheye Nominal Width (*outputs:cameraFisheyeNominalWidth*)", "``int``", "Camera fisheye nominal width", "None"
    "Camera Fisheye Optical Centre (*outputs:cameraFisheyeOpticalCentre*)", "``float[2]``", "Camera fisheye optical centre", "None"
    "Camera Fisheye Polynomial (*outputs:cameraFisheyePolynomial*)", "``float[]``", "Camera fisheye polynomial", "None"
    "Camera Focal Length (*outputs:cameraFocalLength*)", "``float``", "Camera focal length", "None"
    "Camera Focus Distance (*outputs:cameraFocusDistance*)", "``float``", "Camera focus distance", "None"
    "Camera Model (*outputs:cameraModel*)", "``token``", "Camera model (pinhole or fisheye models)", "None"
    "Camera Near Far (*outputs:cameraNearFar*)", "``float[2]``", "Camera near/far clipping range", "None"
    "Camera Open CV Fx (*outputs:cameraOpenCVFx*)", "``float``", "Camera OpenCV fx", "None"
    "Camera Open CV Fy (*outputs:cameraOpenCVFy*)", "``float``", "Camera OpenCV fy", "None"
    "Camera Projection (*outputs:cameraProjection*)", "``matrixd[4]``", "Camera projection matrix", "None"
    "Camera View Transform (*outputs:cameraViewTransform*)", "``matrixd[4]``", "Camera view matrix", "None"
    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Meters Per Scene Unit (*outputs:metersPerSceneUnit*)", "``float``", "Scene units to meters scale", "None"
    "Render Product Resolution (*outputs:renderProductResolution*)", "``int[2]``", "RenderProduct resolution", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.CameraParams"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnCameraParamsDatabase"
    "Python Module", "omni.replicator.core"

