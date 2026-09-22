.. _omni_anim_MatrixMixer_1:

.. _omni_anim_MatrixMixer:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Matrix Mixer
    :keywords: lang-en omnigraph node anim matrix-mixer


Matrix Mixer
============

.. <description>

Mix two matrices.

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.shared.core<ext_omni_anim_shared_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Alpha (*inputs:alpha*)", "``double``", "Alpha blend value between transform_a and transform_b", "1.0"
    "Interpolate Rotation (*inputs:interpolate_rotation*)", "``bool``", "Interpolate the rotation of transform_b", "True"
    "Interpolate Scale (*inputs:interpolate_scale*)", "``bool``", "Interpolate the scale of transform_b", "True"
    "Interpolate Translation (*inputs:interpolate_translation*)", "``bool``", "Interpolate the translation of transform_b", "True"
    "Transform A (*inputs:transform_a*)", "``matrixd[4]``", "A transform matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Transform B (*inputs:transform_b*)", "``matrixd[4]``", "B transform matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform (*outputs:transform*)", "``matrixd[4]``", "Output transform matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.anim.MatrixMixer"
    "Version", "1"
    "Extension", "omni.anim.shared.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Matrix Mixer"
    "Generated Class Name", "OgnMatrixMixerDatabase"
    "Python Module", "omni.anim.shared.core"

