.. include:: Helpers.rst

.. _ef_executor_creation:

Executor Creation
#################

|SHOW_GUIDE_WARNING|

Customizing execution can happen at many levels, let's have a look at different examples.

Customizing Visit Strategy
~~~~~~~~~~~~~~~~~~~~~~~~~~
The default |ExecutorFallback|'s visit strategy and execution order is matching traversal over the entire graph, where each node gets
computed only once when all upstream nodes complete computation. Without changing the traversal order, we can
change the visit strategy to only compute when the underlying node requests to compute.

.. literalinclude:: ../../../../include/omni/graph/exec/unstable/Executor.h
   :language: c++
   :dedent:
   :start-after: ef-docs execution-visit-cache-begin
   :end-before: ef-docs execution-visit-cache-end
   :name: ef_listing_execution_visit_cache
   :caption: A custom visit strategy for visiting only nodes that requested compute.

In this modified version, we will only compute a node and propagate this to the downstream when compute was requested.

Customizing Preallocated Per-node Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sometimes visit strategy must store more data per node to achieve the desired execution behavior.
We will use an example from a pipeline graph that dynamically generates more work based on data and a static graph.

.. literalinclude:: ../tests.cpp/graphs/TestPipelineGraph.h
   :language: c++
   :dedent:
   :start-after: ef-docs pipeline-graph-custom-data-begin
   :end-before: ef-docs pipeline-graph-custom-data-end
   :name: ef_listing_pipeline-graph-custom-data
   :caption: A custom data used by pipeline graph example.

.. literalinclude:: ../tests.cpp/graphs/TestPipelineGraph.h
   :language: c++
   :dedent:
   :start-after: ef-docs pipeline-graph-custom-visit-begin
   :end-before: ef-docs pipeline-graph-custom-visit-end
   :name: ef_listing_pipeline-graph-custom-visit
   :caption: A custom visit strategy for dynamically generating work.

Customizing Scheduler
~~~~~~~~~~~~~~~~~~~~~
The default |ExecutorFallback|'s scheduler will run all the generated tasks serially on a calling thread. We can easily
change that and request task dispatch from a custom scheduler.

.. literalinclude:: ../tests.cpp/TestUtils.h
   :language: c++
   :dedent:
   :start-after: ef-docs scheduler-custom-tbb-begin
   :end-before: ef-docs scheduler-custom-tbb-end
   :name: ef_listing_scheduler_custom_tbb
   :caption: A custom scheduler dispatch implementation to run all generated tasks concurrently.

Customizing Traversal
~~~~~~~~~~~~~~~~~~~~~
In all examples above, the executor was iterating over all children of a node and was able to stop dispatching the node
to compute. We can further customize the continuation loop over children of a node by overriding the |Executor::continueExecute()|
method. This ultimately allows us to change entire traversal behavior. In this final example, we will push this to the
end by also customizing |IExecutor::execute()| and delegating the entire execution to the implementation of |NodeDef|.
We will use Behavior Tree to illustrate it all. Make sure to follow examples from :ref:`ef_definition_creation` to learn
how |NodeGraphDef| were implemented.

.. literalinclude:: ../tests.cpp/graphs/TestBehaviorTree.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs behavior-graph-executor-begin
   :end-before: ef-docs behavior-graph-executor-end
   :name: ef_listing_behavior-graph-executor
   :caption: A custom executor for behavior tree.

.. literalinclude:: ../tests.cpp/graphs/TestBehaviorTree.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs behavior-graph-visit-begin
   :end-before: ef-docs behavior-graph-visit-end
   :name: ef_listing_behavior-graph-visit
   :caption: A custom visit strategy for behavior tree executor.

.. literalinclude:: ../tests.cpp/graphs/TestBehaviorTree.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs behavior-graph-sequence-node-begin
   :end-before: ef-docs behavior-graph-sequence-node-end
   :name: ef_listing_behavior-graph-sequence-node
   :caption: An example implementation of a node responsible to execute children and propagate the result.
