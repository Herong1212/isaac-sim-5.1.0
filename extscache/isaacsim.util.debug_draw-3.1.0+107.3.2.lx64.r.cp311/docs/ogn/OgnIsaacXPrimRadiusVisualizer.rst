.. _isaacsim_util_debug_draw_IsaacXPrimRadiusVisualizer_1:

.. _isaacsim_util_debug_draw_IsaacXPrimRadiusVisualizer:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac xPrim Radius Visualizer Node
    :keywords: lang-en omnigraph node isaacDebugDraw debug_draw isaac-x-prim-radius-visualizer


Isaac xPrim Radius Visualizer Node
==================================

.. <description>

displays the Radius of the xPrim for visualization.

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.util.debug_draw<ext_isaacsim_util_debug_draw>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Draw X Axis (*inputs:drawXAxis*)", "``bool``", "True to draw the x axis circle", "True"
    "Draw Y Axis (*inputs:drawYAxis*)", "``bool``", "True to draw the y axis circle", "True"
    "Draw Z Axis (*inputs:drawZAxis*)", "``bool``", "True to draw the z axis circle", "True"
    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port", "None"
    "Radius (*inputs:radius*)", "``float``", "Radius of the sphere", "1"
    "Segments (*inputs:segments*)", "``int``", "Number of segments in the circle", "30"
    "Thickness (*inputs:thickness*)", "``float``", "Thickness of the radius lines", "1"
    "X Axis Color (*inputs:xAxisColor*)", "``colorf[4]``", "Color of the x axis sphere points", "[1, 0, 0, 1]"
    "xPrim (*inputs:xPrim*)", "``target``", "Usd prim to visualize", "None"
    "Y Axis Color (*inputs:yAxisColor*)", "``colorf[4]``", "Color of the y axis sphere points", "[0, 1, 0, 1]"
    "Z Axis Color (*inputs:zAxisColor*)", "``colorf[4]``", "Color of the z axis sphere points", "[0, 0, 1, 1]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.util.debug_draw.IsaacXPrimRadiusVisualizer"
    "Version", "1"
    "Extension", "isaacsim.util.debug_draw"
    "Icon", "ogn/icons/isaacsim.util.debug_draw.IsaacXPrimRadiusVisualizer.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac xPrim Radius Visualizer Node"
    "Categories", "isaacDebugDraw"
    "Generated Class Name", "OgnIsaacXPrimRadiusVisualizerDatabase"
    "Python Module", "isaacsim.util.debug_draw"

