.. _omni_genproc_core_OrderMatricesByDistance_1:

.. _omni_genproc_core_OrderMatricesByDistance:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Order Matrices by Distance
    :keywords: lang-en omnigraph node spatial core order-matrices-by-distance


Order Matrices by Distance
==========================

.. <description>

Order matrices based on the distance from their translation component to a reference point.

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Matrices (*inputs:matrices*)", "``matrixd[4][]``", "Matrices to be sorted according to the distance from their translation component to the reference point", "[]"
    "Reference Point (*inputs:point*)", "``float[3]``", "Reference point from which distances to matrices are measured.", "[0, 0, 0]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Ordered Matrices (*outputs:matrices*)", "``matrixd[4][]``", "Sorted list of matrices", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Matrices (*state:prevMatrices*)", "``matrixd[4][]``", "Previous matrices value for recompute test", "None"
    "Prev Point (*state:prevPoint*)", "``float[3]``", "Previous point value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.OrderMatricesByDistance"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Order Matrices by Distance"
    "Categories", "spatial"
    "Generated Class Name", "OgnOrderMatricesByDistanceDatabase"
    "Python Module", "omni.genproc.core"

