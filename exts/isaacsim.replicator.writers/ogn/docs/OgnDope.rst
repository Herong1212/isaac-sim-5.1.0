.. _isaacsim_replicator_writers_Dope_1:

.. _isaacsim_replicator_writers_Dope:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Dope
    :keywords: lang-en omnigraph node compute-on-request writers dope


Dope
====

.. <description>

Gets poses of assets as required by ground truth file for DOPE training

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.replicator.writers<ext_isaacsim_replicator_writers>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bounding Box3d (*inputs:boundingBox3d*)", "``uchar[]``", "3d bounding box data.", "[]"
    "Camera Fisheye Max FOV (*inputs:cameraFisheyeMaxFOV*)", "``float``", "Camera fisheye maximum field of view", "0.0"
    "Camera Fisheye Nominal Height (*inputs:cameraFisheyeNominalHeight*)", "``int``", "Camera fisheye nominal height", "0"
    "Camera Fisheye Nominal Width (*inputs:cameraFisheyeNominalWidth*)", "``int``", "Camera fisheye nominal width", "0"
    "Camera Fisheye Optical Centre (*inputs:cameraFisheyeOpticalCentre*)", "``float[2]``", "Camera fisheye optical centre", "[0.0, 0.0]"
    "Camera Fisheye Polynomial (*inputs:cameraFisheyePolynomial*)", "``float[]``", "Camera fisheye polynomial", "[]"
    "Camera Model (*inputs:cameraModel*)", "``token``", "Camera model (pinhole or fisheye models)", ""
    "Camera Near Far (*inputs:cameraNearFar*)", "``float[2]``", "Camera near/far clipping range", "[0.0, 0.0]"
    "Camera Projection (*inputs:cameraProjection*)", "``matrixd[4]``", "Camera projection matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Camera Rotation (*inputs:cameraRotation*)", "``float[3]``", "Camera rotation in euler angles", "[0.0, 0.0, 0.0]"
    "Camera View Transform (*inputs:cameraViewTransform*)", "``matrixd[4]``", "Camera view matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Focal Length (*inputs:focalLength*)", "``float``", "Camera fisheye maximum field of view", "0.0"
    "Height (*inputs:height*)", "``uint``", "Height of the viewport", "0"
    "Horizontal Aperture (*inputs:horizontalAperture*)", "``float``", "Horizontal aperture of camera", "0.0"
    "Occlusion (*inputs:occlusion*)", "``uchar[]``", "Occlusion data", "[]"
    "Sd IM Instance Semantic Map (*inputs:sdIMInstanceSemanticMap*)", "``uchar[]``", "Raw array of uint16_t of size sdIMNumInstances*sdIMMaxSemanticHierarchyDepth containing the mapping from the instances index to their inherited semantic entities", "[]"
    "Sd IM Max Semantic Hierarchy Depth (*inputs:sdIMMaxSemanticHierarchyDepth*)", "``uint``", "Maximal number of semantic entities inherited by an instance", "0"
    "Sd IM Min Semantic Index (*inputs:sdIMMinSemanticIndex*)", "``uint``", "Semantic id of the first instance in the instance arrays", "0"
    "Sd IM Num Semantic Tokens (*inputs:sdIMNumSemanticTokens*)", "``uint``", "Number of semantics token including the semantic entity path, the semantic entity types and if the number of semantic types is greater than one", "0"
    "Sd IM Num Semantics (*inputs:sdIMNumSemantics*)", "``uint``", "Number of semantic entities in the semantic arrays", "0"
    "Sd IM Semantic Token Map (*inputs:sdIMSemanticTokenMap*)", "``token[]``", "Semantic array of token of size numSemantics * numSemanticTypes containing the mapping from the semantic entities to the semantic entity path and semantic types", "[]"
    "Semantic Types (*inputs:semanticTypes*)", "``token[]``", "Semantic Types to consider", "['class']"
    "Width (*inputs:width*)", "``uint``", "Width of the viewport", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*outputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Data (*outputs:data*)", "``uchar[]``", "Semantic array of 4x4 float matrices containing the transform from local to view space for every semantic entity. Additionally, an optional semantic array of float[2] vectors containing the center coordinates of every semantic entity projected in the image space", "None"
    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*outputs:height*)", "``uint``", "Shape of the data", "None"
    "Id To Labels (*outputs:idToLabels*)", "``string``", "Mapping from id to semantic labels.", "None"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.replicator.writers.Dope"
    "Version", "1"
    "Extension", "isaacsim.replicator.writers"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Dope"
    "Generated Class Name", "OgnDopeDatabase"
    "Python Module", "isaacsim.replicator.writers"

