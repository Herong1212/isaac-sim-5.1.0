.. _omni_graph_visualization_nodes_DrawScreenSpaceText_1:

.. _omni_graph_visualization_nodes_DrawScreenSpaceText:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Draw Screen Space Text (Beta)
    :keywords: lang-en omnigraph node debug nodes draw-screen-space-text


Draw Screen Space Text (Beta)
=============================

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

    "Background Color (*inputs:backgroundColor*)", "``colorf[4]``", "Background color", "[0.165, 0.157, 0.145, 0.8]"
    "Text Max Width (*inputs:boxWidth*)", "``int``", "Text box maximum width before wrapping (0 for no wrapping)", "0"
    "In (*inputs:execIn*)", "``execution``", "Execution input", "None"
    "Screen Position (%) (*inputs:position*)", "``double[2]``", "Text position on the viewport (as a percentage of the viewport size)", "[50.0, 50.0]"
    "Size (*inputs:size*)", "``float``", "Text size", "14.0"
    "Text (*inputs:text*)", "``string``", "Label text", ""
    "Text Color (*inputs:textColor*)", "``colorf[4]``", "Text color", "[0.95, 0.95, 0.95, 1.0]"


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

    "Unique ID", "omni.graph.visualization.nodes.DrawScreenSpaceText"
    "Version", "1"
    "Extension", "omni.graph.visualization.nodes"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Draw Screen Space Text (Beta)"
    "Categories", "debug"
    "Generated Class Name", "OgnDrawScreenSpaceTextDatabase"
    "Python Module", "omni.graph.visualization.nodes"

