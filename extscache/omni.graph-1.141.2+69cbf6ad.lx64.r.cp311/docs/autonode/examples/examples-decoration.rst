.. _autonode_examples_decoration:

Examples Using Custom Decoration
================================

This file contains example usage of |autonode| decoration that use the extra decorator parameters. For access to the
other types of examples see :ref:`autonode_examples`.

.. contents::
   :local:

The `@og.create_node_type` decorator takes a number of optional arguments that helps provide the extra information to
the node type that is normally part of the .ogn definition.

.. literalinclude:: ../../../../../../source/extensions/omni.graph/python/_impl/autonode.py
    :language: python
    :start-after: begin-create-node-type
    :end-before: end-create-node-type

These examples show how the definition of the node type is affected by each of them.

.. begin-content

*@og.create_node_type(ui_name=str)*
-----------------------------------

.. literalinclude:: ../../../../../../source/extensions/omni.graph/python/_impl/autonode_examples.py
    :language: python
    :dedent: 4
    :start-after: begin-autonode-decoration-ui-name
    :end-before: end-autonode-decoration-ui-name

*@og.create_node_type(unique_name=str)*
---------------------------------------

.. literalinclude:: ../../../../../../source/extensions/omni.graph/python/_impl/autonode_examples.py
    :language: python
    :dedent: 4
    :start-after: begin-autonode-decoration-unique-name
    :end-before: end-autonode-decoration-unique-name

*@og.create_node_type(add_execution_pins)*
------------------------------------------

.. literalinclude:: ../../../../../../source/extensions/omni.graph/python/_impl/autonode_examples.py
    :language: python
    :dedent: 4
    :start-after: begin-autonode-decoration-add-execution-pins
    :end-before: end-autonode-decoration-add-execution-pins

*@og.create_node_type(metadata=dict(str,any))*
----------------------------------------------

.. literalinclude:: ../../../../../../source/extensions/omni.graph/python/_impl/autonode_examples.py
    :language: python
    :dedent: 4
    :start-after: begin-autonode-decoration-metadata
    :end-before: end-autonode-decoration-metadata
