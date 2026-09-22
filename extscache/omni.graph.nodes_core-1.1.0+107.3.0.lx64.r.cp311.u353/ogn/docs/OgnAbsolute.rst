.. _omni_graph_nodes_Absolute_1:

.. _omni_graph_nodes_Absolute:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Absolute
    :keywords: lang-en omnigraph node math:operator threadsafe nodes absolute


Absolute
========

.. <description>

Compute the absolute value of a scalar, array of scalars, vector, or array of vectors; in the latter three cases the operator is applied to every single scalar element in the corresponding structures.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Input (*inputs:input*)", "``['colord[3]', 'colord[3][]', 'colord[4]', 'colord[4][]', 'colorf[3]', 'colorf[3][]', 'colorf[4]', 'colorf[4][]', 'colorh[3]', 'colorh[3][]', 'colorh[4]', 'colorh[4][]', 'double', 'double[2]', 'double[2][]', 'double[3]', 'double[3][]', 'double[4]', 'double[4][]', 'double[]', 'float', 'float[2]', 'float[2][]', 'float[3]', 'float[3][]', 'float[4]', 'float[4][]', 'float[]', 'half', 'half[2]', 'half[2][]', 'half[3]', 'half[3][]', 'half[4]', 'half[4][]', 'half[]', 'int', 'int64', 'int64[]', 'int[2]', 'int[2][]', 'int[3]', 'int[3][]', 'int[4]', 'int[4][]', 'int[]', 'normald[3]', 'normald[3][]', 'normalf[3]', 'normalf[3][]', 'normalh[3]', 'normalh[3][]', 'pointd[3]', 'pointd[3][]', 'pointf[3]', 'pointf[3][]', 'pointh[3]', 'pointh[3][]', 'quatd[4]', 'quatd[4][]', 'quatf[4]', 'quatf[4][]', 'quath[4]', 'quath[4][]', 'texcoordd[2]', 'texcoordd[2][]', 'texcoordd[3]', 'texcoordd[3][]', 'texcoordf[2]', 'texcoordf[2][]', 'texcoordf[3]', 'texcoordf[3][]', 'texcoordh[2]', 'texcoordh[2][]', 'texcoordh[3]', 'texcoordh[3][]', 'timecode', 'timecode[]', 'uchar', 'uchar[]', 'uint', 'uint64', 'uint64[]', 'uint[]', 'vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The scalar(s) or vector(s) to take the absolute value of.", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Absolute (*outputs:absolute*)", "``['colord[3]', 'colord[3][]', 'colord[4]', 'colord[4][]', 'colorf[3]', 'colorf[3][]', 'colorf[4]', 'colorf[4][]', 'colorh[3]', 'colorh[3][]', 'colorh[4]', 'colorh[4][]', 'double', 'double[2]', 'double[2][]', 'double[3]', 'double[3][]', 'double[4]', 'double[4][]', 'double[]', 'float', 'float[2]', 'float[2][]', 'float[3]', 'float[3][]', 'float[4]', 'float[4][]', 'float[]', 'half', 'half[2]', 'half[2][]', 'half[3]', 'half[3][]', 'half[4]', 'half[4][]', 'half[]', 'int', 'int64', 'int64[]', 'int[2]', 'int[2][]', 'int[3]', 'int[3][]', 'int[4]', 'int[4][]', 'int[]', 'normald[3]', 'normald[3][]', 'normalf[3]', 'normalf[3][]', 'normalh[3]', 'normalh[3][]', 'pointd[3]', 'pointd[3][]', 'pointf[3]', 'pointf[3][]', 'pointh[3]', 'pointh[3][]', 'quatd[4]', 'quatd[4][]', 'quatf[4]', 'quatf[4][]', 'quath[4]', 'quath[4][]', 'texcoordd[2]', 'texcoordd[2][]', 'texcoordd[3]', 'texcoordd[3][]', 'texcoordf[2]', 'texcoordf[2][]', 'texcoordf[3]', 'texcoordf[3][]', 'texcoordh[2]', 'texcoordh[2][]', 'texcoordh[3]', 'texcoordh[3][]', 'timecode', 'timecode[]', 'uchar', 'uchar[]', 'uint', 'uint64', 'uint64[]', 'uint[]', 'vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The original ""Input Value"" with the absolute value operator applied to each scalar value. The structure of the result, arrays and tuples, will mirror that of the input.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.Absolute"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "tags", "absolute"
    "uiName", "Absolute"
    "Categories", "math:operator"
    "Generated Class Name", "OgnAbsoluteDatabase"
    "Python Module", "omni.graph.nodes_core"

