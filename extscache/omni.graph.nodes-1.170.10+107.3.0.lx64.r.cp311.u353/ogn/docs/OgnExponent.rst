.. _omni_graph_nodes_Exponent_1:

.. _omni_graph_nodes_Exponent:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Exponent
    :keywords: lang-en omnigraph node math:operator threadsafe nodes exponent


Exponent
========

.. <description>

Computes the base input raised to the power of the exponent. The result is the same type as the base input for floating point types. The result is double for integral values to allow for negative exponents. If the input is a vector or matrix, then the node calculates the exponent for each element and computes a vector or matrix of the same size.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Base (*inputs:base*)", "``['colord[3]', 'colord[3][]', 'colord[4]', 'colord[4][]', 'colorf[3]', 'colorf[3][]', 'colorf[4]', 'colorf[4][]', 'colorh[3]', 'colorh[3][]', 'colorh[4]', 'colorh[4][]', 'double', 'double[2]', 'double[2][]', 'double[3]', 'double[3][]', 'double[4]', 'double[4][]', 'double[]', 'float', 'float[2]', 'float[2][]', 'float[3]', 'float[3][]', 'float[4]', 'float[4][]', 'float[]', 'frame[4]', 'frame[4][]', 'half', 'half[2]', 'half[2][]', 'half[3]', 'half[3][]', 'half[4]', 'half[4][]', 'half[]', 'int', 'int64', 'int64[]', 'int[2]', 'int[2][]', 'int[3]', 'int[3][]', 'int[4]', 'int[4][]', 'int[]', 'matrixd[2]', 'matrixd[2][]', 'matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]', 'normald[3]', 'normald[3][]', 'normalf[3]', 'normalf[3][]', 'normalh[3]', 'normalh[3][]', 'pointd[3]', 'pointd[3][]', 'pointf[3]', 'pointf[3][]', 'pointh[3]', 'pointh[3][]', 'quatd[4]', 'quatd[4][]', 'quatf[4]', 'quatf[4][]', 'quath[4]', 'quath[4][]', 'texcoordd[2]', 'texcoordd[2][]', 'texcoordd[3]', 'texcoordd[3][]', 'texcoordf[2]', 'texcoordf[2][]', 'texcoordf[3]', 'texcoordf[3][]', 'texcoordh[2]', 'texcoordh[2][]', 'texcoordh[3]', 'texcoordh[3][]', 'timecode', 'timecode[]', 'transform[4]', 'transform[4][]', 'uchar', 'uchar[]', 'uint', 'uint64', 'uint64[]', 'uint[]', 'vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "Base value that will be raised to the power of exponent.", "None"
    "Exponent (*inputs:exponent*)", "``int``", "Power to raise the base value ""Base"" to. If ""Base"" consists of an array, vector, or matrix, then the exponent will be applied to each member of the aforementioned data structures.", "2"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Result (*outputs:result*)", "``['colord[3]', 'colord[3][]', 'colord[4]', 'colord[4][]', 'colorf[3]', 'colorf[3][]', 'colorf[4]', 'colorf[4][]', 'colorh[3]', 'colorh[3][]', 'colorh[4]', 'colorh[4][]', 'double', 'double[2]', 'double[2][]', 'double[3]', 'double[3][]', 'double[4]', 'double[4][]', 'double[]', 'float', 'float[2]', 'float[2][]', 'float[3]', 'float[3][]', 'float[4]', 'float[4][]', 'float[]', 'frame[4]', 'frame[4][]', 'half', 'half[2]', 'half[2][]', 'half[3]', 'half[3][]', 'half[4]', 'half[4][]', 'half[]', 'int', 'int64', 'int64[]', 'int[2]', 'int[2][]', 'int[3]', 'int[3][]', 'int[4]', 'int[4][]', 'int[]', 'matrixd[2]', 'matrixd[2][]', 'matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]', 'normald[3]', 'normald[3][]', 'normalf[3]', 'normalf[3][]', 'normalh[3]', 'normalh[3][]', 'pointd[3]', 'pointd[3][]', 'pointf[3]', 'pointf[3][]', 'pointh[3]', 'pointh[3][]', 'quatd[4]', 'quatd[4][]', 'quatf[4]', 'quatf[4][]', 'quath[4]', 'quath[4][]', 'texcoordd[2]', 'texcoordd[2][]', 'texcoordd[3]', 'texcoordd[3][]', 'texcoordf[2]', 'texcoordf[2][]', 'texcoordf[3]', 'texcoordf[3][]', 'texcoordh[2]', 'texcoordh[2][]', 'texcoordh[3]', 'texcoordh[3][]', 'timecode', 'timecode[]', 'transform[4]', 'transform[4][]', 'uchar', 'uchar[]', 'uint', 'uint64', 'uint64[]', 'uint[]', 'vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "Result of ""Base"" raised to the value in ""Exponent"".", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.Exponent"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Exponent"
    "Categories", "math:operator"
    "Generated Class Name", "OgnExponentDatabase"
    "Python Module", "omni.graph.nodes"

