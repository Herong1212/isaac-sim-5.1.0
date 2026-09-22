.. _omni_anim_curve_core_AnimCurve_5:

.. _omni_anim_curve_core_AnimCurve:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Anim Curve
    :keywords: lang-en omnigraph node animation WriteOnly core anim-curve


Anim Curve
==========

.. <description>

Evaluates curve animation

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.curve.core<ext_omni_anim_curve_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Individual Outputs (*inputs:IndividualOutputs*)", "``string``", "Uses wildcard matching to select curves that are outputed individually.", ""
    "Prim (*inputs:Prim*)", "``target``", "Target prim that is directly animated by node.", "None"
    "", "Metadata", "*literalOnly* = 1", ""
    "Time (*inputs:Time*)", "``timecode``", "Time used to evaluate values. Nan value uses global time.", "0.0"
    "Use Global Time (*inputs:UseGlobalTime*)", "``bool``", "Whether use global time or custom time to evaluate curve values.", "True"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Anim Frame (*outputs:AnimFrame*)", "``bundle``", "Evaluated curve value at given time.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.anim.curve.core.AnimCurve"
    "Version", "5"
    "Extension", "omni.anim.curve.core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "animation"
    "__categoryDescriptions", "animation,Nodes dealing with Animation"
    "Generated Class Name", "AnimCurveDatabase"
    "Python Module", "omni.anim.curve.core"

