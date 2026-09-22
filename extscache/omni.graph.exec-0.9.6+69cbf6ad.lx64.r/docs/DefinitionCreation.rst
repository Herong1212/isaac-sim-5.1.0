.. include:: Helpers.rst

.. _ef_definition_creation:

Definition Creation
###################

|SHOW_GUIDE_WARNING|

|Definitions| in the Execution Framework define the work each |node| represents.  Definitions come in two forms:
|opaque definitions| (implemented by |NodeDef|) and definitions described by a |graph| (i.e. |NodeGraphDef|).  Each is
critical to EF's operation.  This article covers how to create both.

Customizing NodeDef
~~~~~~~~~~~~~~~~~~~

|NodeDef| encapsulates opaque user code the Execution Framework cannot examine/optimize.

Probably the best example of how we can customize |NodeDef| is by looking at how |NodeDefLambda| is implemented. The
implementation is simple.  At creation, the object is given a function pointer, which it stores.  When
|INodeDef::execute()| is called, the stored function is invoked.

.. literalinclude:: ../../../../include/omni/graph/exec/unstable/NodeDefLambda.h
   :language: c++
   :dedent:
   :start-after: ef-docs node-def-lambda-begin
   :end-before: ef-docs node-def-lambda-end
   :name: ef_listing_node-def-lambda
   :caption: Implementation of NodeDefLambda

Customizing NodeGraphDef (static symbols)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When all nodes in the graph are known at compilation time, we can define the nodes as part of the definition.  Below is
an example of constructing a |behavior tree|.  Notice the nodes in the behavior tree are members of the definition and
therefore owned by the definition.

.. literalinclude:: ../tests.cpp/graphs/TestBehaviorTree.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs behavior-graph-train-run-def-begin
   :end-before: ef-docs behavior-graph-train-run-def-end
   :name: ef_listing_behavior-graph-train-run-def
   :caption: Definition of a behavior tree.

Customizing NodeGraphDef
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When we do not know the nodes at compile time, we are still responsible for maintaining the nodes' lifetime. We also are
encouraged to reuse of nodes between :ref:`topology changes <ef_graph_invalidation>`.

In the example below, we create a definition that builds a graph where each node represents a runner.  The number of
runners is not known at compile time and is specified at runtime as an argument to the ``build()`` method.  During
``build()``, each node is stored in a ``std::vector`` and a definition is attached to the node to define each runner's
behavior.

.. literalinclude:: ../tests.cpp/graphs/TestBehaviorTree.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs behavior-graph-runners-begin
   :end-before: ef-docs behavior-graph-runners-end
   :name: ef_listing_behavior-graph-runners
   :caption: Definition of a runner graph using behavior tree.

Next Steps
~~~~~~~~~~

Readers are encouraged to examine :file:`kit/source/extensions/omni.graph.exec/tests.cpp/graphs/TestBehaviorTree.cpp` to
see the full implementation of |behavior trees| using EF.

Now that you saw how to create definitions, make sure to consult the :ref:`ef_pass_creation` guide. If you haven't yet
created a module for extending EF, consult the :ref:`ef_plugin_creation` guide.
