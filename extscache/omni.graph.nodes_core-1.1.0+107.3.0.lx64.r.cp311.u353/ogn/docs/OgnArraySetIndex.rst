.. _omni_graph_nodes_ArraySetIndex_1:

.. _omni_graph_nodes_ArraySetIndex:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Array Index
    :keywords: lang-en omnigraph node math:array threadsafe nodes array-set-index


Set Array Index
===============

.. <description>

Creates a copy of an input array where an index-specified element has been given a new value. Positive indices index from the front of the array, while negative indices index from the back of the array. "Index" values in the domain [-arrayLength, arrayLength) will always be valid for this node type. If "Resize to Fit" is true and "Index" >= arrayLength, then the output array will be resized to length 1 + "Index" and fill the new spaces with zeroes before applying the new element value.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Array (*inputs:array*)", "``['bool[]', 'colord[3][]', 'colord[4][]', 'colorf[3][]', 'colorf[4][]', 'colorh[3][]', 'colorh[4][]', 'double[2][]', 'double[3][]', 'double[4][]', 'double[]', 'float[2][]', 'float[3][]', 'float[4][]', 'float[]', 'frame[4][]', 'half[2][]', 'half[3][]', 'half[4][]', 'half[]', 'int64[]', 'int[2][]', 'int[3][]', 'int[4][]', 'int[]', 'matrixd[2][]', 'matrixd[3][]', 'matrixd[4][]', 'normald[3][]', 'normalf[3][]', 'normalh[3][]', 'pointd[3][]', 'pointf[3][]', 'pointh[3][]', 'quatd[4][]', 'quatf[4][]', 'quath[4][]', 'string', 'texcoordd[2][]', 'texcoordd[3][]', 'texcoordf[2][]', 'texcoordf[3][]', 'texcoordh[2][]', 'texcoordh[3][]', 'timecode[]', 'token[]', 'transform[4][]', 'uchar[]', 'uint64[]', 'uint[]', 'vectord[3][]', 'vectorf[3][]', 'vectorh[3][]']``", "The array that serves as the starting point for the modified output array.", "None"
    "Index (*inputs:index*)", "``int``", "The index of the element that should be modified in the output array.  Indices in the domain [0, arrayLength) correspond to the usual element locations in the array, e.g. an ""Index"" of 2 equates to the third element in the array.  Indices in the domain [-arrayLength, 0) correspond to array indexing starting from the back of the list, e.g. for an array of size 5, an ""Index"" of -5 equates to the last element in the array (i.e. the element at position 4), an ""Index"" of -4 equates to the second-to-last element in the array (i.e. the element at position 3), etc.  Attempting to execute this node with ""Index"" values outside of the [-arrayLength, arrayLength) domain will result in a runtime error, unless ""Index"" >= arrayLength and ""Resize to Fit"" is set to true (see the ""Resize to Fit"" attribute description for more information).", "0"
    "Resize To Fit (*inputs:resizeToFit*)", "``bool``", "When true and the given positive index ""Index"" is larger than the size of the the input array, resize the output array to length 1 + ""Index"", and fill the new spaces with zero values.", "False"
    "Value (*inputs:value*)", "``['bool', 'colord[3]', 'colord[4]', 'colorf[3]', 'colorf[4]', 'colorh[3]', 'colorh[4]', 'double', 'double[2]', 'double[3]', 'double[4]', 'float', 'float[2]', 'float[3]', 'float[4]', 'frame[4]', 'half', 'half[2]', 'half[3]', 'half[4]', 'int', 'int64', 'int[2]', 'int[3]', 'int[4]', 'matrixd[2]', 'matrixd[3]', 'matrixd[4]', 'normald[3]', 'normalf[3]', 'normalh[3]', 'pointd[3]', 'pointf[3]', 'pointh[3]', 'quatd[4]', 'quatf[4]', 'quath[4]', 'texcoordd[2]', 'texcoordd[3]', 'texcoordf[2]', 'texcoordf[3]', 'texcoordh[2]', 'texcoordh[3]', 'timecode', 'token', 'transform[4]', 'uchar', 'uint', 'uint64', 'vectord[3]', 'vectorf[3]', 'vectorh[3]']``", "The value to set at the given ""Index"" in the output array.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Array (*outputs:array*)", "``['bool[]', 'colord[3][]', 'colord[4][]', 'colorf[3][]', 'colorf[4][]', 'colorh[3][]', 'colorh[4][]', 'double[2][]', 'double[3][]', 'double[4][]', 'double[]', 'float[2][]', 'float[3][]', 'float[4][]', 'float[]', 'frame[4][]', 'half[2][]', 'half[3][]', 'half[4][]', 'half[]', 'int64[]', 'int[2][]', 'int[3][]', 'int[4][]', 'int[]', 'matrixd[2][]', 'matrixd[3][]', 'matrixd[4][]', 'normald[3][]', 'normalf[3][]', 'normalh[3][]', 'pointd[3][]', 'pointf[3][]', 'pointh[3][]', 'quatd[4][]', 'quatf[4][]', 'quath[4][]', 'string', 'texcoordd[2][]', 'texcoordd[3][]', 'texcoordf[2][]', 'texcoordf[3][]', 'texcoordh[2][]', 'texcoordh[3][]', 'timecode[]', 'token[]', 'transform[4][]', 'uchar[]', 'uint64[]', 'uint[]', 'vectord[3][]', 'vectorf[3][]', 'vectorh[3][]']``", "A copy of the input array whose index-specified value has been set to ""Value"".", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ArraySetIndex"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set Array Index"
    "Categories", "math:array"
    "Generated Class Name", "OgnArraySetIndexDatabase"
    "Python Module", "omni.graph.nodes_core"

