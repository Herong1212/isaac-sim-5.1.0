.. include:: Helpers.rst

.. _ef_abi:

Application Binary Interface Considerations
-------------------------------------------

|SHOW_ADVANCED_TOPIC_WARNING|

The Execution Framework is designed to be extended with user defined functionality.  New graph types, alternative
schedulers, and graph optimizations are just some of the possibilities with extending EF.

Extensibility Goals
===================

EF has the following goals for the mechanism used to extend EF:

- New functionality injected into EF must be able to come from multiple parties/repos.  If cannot be a requirement that,
  for multiple features from different parties to work in the same EF process, they must be compiled at the same time
  using the same toolchain by the same party.

  EF must allow for a *marketplace* of EF extensions that seamlessly work together.

- Published user functionality must not break when EF is upgraded.  A deployed binary containing EF functionality should
  continue to work even when using a new version of *omni.graph.exec.dll*.

  Publishing an updated version of EF should not invalidated the entire EF marketplace.

- Most of EF should be replaceable/extensible by the user.  EF must not assume the implementation being used.

- Extending EF should not require the user to write a lot of code.  Rather, the user should be able to transparently use
  EF's existing code and tailor its functionality to their wishes.

The mechanisms employed by EF to meet the goals above are two-fold:

- EF functionality can be shipped and dynamically loaded via plugins

- Core EF concepts are represented by immutable interfaces via :doc:`carbonite:docs/OmniverseNativeInterfaces`.

Plugins
=======================

Plugins allow users to package and ship chunks of new EF functionality to downstream users.  Omniverse further expands
upon the concept of plugins with |Kit Extensions|.  Kit Extensions enjoy a vibrant marketplace and software stack that
makes it easy for users to both publish and use new functionality.  EF plugin creation is covered in detail in
:ref:`ef_plugin_creation`.

Omniverse Native Interfaces
===========================

The key to EF's extensibility is its use of |Omniverse Native Interfaces| (ONI).  ONI allows the definition of software
contracts (i.e. interfaces) that outline not only the functionality of a component but also the binary protocol used to
communicate with it.  These contracts allow interfaces implemented by different parties/toolchains to communicate with
each other across DLL boundaries.

ONI interfaces are broken into two parts: the ABI and the API.

The ABI defines the binary protocol used to communicate with the object.  An example of an ABI can be seen in
|INodeGraphDef_abi|.

Using the ABI is cumbersome, as its binary protocol is restricted to C-like features. To make using the ABI easier, an
API layer *wraps* the ABI.  An example of an API wrapping an ABI is |INodeGraphDef|.  The API layer presents a modern
C++ surface, hiding the complexities of the ABI.

When talking about EF, we tend to focus on the API layer, as that is the layer which most code will interact with.  It
is rare, both in code and documentation, that you will see a reference to the ABI layer (e.g. |INodeGraphDef_abi|).

.. _ef_reference_counting:

Reference Counting
==================

ONI objects are reference counted.  This greatly eases interoperability of ONI implementations across various languages
with differing memory models (e.g. Python).

Unfortunately, reference counting has a runtime cost.  Consider the following method:

.. code-block:: c++
   :name: ef_listing_get_background_result
   :caption: Some methods in EF return an |ObjectPtr|, most do not.  This method doesn't really exist (|INode::getChildren()| does though).

    omni::core::ObjectPtr<omni::graph::exec::unstable::INode> getChildNode(unsigned int index);

Before being returned in the |ObjectPtr|, |INode::acquire()| is called to increment the child node's
reference count.  However, imagine any time EF had to return an ONI object, the reference count had to be incremented.
The cost would be small in isolation, but in high-performance code paths such as graph construction, traversal, and
execution; small costs add up quickly.

To avoid "death by a thousand cuts" in high-performance code paths, EF elides incrementing the reference count when
returning ONI objects:

.. literalinclude:: ../../../../include/omni/graph/exec/unstable/ITopology.h
   :language: c++
   :dedent:
   :start-after: ef-docs i_topology_abi_get_root_abi_begin
   :end-before: ef-docs i_topology_abi_get_root_abi_end
   :name: i_topology_abi_get_root_abi
   :caption: |ITopology::getRoot()| returns its root node without incrementing its reference count.

Above, we see |ITopology::getRoot()| signature.  The returned root node's reference count is not incremented before
being returned.  This goes against ONI's reference counting behavior recommendations.  However, it's justified for a
couple of reasons:

- |ITopology::getRoot()| is called a lot during traversal.  The cost can add up.

- The returned root node has no risk of destructing during either traversal or execution since the owning object,
  |ITopology|, is never destructed during traversal or execution.  As long as the use of the root node is short-lived,
  there is little risk it will become invalid.

- If the user wishes to store the node for a longer period of time, they can store it in an |ObjectPtr| (which will
  increment the reference count).

In practice, you won't notice EF's deviation from ONI's reference counting recommendation if you rely on ``auto``:

.. code-block:: c++
   :name: ef_listing_reference_counting_auto
   :caption: When using EF, using ``auto`` is recommended, as it will generally do the right thing in regards to making reference counting both safe and efficient.

    auto root = topology->getRoot();
    auto name = root->getName();
    std::cout << "root's name: " << name '\n';

.. _ef_ref_count_rules:

EF's Reference Counting Rules
#############################

When using EF, observe the following reference counting rules:

- Use ``auto`` when retrieving a value from an EF function.

- When returning a newly created ONI object, return it using |ObjectPtr| and |omni::core::steal()|.

- Be mindful of storing |ObjectPtr| objects in your plugin as doing so complicates plugin unloading.  This is covered in
  more detail in :ref:`ef_definition_creation`.

- When designing new EF interfaces, use
  :doc:`OMNI_ATTR("no_acquire") <carbonite:docs/omni.bind/omni.bind>` at the ABI layer to
  produce an efficient API wrapper.

Avoiding ONI Overhead
=====================

ONI objects are heap allocated.  Heap access has a cost, and that cost can add up in high-performance code paths.

EF has several objects that are rapidly constructed and destroyed during high-performance code paths (such as
execution). Examples of these objects are |ExecutionPath| and |ExecutionTask|.

Volatile objects such as |ExecutionPath| and |ExecutionTask| are not ONI objects.  They avoid heap usage and are
designed to live on the stack. Even though these objects are not ONI objects, they are ABI-safe.  Unfortunately, to make
the objects ABI safe, all implementation details about these objects are exposed.

Immutable vs. Unstable Interfaces
=================================

ONI presents the concept of immutable interfaces.  These are great, as they guarantee that binary components (such as
|Kit Extensions|) will continue to be useful without recompilation.

An ONI interface is considered immutable once "published".  That begs to question, when developing a new interface, when
is it considered published?

EF answers this question by placing all "in-development" interfaces in |omni::graph::exec::unstable|.  Users are free to
use these interfaces for experimentation, but they may change.

Published interfaces live in |omni::graph::exec|.  Users are free to rely on these interfaces and confidently publish
their own interfaces utilizing these interfaces.

If possible, when promoting an unstable interface to a published interface, EF will make the published interface
castable to the unstable interface.


Casting
=======

A core feature of ONI is its ability to ask an ONI object which contracts/interfaces it honors.  This is called
*casting*.

ONI's specification states that |IObject::cast()| must increment the reference count before returning the new interface
pointer.  As explained in :ref:`ef_reference_counting`, this can be costly, specially when trying to determine the type
of an object in high-performance code paths.

To avoid incrementing the reference count, all EF objects inherit from the |IBase| interface.  This interface adds the
|IBase::castWithoutAcquire()| method.  When casting EF objects, it is recommended you use the
|omni::graph::exec::unstable::cast()| function, which calls |IBase::castWithoutAcquire()|.

When is it OK to Call dynamic_cast?
###################################

A question often asked is, "Is it OK to call |dynamic_cast| on an EF object?"  The answer is, "No. Call
|omni::graph::exec::unstable::cast()| instead."  Developers are encouraged to review :ref:`Private Interfaces
<ef_private_interfaces>` to better understand the harm of |dynamic_cast| and see the ABI-safe alternative utilized by
EF.
