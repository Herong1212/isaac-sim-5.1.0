.. _omni_genproc_core_OrderPointsByDistance_1:

.. _omni_genproc_core_OrderPointsByDistance:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Order Points by Distance
    :keywords: lang-en omnigraph node spatial core order-points-by-distance


Order Points by Distance
========================

.. <description>

Order points based on their distance to a reference point.

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Reference Point (*inputs:point*)", "``float[3]``", "Reference point from which distances to matrices are measured.", "[0, 0, 0]"
    "Points (*inputs:points*)", "``float[3][]``", "Points to be sorted according to their distance from the reference point", "[]"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Ordered Points (*outputs:points*)", "``float[3][]``", "Sorted points", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Point (*state:prevPoint*)", "``float[3]``", "Previous point value for recompute test", "None"
    "Prev Points (*state:prevPoints*)", "``float[3][]``", "Previous points value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.OrderPointsByDistance"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Order Points by Distance"
    "Categories", "spatial"
    "Generated Class Name", "OgnOrderPointsByDistanceDatabase"
    "Python Module", "omni.genproc.core"

