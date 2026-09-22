.. _omni_anim_graph_GetCharacterWorldTransform_1:

.. _omni_anim_graph_GetCharacterWorldTransform:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Animation Graph World Transform
    :keywords: lang-en omnigraph node animation graph get-character-world-transform


Get Animation Graph World Transform
===================================

.. <description>

Get the world space transform from the Animation Graph on the specified UsdSkelRoot prim.

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.graph.core<ext_omni_anim_graph_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Skel Root Path (*inputs:skelRootPath*)", "``token``", "The prim path of a UsdSkelRoot to which has the AnimationGraph applied and assigned to it.", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform (*outputs:transform*)", "``matrixd[4]``", "Character world transform of the given UsdSkelRoot.", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.anim.graph.GetCharacterWorldTransform"
    "Version", "1"
    "Extension", "omni.anim.graph.core"
    "Icon", "ogn/icons/omni.anim.graph.GetCharacterWorldTransform.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Animation Graph World Transform"
    "Categories", "animation"
    "__categoryDescriptions", "animation,Nodes dealing with Animation"
    "Generated Class Name", "OgnGetCharacterWorldTransformDatabase"
    "Python Module", "omni.anim.graph.core"

