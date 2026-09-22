.. _omni_anim_graph_WriteAnimationGraphVariable_1:

.. _omni_anim_graph_WriteAnimationGraphVariable:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Write Animation Graph Variable
    :keywords: lang-en omnigraph node animation graph write-animation-graph-variable


Write Animation Graph Variable
==============================

.. <description>

Writes the variable value to the AnimationGraph applied to the specifed UsdSkelRoot prim.

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.graph.core<ext_omni_anim_graph_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "Input execution state", "None"
    "Graph (*inputs:graph*)", "``bundle``", "The animation graph to write to that is applied the the character.", "None"
    "Skel Root Path (*inputs:skelRootPath*)", "``token``", "The prim path of a UsdSkelRoot to which has the AnimationGraph applied and assigned to it. Default behavior: use the graph target.", "None"
    "Value (*inputs:value*)", "``any``", "The variable value that we be written to.", "None"
    "Variable Name (*inputs:variableName*)", "``token``", "The name of the animation graph variable to get.", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "Output execution", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.anim.graph.WriteAnimationGraphVariable"
    "Version", "1"
    "Extension", "omni.anim.graph.core"
    "Icon", "ogn/icons/omni.anim.graph.WriteAnimationGraphVariable.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Write Animation Graph Variable"
    "Categories", "animation"
    "__categoryDescriptions", "animation,Nodes dealing with Animation"
    "Generated Class Name", "OgnWriteAnimationGraphVariableDatabase"
    "Python Module", "omni.anim.graph.core"

