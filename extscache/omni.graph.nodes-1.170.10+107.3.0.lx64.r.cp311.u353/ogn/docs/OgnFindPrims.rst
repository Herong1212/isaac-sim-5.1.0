.. _omni_graph_nodes_FindPrims_2:

.. _omni_graph_nodes_FindPrims:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Find Prims
    :keywords: lang-en omnigraph node sceneGraph threadsafe ReadOnly nodes find-prims


Find Prims
==========

.. <description>

Finds Prims on the stage which match the given criteria

.. </description>


Installation
------------

To use this node enable :ref:`omni.graph.nodes<ext_omni_graph_nodes>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Ignore System Prims (*inputs:ignoreSystemPrims*)", "``bool``", "Ignore system prims such as omni graph nodes that shouldn't be considered during the import.", "False"
    "Prim Name Prefix (*inputs:namePrefix*)", "``token``", "Only prims with a name starting with the given prefix will be returned.", ""
    "Prim Path Pattern (*inputs:pathPattern*)", "``token``", "A list of wildcard patterns used to match the prim paths  Supported syntax of wildcard pattern:     '*' - match an arbitrary number of any characters     '?' - match any single character     '^' - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['/Cube0', '/Cube1', '/Box']     '*' - match any     '* ^/Box' - match any, but exclude '/Box'     '* ^/Cube*' - match any, but exclude '/Cube0' and '/Cube1'", ""
    "Recursive (*inputs:recursive*)", "``bool``", "False means only consider children of the root prim, True means all prims in the hierarchy", "False"
    "Attribute Names (*inputs:requiredAttributes*)", "``string``", "A space-separated list of attribute names that are required to be present on matched prims", ""
    "Relationship Name (*inputs:requiredRelationship*)", "``token``", "The name of a relationship which must have a target specified by requiredRelationshipTarget or requiredTarget", ""
    "Relationship Prim Path (*inputs:requiredRelationshipTarget*)", "``path``", "The path that must be a target of the requiredRelationship", ""
    "Relationship Prim (*inputs:requiredTarget*)", "``target``", "The target of the requiredRelationship", "None"
    "Root Prim (*inputs:rootPrim*)", "``target``", "Only children of the given prim will be considered. If rootPrim is specified, rootPrimPath will be ignored.", "None"
    "Root Prim Path (*inputs:rootPrimPath*)", "``token``", "Only children of the given prim will be considered. Empty will search the whole stage.", ""
    "Prim Type Pattern (*inputs:type*)", "``token``", "A list of wildcard patterns used to match the prim types that are to be imported  Supported syntax of wildcard pattern:     '*' - match an arbitrary number of any characters     '?' - match any single character     '^' - (caret) is used to define a pattern that is to be excluded  Example of wildcard patterns, input: ['Mesh', 'Cone', 'Cube']     '*' - match any     '* ^Mesh' - match any, but exclude 'Mesh'     '* ^Cone ^Cube' - match any, but exclude 'Cone' and 'Cube'", "*"


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Prim Paths (*outputs:primPaths*)", "``token[]``", "A list of Prim paths as tokens which match the given type", "None"
    "Prims (*outputs:prims*)", "``target``", "A list of Prim paths which match the given type", "None"


State
-----
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Ignore System Prims (*state:ignoreSystemPrims*)", "``bool``", "last corresponding input seen", "None"
    "Input Type (*state:inputType*)", "``token``", "last corresponding input seen", "None"
    "Name Prefix (*state:namePrefix*)", "``token``", "last corresponding input seen", "None"
    "Path Pattern (*state:pathPattern*)", "``token``", "last corresponding input seen", "None"
    "Recursive (*state:recursive*)", "``bool``", "last corresponding input seen", "None"
    "Required Attributes (*state:requiredAttributes*)", "``string``", "last corresponding input seen", "None"
    "Required Relationship (*state:requiredRelationship*)", "``token``", "last corresponding input seen", "None"
    "Required Relationship Target (*state:requiredRelationshipTarget*)", "``string``", "last corresponding input seen", "None"
    "Required Target (*state:requiredTarget*)", "``target``", "last corresponding input seen", "None"
    "Root Prim (*state:rootPrim*)", "``target``", "last corresponding input seen", "None"
    "Root Prim Path (*state:rootPrimPath*)", "``token``", "last corresponding input seen", "None"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "omni.graph.nodes.FindPrims"
    "Version", "2"
    "Extension", "omni.graph.nodes"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Find Prims"
    "Categories", "sceneGraph"
    "Generated Class Name", "OgnFindPrimsDatabase"
    "Python Module", "omni.graph.nodes"

