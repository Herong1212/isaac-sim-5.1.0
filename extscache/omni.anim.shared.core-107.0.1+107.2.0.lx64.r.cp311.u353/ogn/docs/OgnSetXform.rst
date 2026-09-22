.. _omni_anim_SetXform_1:

.. _omni_anim_SetXform:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Set Xform
    :keywords: lang-en omnigraph node WriteOnly anim set-xform


Set Xform
=========

.. <description>

Set the world transform of a prim.

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.shared.core<ext_omni_anim_shared_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec In (*inputs:execIn*)", "``execution``", "The input execution port", "None"
    "Prim (*inputs:prim*)", "``bundle``", "Xformable bundle", "None"
    "Transform (*inputs:transform*)", "``matrixd[4]``", "World transform for inputs:prim", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Usd Timecode (*inputs:usdTimecode*)", "``double``", "The time at which to evaluate the transform of the USD prim.", "0"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "The output execution port", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.anim.SetXform"
    "Version", "1"
    "Extension", "omni.anim.shared.core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Set Xform"
    "Generated Class Name", "OgnSetXformDatabase"
    "Python Module", "omni.anim.shared.core"

