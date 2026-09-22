.. include:: Helpers.rst

.. _ef_graph_invalidation:

Graph Invalidation
==================

|SHOW_ADVANCED_TOPIC_WARNING|

EF employs a fast, efficient, and lazy invalidation scheme to detect changes in the |execution graph|.  In this article,
we cover how a graph is invalidated, how it is marked valid, and the various entities used for invalidation.

.. _ef_stamps:

Stamps
##################

The heart of the invalidation system are EF's *stamps*.

Stamps track the state/version of a resource.  Stamps are implemented as an unsigned number.  If the state of a resource
changes, the stamp is incremented.

Stamps are broken into two parts.

The first part is implemented by the |Stamp| class.  As a resource changes, |Stamp::next()| is called to denote the new
state of the resource.  |Stamp| objects are owned by the resource they track.

The second part of stamps is implemented by the |SyncStamp| class.  |SyncStamp| tracks/synchronizes to the state of a
|Stamp|.  |SyncStamp| objects are owned by the entities that wish to utilize the mutating resource.

See |Stamp|'s documentation for further details.

EF makes extensive use of stamps to detect changes in pass registration, graph topology, and graph construction.

Invalidating a Graph
####################

Graph invalidation starts with a call to |ITopology::invalidate()|.  |ITopology| objects are owned by
|graph definitions|. Therefore, a call to |ITopology::invalidate()| is equivalent to saying "this |definition| is no
longer valid."

Unlike some other invalidation schemes, the call to |ITopology::invalidate()| is cheap.  If the |topology| is already
invalid (i.e. |ITopology::invalidate()| has previously been called and the |topology| has not yet be rebuilt),
invalidation exits early. Otherwise, the topology's |stamp| is incremented and the invalidation is "forwarded" to a
list of registered listeners.

This forwarding process may sound expensive.  In practice, it is not for the following reasons:

- As previously mentioned, |ITopology::invalidate()| detects spurious invalidations and performs an early exit.
- Invalidation forwarders do not immediately react to the invalidation (i.e. they do not immediately rebuild the
  |graph|). Rather, they are designed to note the invalidation and handle it later.  For example, rebuilding a graph
  definition is delayed until the start of the next execution of the |execution graph|.
- Usually only a single listener is registered per-|graph definition|.  That listener does not forward the invalidation.

The single invalidation forwarder mentioned above notifies the top-level execution graph (e.g. |IGraph|) that something
within the graph has become invalid.  It does this by incrementing the execution graph's |global topology stamp| via
|IGraph::getGlobalTopologyStamp()|.

.. _ef_global_topology_stamp:

Global Topology Stamp
#####################

The top-level |IGraph| object's global topology |stamp| tracks the validity of all |topologies| within all
|graph definitions| in the |execution graph|.  The |stamp| is incremented each time a graph definition's topology is
invalidated.

Use of this stamp usually falls into two categories.

The first category is cache invalidation.  As an example, |IExecutionContext| uses the global topology stamp to
determine if its cached list of traversed node paths is still valid.

The second category is detecting if the execution graph should be rebuilt. |IPassPipeline| uses the global topology
stamp to determine if the |pipeline|'s |passes| should run.  These passes |traverse| the entire execution graph,
looking for graph definition's whose topology is invalid.

This rebuild process is not a *full* rebuild of the execution graph.  Rather, because invalidation is tracked at the
graph definition level, only those |definitions| that have been invalidated need to be rebuilt.

Graph construction is covered in detail in :ref:`ef_pass_concepts`.

Making a Graph Valid
################################

The |ITopology| object stored in each |graph definition| (e.g. |INodeGraphDef|) has the concept of validity.  The
topology is marked invalid with |ITopology::invalidate()|.  |ITopology::invalidate()| is often called by the authoring
layer. For example, OmniGraph will call |ITopology::invalidate()| when a user connects two nodes.

The validity of a |topology| can be checked with |ITopology::isValid()|.  |ITopology::isValid()| is often used during
graph construction to determine if a |graph definition| needs to be rebuilt.

One of the |ITopology| object's jobs is to store and provide access to the |root node| of the |definition|.
|ITopology::isValid()| works by checking if the |root node|'s |SyncStamp| is synchronized with the topology's |Stamp|.

Once |ITopology::invalidate()| is called, the topology's root node stamp will be out-of-sync until
|INode::validateOrResetTopology()| is called on the root node. |INode::validateOrResetTopology()| is called during
graph construction, usually by |IGraphBuilder::connect()| when the root node is connected to a downstream |node|.  In
some cases, nothing connects to the root node and it is up to the |IPass| (usually via the constructed
graph definition) to call |INode::validateOrResetTopology()| on the root node.

Graph construction is covered in detail in :ref:`ef_pass_concepts`.
