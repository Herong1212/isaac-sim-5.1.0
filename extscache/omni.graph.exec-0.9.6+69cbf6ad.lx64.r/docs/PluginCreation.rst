.. include:: Helpers.rst
.. _ef_plugin_creation:

Plugin Creation
-------------------

|SHOW_GUIDE_WARNING|

The Execution Framework is a *graph of graphs*.  EF allows users, with their own code, to:

- Build the graph

- Optimize the graph

- Defines how/when nodes in the graph are executed

- Provide chunks of code to execute in the graph

- Customize how graph data is stored

- Define custom schedulers to dispatch the graph's tasks

The primary method used to extend EF's functionality is to subclass from EF's implementations of its core interfaces:
|Node|, |NodeDef|, |NodeGraphDef|, |ExecutionContext|, |Executor|, |PopulatePass|, |PartitionPass|, etc.

A reasonable questions is, "How are these custom user implementations instantiated by EF?"  In short:

- |ExecutionContext| objects are usually instantiated by the application.

- |Node| objects are usually instantiated by implementations of |NodeGraphDef|.

- |Executor| objects are instantiated by implementations of |NodeGraphDef|.

- |NodeGraphDef| objects are usually instantiated by passes (e.g. |PopulatePass|).

- |NodeDef| objects are usually instantiated by passes (e.g. |PopulatePass|).

- Passes are instantiated by |PassPipeline| which uses a global registry of available passes.

- |PassPipeline| is usually instantiated by the application.

Visually:

.. mermaid::
    :align: center
    :caption: Who instantiates who in EF.  Upstream entities instantiate downstream entities.

    flowchart TD
        Application --> PassPipeline
        Application --> ExecutionContext
        PassPipeline --> Pass
        Pass --> NodeDef
        Pass --> NodeGraphDef
        NodeDef --> OpaqueCode[Opaque Code]
        NodeGraphDef --> Node
        NodeGraphDef --> Executor

Above, we see there are two objects the application will instantiate: |PassPipeline| and |ExecutionContext|.  The
implementations instantiated here will be application specific.

The creation of all other entities can be tied back to passes.  As mentioned above, passes are instantiated by the
application's |PassPipeline|, which accesses a global registry of available passes.  This global registry, available via
the global |getPassRegistry()| function, can be populated by user plugins.

In this article, we do not cover application level customization, such as |PassPipeline| and |ExecutionContext|, since
such customizations are rare when using the Kit SDK (Kit already does this for you).  We will cover how users can create
their own plugins to define their own passes, and thereby their own nodes, definitions, and executors.  Omniverse has
two methods to define plugins: *Carbonite Plugins* and *Omniverse Modules*.

Creating an Omniverse Module
============================

The minimum needed to implement an Omniverse module can be found in the *omni.kit.exec.example-omni* extension:

.. literalinclude:: ../../omni.kit.exec.example-omni/plugin/Module.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs example_omni_plugin_begin
   :end-before: ef-docs example_omni_plugin_end
   :name: ef_listing_esxample_omni_plugin
   :caption: Example of defining an Omniverse Module using the Kit SDK.

Building the DLL is build system dependent, but when using the Kit SDK, the following snippet from
:file:`source/extensions/omni.kit.exec.example-omni/premake5.lua` should do the job:

.. literalinclude:: ../../omni.kit.exec.example-omni/premake5.lua
   :language: lua
   :dedent:
   :start-after: ef-docs example_omni_plugin_premake_begin
   :end-before: ef-docs example_omni_plugin_premake_end
   :name: ef_listing_example_omni_plugin_premake
   :caption: Example of building an Omniverse Module using the Kit SDK.

The *omni.kit.exec.example-omni* extension is a fully functioning extension found at
:file:`source/extension/omni.kit.exec.example-omni/`.  It includes much more than what is presented above, for
example, how to create tests for your EF extension.  It is a suitable starting point for your own EF extension.

Creating a Carbonite Plugin
============================

The minimum needed to implement a Carbonite plugin can be found in the *omni.kit.exec.example-carb* extension:

.. literalinclude:: ../../omni.kit.exec.example-carb/plugin/Plugin.cpp
   :language: c++
   :dedent:
   :start-after: ef-docs example_carb_plugin_begin
   :end-before: ef-docs example_carb_plugin_end
   :name: ef_listing_esxample_carb_plugin
   :caption: Example of defining an Carbonite plugin using the Kit SDK.

Building the DLL is build system dependent, but when using the Kit SDK, the following snippet from
:file:`source/extensions/omni.kit.exec.example-carb/premake5.lua` should do the job:

.. literalinclude:: ../../omni.kit.exec.example-carb/premake5.lua
   :language: lua
   :dedent:
   :start-after: ef-docs example_carb_plugin_premake_begin
   :end-before: ef-docs example_carb_plugin_premake_end
   :name: ef_listing_example_carb_plugin_premake
   :caption: Example of building a Carbonite plugin using the Kit SDK.

Deciding on Which Approach to Take
==================================

When implementing new EF functionality, it is recommended to use Omniverse modules.  Omniverse modules work well with
EF's ONI based interfaces. Additionally, if you plan on providing your own ONI interfaces that encapsulate global state
that needs to be accessed across many DLLs, Omniverse modules allow you to register interfaces via
|omni::core::ITypeFactory|.  See *omni.kit.exec.core* for an example.

If you are extending an existing Carbonite plugin with EF functionality (e.g. |omni.graph.core|) using the existing Carbonite
plugin is the path of least resistance. By taking this approach, your new EF implementation will be able to access
implementation details of existing functionality located in the same plugin.

Avoiding Crashes at Exit
==================================

.. note::

    This section covers a crash on exit problem often seen when using the Kit SDK.  The solution provided is not
    implemented in the core EF library, rather it is implemented in the |omni.kit.exec.core| extension, which bridges EF
    with Kit.  Both the problem and solution are presented here, in the core EF docs, to help users of EF outside of the
    Kit SDK to understand potential edge cases with EF integration.

Applications based on the Kit SDK will shutdown each extension/plugin/module before exit.  This can lead to unexpected
crashes when DLLs depend upon each other.  This coupling of functionality between DLLs is often the case in EF.

As an example, consider the |omni.graph.action| extension, which provides definitions and passes to implement
|OmniGraph|'s |Action Graph| extension.  The |omni.graph.action| extension depends upon |omni.graph.core| which in turn
depends upon |omni.kit.exec.core|, which depends upon the core EF extension (|omni.graph.exec|).  When the application
starts, this dependency information is used to load |omni.graph.exec| first, followed by |omni.kit.exec.core| second,
then |omni.graph.core|, and finally |omni.graph.action|.  During shutdown, the extensions are unloaded in reverse order.

.. mermaid::
    :align: center
    :caption: Safely unloading extensions is no easy task.  Explicit extension dependencies are depicted with solid lines.  Implicit reference counting dependencies are depicted with dotted lines.

    flowchart LR
        oge[omni.graph.exec] -- Provides PassRegistry To --> okec[omni.kit.exec.core]
        okec -- Provides ExecutionController To --> ogc[omni.graph.core]
        ogc -- Provides OG To --> oga[omni.graph.action]
        oga -. Stores Data In .-> ogc
        ogc -. Stores Data In .-> okec

During shutdown, |omni.graph.action| will unload without issue.  However, when unloading |omni.graph.core| you're likely
to see a crash when OmniGraph's destructs its internal objects.  This is because OmniGraph stores an |ObjectPtr| to each
EF |definition| is creates.  This isn't a bug, as it allows OmniGraph to quickly and precisely |invalidate| parts of
EF's execution graph.  However, during shutdown, definitions provided by |omni.graph.action| will crash, because
attempting to invoke their destructors will call into unloaded code.

EF's solution to this problem is |OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED()|.  This macro's second argument is a callback
function that will be invoked before any DLL that called |OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED()| is unloaded.  This
gives EF enabled DLLs the opportunity to clean up any references to objects implemented in external DLLs that are
possibly about to be unloaded.

Next Steps
============================

Above, we covered the creation of plugins to extend EF's functionality.  Readers are encouraged to move onto to either
:ref:`ef_definition_creation`, :ref:`ef_pass_creation`, and :ref:`ef_executor_creation` to being implementing new
graphs.
