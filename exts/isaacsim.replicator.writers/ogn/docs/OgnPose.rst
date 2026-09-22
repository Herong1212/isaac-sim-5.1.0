.. _isaacsim_replicator_writers_Pose_1:

.. _isaacsim_replicator_writers_Pose:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Pose
    :keywords: lang-en omnigraph node compute-on-request writers pose


Pose
====

.. <description>

This node outputs the poses of assets with semantic labels

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.replicator.writers<ext_isaacsim_replicator_writers>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*inputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "0"
    "Camera Projection (*inputs:cameraProjection*)", "``matrixd[4]``", "Camera projection matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Camera Rotation (*inputs:cameraRotation*)", "``float[]``", "Rotation of the desired camera frame from the default camera frame, as XYZ Euler angles", "[]"
    "Camera View Transform (*inputs:cameraViewTransform*)", "``matrixd[4]``", "Camera view matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Data (*inputs:data*)", "``uchar[]``", "Buffer array data", "[]"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Get Centers (*inputs:getCenters*)", "``bool``", "Set to True if producing center coordinates of every semantic entity projected in the image space", "False"
    "Image Height (*inputs:imageHeight*)", "``uint``", "Height of the viewport", "0"
    "Image Width (*inputs:imageWidth*)", "``uint``", "Width of the viewport", "0"
    "Include Occluded Prims (*inputs:includeOccludedPrims*)", "``bool``", "Set to True if poses (and if enabled, centers) of fully occluded/out-of-frame semantic entities should be output", "False"
    "Sd IM Instance Semantic Map (*inputs:sdIMInstanceSemanticMap*)", "``uchar[]``", "Raw array of uint16_t of size sdIMNumInstances*sdIMMaxSemanticHierarchyDepth containing the mapping from the instances index to their inherited semantic entities", "[]"
    "Sd IM Max Semantic Hierarchy Depth (*inputs:sdIMMaxSemanticHierarchyDepth*)", "``uint``", "Maximal number of semantic entities inherited by an instance", "0"
    "Sd IM Min Semantic Index (*inputs:sdIMMinSemanticIndex*)", "``uint``", "Semantic id of the first instance in the instance arrays", "0"
    "Sd IM Num Semantic Tokens (*inputs:sdIMNumSemanticTokens*)", "``uint``", "Number of semantics token including the semantic entity path, the semantic entity types and if the number of semantic types is greater than one", "0"
    "Sd IM Num Semantics (*inputs:sdIMNumSemantics*)", "``uint``", "Number of semantic entities in the semantic arrays", "0"
    "Sd IM Semantic Token Map (*inputs:sdIMSemanticTokenMap*)", "``token[]``", "Semantic array of token of size numSemantics * numSemanticTypes containing the mapping from the semantic entities to the semantic entity path and semantic types", "[]"
    "Sd IM Semantic World Transform (*inputs:sdIMSemanticWorldTransform*)", "``float[]``", "Semantic array of 4x4 float matrices containing the transform from local to world space for every semantic entity", "[]"
    "Semantic Types (*inputs:semanticTypes*)", "``token[]``", "Semantic Types to consider", "['class']"


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
    "Prim Paths (*outputs:primPaths*)", "``token[]``", "Prim paths corresponding to each pose.", "None"
    "Width (*outputs:width*)", "``uint``", "Shape of the data", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.replicator.writers.Pose"
    "Version", "1"
    "Extension", "isaacsim.replicator.writers"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Pose"
    "Generated Class Name", "OgnPoseDatabase"
    "Python Module", "isaacsim.replicator.writers"

