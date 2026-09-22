.. _omni_genproc_core_MotionPath_1:

.. _omni_genproc_core_MotionPath:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Motion Path
    :keywords: lang-en omnigraph node core motion-path


Motion Path
===========

.. <description>

Constraint an xformable prim to the given curve  User offer the u value to specify the point on the curve  The output is the transform matrix.

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Aim offset (*inputs:aimRotation*)", "``float[3]``", "Pitch, Roll, Yaw", "[0.0, 0.0, 0.0]"
    "Curves Bundle (*inputs:curveBundle*)", "``bundle``", "Bundle containing curves data", "None"
    "Cycle U value (*inputs:cycle*)", "``bool``", "If true, the input U value would be cycled between 0.0 and 1.0 If false, the input U value would be clamped between 0.0 and 1.0", "True"
    "Forward Axis (*inputs:forwardAxis*)", "``int``", "Object Forward Axis", "0"
    "U Value (*inputs:uValue*)", "``float``", "Value from zero to one along curve at which we want to get a point", "0.0"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Up Axis (*inputs:upAxis*)", "``int``", "Object Up Axis", "1"
    "World Up Object Bundle (*inputs:worldUpObject*)", "``bundle``", "Bundle containing the world up object xformable prim", "None"
    "World Up Type (*inputs:worldUpType*)", "``int``", "World Up Type", "0"
    "World Up Vector (*inputs:worldUpVector*)", "``float[3]``", "World Up Vector", "[0.0, 1.0, 0.0]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform (*outputs:transform*)", "``matrixd[4]``", "output World transform", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev U Value (*state:prevUValue*)", "``float``", "Previous uValue value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.MotionPath"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Motion Path"
    "Generated Class Name", "OgnMotionPathDatabase"
    "Python Module", "omni.genproc.core"

