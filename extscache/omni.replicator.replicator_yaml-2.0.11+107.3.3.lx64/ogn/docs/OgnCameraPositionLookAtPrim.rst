.. _omni_replicator_replicator_yaml_OgnCameraPositionLookAtPrim_1:

.. _omni_replicator_replicator_yaml_OgnCameraPositionLookAtPrim:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Calculate camera position when looking at a prim.
    :keywords: lang-en omnigraph node ReplicatorYAML compute-on-request replicator_yaml ogn-camera-position-look-at-prim


Calculate camera position when looking at a prim.
=================================================

.. <description>

Compute proper camera positions when it looks at a prim.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.replicator_yaml<ext_omni_replicator_replicator_yaml>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Axes (*inputs:axes*)", "``float[3][]``", "Axes that the camera is aligned to.", "[]"
    "Exec In (*inputs:execIn*)", "``execution``", "exec", "None"
    "Scale (*inputs:scale*)", "``float``", "Scale determines how far away the camera is from the target prim.", "0.0"
    "Target Prim (*inputs:targetPrim*)", "``target``", "prim to be looked at", "None"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec Out (*outputs:execOut*)", "``execution``", "exec", "None"
    "Samples (*outputs:samples*)", "``float[3][]``", "New positions of each prim in the world space", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.replicator_yaml.OgnCameraPositionLookAtPrim"
    "Version", "1"
    "Extension", "omni.replicator.replicator_yaml"
    "Has State?", "False"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Calculate camera position when looking at a prim."
    "Categories", "ReplicatorYAML"
    "__categoryDescriptions", "ReplicatorYAML,ReplicatorYAML nodes"
    "Generated Class Name", "OgnCameraPositionLookAtPrimDatabase"
    "Python Module", "omni.replicator.replicator_yaml"

