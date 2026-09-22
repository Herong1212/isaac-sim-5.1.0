.. _omni_anim_GetJointXform_1:

.. _omni_anim_GetJointXform:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Joint Xform
    :keywords: lang-en omnigraph node WriteOnly anim get-joint-xform


Get Joint Xform
===============

.. <description>

Get Joint Xform

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.shared.core<ext_omni_anim_shared_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "jointName (*inputs:jointName*)", "``token``", "Joint name to extract its world transform from inputs:skel bundle", ""
    "Prim (*inputs:prim*)", "``bundle``", "Xformable prim bundle to set the found transform (optional)", "None"
    "Skel (*inputs:skel*)", "``bundle``", "Skeletal pose bundle", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform (*outputs:transform*)", "``matrixd[4]``", "World transform of the given joint name from inputs:skel bundle", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.anim.GetJointXform"
    "Version", "1"
    "Extension", "omni.anim.shared.core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Get Joint Xform"
    "__tokens", "[""worldMatrix"", ""joints"", ""jointWorldTransforms"", ""prim""]"
    "Generated Class Name", "OgnGetJointXformDatabase"
    "Python Module", "omni.anim.shared.core"

