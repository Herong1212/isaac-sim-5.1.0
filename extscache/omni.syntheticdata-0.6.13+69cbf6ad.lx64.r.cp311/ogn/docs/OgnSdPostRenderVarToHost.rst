.. _omni_syntheticdata_SdPostRenderVarToHost_1:

.. _omni_syntheticdata_SdPostRenderVarToHost:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Post Render Var To Host
    :keywords: lang-en omnigraph node graph:postRender,rendering syntheticdata sd-post-render-var-to-host


Sd Post Render Var To Host
==========================

.. <description>

Expose a host renderVar from the input device renderVar.

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Gpu (*inputs:gpu*)", "``uint64``", "Pointer to shared context containing gpu foundations", "0"
    "Render Var (*inputs:renderVar*)", "``token``", "Name of the device renderVar to expose on the host", ""
    "Render Var Host Suffix (*inputs:renderVarHostSuffix*)", "``string``", "Suffix appended to the renderVar name", "host"
    "Rp (*inputs:rp*)", "``uint64``", "Pointer to render product for this view", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Trigger", "None"
    "Render Var (*outputs:renderVar*)", "``token``", "Name of the resulting renderVar on the host", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdPostRenderVarToHost"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "graph:postRender,rendering"
    "Generated Class Name", "OgnSdPostRenderVarToHostDatabase"
    "Python Module", "omni.syntheticdata"

