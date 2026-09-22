.. _omni_syntheticdata_SdTestPrintRawArray_1:

.. _omni_syntheticdata_SdTestPrintRawArray:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Sd Test Print Raw Array
    :keywords: lang-en omnigraph node graph:action,internal:test syntheticdata sd-test-print-raw-array


Sd Test Print Raw Array
=======================

.. <description>

Synthetic Data test node printing the input linear array

.. </description>


Installation
------------

To use this node enable :ref:`omni.syntheticdata<ext_omni_syntheticdata>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Buffer Size (*inputs:bufferSize*)", "``uint``", "Size (in bytes) of the buffer (0 if the input is a texture)", "0"
    "Data (*inputs:data*)", "``uchar[]``", "Buffer array data", "[]"
    "Data File Base Name (*inputs:dataFileBaseName*)", "``token``", "Basename of the output npy file", "/tmp/sdTestRawArray"
    "Element Count (*inputs:elementCount*)", "``int``", "Number of array element", "1"
    "Element Type (*inputs:elementType*)", "``token``", "Type of the array element", "uint8"
    "Exec (*inputs:exec*)", "``execution``", "Trigger", "None"
    "Height (*inputs:height*)", "``uint``", "Height  (0 if the input is a buffer)", "0"
    "Mode (*inputs:mode*)", "``token``", "Mode in [printFormatted, printReferences, testReferences]", "printFormatted"
    "Random Seed (*inputs:randomSeed*)", "``int``", "Random seed", "0"
    "Reference Num Unique Random Values (*inputs:referenceNumUniqueRandomValues*)", "``int``", "Number of reference unique random values to compare", "7"
    "Reference SWH Frame Numbers (*inputs:referenceSWHFrameNumbers*)", "``uint[]``", "Reference swhFrameNumbers relative to the first one", "[11, 17, 29]"
    "Reference Tolerance (*inputs:referenceTolerance*)", "``float``", "Reference tolerance", "0.1"
    "Reference Values (*inputs:referenceValues*)", "``float[]``", "Reference data point values", "[]"
    "Swh Frame Number (*inputs:swhFrameNumber*)", "``uint64``", "Frame number", "0"
    "Width (*inputs:width*)", "``uint``", "Width  (0 if the input is a buffer)", "0"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Received (*outputs:exec*)", "``execution``", "Executes when the event is received", "None"
    "Swh Frame Number (*outputs:swhFrameNumber*)", "``uint64``", "FrameNumber just rendered", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Initial SWH Frame Number (*state:initialSWHFrameNumber*)", "``int64``", "Initial swhFrameNumber", "-1"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.syntheticdata.SdTestPrintRawArray"
    "Version", "1"
    "Extension", "omni.syntheticdata"
    "Has State?", "True"
    "Implementation Language", "Python"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "tests"
    "__tokens", "[""uint16"", ""int16"", ""uint32"", ""int32"", ""float32"", ""token"", ""printFormatted"", ""printReferences"", ""writeToDisk""]"
    "Categories", "graph:action,internal:test"
    "Generated Class Name", "OgnSdTestPrintRawArrayDatabase"
    "Python Module", "omni.syntheticdata"

