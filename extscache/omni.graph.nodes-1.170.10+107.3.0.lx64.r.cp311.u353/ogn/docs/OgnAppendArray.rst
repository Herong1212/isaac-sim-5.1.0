.. _omni_graph_nodes_AppendArray_1:

.. _omni_graph_nodes_AppendArray:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Append Array
    :keywords: lang-en omnigraph node math:array threadsafe nodes append-array


Append Array
============

.. <description>

Combines the input arrays into a single new array in order of the inputs and the elements within each input array.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Input0 (*inputs:input0*)", "``['bool[]', 'colord[3][]', 'colord[4][]', 'colorf[3][]', 'colorf[4][]', 'colorh[3][]', 'colorh[4][]', 'double[2][]', 'double[3][]', 'double[4][]', 'double[]', 'float[2][]', 'float[3][]', 'float[4][]', 'float[]', 'frame[4][]', 'half[2][]', 'half[3][]', 'half[4][]', 'half[]', 'int64[]', 'int[2][]', 'int[3][]', 'int[4][]', 'int[]', 'matrixd[2][]', 'matrixd[3][]', 'matrixd[4][]', 'normald[3][]', 'normalf[3][]', 'normalh[3][]', 'pointd[3][]', 'pointf[3][]', 'pointh[3][]', 'quatd[4][]', 'quatf[4][]', 'quath[4][]', 'string', 'texcoordd[2][]', 'texcoordd[3][]', 'texcoordf[2][]', 'texcoordf[3][]', 'texcoordh[2][]', 'texcoordh[3][]', 'timecode[]', 'token[]', 'transform[4][]', 'uchar[]', 'uint64[]', 'uint[]', 'vectord[3][]', 'vectorf[3][]', 'vectorh[3][]']``", "The first of the two arrays to combine. The elements in this array will come before all of the second input array's elements in the final output array.", "None"
    "Input1 (*inputs:input1*)", "``['bool[]', 'colord[3][]', 'colord[4][]', 'colorf[3][]', 'colorf[4][]', 'colorh[3][]', 'colorh[4][]', 'double[2][]', 'double[3][]', 'double[4][]', 'double[]', 'float[2][]', 'float[3][]', 'float[4][]', 'float[]', 'frame[4][]', 'half[2][]', 'half[3][]', 'half[4][]', 'half[]', 'int64[]', 'int[2][]', 'int[3][]', 'int[4][]', 'int[]', 'matrixd[2][]', 'matrixd[3][]', 'matrixd[4][]', 'normald[3][]', 'normalf[3][]', 'normalh[3][]', 'pointd[3][]', 'pointf[3][]', 'pointh[3][]', 'quatd[4][]', 'quatf[4][]', 'quath[4][]', 'string', 'texcoordd[2][]', 'texcoordd[3][]', 'texcoordf[2][]', 'texcoordf[3][]', 'texcoordh[2][]', 'texcoordh[3][]', 'timecode[]', 'token[]', 'transform[4][]', 'uchar[]', 'uint64[]', 'uint[]', 'vectord[3][]', 'vectorf[3][]', 'vectorh[3][]']``", "The second of the two arrays to combine. The elements in this array will come after all of the first input array's elements in the final output array.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Array (*outputs:array*)", "``['bool[]', 'colord[3][]', 'colord[4][]', 'colorf[3][]', 'colorf[4][]', 'colorh[3][]', 'colorh[4][]', 'double[2][]', 'double[3][]', 'double[4][]', 'double[]', 'float[2][]', 'float[3][]', 'float[4][]', 'float[]', 'frame[4][]', 'half[2][]', 'half[3][]', 'half[4][]', 'half[]', 'int64[]', 'int[2][]', 'int[3][]', 'int[4][]', 'int[]', 'matrixd[2][]', 'matrixd[3][]', 'matrixd[4][]', 'normald[3][]', 'normalf[3][]', 'normalh[3][]', 'pointd[3][]', 'pointf[3][]', 'pointh[3][]', 'quatd[4][]', 'quatf[4][]', 'quath[4][]', 'string', 'texcoordd[2][]', 'texcoordd[3][]', 'texcoordf[2][]', 'texcoordf[3][]', 'texcoordh[2][]', 'texcoordh[3][]', 'timecode[]', 'token[]', 'transform[4][]', 'uchar[]', 'uint64[]', 'uint[]', 'vectord[3][]', 'vectorf[3][]', 'vectorh[3][]']``", "A new array containing all of the elements in the ""Input0"" array followed by all of the elements in the ""Input1"" array.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.AppendArray"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Append Array"
    "Categories", "math:array"
    "Generated Class Name", "OgnAppendArrayDatabase"
    "Python Module", "omni.graph.nodes"

