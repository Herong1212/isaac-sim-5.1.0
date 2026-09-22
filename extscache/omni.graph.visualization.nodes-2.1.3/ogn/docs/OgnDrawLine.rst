.. _omni_graph_visualization_nodes_DrawLine_1:

.. _omni_graph_visualization_nodes_DrawLine:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Draw Line
    :keywords: lang-en omnigraph node debug nodes draw-line


Draw Line
=========

.. <description>

Draw a line between two points

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.visualization.nodes<ext_omni_graph_visualization_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Color (*inputs:color*)", "``colorf[4]``", "Line color", "[1.0, 1.0, 1.0, 1.0]"
    "End (*inputs:end*)", "``float[3]``", "Line end point", "[0.0, 0.0, 1.0]"
    "In (*inputs:execIn*)", "``execution``", "Execution input", "None"
    "Start (*inputs:start*)", "``float[3]``", "Line start point", "[0.0, 0.0, 0.0]"
    "Thickness (*inputs:thickness*)", "``float``", "Line thickness", "1.0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Out (*outputs:execOut*)", "``execution``", "Execution output", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.visualization.nodes.DrawLine"
    "Version", "1"
    "Extension", "omni.graph.visualization.nodes"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Draw Line"
    "Categories", "debug"
    "Generated Class Name", "OgnDrawLineDatabase"
    "Python Module", "omni.graph.visualization.nodes"

