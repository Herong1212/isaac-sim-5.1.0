.. _isaacsim_util_debug_draw_DebugDrawRayCast_1:

.. _isaacsim_util_debug_draw_DebugDrawRayCast:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Debug Draw RayCast
    :keywords: lang-en omnigraph node isaacDebugDraw debug_draw debug-draw-ray-cast


Isaac Debug Draw RayCast
========================

.. <description>

Take arrays of ray start and end points as input and display it in the scene.

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.util.debug_draw<ext_isaacsim_util_debug_draw>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Beam End Points (*inputs:beamEndPoints*)", "``pointf[3][]``", "Array containing end points of each ray", "[]"
    "Beam Origins (*inputs:beamOrigins*)", "``pointf[3][]``", "Array containing origins of each ray", "[]"
    "Beam Width (*inputs:beamWidth*)", "``float``", "Width of rays", "0.02"
    "Color (*inputs:color*)", "``colorf[4]``", "Color of rays", "[0.75, 0.75, 1, 1]"
    "Do Transform (*inputs:doTransform*)", "``bool``", "Translate and Rotate rays by transform", "True"
    "Exec (*inputs:exec*)", "``execution``", "The input execution port", "None"
    "Num Rays (*inputs:numRays*)", "``int``", "The number of rays to draw", "0"
    "Transform (*inputs:transform*)", "``matrixd[4]``", "The matrix to transform the rays by", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.util.debug_draw.DebugDrawRayCast"
    "Version", "1"
    "Extension", "isaacsim.util.debug_draw"
    "Icon", "ogn/icons/isaacsim.util.debug_draw.DebugDrawRayCast.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Debug Draw RayCast"
    "Categories", "isaacDebugDraw"
    "Generated Class Name", "OgnDebugDrawRayCastDatabase"
    "Python Module", "isaacsim.util.debug_draw"

