.. _omni_genproc_core_TagPrims_1:

.. _omni_genproc_core_TagPrims:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Tag Prims
    :keywords: lang-en omnigraph node tagging core tag-prims


Tag Prims
=========

.. <description>

Add tag attribute to prims in bundle

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle Prims (*inputs:bundle*)", "``bundle``", "Multiple Prims in Bundle input", "None"
    "Tag Name (*inputs:tagName*)", "``token``", "Name of tag attribute that will be added to prims", "tag"
    "Tag Value (*inputs:tagValue*)", "``token``", "Value to be assigned to tag", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle Prims (*outputs:bundle*)", "``bundle``", "Multiple Prims in Bundle with tag added", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Tag Name (*state:prevTagName*)", "``token``", "Previous tagName value for recompute test", "None"
    "Prev Tag Value (*state:prevTagValue*)", "``token``", "Previous tagValue value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.TagPrims"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Tag Prims"
    "Categories", "tagging"
    "Generated Class Name", "OgnTagPrimsDatabase"
    "Python Module", "omni.genproc.core"

