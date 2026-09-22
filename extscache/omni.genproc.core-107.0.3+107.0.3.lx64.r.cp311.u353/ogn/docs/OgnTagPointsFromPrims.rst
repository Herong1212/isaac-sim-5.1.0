.. _omni_genproc_core_TagPointsFromPrims_1:

.. _omni_genproc_core_TagPointsFromPrims:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Tag Points from Prims
    :keywords: lang-en omnigraph node tagging core tag-points-from-prims


Tag Points from Prims
=====================

.. <description>

Given input points and tagged mesh prims, create a tag for each point based on what prim contains that point.  If a point is not contained within any tagged mesh prim, it is given the defaultTag.  If a point is contained within multiple tagged mesh prims, the tag from the first encountered prim is used.

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Tagged Bundle Prims (*inputs:bundle*)", "``bundle``", "Bundle containing tagged prims", "None"
    "Default Tag Value (*inputs:defaultTag*)", "``token``", "Default value assigned to any point not inside a tagged prim", ""
    "Points (*inputs:points*)", "``float[3][]``", "Vertices to be tagged", "[]"
    "Tag Attribute Name (*inputs:tagName*)", "``token``", "Tag attribute to look for in prims", "tag"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Tags (*outputs:tags*)", "``token[]``", "Per-point tags", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Default Tag (*state:prevDefaultTag*)", "``token``", "Previous defaultTag value for recompute test", "None"
    "Prev Points (*state:prevPoints*)", "``float[3][]``", "Previous points value for recompute test", "None"
    "Prev Tag Name (*state:prevTagName*)", "``token``", "Previous tagName value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.TagPointsFromPrims"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Tag Points from Prims"
    "Categories", "tagging"
    "Generated Class Name", "OgnTagPointsFromPrimsDatabase"
    "Python Module", "omni.genproc.core"

