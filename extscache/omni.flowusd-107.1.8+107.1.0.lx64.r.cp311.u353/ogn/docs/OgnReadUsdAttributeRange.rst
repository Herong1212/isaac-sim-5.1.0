.. _omni_flowusd_ReadUsdAttributeRange_1:

.. _omni_flowusd_ReadUsdAttributeRange:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Read USD Attribute Range
    :keywords: lang-en omnigraph node threadsafe ReadOnly flowusd read-usd-attribute-range


Read USD Attribute Range
========================

.. <description>

Given a path to a prim on the current USD stage and the name of an attribute on  that prim, gets the requested range of that attribute array, at the global timeline value.

.. </description>


Installation
------------

To use this node enable :ref:`omni.flowusd<ext_omni_flowusd>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "First Element (*inputs:firstElement*)", "``uint64``", "Index to the array attribute for the start of the range", "0"
    "Attribute Name (*inputs:name*)", "``token``", "The name of the attribute to get on the specified prim", ""
    "Prim (*inputs:prim*)", "``bundle``", "The prim to be read from when 'usePath' is false", "None"
    "Prim Path (*inputs:primPath*)", "``token``", "The path of the prim to be modified when 'usePath' is true", "None"
    "Range Size (*inputs:rangeSize*)", "``uint64``", "Maximum Number of elements to include in the output. Set 0 to only get the size of the input array", "0"
    "Usd Timecode (*inputs:usdTimecode*)", "``timecode``", "The time at which to evaluate the transform of the USD prim attribute. A value of ""-1"" indicates that the default USD time stamp should be used", "-1"
    "Use Path (*inputs:usePath*)", "``bool``", "When true, the 'primPath' attribute is used as the path to the prim being read, otherwise it will read the connection at the 'prim' attribute", "False"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Input Array Size (*outputs:inputArraySize*)", "``uint64``", "Size of the input array", "0"
    "Value (*outputs:value*)", "``any``", "The attribute value", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.flowusd.ReadUsdAttributeRange"
    "Version", "1"
    "Extension", "omni.flowusd"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "usd"
    "uiName", "Read USD Attribute Range"
    "Generated Class Name", "OgnReadUsdAttributeRangeDatabase"
    "Python Module", "omni.flowusd"

