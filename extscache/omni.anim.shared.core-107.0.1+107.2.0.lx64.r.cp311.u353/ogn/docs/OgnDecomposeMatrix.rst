.. _omni_anim_DecomposeMatrix_1:

.. _omni_anim_DecomposeMatrix:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Decompose Matrix
    :keywords: lang-en omnigraph node anim decompose-matrix


Decompose Matrix
================

.. <description>

xform matrix decomposition

.. </description>


Installation
------------

To use this node enable :ref:`omni.anim.shared.core<ext_omni_anim_shared_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrix (*inputs:matrix*)", "``matrixd[4]``", "Input matrix.", "[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]"
    "Rotate Order (*inputs:rotateOrder*)", "``int``", "controls the order in which rx, ry, rz are applied in the transformation matrix.", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Quaternion (*outputs:quaternion*)", "``double[4]``", "Rotation part of the matrix expressed as quaternion.", "[0.0, 0.0, 0.0, 1.0]"
    "Rotate (*outputs:rotate*)", "``double[3]``", "Rotation part of the matrix expressed as euler angles.", "[0.0, 0.0, 0.0]"
    "Scale (*outputs:scale*)", "``double[3]``", "Scale part of the matrix.", "[1.0, 1.0, 1.0]"
    "Translate (*outputs:translate*)", "``double[3]``", "Translation part of the matrix.", "[0.0, 0.0, 0.0]"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.anim.DecomposeMatrix"
    "Version", "1"
    "Extension", "omni.anim.shared.core"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Decompose Matrix"
    "Generated Class Name", "OgnDecomposeMatrixDatabase"
    "Python Module", "omni.anim.shared.core"

