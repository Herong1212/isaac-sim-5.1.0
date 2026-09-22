.. _omni_syntheticdata_SdFrameIdentifier_1:

.. _omni_syntheticdata_SdFrameIdentifier:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Frame Identifier
    :keywords: lang-en omnigraph node graph:postRender,graph:action syntheticdata sd-frame-identifier


Sd Frame Identifier
===================

.. <description>

Synthetic Data node to expose pipeline frame identifier.

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
    "Render Results (*inputs:renderResults*)", "``uint64``", "Render results", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Duration Denominator (*outputs:durationDenominator*)", "``uint64``", "Duration denominator. Only valid if eConstantFramerateFrameNumber", "0"
    "Duration Numerator (*outputs:durationNumerator*)", "``int64``", "Duration numerator. Only valid if eConstantFramerateFrameNumber.", "0"
    "Received (*outputs:exec*)", "``execution``", "Executes for each newFrame event received", "None"
    "External Time Of Sim Ns (*outputs:externalTimeOfSimNs*)", "``int64``", "External time in Ns. Only valid if eConstantFramerateFrameNumber.", "-1"
    "Frame Number (*outputs:frameNumber*)", "``int64``", "Frame number. Valid if eFrameNumber or eConstantFramerateFrameNumber.", "-1"
    "Rational Time Of Sim Denominator (*outputs:rationalTimeOfSimDenominator*)", "``uint64``", "rational time of simulation denominator.", "0"
    "Rational Time Of Sim Numerator (*outputs:rationalTimeOfSimNumerator*)", "``int64``", "rational time of simulation numerator.", "0"
    "Sample Time Offset In Sim Frames (*outputs:sampleTimeOffsetInSimFrames*)", "``uint64``", "Sample time offset. Only valid if eConstantFramerateFrameNumber.", "0"
    "Type (*outputs:type*)", "``token``", "Type of the frame identifier.", "NoFrameNumber"
    "", "Metadata", "*allowedTokens* = NoFrameNumber,FrameNumber,ConstantFramerateFrameNumber", ""


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdFrameIdentifier"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "graph:postRender,graph:action"
    "Generated Class Name", "OgnSdFrameIdentifierDatabase"
    "Python Module", "omni.syntheticdata"

