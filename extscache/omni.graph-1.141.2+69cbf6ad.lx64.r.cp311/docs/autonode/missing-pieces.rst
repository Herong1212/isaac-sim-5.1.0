.. _autonode_missing_pieces:

:fa:`puzzle-piece` Missing Pieces
#################################

Due to the compact nature of the Python function definitions and the decorator syntax there are a number of features
that are supported by the .ogn file that are not supported directly by the decorator syntax. In some cases the Python
API is able to fill in the gaps if you really need this extra functionality, albeit in a much less intuitive way
than you get if you implement the .ogn/.py file pairs instead. This is intentional as the goal of |autonode| is rapid
node creation so tradeoffs were made accordingly.

Structural Pieces
=================

These definitions are typically found in the .ogn file and describe part of the attribute or node type's
structural characteristics.

Node Type Version Number
------------------------

Every .ogn file is required to supply a node version number using the `"version": N` keyword. With an |autonode|
definition there is no version number, partly due to the fact that it is less useful for this type of node type
definition. In particular for an |autonode| definition:

- the node types are not serialized so the version number would not persist
- there is no mechanism for updating a node from an earlier version number, if one was requested

Node Types Not Implemented In Python
------------------------------------

It may seem obvious but is still worth mentioning that all |autonode| definitions create node type definitions for
node types that are implemented in Python. The decorator is in Python and the function it decorates is in Python so
it is natural that the node type stays in Python. This does not preclude using Python libraries such as Warp to
move the Python code to other languages such as Cuda or C++, however that is something the user would have to do.

Generation Of Documentation, Tests, And USD Example Files
---------------------------------------------------------

One of the side benefits of having a definition in a .ogn file is that the code generator can take that definition and
create other useful outputs from that definition. In particular it is typical to have node type documentation
automatically generated, which is a restructuredText file containing a nicely formatted page with the node type
metadata and all of the attribute information.

Similarly a set of standardized tests can be created that test basic node operation, including reading the node
type definition from a .usda file to confirm that things like default values behave correctly. With an |autonode|
definition this is less useful to have since the whole point is rapid development and extra elements such as
documentation and tests are more suited to more permanent node type definitions, where they might belong to an
extension or be indexed in a library for easy discovery.

Attribute Documentation
-----------------------

While the node type documentation can be pulled from the decorated function's docstring there is no similar location
to attach such information to the input or output attributes. As a result the attributes will be undocumented and
when users are interacting with them they will not have that information available.

An easy workaround to this shortcoming is to embed the attribute information in the function docstring, much in the
same way as you might see in regular coding documentation styles. For example, here's a function that uses the
Google developer documentation style.

.. literalinclude:: ../../../../../source/extensions/omni.graph/python/_impl/autonode_examples.py
    :language: python
    :dedent: 4
    :start-after: begin-autonode-documented
    :end-before: end-autonode-documented

Attribute Metadata
------------------

Like node types, attributes also have useful metadata such as *ui_name* that is not possible to
provide directly. Some metadata values will take on useful defaults while others, such as *minimum value*, will just
be absent. It is an implementation detail about attributes that while their structure is specified in the arguments
of a decorated |autonode| function, or in the .ogn file, the actual `Attribute` object is copied from that structure
and contains its own unique metadata.

For that reason, you can work around the missing metadata if you really need to by accessing the attributes directly
and modifying the metadata after a node of the new type has been created. Here is a brute force method to get all
nodes of the type `omni.graph.normalize` and set the output attribute's UI name to "Normalized Vector".

.. code-block:: python

    import omni.graph.core as og
    import omni.graph.tools.ogn as ogn
    for graph in og.get_all_graphs():
        for node in graph.get_nodes():
            if node.get_type_name() != "omni.graph.normalize":
                continue
            node.get_attribute("outputs:out_0").set_metadata(ogn.MetadataKeys.UI_NAME, "Normalized Vector")


Custom Naming Of Attribute Outputs
----------------------------------

As you have probably noted from the examples, the output attributes all have numbered names such as *out_0*, *out_1*,
etc. whereas node types defined through a .ogn file have explicit names. The name of an attribute is intentionally
immutable so there is no API that will let you assign a new name to the output as there is for setting the UI name
through the metadata. Short of doing something heroic, like setting up an indirection table to remap all of your
attribute names from the ones you want to use to the numbered names, there is no way to use a more meaningful name
for the output attributes.

Attribute Memory Types
----------------------

In a .ogn file you can specify an attribute's memory affinity using the *memoryType* keyword, either at the node type
level or on a per-attribute basis. What this does is to cause the generated code to request the attribute's value on
the appropriate device without need for user intervention. With the |autonode| wrapping around the actual data
retrieval there is no access to allow specification for attribute values to be retrieved from anywhere other than
the CPU.

Outside of a compute method you are still free to request that the data be retrieved from any arbitrary device but
inside the decorated function you are restricted to CPU access only.

Extended Attribute Types
------------------------

While you can specify extended attribute types as part of an |autonode| decorated function argument list you will be
unable to resolve the attribute types to a concrete type at runtime. Therefore they won't be very useful types as
they will never contain real values.

Instead, stick with concrete data types. |autonode| functions are meant to be simple anyway so overloading a function
to handle many different types of data is against its purpose. Favor a quick function that adds two integers together
over a more complex node type definition that reads the underlying types and dispatches the correct add code to the
resolved data type values.

Runtime Pieces
==============

In addition to the structural elements above there are a few runtime features that are similarly not available when
using |autonode| node type definitions, since it is just a single function.

Defining Methods Other Than compute()
-------------------------------------

As you might have guessed from some of the above limitations, there are some features on the node type that rely on
access to other functions that might be overridden in a node type implementation. The more common ones of these are
`initialize()`, `initialize_type()`, and `release()`.

As |autonode| functions are not full fledged class objects it is only possible for them to override a single function,
which will always be the `compute()`. (In fact it actually wraps the function in some helper code that sets up and
tears down the data for the function call.)

Some features of these extra functions can be handled in other ways, such as the use of the *metadata* keyword in the
decorator arguments, or the brute force addition of attribute metadata seen above. For anything more complex you are
better off creating a full node type implementation with a .ogn/.py file pair.

.. _autonode_access_node:

Accessing Node And Context In compute()
---------------------------------------

As the decorated function assumes every argument passed in to it is an input attribute there is no room for accessing
other types of information. In particular, in a normal `compute()` override the function will have access to both the
node and the context of the current evaluation. (In generated node types the information is further wrapped in a
more feature-rich database class.)

Although the node and context are available in the wrapper function they cannot be accessed directly as they have
not been passed in to the decorated function. However you can make use of the Python **inspect** module and some
implementation information that the arguments will always be named *node* and *context* to look up that information.

.. literalinclude:: ../../../../../source/extensions/omni.graph/python/_impl/autonode_examples.py
    :language: python
    :dedent: 4
    :start-after: begin-autonode-access-node
    :end-before: end-autonode-access-node


Emitting Errors And Warnings In compute()
-----------------------------------------

The database generated when using a .ogn file has some useful utilities, one of which is the ability to log an error
or a warning with the node so that the UI can report on execution failures. As the |autonode| function has no
database this convenience cannot be used.

Fortunately the logging capability is in the node's API so all you need to do to manually log messages is to access
the node using the inspect module as above and call the log function with the appropriate logging level set. Here
is an example that uses both warnings and errors to provide status information to the UI.

.. literalinclude:: ../../../../../source/extensions/omni.graph/python/_impl/autonode_examples.py
    :language: python
    :dedent: 4
    :start-after: begin-autonode-logging
    :end-before: end-autonode-logging

Creating New Output Bundles In compute()
----------------------------------------

Normally when you want to output a bundle you would construct one using the generated database's convenience function
for doing that. You can also implement this yourself, however you need to emulate that same convenience function, which
requires access to both the node and the context via the inspect module.

.. literalinclude:: ../../../../../source/extensions/omni.graph/python/_impl/autonode_examples.py
    :language: python
    :dedent: 4
    :start-after: begin-autonode-output-bundles
    :end-before: end-autonode-output-bundles

Accessing Per-Node Data
-----------------------

As with the message logging, the generated database provides access to internal state data that is associated with each
individual node. This data is controlled by the user. Again since there is no database with an |autonode| node type
this feature is not available, though with the help of the inspect module it can be implemented locally with not
too much effort:

.. literalinclude:: ../../../../../source/extensions/omni.graph/python/_impl/autonode_examples.py
    :language: python
    :dedent: 4
    :start-after: begin-autonode-per-node-data
    :end-before: end-autonode-per-node-data

Saving The Node Type Definition
-------------------------------

As the node type definition is created at runtime there is no artifact to be referenced to find that node type
definition in another session. Although the node type definition may have a particular extension associated with it
there is no guarantee that merely loading that extension will recreate that node type definition. Indeed it may be
impossible if some of the parameters used in its creation are session-dependent, such as date of creation.

To warn the user that they might be saving node types that cannot be retrieved a warning will be issued when a file is
saved that contains an instantiated node of any |autonode| type. And in future when required extensions are saved
with the USD files any extension called out in an |autonode| definition will be included.

Concrete Extension Dependencies
-------------------------------

Further to the above, it is quite possible that an |autonode| decorated function could have dependencies on any
arbitrary extension that is currently loaded. For this reason it's also possible that another user running the exact
same decorated function may not get a functioning node type if they do not have the requisite extensions enabled.

Again, another reason why nodes with these types will not be silently saved as they could cause the graph to become
non-functional when read into another session.
