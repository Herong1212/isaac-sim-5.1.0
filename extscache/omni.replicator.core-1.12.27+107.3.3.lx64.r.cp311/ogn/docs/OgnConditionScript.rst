.. _omni_replicator_core_OgnConditionScript_1:

.. _omni_replicator_core_OgnConditionScript:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Condition
    :keywords: lang-en omnigraph node Replicator:Annotators core ogn-condition-script


Condition
=========

.. <description>

Condition node returns True or False based on supplied script

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Script (*inputs:conditionScript*)", "``string``", "Condition script", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Is Condition Met (*outputs:isConditionMet*)", "``bool``", "Result of condition evaluation", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Omni Initialized (*state:omni_initialized*)", "``bool``", "Hidden state attribute used internally to control when the setup script is executed", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnConditionScript"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Condition"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnConditionScriptDatabase"
    "Python Module", "omni.replicator.core"

