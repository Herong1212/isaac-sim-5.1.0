.. _omni_graph_nodes_ConstructArray_1:

.. _omni_graph_nodes_ConstructArray:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Make Array
    :keywords: lang-en omnigraph node math:array threadsafe nodes construct-array


Make Array
==========

.. <description>

Makes an output array attribute from input values, in the order of the inputs. If 'Array Size' is less than the number of input elements, the first 'Array Size' elements will be used. If 'Array Size' is greater than the number of input elements, the last input element will be repeated to fill the remaining space.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Array Size (*inputs:arraySize*)", "``int``", "The size of the array to construct.", "1"
    "", "Metadata", "*literalOnly* = 1", ""
    "Array Type (*inputs:arrayType*)", "``token``", "The type of the array to construct. A value of 'auto' infers the type from the first connected and resolved input.", "auto"
    "", "Metadata", "*literalOnly* = 1", ""
    "", "Metadata", "*allowedTokens* = auto,bool[],double[],float[],half[],int[],int64[],token[],uchar[],uint[],uint64[],double[2][],double[3][],double[4][],matrixd[2][],matrixd[3][],matrixd[4][],float[2][],float[3][],float[4][],half[2][],half[3][],half[4][],int[2][],int[3][],int[4][],timecode[],frame[4][],colord[3][],colorf[3][],colorh[3][],colord[4][],colorf[4][],colorh[4][],normald[3][],normalf[3][],normalh[3][],pointd[3][],pointf[3][],pointh[3][],quatd[4][],quatf[4][],quath[4][],texcoordd[2][],texcoordf[2][],texcoordh[2][],texcoordd[3][],texcoordf[3][],texcoordh[3][],vectord[3][],vectorf[3][],vectorh[3][]", ""
    "Input0 (*inputs:input0*)", "``['bool', 'colord[3]', 'colord[4]', 'colorf[3]', 'colorf[4]', 'colorh[3]', 'colorh[4]', 'double', 'double[2]', 'double[3]', 'double[4]', 'float', 'float[2]', 'float[3]', 'float[4]', 'frame[4]', 'half', 'half[2]', 'half[3]', 'half[4]', 'int', 'int64', 'int[2]', 'int[3]', 'int[4]', 'matrixd[2]', 'matrixd[3]', 'matrixd[4]', 'normald[3]', 'normalf[3]', 'normalh[3]', 'pointd[3]', 'pointf[3]', 'pointh[3]', 'quatd[4]', 'quatf[4]', 'quath[4]', 'texcoordd[2]', 'texcoordd[3]', 'texcoordf[2]', 'texcoordf[3]', 'texcoordh[2]', 'texcoordh[3]', 'timecode', 'token', 'transform[4]', 'uchar', 'uint', 'uint64', 'vectord[3]', 'vectorf[3]', 'vectorh[3]']``", "Input array element", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Array (*outputs:array*)", "``['bool[]', 'colord[3][]', 'colord[4][]', 'colorf[3][]', 'colorf[4][]', 'colorh[3][]', 'colorh[4][]', 'double[2][]', 'double[3][]', 'double[4][]', 'double[]', 'float[2][]', 'float[3][]', 'float[4][]', 'float[]', 'frame[4][]', 'half[2][]', 'half[3][]', 'half[4][]', 'half[]', 'int64[]', 'int[2][]', 'int[3][]', 'int[4][]', 'int[]', 'matrixd[2][]', 'matrixd[3][]', 'matrixd[4][]', 'normald[3][]', 'normalf[3][]', 'normalh[3][]', 'pointd[3][]', 'pointf[3][]', 'pointh[3][]', 'quatd[4][]', 'quatf[4][]', 'quath[4][]', 'texcoordd[2][]', 'texcoordd[3][]', 'texcoordf[2][]', 'texcoordf[3][]', 'texcoordh[2][]', 'texcoordh[3][]', 'timecode[]', 'token[]', 'transform[4][]', 'uchar[]', 'uint64[]', 'uint[]', 'vectord[3][]', 'vectorf[3][]', 'vectorh[3][]']``", "The constructed array of size 'Array Size' with the data type specified in 'Array Type' and values populated from the input array.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ConstructArray"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Make Array"
    "Categories", "math:array"
    "Generated Class Name", "OgnConstructArrayDatabase"
    "Python Module", "omni.graph.nodes_core"

