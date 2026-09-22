.. _omni_replicator_core_OgnRefTime_1:

.. _omni_replicator_core_OgnRefTime:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Reference Time Annotator
    :keywords: lang-en omnigraph node Replicator:Annotators compute-on-request core ogn-ref-time


Reference Time Annotator
========================

.. <description>

Reference Time Annotator

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "exec", "None"
    "Reference Time Denominator (*inputs:referenceTimeDenominator*)", "``uint64``", "Reference time represented as a rational number : denominator", "0"
    "Reference Time Numerator (*inputs:referenceTimeNumerator*)", "``int64``", "Reference time represented as a rational number : numerator", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "exec", "None"
    "Reference Time Denominator (*outputs:referenceTimeDenominator*)", "``uint64``", "Reference time represented as a rational number : denominator", "None"
    "Reference Time Numerator (*outputs:referenceTimeNumerator*)", "``int64``", "Reference time represented as a rational number : numerator", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnRefTime"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Reference Time Annotator"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnRefTimeDatabase"
    "Python Module", "omni.replicator.core"

