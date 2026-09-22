.. |Action Graph| replace:: `Action Graph <https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_omnigraph/tutorials/quickstart.html>`__
.. |BFS| replace:: :ref:`BFS <breadth_first_search>`
.. |Crash Reporter| replace:: :ref:`carbonite:crashreporter-label`
.. |Edges| replace:: :ref:`Edges <ef_edges>`
.. |Executor| replace:: :cpp:class:`Executor <omni::graph::exec::unstable::Executor>`
.. |Executor::execute()| replace:: :cpp:func:`Executor::execute() <omni::graph::exec::unstable::Executor::execute()>`

.. Executor continue() won't link.  using IExecutor instead
.. |Executor::continueExecute()| replace:: :cpp:func:`Executor::continueExecute(const ExecutionTask&) <omni::graph::exec::unstable::IExecutor::continueExecute()>`

.. |Executor::Info| replace:: :cpp:class:`Executor::Info <omni::graph::exec::unstable::Executor::Info>`
.. |DFS| replace:: :ref:`DFS <depth_first_search>`
.. |Definition| replace:: :ref:`Definition <ef_definition>`
.. |Definitions| replace:: :ref:`Definitions <ef_definition>`
.. |IDef| replace:: :cpp:class:`IDef <omni::graph::exec::unstable::IDef>`
.. |IBase| replace:: :cpp:class:`IBase <omni::graph::exec::unstable::IBase>`
.. |IBase::castWithoutAcquire()| replace:: :cpp:func:`IBase::castWithoutAcquire() <omni::graph::exec::unstable::IBase::castWithoutAcquire()>`
.. |IExecutionContext| replace:: :cpp:class:`IExecutionContext <omni::graph::exec::unstable::IExecutionContext>`
.. |IExecutionContext::execute()| replace:: :cpp:func:`IExecutionContext::execute() <omni::graph::exec::unstable::IExecutionContext::execute()>`
.. |IExecutionContext::getNodeData()| replace:: :cpp:func:`IExecutionContext::getNodeData() <omni::graph::exec::unstable::IExecutionContext::getNodeData()>`
.. |IExecutionCurrentThread| replace:: :cpp:class:`IExecutionCurrentThread <omni::graph::exec::unstable::IExecutionCurrentThread>`
.. |IExecutionCurrentThread::execute()| replace:: :cpp:func:`IExecutionCurrentThread::execute() <omni::graph::exec::unstable::IExecutionCurrentThread::execute()>`
.. |IExecutionCurrentThread::executeGraph()| replace:: :cpp:func:`IExecutionCurrentThread::executeGraph() <omni::graph::exec::unstable::IExecutionCurrentThread::executeGraph()>`
.. |IExecutionStateInfo| replace:: :cpp:class:`IExecutionStateInfo <omni::graph::exec::unstable::IExecutionStateInfo>`
.. |IExecutor| replace:: :cpp:class:`IExecutor <omni::graph::exec::unstable::IExecutor>`
.. |IExecutor::continueExecute()| replace:: :cpp:func:`IExecutor::continueExecute() <omni::graph::exec::unstable::IExecutor::continueExecute()>`
.. |IExecutor::execute()| replace:: :cpp:func:`IExecutor::execute() <omni::graph::exec::unstable::IExecutor::execute()>`
.. |IExecutor::schedule()| replace:: :cpp:func:`IExecutor::schedule(ScheduleFunction&&, SchedulingInfo) <omni::graph::exec::unstable::IExecutor::schedule()>`
.. |IGraph| replace:: :cpp:class:`IGraph <omni::graph::exec::unstable::IGraph>`
.. |IGraph::getGlobalTopologyStamp()| replace:: :cpp:func:`IGraph::getGlobalTopologyStamp() <omni::graph::exec::unstable::IGraph::getGlobalTopologyStamp()>`
.. |IGraphBuilder::connect()| replace:: :cpp:func:`IGraphBuilder::connect(INode*, INode*) <omni::graph::exec::unstable::IGraphBuilder::connect()>`
.. |INode| replace:: :cpp:class:`INode <omni::graph::exec::unstable::INode>`
.. |IPopulatePass::run()| replace:: :cpp:func:`IPopulatePass::run() <omni::graph::exec::unstable::IPopulatePass::run()>`
.. |INode::acquire()| replace:: :cpp:func:`INode::acquire() <omni::graph::exec::unstable::INode::acquire()>`
.. |INode::getChildren()| replace:: :cpp:func:`INode::getChildren() <omni::graph::exec::unstable::INode::getChildren()>`
.. |INode::getDef()| replace:: :cpp:func:`INode::getDef() <omni::graph::exec::unstable::INode::getDef()>`
.. |INode::getParents()| replace:: :cpp:func:`INode::getParents() <omni::graph::exec::unstable::INode::getParents()>`
.. |INode::validateOrResetTopology()| replace:: :cpp:func:`INode::validateOrResetTopology() <omni::graph::exec::unstable::INode::validateOrResetTopology()>`
.. |INodeDef| replace:: :cpp:class:`INodeDef <omni::graph::exec::unstable::INodeDef>`

.. INodeGraphDef execute() / getSchedulingInfo doesn't work so linking to IDef
.. |INodeDef::execute()| replace:: :cpp:func:`INodeDef::execute() <omni::graph::exec::unstable::IDef::execute()>`
.. |INodeDef::getSchedulingInfo()| replace:: :cpp:func:`INodeDef::getSchedulingInfo() <omni::graph::exec::unstable::IDef::getSchedulingInfo()>`

.. |INodeGraphDef| replace:: :cpp:class:`INodeGraphDef <omni::graph::exec::unstable::INodeGraphDef>`

.. INodeGraphDef execute() doesn't work so linking to IDef
.. |INodeGraphDef::execute()| replace:: :cpp:func:`INodeGraphDef::execute(ExecutionTask*) <omni::graph::exec::unstable::IDef::execute()>`

.. |INodeGraphDef::getTopology()| replace:: :cpp:func:`INodeGraphDef::getTopology() <omni::graph::exec::unstable::INodeGraphDef::getTopology()>`
.. |INodeGraphDef::preExecute()| replace:: :cpp:func:`INodeGraphDef::preExecute(ExecutionTask*) <omni::graph::exec::unstable::INodeGraphDef::preExecute>`
.. |INodeGraphDef::postExecute()| replace:: :cpp:func:`INodeGraphDef::postExecute(ExecutionTask*) <omni::graph::exec::unstable::INodeGraphDef::postExecute>`
.. |INodeGraphDef_abi| replace:: :cpp:class:`INodeGraphDef_abi <omni::graph::exec::unstable::INodeGraphDef_abi>`
.. |INodeGraphDefDebug| replace:: :cpp:class:`INodeGraphDefDebug <omni::graph::exec::unstable::INodeGraphDefDebug>`
.. |NodeGraphDefT| replace:: :cpp:class:`NodeGraphDefT <omni::graph::exec::unstable::NodeGraphDefT>`
.. |IObject::cast()| replace:: :cpp:func:`IObject::cast() <omni::core::IObject::cast()>`
.. |IPass| replace:: :cpp:class:`IPass <omni::graph::exec::unstable::IPass>`
.. |IPassPipeline| replace:: :cpp:class:`IPassPipeline <omni::graph::exec::unstable::IPassPipeline>`
.. |ITopology| replace:: :cpp:class:`ITopology <omni::graph::exec::unstable::ITopology>`
.. |ITopology::getRoot()| replace:: :cpp:func:`ITopology::getRoot() <omni::graph::exec::unstable::ITopology::getRoot()>`
.. |ITopology::invalidate()| replace:: :cpp:func:`ITopology::invalidate() <omni::graph::exec::unstable::ITopology::invalidate()>`
.. |ITopology::isValid()| replace:: :cpp:func:`ITopology::isValid() <omni::graph::exec::unstable::ITopology::isValid()>`
.. |ExecutorFactory| replace:: :cpp:type:`ExecutorFactory <omni::graph::exec::unstable::ExecutorFactory>`
.. |ExecutorFallback| replace:: :cpp:type:`ExecutorFallback <omni::graph::exec::unstable::ExecutorFallback>`
.. |ExecutionPath| replace:: :cpp:class:`ExecutionPath <omni::graph::exec::unstable::ExecutionPath>`
.. |ExecutionContext| replace:: :cpp:class:`ExecutionContext <omni::graph::exec::unstable::ExecutionContext>`
.. |ExecutionContext::execute()| replace:: :cpp:func:`ExecutionContext::execute() <omni::graph::exec::unstable::IExecutionContext::execute()>`
.. |ExecutionStateInfo| replace:: :cpp:class:`ExecutionStateInfo <omni::graph::exec::unstable::IExecutionStateInfo>`
.. |ExecutionTask| replace:: :cpp:class:`ExecutionTask <omni::graph::exec::unstable::ExecutionTask>`
.. |ExecutionTask::getContext()| replace:: :cpp:func:`ExecutionTask::getContext() <omni::graph::exec::unstable::ExecutionTask::getContext()>`
.. |ExecutionTask::execute()| replace:: :cpp:func:`ExecutionTask::execute(IExecutor&) <omni::graph::exec::unstable::ExecutionTask::execute()>`
.. |ExecutionTask::getNode()| replace:: :cpp:func:`ExecutionTask::getNode() <omni::graph::exec::unstable::ExecutionTask::getNode()>`
.. |ExecutionTask::getTag()| replace:: :cpp:func:`ExecutionTask::getTag() <omni::graph::exec::unstable::ExecutionTask::getTag()>`
.. |ExecutionTask::getUpstreamPath()| replace:: :cpp:func:`ExecutionTask::getUpstreamPath() <omni::graph::exec::unstable::ExecutionTask::getUpstreamPath()>`
.. |ExecutionVisit| replace:: :cpp:class:`ExecutionVisit <omni::graph::exec::unstable::ExecutionVisit>`
.. |ExecStrategy| replace:: ``ExecStrategy``
.. |ExecStrategy::tryVisit()| replace:: ``ExecStrategy::tryVisit()``
.. |Graph| replace:: :cpp:class:`Graph <omni::graph::exec::unstable::GraphT\<\>>`
.. |Graph::execute()| replace:: :cpp:func:`Graph::execute(IExecutionContext*) <omni::graph::exec::unstable::IGraph::execute>`
.. |GraphBuilderContext| replace:: :cpp:class:`GraphBuilderContext <omni::graph::exec::unstable::GraphBuilderContextT\<\>>`
.. |GraphBuilder| replace:: :cpp:class:`GraphBuilder <omni::graph::exec::unstable::GraphBuilderT\<\>>`
.. |Graph Definitions| replace:: :ref:`Graph Definitions <ef_graph_definition>`
.. |IGraphBuilderNode| replace:: :cpp:class:`IGraphBuilderNode <omni::graph::exec::unstable::IGraphBuilderNode\<\>>`
.. |Kit| replace:: `Kit <https://docs.omniverse.nvidia.com/prod_kit/prod_kit/kit-architecture.html>`__
.. |Kit SDK| replace:: `Kit SDK <https://docs.omniverse.nvidia.com/prod_kit/prod_kit/kit-architecture.html>`__
.. |Kit Extensions| replace:: `Kit Extensions <https://docs.omniverse.nvidia.com/prod_kit/prod_kit/extensions.html>`__
.. |Node| replace:: :cpp:class:`Node <omni::graph::exec::unstable::NodeT<omni::graph::exec::unstable::INode, omni::graph::exec::unstable::IGraphBuilderNode>>`
.. |Nodes| replace:: :ref:`Nodes <ef_nodes>`
.. |NodeDef| replace:: :cpp:class:`NodeDef <omni::graph::exec::unstable::NodeDefT<omni::graph::exec::unstable::INodeDef>>`

..  shouldn't link to IDef::execute
.. |NodeDef::execute()| replace:: :cpp:func:`NodeDef::execute(ExecutionTask*) <omni::graph::exec::unstable::IDef::execute()>`

.. |NodeDefLambda| replace:: :cpp:class:`NodeDefLambda <omni::graph::exec::unstable::NodeDefLambda>`
.. |NodeDefLambda::create()| replace:: :cpp:func:`NodeDefLambda::create() <omni::graph::exec::unstable::NodeDefLambda::create()>`
.. |NodeGraphDef| replace:: :cpp:class:`NodeGraphDef <omni::graph::exec::unstable::INodeGraphDef>`
.. |NodeGraphDef::preExecute()| replace:: :cpp:func:`NodeGraphDef::preExecute(ExecutionTask*) <omni::graph::exec::unstable::INodeGraphDef::preExecute>`

..  shouldn't link to IDef::execute
.. |NodeGraphDef::execute()| replace:: :cpp:func:`NodeGraphDef::execute(ExecutionTask*) <omni::graph::exec::unstable::IDef::execute()>`

.. |NodeGraphDef::postExecute()| replace:: :cpp:func:`NodeGraphDef::postExecute(ExecutionTask*) <omni::graph::exec::unstable::INodeGraphDef::postExecute>`
.. |OMNI_GRAPH_EXEC_ASSERT()| replace:: :c:macro:`OMNI_GRAPH_EXEC_ASSERT() <OMNI_GRAPH_EXEC_ASSERT()>`
.. |OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG()| replace:: :c:macro:`OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG() <OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG()>`
.. |OMNI_GRAPH_EXEC_FATAL_UNLESS()| replace:: :c:macro:`OMNI_GRAPH_EXEC_FATAL_UNLESS() <OMNI_GRAPH_EXEC_FATAL_UNLESS()>`
.. |OMNI_GRAPH_EXEC_REGISTER_GLOBAL_PASS()| replace:: :c:macro:`OMNI_GRAPH_EXEC_REGISTER_GLOBAL_PASS() <OMNI_GRAPH_EXEC_REGISTER_GLOBAL_PASS()>`
.. |OMNI_GRAPH_EXEC_REGISTER_PARTITION_PASS()| replace:: :c:macro:`OMNI_GRAPH_EXEC_REGISTER_PARTITION_PASS() <OMNI_GRAPH_EXEC_REGISTER_PARTITION_PASS()>`
.. |OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS()| replace:: :c:macro:`OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS() <OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS()>`
.. |OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED()| replace:: :cpp:any:`OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED() <OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED()>`
.. |ObjectPtr| replace:: :cpp:class:`ObjectPtr <omni::core::ObjectPtr>`
.. |Omniverse| replace:: `Omniverse <https://www.nvidia.com/en-us/omniverse/>`__
.. |Omniverse Kit| replace:: `Omniverse Kit <https://docs.omniverse.nvidia.com/prod_kit/prod_kit/kit-architecture.html>`__
.. |Omniverse Native Interfaces| replace:: :doc:`Omniverse Native Interfaces <carbonite:docs/OmniverseNativeInterfaces>`
.. |Omniverse USD Composer| replace:: `Omniverse USD Composer <https://www.nvidia.com/en-us/omniverse/apps/create>`__
.. |OmniGraph| replace:: `OmniGraph <https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_omnigraph.html>`__
.. |Opaque Definitions| replace:: :ref:`Opaque Definitions <ef_opaque_definition>`
.. |ParallelSpawner| replace:: :cpp:class:`ParallelSpawner <omni::graph::exec::unstable::ParallelSpawner>`
.. |PartitionPass| replace:: :cpp:class:`PartitionPass <omni::graph::exec::unstable::IPartitionPass>`
.. |PassPipeline| replace:: :cpp:class:`PassPipeline <omni::graph::exec::unstable::PassPipelineT>`
.. |PassRegistry| replace:: :cpp:class:`PassRegistry <omni::graph::exec::unstable::IPassRegistry>`
.. |PassType| replace:: :cpp:enum:`PassType <omni::graph::exec::unstable::PassType>`
.. |PhysX| replace:: `PhysX <https://developer.nvidia.com/physx-sdk>`__
.. |PopulatePass| replace:: :cpp:class:`PopulatePass <omni::graph::exec::unstable::IPopulatePass>`
.. |IPopulatePass| replace:: :cpp:class:`IPopulatePass <omni::graph::exec::unstable::IPopulatePass>`
.. |IPartitionPass| replace:: :cpp:class:`IPartitionPass <omni::graph::exec::unstable::IPartitionPass>`
.. |IGlobalPass| replace:: :cpp:class:`IGlobalPass <omni::graph::exec::unstable::IGlobalPass>`
.. |Root Nodes| replace:: :ref:`Root Nodes <ef_root_node>`
.. |SerialScheduler| replace:: :cpp:class:`SerialScheduler <omni::graph::exec::unstable::SerialScheduler>`
.. |Scheduler| replace:: ``Scheduler``
.. |Scheduler::scheduleDeferred()| replace:: ``Scheduler::scheduleDeferred()``
.. |SchedulingInfo| replace:: :cpp:enum:`SchedulingInfo <omni::graph::exec::unstable::SchedulingInfo>`
.. |SchedulingStrategy| replace:: ``SchedulingStrategy``
.. |Stamp| replace:: :cpp:type:`Stamp <omni::graph::exec::unstable::Stamp>`
.. |Stamp::next()| replace:: :cpp:func:`Stamp::next() <omni::graph::exec::unstable::Stamp::next()>`
.. |Status| replace:: :cpp:enum:`Status <omni::graph::exec::unstable::Status>`
.. |SyncStamp| replace:: :cpp:type:`SyncStamp <omni::graph::exec::unstable::SyncStamp>`
.. |USD Composer| replace:: `USD Composer <https://www.nvidia.com/en-us/omniverse/apps/create>`__
.. |USD| replace:: `USD <https://developer.nvidia.com/usd>`__
.. |RTX| replace:: `RTX <https://www.nvidia.com/en-us/design-visualization/technologies/rtx/>`__

.. |eSerial| replace:: :cpp:enumerator:`SchedulingInfo::eSerial <omni::graph::exec::unstable::SchedulingInfo::eSerial>`
.. |eParallel| replace:: :cpp:enumerator:`SchedulingInfo::eParallel <omni::graph::exec::unstable::SchedulingInfo::eParallel>`
.. |eMainThread| replace:: :cpp:enumerator:`SchedulingInfo::eMainThread <omni::graph::exec::unstable::SchedulingInfo::eMainThread>`
.. |eIsolate| replace:: :cpp:enumerator:`SchedulingInfo::eIsolate <omni::graph::exec::unstable::SchedulingInfo::eIsolate>`
.. |eSchedulerBypass| replace:: :cpp:enumerator:`SchedulingInfo::eSchedulerBypass <omni::graph::exec::unstable::SchedulingInfo::eSchedulerBypass>`

.. |eDeferred| replace:: :cpp:enumerator:`Status::eDeferred <omni::graph::exec::unstable::Status::eDeferred>`
.. |eSkip| replace:: :cpp:enumerator:`Status::eSkip <omni::graph::exec::unstable::Status::eSkip>`
.. |eSuccess| replace:: :cpp:enumerator:`Status::eSuccess <omni::graph::exec::unstable::Status::eSuccess>`


.. |behavior tree| replace:: `behavior tree <https://www.gamedeveloper.com/programming/behavior-trees-for-ai-how-they-work>`__
.. |behavior trees| replace:: `behavior trees <https://www.gamedeveloper.com/programming/behavior-trees-for-ai-how-they-work>`__
.. |VisitFirst| replace:: :cpp:struct:`VisitFirst <omni::graph::exec::unstable::detail::VisitFirst>`
.. |VisitLast| replace:: :cpp:struct:`VisitLast <omni::graph::exec::unstable::detail::VisitLast>`
.. |VisitAll| replace:: :cpp:struct:`VisitAll <omni::graph::exec::unstable::detail::VisitAll>`
.. |PassStronglyConnectedComponents| replace:: :cpp:class:`PassStronglyConnectedComponents <omni::graph::exec::unstable::PassStronglyConnectedComponents>`
.. |IExecutionContext::applyOnEachDef_abi()| replace:: :cpp:func:`IExecutionContext::applyOnEachDef_abi() <omni::graph::exec::unstable::IExecutionContext::applyOnEachDef_abi()>`
.. |IExecutionContext::applyOnEachDefWithName_abi()| replace:: :cpp:func:`IExecutionContext::applyOnEachDefWithName_abi() <omni::graph::exec::unstable::IExecutionContext::applyOnEachDefWithName_abi()>`
.. |Executor::continueExecute_abi()| replace:: :cpp:func:`Executor::continueExecute_abi() <omni::graph::exec::unstable::Executor::continueExecute_abi()>`
.. |_runPopulatePass()| replace:: :cpp:func:`_runPopulatePass() <omni::graph::exec::unstable::_runPopulatePass()>`
.. |Traversal| replace:: :cpp:class:`Traversal <omni::graph::exec::unstable::Traversal>`

.. |breadth-first| replace:: :ref:`breadth-first <breadth_first_search>`
.. |carb::allocate()| replace:: :cpp:func:`carb::allocate() <carb::allocate()>`
.. |definition| replace:: :ref:`definition <ef_definition>`
.. |definitions| replace:: :ref:`definitions <ef_definition>`
.. |depth-first| replace:: :ref:`depth-first <depth_first_search>`
.. |dynamic_cast| replace:: `dynamic_cast <https://en.cppreference.com/w/cpp/language/dynamic_cast>`__
.. |edge| replace:: :ref:`edge <ef_edges>`
.. |edges| replace:: :ref:`edges <ef_edges>`
.. |executor| replace:: :ref:`executor <ef_executor>`
.. |executors| replace:: :ref:`executors <ef_executor>`
.. |execution| replace:: :ref:`execution <ef_execution_concepts>`
.. |execution graph| replace:: :ref:`execution graph <ef_execution_graph>`
.. |extension| replace:: `extension <https://docs.omniverse.nvidia.com/prod_kit/prod_kit/extensions.html>`__
.. |extensions| replace:: `extensions <https://docs.omniverse.nvidia.com/prod_kit/prod_kit/extensions.html>`__
.. |getCurrentExecutor()| replace:: :cpp:func:`getCurrentExecutor() <omni::graph::exec::unstable::getCurrentExecutor()>`
.. |getCurrentTask()| replace:: :cpp:func:`getCurrentTask() <omni::graph::exec::unstable::getCurrentTask()>`
.. |getPassRegistry()| replace:: :cpp:func:`getPassRegistry() <omni::graph::exec::unstable::getPassRegistry()>`
.. |std::malloc()| replace:: `std::malloc() <https://en.cppreference.com/w/cpp/memory/c/malloc>`__
.. |new| replace:: `new <https://en.cppreference.com/w/cpp/language/new>`__
.. |node| replace:: :ref:`node <ef_nodes>`
.. |nodes| replace:: :ref:`nodes <ef_nodes>`
.. |noexcept| replace:: `noexcept <https://en.cppreference.com/w/cpp/language/noexcept_spec>`__
.. |omni.graph.action| replace:: *omni.graph.action*
.. |omni.graph.core| replace:: *omni.graph.core*
.. |omni.graph.exec| replace:: *omni.graph.exec*
.. |omni.kit.exec.core| replace:: *omni.kit.exec.core*
.. |omni::core::ITypeFactory| replace:: :cpp:class:`omni::core::ITypeFactory <omni::core::ITypeFactory>`
.. |omni::core::Result| replace:: :cpp:type:`omni::core::Result <omni::core::Result>`
.. |omni::core::kResultNotFound| replace:: :cpp:var:`omni::core::kResultNotFound <omni::core::kResultNotFound>`
.. |omni::core::steal()| replace:: :cpp:func:`omni::core::steal() <omni::core::steal()>`
.. |omni::expected| replace:: :cpp:class:`omni::expected <omni::expected>`
.. |omni::graph::action| replace:: *omni::graph::action*
.. |omni::graph::core| replace:: *omni::graph::core*
.. |omni::graph::exec| replace:: *omni::graph::exec*
.. |omni::graph::exec::unstable| replace:: *omni::graph::exec::unstable*
.. |omni::graph::exec::unstable::cast()| replace:: :cpp:func:`omni::graph::exec::unstable::cast() <omni::graph::exec::unstable::cast()>`
.. |omni::kit::exec::core| replace:: *omni::kit::exec::core*
.. |opaque| replace:: :ref:`opaque<ef_opaque_definition>`
.. |opaque definition| replace:: :ref:`opaque definition <ef_opaque_definition>`
.. |opaque definitions| replace:: :ref:`opaque definitions <ef_opaque_definition>`
.. |pass pipeline| replace:: :cpp:class:`pass pipeline <omni::graph::exec::unstable::IPassPipeline>`
.. |passes| replace:: :ref:`passes <ef_pass_concepts>`
.. |path| replace:: :cpp:class:`path <omni::graph::exec::unstable::ExecutionPath>`
.. |pipeline| replace:: :ref:`pipeline <ef_pass_concepts>`
.. |plugins| replace:: :ref:`plugins <ef_plugin_creation>`
.. |population pass| replace:: :cpp:class:`population pass <omni::graph::exec::unstable::IPopulatePass>`
.. |global topology stamp| replace:: :ref:`global topology stamp <ef_global_topology_stamp>`
.. |graph| replace:: :ref:`graph <ef_graph_definition>`
.. |graphs| replace:: :ref:`graphs <ef_graph_definition>`
.. |graph construction| replace:: :ref:`graph construction <ef_pass_concepts>`
.. |graph definition| replace:: :ref:`graph definition <ef_graph_definition>`
.. |graph definitions| replace:: :ref:`graph definitions <ef_graph_definition>`
.. |invalidate| replace:: :ref:`invalidate <ef_graph_invalidation>`
.. |invalidated| replace:: :ref:`invalidated <ef_graph_invalidation>`
.. |invalidation| replace:: :ref:`invalidation <ef_graph_invalidation>`
.. |quickPartitioning()| replace:: :cpp:func:`quickPartitioning() <omni::graph::exec::unstable::quickPartitioning()>`
.. |root node| replace:: :ref:`root node <ef_root_node>`
.. |scheduler| replace:: :ref:`scheduler <ef_execution_concepts>`
.. |scheduling| replace:: :ref:`scheduling <ef_execution_concepts>`
.. |std::terminate()| replace:: `std::terminate() <https://en.cppreference.com/w/cpp/error/terminate>`__
.. |std::unexpected()| replace:: `std::unexpected() <https://en.cppreference.com/w/cpp/error/unexpected>`__
.. |root nodes| replace:: :ref:`root nodes <ef_root_node>`
.. |stamp| replace:: :ref:`stamps <ef_stamps>`
.. |stamps| replace:: :ref:`stamps <ef_stamps>`
.. |topology| replace:: :ref:`topology <ef_topology>`
.. |topologies| replace:: :ref:`topologies <ef_topology>`
.. |transformation| replace:: :ref:`transformation <ef_pass_concepts>`
.. |transformations| replace:: :ref:`transformations <ef_pass_concepts>`
.. |traversal| replace:: :ref:`traversal <ef_graph_traversal_guide>`
.. |traversals| replace:: :ref:`traversals <ef_graph_traversal_guide>`
.. |traverse| replace:: :ref:`traverse <ef_graph_traversal_guide>`
.. |traverseBreadthFirst| replace:: :cpp:func:`traverseBreadthFirst() <omni::graph::exec::unstable::traverseBreadthFirst()>`
.. |traverseBreadthFirstAsync| replace:: :cpp:func:`traverseBreadthFirstAsync() <omni::graph::exec::unstable::traverseBreadthFirstAsync()>`
.. |traverseDepthFirst| replace:: :cpp:func:`traverseDepthFirst() <omni::graph::exec::unstable::traverseDepthFirst()>`
.. |traverseDepthFirstAsync| replace:: :cpp:func:`traverseDepthFirstAsync() <omni::graph::exec::unstable::traverseDepthFirstAsync()>`
.. |traverses| replace:: :ref:`traverses <ef_graph_traversal_guide>`

.. |serial| replace:: :ref:`serial <serial_graph_traversal>`
.. |Serial| replace:: :ref:`Serial <serial_graph_traversal>`
.. |parallel| replace:: :ref:`parallel <parallel_graph_traversal>`
.. |Parallel| replace:: :ref:`Parallel <parallel_graph_traversal>`

.. |SHOW_ADVANCED_TOPIC_WARNING| replace:: *This is an advanced Execution Framework topic.  It is recommended you first review the* :ref:`ef_framework` *along with basic topics such as* :ref:`Graphs Concepts <ef_graph_concepts>`, :ref:`Pass Concepts <ef_pass_concepts>`, *and* :ref:`Execution Concepts <ef_execution_concepts>`.

.. |SHOW_GUIDE_WARNING| replace:: *This is a practitioner's guide to using the Execution Framework. Before continuing, it is recommended you first review the* :ref:`ef_framework` *along with basic topics such as* :ref:`Graphs Concepts <ef_graph_concepts>`, :ref:`Pass Concepts <ef_pass_concepts>`, *and* :ref:`Execution Concepts <ef_execution_concepts>`.
