.. _omni_graph_nodes_Noise_1:

.. _omni_graph_nodes_Noise:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Noise
    :keywords: lang-en omnigraph node math:operator threadsafe nodes noise


Noise
=====

.. <description>

Sample values from a Perlin noise field.
The noise field for any given seed is static: the same input position will always give the same result. This is useful in many areas, such as texturing and animation, where repeatability is essential. If you want a result that varies then you will need to vary either the position or the seed. For example, connecting the "Frame" output of an OnTick node to position will provide a noise result which varies from frame to frame. Perlin noise is locally smooth, meaning that small changes in the sample position will produce small changes in the resulting noise. Varying the seed value will produce a more chaotic result.
Another characteristic of Perlin noise is that it is zero at the corners of each cell in the field. In practical terms this means that integral positions, such as 5.0 in a one-dimensional field or (3.0, -1.0) in a two-dimensional field, will return a result of 0.0. Thus, if the source of your sample positions provides only integral values then all of your results will be zero. To avoid this try offsetting your position values by a fractional amount, such as 0.5.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Position (*inputs:position*)", "``['float', 'float[2]', 'float[2][]', 'float[3]', 'float[3][]', 'float[4]', 'float[4][]', 'float[]']``", "Position(s) within the noise field to be sampled. For a given seed, the same position will always return the same noise value.", "None"
    "Seed (*inputs:seed*)", "``uint``", "Positive seeding value for generating the Perlin noise field.", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Result (*outputs:result*)", "``['float', 'float[]']``", "Value at the selected position(s) in the noise field.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.Noise"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Noise"
    "Categories", "math:operator"
    "Generated Class Name", "OgnNoiseDatabase"
    "Python Module", "omni.graph.nodes"

