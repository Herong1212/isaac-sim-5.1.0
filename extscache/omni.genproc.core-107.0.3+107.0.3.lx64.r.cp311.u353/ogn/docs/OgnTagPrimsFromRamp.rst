.. _omni_genproc_core_TagPrimsFromRamp_1:

.. _omni_genproc_core_TagPrimsFromRamp:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Tag Prims from Ramp
    :keywords: lang-en omnigraph node tagging core tag-prims-from-ramp


Tag Prims from Ramp
===================

.. <description>

Add ramp and tag information to a bundle of prims. This data can be subsequently sampled in downstream nodes  (e.g. GetCurveData in the case of curve prims)

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*inputs:bundle*)", "``bundle``", "Bundle Prims", "None"
    "Ramp Interpolations (*inputs:rampInterpolations*)", "``int[]``", "Interpolation method between keys. Linear is a creates a flat curve from point to point. Smooth creates an ease in or ease out curve from point to point.", "[1, 1]"
    "Ramp Interpolations Name (*inputs:rampInterpolationsName*)", "``token``", "Name of bundle attribute to be created for ramp interpolations.", "ramp_interpolations"
    "Ramp Positions (*inputs:rampPositions*)", "``float[]``", "Parametetric values from [0,1]", "[0.0, 1.0]"
    "Ramp Positions Name (*inputs:rampPositionsName*)", "``token``", "Name of bundle attribute to be created for ramp positions.", "ramp_positions"
    "Ramp Tags (*inputs:rampTags*)", "``token[]``", "Possible tag values for ramp", "['run', 'walk', 'idle']"
    "Ramp Tags Name (*inputs:rampTagsName*)", "``token``", "Name of bundle attribute to be created for ramp tags.", "tags"
    "Ramp Values (*inputs:rampValues*)", "``float[]``", "Value of the ramp at the corresponding position entry.", "[0.0, 0.0]"
    "Ramp Values Name (*inputs:rampValuesName*)", "``token``", "Name of bundle attribute to be created for ramp values.", "ramp_values"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*outputs:bundle*)", "``bundle``", "Prims bundle with ramp data", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Ramp Interpolations (*state:prevRampInterpolations*)", "``int[]``", "Previous rampInterpolations values for recompute test", "None"
    "Prev Ramp Interpolations Name (*state:prevRampInterpolationsName*)", "``token``", "Previous rampInterpolationsName value for recompute test", "None"
    "Prev Ramp Positions (*state:prevRampPositions*)", "``float[]``", "Previous rampPositions values for recompute test", "None"
    "Prev Ramp Positions Name (*state:prevRampPositionsName*)", "``token``", "Previous rampPositionsName value for recompute test", "None"
    "Prev Ramp Tags (*state:prevRampTags*)", "``token[]``", "Previous rampTags values for recompute test", "None"
    "Prev Ramp Tags Name (*state:prevRampTagsName*)", "``token``", "Previous rampTagsName value for recompute test", "None"
    "Prev Ramp Values (*state:prevRampValues*)", "``float[]``", "Previous rampValues values for recompute test", "None"
    "Prev Ramp Values Name (*state:prevRampValuesName*)", "``token``", "Previous rampValuesName value for recompute test", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.TagPrimsFromRamp"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Tag Prims from Ramp"
    "Categories", "tagging"
    "Generated Class Name", "OgnTagPrimsFromRampDatabase"
    "Python Module", "omni.genproc.core"

