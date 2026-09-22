.. _isaacsim_util_debug_draw_DebugDrawPointCloud_1:

.. _isaacsim_util_debug_draw_DebugDrawPointCloud:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Debug Draw Point Cloud
    :keywords: lang-en omnigraph node isaacDebugDraw debug_draw debug-draw-point-cloud


Isaac Debug Draw Point Cloud
============================

.. <description>

Take a point cloud as input and display it in the scene.

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.util.debug_draw<ext_isaacsim_util_debug_draw>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*inputs:bufferSize*)", "``uint64``", "Size (in bytes) of the buffer (0 if the input is a texture)", "0"
    "Color (*inputs:color*)", "``colorf[4]``", "Color of points", "[0.75, 0.75, 1, 1]"
    "Cuda Device Index (*inputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Cuda Stream (*inputs:cudaStream*)", "``uint64``", "Cuda Stream Input", "0"
    "Data Ptr (*inputs:dataPtr*)", "``uint64``", "Buffer of points containing point cloud data", "0"
    "Do Transform (*inputs:doTransform*)", "``bool``", "Translate and Rotate point cloud by transform", "True"
    "Exec (*inputs:exec*)", "``execution``", "The input execution port", "None"
    "Size (*inputs:size*)", "``float``", "Size of points", "0.02"
    "Test Mode (*inputs:testMode*)", "``bool``", "Act as Writer with no rendering", "False"
    "Transform (*inputs:transform*)", "``matrixd[4]``", "The matrix to transform the points by", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.util.debug_draw.DebugDrawPointCloud"
    "Version", "1"
    "Extension", "isaacsim.util.debug_draw"
    "Icon", "ogn/icons/isaacsim.util.debug_draw.DebugDrawPointCloud.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Debug Draw Point Cloud"
    "Categories", "isaacDebugDraw"
    "Generated Class Name", "OgnDebugDrawPointCloudDatabase"
    "Python Module", "isaacsim.util.debug_draw"

