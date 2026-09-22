.. _omni_replicator_core_OgnGetSkeletonAttributes_1:

.. _omni_replicator_core_OgnGetSkeletonAttributes:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Ogn Get Skeleton Attributes
    :keywords: lang-en omnigraph node Replicator:Annotators core ogn-get-skeleton-attributes


Ogn Get Skeleton Attributes
===========================

.. <description>

Replicator node to expose prim skeleton atrribute data

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Gpu (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations.", "0"
    "Rp (*inputs:rp*)", "``uint64``", "Render results", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Joint Paths (*outputs:jointPaths*)", "``token[]``", "Array of skeleton joint paths", "None"
    "Joint World Orientations (*outputs:jointWorldOrientations*)", "``float[4][]``", "Array of skeleton joint world orientations (rotations)", "None"
    "Joint World Positions (*outputs:jointWorldPositions*)", "``double[3][]``", "Array of skeleton joint world positions", "None"
    "Joint World Scales (*outputs:jointWorldScales*)", "``float[3][]``", "Array of skeleton joint world scales", "None"
    "Prim Paths (*outputs:primPaths*)", "``token[]``", "Array of prim paths", "None"
    "Prim World Orientations (*outputs:primWorldOrientations*)", "``float[4][]``", "Array of entity world orientations (rotations)", "None"
    "Prim World Positions (*outputs:primWorldPositions*)", "``double[3][]``", "Array of entity world positions", "None"
    "Prim World Scales (*outputs:primWorldScales*)", "``float[3][]``", "Array of entity world scales", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnGetSkeletonAttributes"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "__tokens", "[""primWorldPositionDS"", ""primWorldOrientationDS"", ""primWorldScaleDS"", ""jointWorldPositionDS"", ""jointWorldOrientationDS"", ""jointWorldScaleDS"", ""primPathDS"", ""jointPathDS""]"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnGetSkeletonAttributesDatabase"
    "Python Module", "omni.replicator.core"

