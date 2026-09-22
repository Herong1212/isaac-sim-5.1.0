.. _omni_anim_GetXform_1:

.. _omni_anim_GetXform:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Get Xform
    :keywords: lang-en omnigraph node threadsafe anim get-xform


Get Xform
=========

.. <description>

Get Xform

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.shared.core<ext_omni_anim_shared_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim (*inputs:prim*)", "``bundle``", "Xformable bundle", "None"
    "Usd Timecode (*inputs:usdTimecode*)", "``double``", "The time at which to evaluate the transform of the USD prim.", "0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Use Local (*inputs:useLocal*)", "``bool``", "Use Local Matrix or World Matrix.", "False"
    "", "Metadata", "*displayGroup* = parameters", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform (*outputs:transform*)", "``matrixd[4]``", "World transform of inputs:prim", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.anim.GetXform"
    "Version", "1"
    "Extension", "omni.anim.shared.core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "uiName", "Get Xform"
    "Generated Class Name", "OgnGetXformDatabase"
    "Python Module", "omni.anim.shared.core"

