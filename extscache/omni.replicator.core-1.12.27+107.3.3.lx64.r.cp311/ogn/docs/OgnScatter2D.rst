.. _omni_replicator_core_OgnScatter2D_1:

.. _omni_replicator_core_OgnScatter2D:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Scatter Node: 2D Polygon Scattering
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-scatter2-d


Scatter Node: 2D Polygon Scattering
===================================

.. <description>

Randomly scatters the prim locations of inputs:prims onto the polygons in inputs:surfacePrims.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Check For Collisions (*inputs:checkForCollisions*)", "``bool``", "whether sampling procedure should ensure that no prims overlap", "False"
    "Exec In (*inputs:execIn*)", "``execution``", "exec", "None"
    "Max Samp (*inputs:maxSamp*)", "``float[3]``", "maximum position in global space to sample from", "[3.4028235e+38, 3.4028235e+38, 3.4028235e+38]"
    "Min Samp (*inputs:minSamp*)", "``float[3]``", "minimum position in global space to sample from", "[-3.4028235e+38, -3.4028235e+38, -3.4028235e+38]"
    "No Coll Prims (*inputs:noCollPrims*)", "``target``", "existing prim(s) to prevent collisions with", "None"
    "Normal Offset (*inputs:normalOffset*)", "``float``", "optional offset for sampled prims along surface normal", "0"
    "Prims (*inputs:prims*)", "``target``", "prim(s) to set location", "None"
    "Seed (*inputs:seed*)", "``int``", "Random Number Generator seed. A value of less than 0 will indicate using the global seed.", "-1"
    "Surface Prims (*inputs:surfacePrims*)", "``target``", "prim(s) from which to sample", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "exec", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnScatter2D"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Scatter Node: 2D Polygon Scattering"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnScatter2DDatabase"
    "Python Module", "omni.replicator.core"

