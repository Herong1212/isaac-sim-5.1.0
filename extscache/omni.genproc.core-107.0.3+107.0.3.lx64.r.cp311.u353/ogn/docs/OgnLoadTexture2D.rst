.. _omni_genproc_core_LoadTexture2D_1:

.. _omni_genproc_core_LoadTexture2D:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: load texture 2d
    :keywords: lang-en omnigraph node core load-texture2-d


load texture 2d
===============

.. <description>

Loads one or more textures from disk and output them in a bundle

.. </description>


Installation
------------

To use this node enable :ref:`omni.genproc.core<ext_omni_genproc_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Active (*inputs:active*)", "``bool``", "Is the LoadTexture2D node currently active?", "True"
    "", "Metadata", "*displayGroup* = parameters", ""
    "Textures (*inputs:textures*)", "``string``", "Texture paths to load from", ""
    "", "Metadata", "*allowMultiInputs* = 1", ""
    "", "Metadata", "*uiType* = filePath", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Bundle (*outputs:bundle*)", "``bundle``", "output bundle of texture(s) data", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prev Active (*state:prevActive*)", "``bool``", "Previous active value for recompute test", "None"
    "Prev Textures (*state:prevTextures*)", "``string``", "Combined texture paths from previous run", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.genproc.core.LoadTexture2D"
    "Version", "1"
    "Extension", "omni.genproc.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "load texture 2d"
    "__tokens", "[""valid"", ""width"", ""height"", ""bitDepth"", ""componentCount"", ""mode"", ""data""]"
    "Generated Class Name", "OgnLoadTexture2DDatabase"
    "Python Module", "omni.genproc.core"

