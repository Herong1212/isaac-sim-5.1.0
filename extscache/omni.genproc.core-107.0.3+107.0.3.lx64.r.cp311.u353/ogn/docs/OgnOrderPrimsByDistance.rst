.. _omni_genproc_core_OrderPrimsByDistance_1:

.. _omni_genproc_core_OrderPrimsByDistance:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Order Prims by Distance
    :keywords: lang-en omnigraph node spatial core order-prims-by-distance


Order Prims by Distance
=======================

.. <description>

Order mesh prims based on their distance to a reference point.

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle Prims (*inputs:bundle*)", "``bundle``", "Bundle Prims", "None"
    "Reference Point (*inputs:point*)", "``float[3]``", "Point from which to measure distances to prims", "[0, 0, 0]"
    "Verbose (*inputs:verbose*)", "``bool``", "Log verbose information", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Ordered Bundle Prims (*outputs:bundle*)", "``bundle``", "Bundle Prims", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Point (*state:prevPoint*)", "``float[3]``", "Previous point value for recompute test", "None"
    "Prev Verbose (*state:prevVerbose*)", "``bool``", "Previous verbose value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.OrderPrimsByDistance"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Order Prims by Distance"
    "Categories", "spatial"
    "Generated Class Name", "OgnOrderPrimsByDistanceDatabase"
    "Python Module", "omni.genproc.core"

