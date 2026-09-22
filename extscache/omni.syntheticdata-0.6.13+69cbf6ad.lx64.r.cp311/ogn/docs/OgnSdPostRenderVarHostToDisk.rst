.. _omni_syntheticdata_SdPostRenderVarHostToDisk_1:

.. _omni_syntheticdata_SdPostRenderVarHostToDisk:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Post Render Var Host To Disk
    :keywords: lang-en omnigraph node graph:postRender,rendering syntheticdata sd-post-render-var-host-to-disk


Sd Post Render Var Host To Disk
===============================

.. <description>

Dispatch the writting of a host renderVar to disk.

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Detach Resource Before Dispatch (*inputs:detachResourceBeforeDispatch*)", "``bool``", "Duplicate the resource before dispatching the copy", "False"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Gpu (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Output Basename (*inputs:outputBasename*)", "``string``", "Basename to write renderVar file. (use {renderVar} if empty)", ""
    "Output Folder (*inputs:outputFolder*)", "``string``", "Folder to write renderVar file", "/tmp/ovSdOut"
    "Output Rational Render Time (*inputs:outputRationalRenderTime*)", "``bool``", "Add rational render time to the basename", "True"
    "Render Product Path (*inputs:renderProductPath*)", "``token``", "Path of the render product prim", ""
    "Render Var (*inputs:renderVar*)", "``token``", "Name of the renderVar to write to disk", ""
    "Rp (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Output Path (*outputs:outputPath*)", "``string``", "Output path to be written", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdPostRenderVarHostToDisk"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "graph:postRender,rendering"
    "Generated Class Name", "OgnSdPostRenderVarHostToDiskDatabase"
    "Python Module", "omni.syntheticdata"

