.. _omni_graph_visualization_nodes_DrawLabel_1:

.. _omni_graph_visualization_nodes_DrawLabel:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Draw Label
    :keywords: lang-en omnigraph node debug nodes draw-label


Draw Label
==========

.. <description>

Draw text at a prescribed position in the viewport

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.visualization.nodes<ext_omni_graph_visualization_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Color (*inputs:color*)", "``colorf[4]``", "Text color", "[1.0, 1.0, 1.0, 1.0]"
    "In (*inputs:execIn*)", "``execution``", "Execution input", "None"
    "Offset (*inputs:offset*)", "``double[3]``", "Offset to be applied to label, in addition to transform input", "[0.0, 0.0, 0.0]"
    "Size (*inputs:size*)", "``float``", "Text size", "12.0"
    "Text (*inputs:text*)", "``string``", "Label text", ""
    "Transform (*inputs:transform*)", "``matrixd[4]``", "Transform used to position the label", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


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

    "Unique ID", "omni.graph.visualization.nodes.DrawLabel"
    "Version", "1"
    "Extension", "omni.graph.visualization.nodes"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Draw Label"
    "Categories", "debug"
    "Generated Class Name", "OgnDrawLabelDatabase"
    "Python Module", "omni.graph.visualization.nodes"

