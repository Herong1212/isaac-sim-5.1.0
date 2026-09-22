.. _omni_graph_nodes_Normalize_1:

.. _omni_graph_nodes_Normalize:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Normalize
    :keywords: lang-en omnigraph node math:operator threadsafe nodes normalize


Normalize
=========

.. <description>

Normalize the input vector (or array of input vectors). If the input vector has a magnitude of zero, the null vector is returned. The inputs will be copied into the output attribute before the normalization is performed on said output (i.e. the input vector(s) are not mutated in-place).

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Vector (*inputs:vector*)", "``['double[2]', 'double[2][]', 'double[3]', 'double[3][]', 'double[4]', 'double[4][]', 'float[2]', 'float[2][]', 'float[3]', 'float[3][]', 'float[4]', 'float[4][]', 'half[2]', 'half[2][]', 'half[3]', 'half[3][]', 'half[4]', 'half[4][]']``", "Input vector (or an array of input vectors) to normalize.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Result (*outputs:result*)", "``['double[2]', 'double[2][]', 'double[3]', 'double[3][]', 'double[4]', 'double[4][]', 'float[2]', 'float[2][]', 'float[3]', 'float[3][]', 'float[4]', 'float[4][]', 'half[2]', 'half[2][]', 'half[3]', 'half[3][]', 'half[4]', 'half[4][]']``", "Copy of the input vector (or array of vectors) after applying the corresponding normalization operations.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.Normalize"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Normalize"
    "Categories", "math:operator"
    "Generated Class Name", "OgnNormalizeDatabase"
    "Python Module", "omni.graph.nodes_core"

