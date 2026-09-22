.. include:: Helpers.rst

.. _ef_pass_creation:

Pass Creation
#############

|SHOW_GUIDE_WARNING|

There are two parts to adding a new pass to the pass pipeline. First, we need to define the new pass and then we need to
register it.

There are multiple types of passes supported in EF.  A full list can be found at |PassType|.  To create a pass, we start
by implementing the relevant pass type's interface.  In practice, this will be either |IPopulatePass| or
|IPartitionPass|.  In rare cases, a pass may inherit from |IGlobalPass|, but such a pass is discouraged for performance
reasons.  Implementing population and partition passes is covered below.

Once a pass is implemented, it must be registered with one of the following macros:
|OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS()|, |OMNI_GRAPH_EXEC_REGISTER_PARTITION_PASS()|,
|OMNI_GRAPH_EXEC_REGISTER_GLOBAL_PASS()|.

.. code-block:: c++
   :name: ef_listing_pass_registrations
   :caption: Registration code for different pass types. These macros should be called at global scope.

    // Register MyPopulatePass against a symbol (node or node graph def) name
    OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS(MyPopulatePass, "symbol_name");

    // Register MyPartitionPass with a given priority
    OMNI_GRAPH_EXEC_REGISTER_PARTITION_PASS(MyPartitionPass, 1);

    // Register MyGlobalPass
    OMNI_GRAPH_EXEC_REGISTER_GLOBAL_PASS(MyGlobalPass);


Implementing a Populate Pass
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The example below implements a new populate pass that will instantiate a new ``MyInstancedDef`` definition and attach it
to any node or definition that matches the name given during registration.

.. literalinclude:: ../tests.cpp/TestPass.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs populate-example-begin
   :end-before: ef-docs populate-example-end
   :name: ef_listing_populate_pass_impl
   :caption: Example populate pass

Here, we register the pass, telling EF that this pass should be run on nodes named "my.special.node".

.. code-block:: c++
   :name: ef_listing_populate_pass_node_registration
   :caption: Register ``TestPopulateInstances`` pass to run on every node named "my.special.node"

    OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS(TestPopulateInstances, "my.special.node");

We can also register the pass to run on nodes with a definition named "my.def.special" already attached to the node.

.. code-block:: c++
   :name: ef_listing_populate_pass_graph_registration
   :caption: Register ``TestPopulateInstances`` pass to run on every node with "my.def.special" definition attached

    OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS(TestPopulateInstances, "my.def.special");

Above, we see that the name given during registration can match either the node name or definition name.  See
:ref:`ef_pass_concepts` to better understand EF's algorithm for running population passes.

Implementing a Partition Pass
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example, we will be partitioning the following graph using either manual or automatic partition generation

.. literalinclude:: ../tests.cpp/TestPartitionPass.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs partition-example-begin
   :end-before: ef-docs partition-example-end
   :name: ef_listing_partition_pass_input
   :caption: An example input graph for partitioning passes


The task for our first partition pass will be to recognize two clusters of nodes *(B/Ax, B/Bx, B/Cx)* and *(Cx, Dx,
Ex)*, but not recognize *(H, J, K)* since node I causes the cluster to form a cycle after replacing. The following
implementation will do this manually from the ``run_abi()`` method.

.. literalinclude:: ../tests.cpp/TestPartitionPass.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs partition-manual-example-begin
   :end-before: ef-docs partition-manual-example-end
   :name: ef_listing_partition_pass_manual_example
   :caption: An example implementation of a partitioning pass forming clusters manually


Now let's implement the same partitioning strategy but leverage the |quickPartitioning()| utility to forming clusters.

.. literalinclude:: ../tests.cpp/TestPartitionPass.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs partition-auto-example-begin
   :end-before: ef-docs partition-auto-example-end
   :name: ef_listing_partition_pass_auto_example
   :caption: An example implementation of a partitioning pass forming clusters manually

Finally, we have to remember to register our new pass.

.. code-block:: c++
   :name: ef_listing_partition_pass_node_registration
   :caption: Register ``TestPartitionPassX`` pass with priority 1

    OMNI_GRAPH_EXEC_REGISTER_PARTITION_PASS(TestPartitionPassX, 1);

.. _implementing_global_pass:

Implementing a Global Pass
~~~~~~~~~~~~~~~~~~~~~~~~~~

Users are discouraged from authoring global passes as they can severely slow down graph construction and/or create
ordering issues if a specific execution order is required. For all these reasons, users should try implementing new
functionality with the pass types above rather than global passes.

The following is a complete implementation of a global pass that EF useds to detect cycles in the graph.

.. literalinclude:: ../plugins/PassStronglyConnectedComponents.h
   :language: c++
   :dedent:
   :start-after: ef-docs global-pass-scc-begin
   :end-before: ef-docs global-pass-scc-end
   :name: ef_listing_global_pass_scc
   :caption: The global pass used for detecting cycles in the execution graph.

Next Steps
~~~~~~~~~~

Pass creation is often the first step to adding new functionality to EF.  The next logical steps often involve
adding custom definitions, graph traversals, and executors. See :ref:`ef_definition_creation`,
:ref:`ef_graph_traversal_guide`, and :ref:`ef_executor_creation` for details.
