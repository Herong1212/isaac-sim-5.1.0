.. _omni_anim_graph_SetCharacterWorldTransform_1:

.. _omni_anim_graph_SetCharacterWorldTransform:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Animation Graph World Transform
    :keywords: lang-en omnigraph node animation graph set-character-world-transform


Set Animation Graph World Transform
===================================

.. <description>

Set the specified character's animation graph world transform using translation and rotation from the provided transform.

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
    "Skel Root Path (*inputs:skelRootPath*)", "``token``", "The prim path of a UsdSkelRoot to which has the AnimationGraph applied and assigned to it. Default behavior: use the graph target.", "None"
    "Transform (*inputs:transform*)", "``matrixd[4]``", "Desired world transform. Note: only rotation and translation will be extracted, scale is currently ignored.", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


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

    "Unique ID", "omni.anim.graph.SetCharacterWorldTransform"
    "Version", "1"
    "Extension", "omni.anim.graph.core"
    "Icon", "ogn/icons/omni.anim.graph.SetCharacterWorldTransform.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set Animation Graph World Transform"
    "Categories", "animation"
    "__categoryDescriptions", "animation,Nodes dealing with Animation"
    "Generated Class Name", "OgnSetCharacterWorldTransformDatabase"
    "Python Module", "omni.anim.graph.core"

