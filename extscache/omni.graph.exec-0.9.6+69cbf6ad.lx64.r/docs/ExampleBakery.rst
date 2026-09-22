.. include:: Helpers.rst

.. |BakeryGraphDef| replace:: :ref:`BakeryGraphDef <ef_listing_bakery_bakerygraphdef>`
.. |PreHeatOvenNodeDef| replace:: :ref:`PreHeatOvenNodeDef <ef_listing_bakery_preheatovennodedef>`
.. |PrepareBakedGoodGraphDef| replace:: :ref:`PrepareBakedGoodGraphDef <ef_listing_bakery_preparebakedgoodgraphdef>`
.. |PopulateChickenPotPiePass| replace:: :ref:`PopulateChickenPotPiePass <ef_listing_bakery_populatechickenpotpiepass>`
.. |IPrivateBakedGoodGetter| replace:: :ref:`IPrivateBakedGoodGetter <ef_listing_bakery_iprivatebakedgoodgetter>`
.. |PopulatePiePass| replace:: :ref:`PopulatePiePass <ef_listing_bakery_populatepiepass>`

.. _ef_example_the_bakery:

Integrating an Authoring Layer
------------------------------

In this article, a toy example using the Execution Framework is used to describe an online bakery.  While the simplistic
subject matter of the example is contrived, the concepts demonstrated in the example have real-world applications.

The article is structured such that the example starts simple, and new concepts are introduced piecemeal.

The Authoring Layer
===================

The Execution Framework, in particular the |execution graph|, is a common language to describe execution across
disparate software components.  It is the job of each component (or an intermediary) to populate the execution graph
based on some internal description.  We call this per-component, internal description the *authoring layer*.  It is
common to have multiple different authoring layers contribute to a single execution graph.

This example demonstrate a single authoring layer that describes several online bakeries.  The data structures used by
this authoring layer is as follows:

.. literalinclude:: ../tests.cpp/TestBakeryDocs.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs bakery_authoring_structs_begin
   :end-before: ef-docs bakery_authoring_structs_end
   :name: ef_listing_bakery_authoring_structs
   :caption: Data structures used in the authoring layer to describe each bakery.

The example starts by describing two bakeries at the authoring layer:

.. literalinclude:: ../tests.cpp/TestBakeryDocs.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs bakery_multiple_code_begin
   :end-before: ef-docs bakery_multiple_code_end
   :name: ef_listing_bakery_multiple_code
   :caption: Authoring layer code that describes the orders for two bakeries.

Setting Up the Execution Graph
==============================

With the authoring layer defined, the following code is then used to populate the execution graph based on the authoring
layer description:

.. literalinclude:: ../tests.cpp/TestBakeryDocs.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs bakery_multiple_populate_begin
   :end-before: ef-docs bakery_multiple_populate_end
   :name: ef_listing_bakery_multiple_populate
   :caption: Top-level code to populate the execution graph from the authoring layer's description.

The execution graph can be visualized as follows:

.. mermaid:: bakery-multiple.mmd
    :align: center
    :caption: The execution graph showing both bakeries.  Arrows with solid lines represent orchestration ordering while arrows with dotted lines represent the |definition| a |node| is using.

You can see the execution graph has several types of entities:

- |Nodes| are represented by rounded boxes.  Their name starts with "*node.*".
- |Opaque Definitions| are represented by angled boxes.  Their name starts with "*def.*".
- |Graph Definitions| are represented by shaded boxes.  Their name, at the top of the box, starts with "*def.*".
- |Root Nodes| are represented by circles.  Their name is not shown.
- |Edges|, represented by an arrow with a solid line, show the orchestration ordering between nodes.
- Each node points to a |definition|, either an |opaque definition| or a |graph definition|.  This relationship is
  represented by an arrow with a dotted line.  Note, definitions can be pointed to by multiple nodes, though this
  example does not utilize the definition sharing feature of EF.

To simplify the example, this article focuses on a single bakery.  Below, you can see a visualization of only *The Pie
Hut*'s graph definition:

.. _ef_figure_bakery_simplified:

.. mermaid:: bakery-simplified.mmd
    :align: center
    :caption: Above, only the graph definition (*def.bakery*) describing "The Pie Hut" is shown.  To simplify the example, only this part of the execution graph will be shown in the following figures.

Building a Graph Definition
===========================

When creating the execution graph, most of the work is done in |BakeryGraphDef|, which is defined as follows:

.. literalinclude:: ../tests.cpp/TestBakeryDocs.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs bakery_bakerygraphdef_begin
   :end-before: ef-docs bakery_bakerygraphdef_end
   :name: ef_listing_bakery_bakerygraphdef
   :caption: An implementation of |INodeGraphDef| that represents a bakery.

In :numref:`ef_figure_bakery_simplified`, you can see:

- Preparation of the ingredients can run concurrently with pre-heating the oven.
- Once pre-heating and ingredient preparation has completed, the goods are baked in parallel.
- Once all goods in an order have baked, they are shipped to the customer.
- Once all goods across all orders have finished baking, the oven is turned off.  This action can happen in parallel
  with shipping the goods.

There are two types of definitions seen in the graph: |graph definitions| and |opaque definitions|.

Opaque Definitions
~~~~~~~~~~~~~~~~~~

Opaque definitions are represented by angled boxes.  An example of an opaque definition is the definition used to
pre-heat the oven:

.. literalinclude:: ../tests.cpp/TestBakeryDocs.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs bakery_preheatovennodedef_begin
   :end-before: ef-docs bakery_preheatovennodedef_end
   :name: ef_listing_bakery_preheatovennodedef
   :caption: An example of an opaque definition used to pre-heat the oven.

The two main methods to overload are |INodeDef::execute()| and |INodeDef::getSchedulingInfo()|.  |INodeDef::execute()|
performs the definition's work while |INodeDef::getSchedulingInfo()| provides hints to EF about how to schedule the
work.

Because this is an example, the work performed in |PreHeatOvenNodeDef| is trivial.  When performing uncomplicated work,
developers are often better served using |NodeDefLambda::create()| which accepts a lambda, a |SchedulingInfo| object,
and produces an |INodeDef| object.  See the ``bake`` node in |BakeryGraphDef| for an example use of |NodeDefLambda|.

Creating an opaque definition by sub-classing from |NodeDef| (e.g. |PreHeatOvenNodeDef|) is useful when:

- The developer wishes to provide additional methods on the definition.
- The opaque definition needs to store authoring data whose ownership and lifetime can't be adequately captured in the
  lambda provided to |NodeDefLambda|.

Graph Definitions
~~~~~~~~~~~~~~~~~~

The second type of definitions seen in :numref:`ef_figure_bakery_simplified` are graph definitions.  Graph definitions
are represented by shaded boxes.  Each graph definition has a root node, represented by a circle.  In
:numref:`ef_figure_bakery_simplified`, there is one type of graph definition: ``PrepareBakedGoodGraphDef``.

Here, you can see the code behind ``PrepareBakedGoodGraphDef``:

.. literalinclude:: ../tests.cpp/TestBakeryDocs.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs bakery_preparebakedgoodgraphdef_begin
   :end-before: ef-docs bakery_preparebakedgoodgraphdef_end
   :name: ef_listing_bakery_preparebakedgoodgraphdef
   :caption: An example of a graph definition used to prepare a baked good.

|PrepareBakedGoodGraphDef| creates a simple graph with two opaque nodes, one which gathers all of the ingredients of the
baked good and another which assembles the baked good.

Population Passes
=================

A powerful feature in EF are |passes|.  Passes are user created chunks of code that transform the graph during |graph
construction|.  As an example, an oft performed transformation is one in which a generic graph definition is replaced
with an optimized user defined graph definition.

:numref:`ef_figure_bakery_simplified` shows *node.bakedGood.prepare.chickenPotPie* has a fairly generic graph
definition.  An opportunity exists to replace this definition with one which can prepare ingredients in parallel.  To do
this, a |population pass| is used:

.. literalinclude:: ../tests.cpp/TestBakeryDocs.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs bakery_populatechickenpotpiepass_begin
   :end-before: ef-docs bakery_populatechickenpotpiepass_end
   :name: ef_listing_bakery_populatechickenpotpiepass
   :caption: The ``PopulateChickenPotPiePass`` is a population pass which replaces the generic baked good preparation definition with one which optimizes the preparation of chicken pot pie.

Population passes are registered via |OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS()|.  The registration processes requires
supplying a name the pass will match.  In this example, the name to match when registering |PopulateChickenPotPiePass|
is "node.bakedGood.prepare.chickenPotPie".

Passes are run by the application's |PassPipeline|.  The default |PassPipeline| will match the population pass against
the node's name.  If a node's name does not match, the |PassPipeline| will check if a *graph definition* is attached to
the node and see if the graph definition's name matches.  For more details on how passes are applied, see
:ref:`ef_pass_concepts`.

.. _ef_private_interfaces:

Private Interfaces
~~~~~~~~~~~~~~~~~~

Above, the population pass first checks if the given node's definition implements the ``IPrivateBakedGoodGetter``
interface.  That interface is defined as follows:

.. literalinclude:: ../tests.cpp/TestBakeryDocs.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs bakery_iprivatebakedgoodgetter_begin
   :end-before: ef-docs bakery_iprivatebakedgoodgetter_end
   :name: ef_listing_bakery_iprivatebakedgoodgetter
   :caption: The ``IPrivateBakedGoodGetter`` allows the bakery library to safely access private implementation details via EF.

|IPrivateBakedGoodGetter| is an example of a *private interface*.  Private interfaces are often used in graph
construction and graph execution to safely access non-public implementation details.

To understand the need of private interfaces, consider what the ``run_abi()`` method is doing in
:numref:`ef_listing_bakery_populatechickenpotpiepass`.  The purpose of the method is to replace the generic "prepare"
graph definition with a higher-fidelity graph definition specific to the preparation of chicken pot pie.  In order to
build that new definition, parameters in the chicken pot pie's ``BakedGood`` object are needed.  Therein lies the
problem: EF has no concept of a "baked good".  The population pass is only given a pointer to an |INode| EF interface.
With that pointer, the pass is able to get yet another EF interface, |IDef|.  Neither of these interfaces have a clue
what a ``BakedGood`` is.  So, how does one go about getting a ``BakedGood`` from an |INode|?

The answer lies in the type casting mechanism |Omniverse Native Interfaces| provides.  The idea is simple, when creating
a definition (e.g. |PrepareBakedGoodGraphDef| or ``ChickenPotPieGraphDef``), do the following:

- Store a reference to the baked good on the definition.
- In addition to implementing the |INodeGraphDef| interface, also implement the |IPrivateBakedGoodGetter| private
  interface.

To demonstrate the latter point, consider the code used to define the ``ChickenPotPieGraphDef`` class used in the
population pass:

.. literalinclude:: ../tests.cpp/TestBakeryDocs.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs bakery_chickenpotpiegraphdef_decl_begin
   :end-before: ef-docs bakery_chickenpotpiegraphdef_decl_end
   :name: ef_listing_bakery_chickenpotpiegraphdef_decl
   :caption: EF's |NodeGraphDefT| provides a default implementation of |INodeGraphDef| and |INodeGraphDefDebug| while allowing users to implement additional interfaces.

|NodeGraphDefT| is an implementation of |INodeGraphDef| and |INodeGraphDefDebug|.  |NodeGraphDefT|'s template arguments
allow the developer to specify all of the interfaces the subclass will implement, including interfaces EF has no notion
about (e.g. |IPrivateBakedGoodGetter|).  Recall, much like ``ChickenPotPieGraphDef``, |PrepareBakedGoodGraphDef|'s
implementation also inherits from |NodeGraphDefT| and specifies |IPrivateBakedGoodGetter| as a template argument.

To access the ``BakedGood`` from the given |INode|, the population pass calls |omni::graph::exec::unstable::cast()| on
the node's definition.  If the definition implements |IPrivateBakedGoodGetter|, a valid pointer is returned, on which
``getBakedGood()`` can be called.  With the ``BakedGood`` in hand, it can be used to create the new
``ChickenPotPieGraphDef`` graph definition, which the builder attaches to the node, replacing the generic graph
definition.

Why Not Use dynamic_cast?
^^^^^^^^^^^^^^^^^^^^^^^^^

A valid question that may arise from the code above is, "Why not use |dynamic_cast|?"  There are two things to note
about |dynamic_cast|:

- |dynamic_cast| is not ABI-safe.  Said differently, different compilers may choose to implement its ABI differently.
- |dynamic_cast| relies on runtime type information (RTTI).  When compiling C++, RTTI is an optional feature that can be
  disabled.

In :numref:`ef_listing_bakery_populatechickenpotpiepass`, ``run_abi()``'s' |INode| pointer (and its attached |IDef|) may
point to an object implemented by a DLL different than the DLL that implements the population pass. That means if
|dynamic_cast| is called on the pointer, the compiler will assume the pointer utilizes its |dynamic_cast| ABI contract.
However, since the pointer is from another DLL, possibly compiled with a different ABI and compiler settings, that
assumption may be bad, leading to undefined behavior.

In contrast to |dynamic_cast|, |omni::graph::exec::unstable::cast()| is ABI-safe due to its use of |Omniverse Native
Interfaces| (ONI).  ONI defines iron-clad, ABI-safe contracts that work across different compiler tool chains.  Calling
|omni::graph::exec::unstable::cast()| on an ONI object (e.g. |IDef|) has predictable behavior regardless of the compiler
and compiler settings used to compile the object.

Private vs. Public Interfaces
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ONI objects are designed to be ABI-safe.  However, it is clear that |IPrivateBakedGoodGetter| is not ABI-safe.
``getBakedGood()`` returns a reference, which is not allowed by ONI.  Furthermore, the returned object, ``BakedGood``,
also is not ABI-safe due to its use of complex C++ objects like ``std::string`` and ``std::vector``.

Surprisingly, since |IPrivateBakedGoodGetter| is a private interface that is defined, implemented, and only used within
a single DLL, the interface can violate ONI's ABI rules because the ABI will be consistent once
|omni::graph::exec::unstable::cast()| returns a valid |IPrivateBakedGoodGetter|.  If |IPrivateBakedGoodGetter| was able
to be implemented by other DLLs, this scheme would not work due the ambiguities of the C++ ABI across DLL borders.

Private interfaces allow developers to *safely* access private implementation details (e.g. ``BakedGood``) as long as
the interfaces are truly private.  The example above illustrates a common EF pattern, a library embedding implementation
specific data in either nodes or definitions, and then defining passes which cast the generic EF |INode| and |IDef|
pointers to a private interface to access the private data.

But what if the developer wants to *not* be limited to accessing this data in a single DLL?  What if the developer wants
to allow other developers, authoring their own DLLs, to access this data?  In the bakery example, such a system would
allow anyone to create DLLs that implement passes which can optimize the production of any baked good.

The answer to these questions are *public interfaces*.  Unlike private interfaces, public interfaces are designed to be
implemented by many DLLs.  As such, public interfaces must abide by ONI's strict ABI rules.

In the context of the example above, the following public interface can be defined to allow external developers to
access baked good information:

.. literalinclude:: ../tests.cpp/TestBakeryDocs.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs bakery_ibakedgood_abi_begin
   :end-before: ef-docs bakery_ibakedgood_abi_end
   :name: ef_listing_bakery_ibakedgood_abi
   :caption: An example of replacing the private |IPrivateBakedGoodGetter| with a public interface.  Such an interface allows external developers to access baked good information in novel passes to optimize the bakery.

To utilize the public interface, definitions simply need to inherit from it and implement its methods.  For example:

.. code-block:: c++
    :caption: This version of ``PrepareBakedGoodGraphDef`` is similar to the previous one, but now inherits and implements (not shown) the public inteface ``IBakedGood`` rather than the private ``IPrivateBakedGoodGetter``.  ``IBakedGood`` is an API class generated by the *omni.bind* tool which wraps the raw ``IBakedGood_abi`` into a more friendly C++ class.
    :name: ef_listing_bakery_preparebakedgoodgraphdef_public

    class PrepareBakedGoodGraphDef : public NodeGraphDefT<INodeGraphDef, INodeGraphDefDebug, IBakedGood>

Using public interfaces is often more work, but unlocks the ability for external developers to improve and extend a
libary's execution graph.  When deciding whether to use a public or private interface, consult the following flowchart.

.. mermaid::
    :align: center
    :caption: Flowchart of when to use public or private interfaces.

    flowchart TD
        S[Start]
        external{{Will external devs require data stored in your library to extend and improve your part of the execution graph?}}
        data{{Do you need private data for graph construction or execution?}}
        public[Create a public interface.]
        private[Create a private interface.]
        none[No interface is needed.]
        S --> external
        external -- Yes --> public
        external -- No --> data
        data -- Yes --> private
        data -- No --> none

Back to the Population Pass
~~~~~~~~~~~~~~~~~~~~~~~~~~~

After |PopulateChickenPotPiePass| runs and replaces node *node.bakedGood.prepare.chickenPotPie*'s generic graph
definition with a new ``ChickenPotPieGraphDef``, the bakery's definition is as follows:

.. _ef_figure_bakery_chickenPotPie:

.. mermaid:: bakery-chickenPotPie.mmd
    :align: center
    :caption: The execution graph after the ``PopulateChickenPotPiePass`` runs.

Above, you can see *node.bakedGood.prepare.chickenPotPie* now points to a new graph definition which performs task such
as preparing the crust and cooking the chicken in parallel.

Populating Graph Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As mentioned earlier, population passes run on either matching node names or matching graph definition names. You are
encouraged to inspect the names used in :numref:`ef_figure_bakery_chickenPotPie`.  There, node names are fairly
specific. For example, *node.bakedGood.prepare.chickenPotPie* rather than *node.bakedGood.prepare*.  Definitions, on the
other hand, are generic.  For example, *def.bakedGood.prepare* instead of *def.bakedGood.prepare.applePie*.  This naming
scheme allows for a clever use of the rules for population passes.

Earlier, you saw a population pass that optimized chicken pot pie orders by matching *node* names.  Here, a new pass is
created: |PopulatePiePass|:

.. literalinclude:: ../tests.cpp/TestBakeryDocs.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs bakery_populatepiepass_begin
   :end-before: ef-docs bakery_populatepiepass_end
   :name: ef_listing_bakery_populatepiepass
   :caption: ``PopulatePiePass`` finds definitions for pies and replaces the definition with a new definition optimized for the baking of pies.

|PopulatePiePass|'s purpose is to better define the process of baking pies.  This is achieved by registering
|PopulatePiePass| with a matching name of "def.bakedGood.prepare".  Any graph definition matching
"def.bakedGood.prepare" with be given to |PopulatePiePass|.  Above, |PopulatePiePass|'s ``run_abi()`` method first
checks if the currently attached definition can provide the associated ``BakedGood``.  If so, the *name* of the baked
good is checked.  If the name of the baked good ends with "Pie" the node's definition is replaced with a new
``PieGraphDef``, which is a graph definition that better describes the preparation of pies.  The resulting bakery graph
definition is as follows:

.. mermaid:: bakery-pies.mmd
    :align: center
    :caption: The execution graph after the ``PopulatePiePass`` runs.

It is important to note that EF's default |pass pipeline| only matches population passes with either node names or graph
definition names.  Opaque definition names are not matched.

The example above shows that knowing the rules of the application's |pass pipeline| can help EF developers name their
nodes and definitions in such as way to make more effective use of passes.

Conclusion
==========

The bakery example is trivial in nature, but shows several of the patterns and concepts found in the wild when using the
Execution Framework.  An inspection of |OmniGraph|'s use of EF will reveal the use of all of the patterns outlined
above.

A full source listing for the example can be found at *source/extensions/omni.graph.exec/tests.cpp/TestBakeryDocs.cpp*.
