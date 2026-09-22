.. _omni_anim_graph_GetCharacterJointTransform_1:

.. _omni_anim_graph_GetCharacterJointTransform:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Animation Graph Joint Transform
    :keywords: lang-en omnigraph node animation graph get-character-joint-transform


Get Animation Graph Joint Transform
===================================

.. <description>

Get the joint transform in world space from the Animation Graph on the specified UsdSkelRoot prim.

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.graph.core<ext_omni_anim_graph_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Joint (*inputs:joint*)", "``token``", "The joint name to query.", ""
    "Skel Root Path (*inputs:skelRootPath*)", "``token``", "The prim path of a UsdSkelRoot to which has the AnimationGraph applied and assigned to it.", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform (*outputs:transform*)", "``matrixd[4]``", "Joint transform in the world space.", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.anim.graph.GetCharacterJointTransform"
    "Version", "1"
    "Extension", "omni.anim.graph.core"
    "Icon", "ogn/icons/omni.anim.graph.GetCharacterJointTransform.svg"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Get Animation Graph Joint Transform"
    "Categories", "animation"
    "__categoryDescriptions", "animation,Nodes dealing with Animation"
    "Generated Class Name", "OgnGetCharacterJointTransformDatabase"
    "Python Module", "omni.anim.graph.core"

