.. include:: Helpers.rst

.. _ef_debugging:

Debugging
#########

When things are not behaving as expected, it is good to start by understanding the topology of the execution graph.
As described in the :ref:`ef_graph_concepts` section, the execution graph is built of many nested graphs. The framework allows
you to visualize a flattened versions of this graph.

.. literalinclude:: ../tests.cpp/TestGraph.cpp
   :language: c++
   :start-after: ef-docs graph-dump-begin
   :end-before: ef-docs graph-dump-end

Graph utilities will traverse the entire topology of the graph and write it out to a given stream in GraphViz format. Below
is an interactive example of an execution graph. The `svg` file was generated using an `online editor <http://magjac.com/graphviz-visual-editor/>`_.

.. raw:: html
   :file: ef-debugging-serialization.svg

The output is flattened, which means that all instantiated |NodeGraphDef| are expanded in place. We use a small number
of colors to help visually distinguish nodes that are in the same topology. It also helps identify when two expanded
node graph definitions are references of the same definition in memory.
