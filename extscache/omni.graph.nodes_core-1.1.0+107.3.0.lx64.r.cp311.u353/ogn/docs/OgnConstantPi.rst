.. _omni_graph_nodes_ConstantPi_1:

.. _omni_graph_nodes_ConstantPi:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Constant Pi
    :keywords: lang-en omnigraph node constants threadsafe nodes constant-pi


Constant Pi
===========

.. <description>

Computes a double precision floating point constant value that is a multiple of the mathematical constant 'pi'.

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes_core<ext_omni_graph_nodes_core>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Factor (*inputs:factor*)", "``double``", "Multiply this by the mathematical constant 'pi' to compute the output.", "1"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Value (*outputs:value*)", "``double``", "The mathematical constant 'pi' multiplied by 'Factor'.", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.ConstantPi"
    "Version", "1"
    "Extension", "omni.graph.nodes_core"
    "Has State?", "False"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "Categories", "constants"
    "Generated Class Name", "OgnConstantPiDatabase"
    "Python Module", "omni.graph.nodes_core"

