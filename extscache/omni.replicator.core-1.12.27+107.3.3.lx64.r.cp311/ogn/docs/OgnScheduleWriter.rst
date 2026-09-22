.. _omni_replicator_core_OgnScheduleWriter_1:

.. _omni_replicator_core_OgnScheduleWriter:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Schedule Writer
    :keywords: lang-en omnigraph node Replicator:Annotators compute-on-request core ogn-schedule-writer


Schedule Writer
===============

.. <description>

Schedule writer to automatically write annotator data.

.. </description>


Installation
------------

To use this node enable :ref:`omni.replicator.core<ext_omni_replicator_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*inputs:exec*)", "``execution``", "Execution in", "None"
    "Rational Time Of Sim Denominator (*inputs:rationalTimeOfSimDenominator*)", "``uint64``", "rational time of simulation denominator.", "0"
    "Rational Time Of Sim Numerator (*inputs:rationalTimeOfSimNumerator*)", "``int64``", "rational time of simulation numerator.", "0"
    "Writer Id (*inputs:writer_id*)", "``token``", "Writer Identifier", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Exec (*outputs:exec*)", "``execution``", "Execution out", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.replicator.core.OgnScheduleWriter"
    "Version", "1"
    "Extension", "omni.replicator.core"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Schedule Writer"
    "Categories", "Replicator:Annotators"
    "__categoryDescriptions", "Replicator:Annotators,Replicator annotator nodes."
    "Generated Class Name", "OgnScheduleWriterDatabase"
    "Python Module", "omni.replicator.core"

