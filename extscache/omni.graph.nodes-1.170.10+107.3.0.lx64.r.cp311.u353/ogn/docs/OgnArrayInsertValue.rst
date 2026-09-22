.. _omni_graph_nodes_ArrayInsertValue_1:

.. _omni_graph_nodes_ArrayInsertValue:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Insert Array Value
    :keywords: lang-en omnigraph node math:array threadsafe nodes array-insert-value


Insert Array Value
==================

.. <description>

Creates a copy of an input array with an element that has been inserted at the given index. The indexing is zero-based and clamped in such a way as to ensure that values of "Index" <= 0 result in the element getting inserted at the beginning of the array, while values of "Index" >= arrayLength result in the element getting inserted at the end of the array.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Array (*inputs:array*)", "``['bool[]', 'colord[3][]', 'colord[4][]', 'colorf[3][]', 'colorf[4][]', 'colorh[3][]', 'colorh[4][]', 'double[2][]', 'double[3][]', 'double[4][]', 'double[]', 'float[2][]', 'float[3][]', 'float[4][]', 'float[]', 'frame[4][]', 'half[2][]', 'half[3][]', 'half[4][]', 'half[]', 'int64[]', 'int[2][]', 'int[3][]', 'int[4][]', 'int[]', 'matrixd[2][]', 'matrixd[3][]', 'matrixd[4][]', 'normald[3][]', 'normalf[3][]', 'normalh[3][]', 'pointd[3][]', 'pointf[3][]', 'pointh[3][]', 'quatd[4][]', 'quatf[4][]', 'quath[4][]', 'string', 'texcoordd[2][]', 'texcoordd[3][]', 'texcoordf[2][]', 'texcoordf[3][]', 'texcoordh[2][]', 'texcoordh[3][]', 'timecode[]', 'token[]', 'transform[4][]', 'uchar[]', 'uint64[]', 'uint[]', 'vectord[3][]', 'vectorf[3][]', 'vectorh[3][]']``", "The array to be copied into the output array prior to element insertion.", "None"
    "Index (*inputs:index*)", "``int``", "The index at which a copy of ""Value"" should be inserted into the output array (which in turn is a copy of the input array). The indexing is zero-based and clamped so that values less than or equal to zero result in ""Value"" getting inserted at the front of the array, while values greater than or equal to the length of the array result in ""Value"" getting inserted at the back of the array.", "0"
    "Value (*inputs:value*)", "``['bool', 'colord[3]', 'colord[4]', 'colorf[3]', 'colorf[4]', 'colorh[3]', 'colorh[4]', 'double', 'double[2]', 'double[3]', 'double[4]', 'float', 'float[2]', 'float[3]', 'float[4]', 'frame[4]', 'half', 'half[2]', 'half[3]', 'half[4]', 'int', 'int64', 'int[2]', 'int[3]', 'int[4]', 'matrixd[2]', 'matrixd[3]', 'matrixd[4]', 'normald[3]', 'normalf[3]', 'normalh[3]', 'pointd[3]', 'pointf[3]', 'pointh[3]', 'quatd[4]', 'quatf[4]', 'quath[4]', 'texcoordd[2]', 'texcoordd[3]', 'texcoordf[2]', 'texcoordf[3]', 'texcoordh[2]', 'texcoordh[3]', 'timecode', 'token', 'transform[4]', 'uchar', 'uint', 'uint64', 'vectord[3]', 'vectorf[3]', 'vectorh[3]']``", "The value to be copied and inserted into the output array.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Array (*outputs:array*)", "``['bool[]', 'colord[3][]', 'colord[4][]', 'colorf[3][]', 'colorf[4][]', 'colorh[3][]', 'colorh[4][]', 'double[2][]', 'double[3][]', 'double[4][]', 'double[]', 'float[2][]', 'float[3][]', 'float[4][]', 'float[]', 'frame[4][]', 'half[2][]', 'half[3][]', 'half[4][]', 'half[]', 'int64[]', 'int[2][]', 'int[3][]', 'int[4][]', 'int[]', 'matrixd[2][]', 'matrixd[3][]', 'matrixd[4][]', 'normald[3][]', 'normalf[3][]', 'normalh[3][]', 'pointd[3][]', 'pointf[3][]', 'pointh[3][]', 'quatd[4][]', 'quatf[4][]', 'quath[4][]', 'string', 'texcoordd[2][]', 'texcoordd[3][]', 'texcoordf[2][]', 'texcoordf[3][]', 'texcoordh[2][]', 'texcoordh[3][]', 'timecode[]', 'token[]', 'transform[4][]', 'uchar[]', 'uint64[]', 'uint[]', 'vectord[3][]', 'vectorf[3][]', 'vectorh[3][]']``", "A copy of the input array with a new ""Value"" inserted at the specified ""Index"".", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ArrayInsertValue"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Insert Array Value"
    "Categories", "math:array"
    "Generated Class Name", "OgnArrayInsertValueDatabase"
    "Python Module", "omni.graph.nodes"

