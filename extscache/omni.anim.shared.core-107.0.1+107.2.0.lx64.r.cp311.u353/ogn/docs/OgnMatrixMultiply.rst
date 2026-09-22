.. _omni_anim_MatrixMultiply_1:

.. _omni_anim_MatrixMultiply:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Matrix Multiply
    :keywords: lang-en omnigraph node anim matrix-multiply


Matrix Multiply
===============

.. <description>

Multiply transform_a and transform_b

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.shared.core<ext_omni_anim_shared_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

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

    "Unique ID", "omni.anim.MatrixMultiply"
    "Version", "1"
    "Extension", "omni.anim.shared.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Matrix Multiply"
    "Generated Class Name", "OgnMatrixMultiplyDatabase"
    "Python Module", "omni.anim.shared.core"

