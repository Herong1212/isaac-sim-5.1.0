.. _omni_replicator_core_OgnSelectSwitch_1:

.. _omni_replicator_core_OgnSelectSwitch:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Select Switch
    :keywords: lang-en omnigraph node flowControl threadsafe core ogn-select-switch


Select Switch
=============

.. <description>

Selects an output from the given inputs based on an integer condition. The switch pipes through the input indexed by the condition (eg. condition=3, output=data3)

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Condition (*inputs:condition*)", "``int``", "The index of the input to select", "0"
    "Input 0 (*inputs:data0*)", "``['colord[3]', 'colord[3][]', 'colord[4]', 'colord[4][]', 'colorf[3]', 'colorf[3][]', 'colorf[4]', 'colorf[4][]', 'colorh[3]', 'colorh[3][]', 'colorh[4]', 'colorh[4][]', 'double', 'double[2]', 'double[2][]', 'double[3]', 'double[3][]', 'double[4]', 'double[4][]', 'double[]', 'float', 'float[2]', 'float[2][]', 'float[3]', 'float[3][]', 'float[4]', 'float[4][]', 'float[]', 'frame[4]', 'frame[4][]', 'half', 'half[2]', 'half[2][]', 'half[3]', 'half[3][]', 'half[4]', 'half[4][]', 'half[]', 'int', 'int64', 'int64[]', 'int[2]', 'int[2][]', 'int[3]', 'int[3][]', 'int[4]', 'int[4][]', 'int[]', 'matrixd[2]', 'matrixd[2][]', 'matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]', 'normald[3]', 'normald[3][]', 'normalf[3]', 'normalf[3][]', 'normalh[3]', 'normalh[3][]', 'pointd[3]', 'pointd[3][]', 'pointf[3]', 'pointf[3][]', 'pointh[3]', 'pointh[3][]', 'quatd[4]', 'quatd[4][]', 'quatf[4]', 'quatf[4][]', 'quath[4]', 'quath[4][]', 'texcoordd[2]', 'texcoordd[2][]', 'texcoordd[3]', 'texcoordd[3][]', 'texcoordf[2]', 'texcoordf[2][]', 'texcoordf[3]', 'texcoordf[3][]', 'texcoordh[2]', 'texcoordh[2][]', 'texcoordh[3]', 'texcoordh[3][]', 'timecode', 'timecode[]', 'transform[4]', 'transform[4][]', 'uchar', 'uchar[]', 'uint', 'uint64', 'uint64[]', 'uint[]', 'vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "Value if index is 0", "None"
    "Num Samples (*inputs:numSamples*)", "``int``", "number of samples to generate", "1"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Samples (*outputs:samples*)", "``['colord[3]', 'colord[3][]', 'colord[4]', 'colord[4][]', 'colorf[3]', 'colorf[3][]', 'colorf[4]', 'colorf[4][]', 'colorh[3]', 'colorh[3][]', 'colorh[4]', 'colorh[4][]', 'double', 'double[2]', 'double[2][]', 'double[3]', 'double[3][]', 'double[4]', 'double[4][]', 'double[]', 'float', 'float[2]', 'float[2][]', 'float[3]', 'float[3][]', 'float[4]', 'float[4][]', 'float[]', 'frame[4]', 'frame[4][]', 'half', 'half[2]', 'half[2][]', 'half[3]', 'half[3][]', 'half[4]', 'half[4][]', 'half[]', 'int', 'int64', 'int64[]', 'int[2]', 'int[2][]', 'int[3]', 'int[3][]', 'int[4]', 'int[4][]', 'int[]', 'matrixd[2]', 'matrixd[2][]', 'matrixd[3]', 'matrixd[3][]', 'matrixd[4]', 'matrixd[4][]', 'normald[3]', 'normald[3][]', 'normalf[3]', 'normalf[3][]', 'normalh[3]', 'normalh[3][]', 'pointd[3]', 'pointd[3][]', 'pointf[3]', 'pointf[3][]', 'pointh[3]', 'pointh[3][]', 'quatd[4]', 'quatd[4][]', 'quatf[4]', 'quatf[4][]', 'quath[4]', 'quath[4][]', 'texcoordd[2]', 'texcoordd[2][]', 'texcoordd[3]', 'texcoordd[3][]', 'texcoordf[2]', 'texcoordf[2][]', 'texcoordf[3]', 'texcoordf[3][]', 'texcoordh[2]', 'texcoordh[2][]', 'texcoordh[3]', 'texcoordh[3][]', 'timecode', 'timecode[]', 'transform[4]', 'transform[4][]', 'uchar', 'uchar[]', 'uint', 'uint64', 'uint64[]', 'uint[]', 'vectord[3]', 'vectord[3][]', 'vectorf[3]', 'vectorf[3][]', 'vectorh[3]', 'vectorh[3][]']``", "The selected value from all inputs", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnSelectSwitch"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Select Switch"
    "Categories", "flowControl"
    "Generated Class Name", "OgnSelectSwitchDatabase"
    "Python Module", "omni.replicator.core"

