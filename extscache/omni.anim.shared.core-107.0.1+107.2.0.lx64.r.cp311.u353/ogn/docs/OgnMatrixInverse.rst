.. _omni_anim_MatrixInverse_1:

.. _omni_anim_MatrixInverse:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Matrix Inverse
    :keywords: lang-en omnigraph node anim matrix-inverse


Matrix Inverse
==============

.. <description>

Compute the inverse of the input transform matrix

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.shared.core<ext_omni_anim_shared_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Transform (*inputs:transform*)", "``matrixd[4]``", "Transform matrix", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"


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

    "Unique ID", "omni.anim.MatrixInverse"
    "Version", "1"
    "Extension", "omni.anim.shared.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Matrix Inverse"
    "Generated Class Name", "OgnMatrixInverseDatabase"
    "Python Module", "omni.anim.shared.core"

