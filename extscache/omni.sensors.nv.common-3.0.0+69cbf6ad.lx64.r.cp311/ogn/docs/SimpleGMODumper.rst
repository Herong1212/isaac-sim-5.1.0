.. _omni_sensors_nv_common_SimpleGMODumper_1:

.. _omni_sensors_nv_common_SimpleGMODumper:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Simple GMO Dumper
    :keywords: lang-en omnigraph node common simple-g-m-o-dumper


Simple GMO Dumper
=================

.. <description>

Dumps GMO buffer to bin file

.. </description>


Installation
------------

To use this node enable :ref:`omni.sensors.nv.common<ext_omni_sensors_nv_common>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Cuda Stream (*inputs:cudaStream*)", "``uint64``", "Cuda Stream Input", "0"
    "Dump Packets (*inputs:dumpPackets*)", "``bool``", "Dump packets as dwBinFile", "False"
    "File Name (*inputs:fileName*)", "``string``", "File name of the packets", "lidar.h5"
    "Is Radar (*inputs:isRadar*)", "``bool``", "True for radar sensor", "False"
    "Sim Time (*inputs:simTime*)", "``double``", "Simulation time given from PostProcessEntryNode", "0"
    "Src (*inputs:src*)", "``uint64``", "RtSensor buffer id", "0"
    "Src Meta (*inputs:srcMeta*)", "``uint64``", "Lidar Meta Data", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.sensors.nv.common.SimpleGMODumper"
    "Version", "1"
    "Extension", "omni.sensors.nv.common"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Generated Class Name", "SimpleGMODumperDatabase"
    "Python Module", "omni.sensors.nv.common"

