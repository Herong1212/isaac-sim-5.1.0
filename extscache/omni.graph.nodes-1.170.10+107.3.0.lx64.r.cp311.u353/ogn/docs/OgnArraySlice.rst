.. _omni_graph_nodes_ArraySlice_1:

.. _omni_graph_nodes_ArraySlice:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Array Slice
    :keywords: lang-en omnigraph node math:array threadsafe nodes array-slice


Get Array Slice
===============

.. <description>

Returns a section of the input "Array" between the index values of "Start Index" and "End Index" (or the end of "Array" if the input "Use Length" is true). The index values will be truncated to be within the range of the input array. If "Start Index" is greater than or equal to "End Index" then an empty array will be outputted. Note that the element at "End Index" (assuming said index is not greater than or equal to the input "Array" length) will not be included in the final result.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Array (*inputs:array*)", "``['bool[]', 'colord[3][]', 'colord[4][]', 'colorf[3][]', 'colorf[4][]', 'colorh[3][]', 'colorh[4][]', 'double[2][]', 'double[3][]', 'double[4][]', 'double[]', 'float[2][]', 'float[3][]', 'float[4][]', 'float[]', 'frame[4][]', 'half[2][]', 'half[3][]', 'half[4][]', 'half[]', 'int64[]', 'int[2][]', 'int[3][]', 'int[4][]', 'int[]', 'matrixd[2][]', 'matrixd[3][]', 'matrixd[4][]', 'normald[3][]', 'normalf[3][]', 'normalh[3][]', 'pointd[3][]', 'pointf[3][]', 'pointh[3][]', 'quatd[4][]', 'quatf[4][]', 'quath[4][]', 'string', 'texcoordd[2][]', 'texcoordd[3][]', 'texcoordf[2][]', 'texcoordf[3][]', 'texcoordh[2][]', 'texcoordh[3][]', 'timecode[]', 'token[]', 'transform[4][]', 'uchar[]', 'uint64[]', 'uint[]', 'vectord[3][]', 'vectorf[3][]', 'vectorh[3][]']``", "The original array, before the slicing operation is applied.", "None"
    "End Index (*inputs:end*)", "``int``", "The end index into the input array. If this value is less than or equal to ""Start Index"" an empty array will be returned. A negative value indexes from the end of the array. Values less than -arrayLength will be treated as 0, while values greater than arrayLength will be treated as arrayLength.", "0"
    "Start Index (*inputs:start*)", "``int``", "The start index into the input array. If this value is greater than ""End Index"" an empty array will be returned. A negative value indexes from the end of the array. Values less than -arrayLength will be treated as 0, while values greater than arrayLength will be treated as arrayLength.", "0"
    "Use Length (*inputs:useLength*)", "``bool``", "If true, use the length of the array as the value for the ""End Index"" rather than the actual value stored on the attribute. If false, simply use the actual value stored on the ""End Index"" attribute.", "True"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Array (*outputs:array*)", "``['bool[]', 'colord[3][]', 'colord[4][]', 'colorf[3][]', 'colorf[4][]', 'colorh[3][]', 'colorh[4][]', 'double[2][]', 'double[3][]', 'double[4][]', 'double[]', 'float[2][]', 'float[3][]', 'float[4][]', 'float[]', 'frame[4][]', 'half[2][]', 'half[3][]', 'half[4][]', 'half[]', 'int64[]', 'int[2][]', 'int[3][]', 'int[4][]', 'int[]', 'matrixd[2][]', 'matrixd[3][]', 'matrixd[4][]', 'normald[3][]', 'normalf[3][]', 'normalh[3][]', 'pointd[3][]', 'pointf[3][]', 'pointh[3][]', 'quatd[4][]', 'quatf[4][]', 'quath[4][]', 'string', 'texcoordd[2][]', 'texcoordd[3][]', 'texcoordf[2][]', 'texcoordf[3][]', 'texcoordh[2][]', 'texcoordh[3][]', 'timecode[]', 'token[]', 'transform[4][]', 'uchar[]', 'uint64[]', 'uint[]', 'vectord[3][]', 'vectorf[3][]', 'vectorh[3][]']``", "A new array containing a subsection of the specified input ""Array"".", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ArraySlice"
    "Version", "1"
    "Extension", "omni.graph.nodes"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Array Slice"
    "Categories", "math:array"
    "Generated Class Name", "OgnArraySliceDatabase"
    "Python Module", "omni.graph.nodes"

