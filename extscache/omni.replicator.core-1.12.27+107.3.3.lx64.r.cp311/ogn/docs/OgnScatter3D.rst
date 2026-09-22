.. _omni_replicator_core_OgnScatter3D_1:

.. _omni_replicator_core_OgnScatter3D:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Scatter Node: 3D Scattering
    :keywords: lang-en omnigraph node Replicator:Core compute-on-request core ogn-scatter3-d


Scatter Node: 3D Scattering
===========================

.. <description>

This node generates random points within any 3D mesh.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Check For Collisions (*inputs:checkForCollisions*)", "``bool``", "whether sampling procedure should ensure that no sampled prims overlap", "False"
    "Exec In (*inputs:execIn*)", "``execution``", "exec", "None"
    "Max Samp (*inputs:maxSamp*)", "``float[3]``", "maximum position in global space to sample from", "[3.4028235e+38, 3.4028235e+38, 3.4028235e+38]"
    "Min Samp (*inputs:minSamp*)", "``float[3]``", "minimum position in global space to sample from", "[-3.4028235e+38, -3.4028235e+38, -3.4028235e+38]"
    "No Coll Prims (*inputs:noCollPrims*)", "``target``", "existing prim(s) to prevent collisions with - if any prims are passed they will be checked for collisions which may slow down compute, regardless if checkForCollisions is True/False", "None"
    "Prevent Vol Overlap (*inputs:preventVolOverlap*)", "``bool``", "If true, prevent double sampling even when multiple enclosing volumes overlap, so that the entire enclosed volume is sampled uniformly. If false, it allows overlapped sampling with higher density in overlapping areas.", "True"
    "Prims (*inputs:prims*)", "``target``", "prim(s) to set location", "None"
    "Resolution Scaling (*inputs:resolutionScaling*)", "``float``", "Amount the default voxel resolution used in sampling should be scaled. More complex meshes may require higher resolution. Default voxel resolution is 30 for the longest side of the mean sized volumePrim mesh provided.", "1.0"
    "Seed (*inputs:seed*)", "``int``", "Random Number Generator seed. A value of less than 0 will indicate using the global seed.", "-1"
    "Viz Sampled Voxels (*inputs:vizSampledVoxels*)", "``bool``", "Visualize the voxel space that input prim positions are sampled from", "False"
    "Volume Excl Prims (*inputs:volumeExclPrims*)", "``target``", "prim(s) from which to exclude from sampling. similar effect to noCollPrims, but more efficient and less accurate", "None"
    "Volume Prims (*inputs:volumePrims*)", "``target``", "prim(s) from which to sample", "None"
    "Voxel Size (*inputs:voxelSize*)", "``float``", "Voxel size used to compute the resolution. If this is provided, then resolutionScaling is ignored, otherwise (if it is zero by default) resolutionScaling is used.", "0.0"


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

    "Unique ID", "omni.replicator.core.OgnScatter3D"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Scatter Node: 3D Scattering"
    "Categories", "Replicator:Core"
    "__categoryDescriptions", "Replicator:Core,Core Replicator nodes"
    "Generated Class Name", "OgnScatter3DDatabase"
    "Python Module", "omni.replicator.core"

