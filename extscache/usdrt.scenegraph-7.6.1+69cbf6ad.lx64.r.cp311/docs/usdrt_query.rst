Fast Stage Queries with USDRT Scenegraph API
============================================

#####
About
#####

usdrt-6.0.6 adds new APIs to the ``usdrt::UsdStage`` implementation that
leverage the capability of Fabric to do constant-time queries of
data in Fabric. This document reviews those APIs, their behavior, and
how you can leverage them to increase performance in your own application or
extension.

#######################################################
Query the stage for prims by type or applied API schema
#######################################################

There are three new APIs to do fast queries of the stage for
prims of a given type, prims with a specific applied API schema, or both.
These are specific to USDRT's UsdStage implementation, and 
leverage Fabric's unique data layout to return information about
the stage without requiring a complete stage traversal with
per-prim inquiries.

* ``std::vector<SdfPath> UsdStage::GetPrimsWithTypeName(TfToken typeName)``
* ``std::vector<SdfPath> UsdStage::GetPrimsWithAppliedAPIName(TfToken apiName)``
* ``std::vector<SdfPath> UsdStage::GetPrimsWithTypeAndAppliedAPIName(TfToken typeName, TfTokenVector apiNames)``

The first call to any of these APIs will populate Fabric with a minimal
representation of the USD stage if necessary. Subsequent
calls will leverage the existing data in Fabric and query Fabric directly.

Query by prim type
------------------

Both of these examples discover all Mesh prims, and set the
`primvars:displayColor` attribute if it exists on the prim. Note that
these APIs return a vector of SdfPaths, so an additional call
to ``UsdStage::GetPrimAtPath`` is necessary to access the related
UsdPrim.

C++
~~~

.. literalinclude::  test_example_code/TestExampleCode.cpp
    :language: c++
    :dedent:
    :start-after: Begin example many prims and types RT
    :end-before: End example many prims and types RT

Python
~~~~~~

.. literalinclude::  test_example_code/test_examples.py
    :language: python
    :dedent:
    :start-after: Begin example many prims RT
    :end-before: End example many prims RT


It is also possible to search by *inherited* types.
This example discovers all prims where "doubleSided" is true for the stage.

.. literalinclude::  test_example_code/test_examples.py
    :language: python
    :dedent:
    :start-after: Begin example abstract query
    :end-before: End example abstract query

Query by applied API schema
---------------------------

It may be useful in some cases to discover every prim where
a particular API schema has been applied. It is possible to
query by individual API schema, or by a list of API schemas
for a specific prim type. The following examples from the
USDRT Scenegraph unit tests demonstrate the concept:

.. literalinclude::  test_example_code/test_stage.py
    :language: python
    :dedent:
    :start-after: Begin example query by API
    :end-before: End example query by API

.. literalinclude::  test_example_code/test_stage.py
    :language: python
    :dedent:
    :start-after: Begin example query mixed
    :end-before: End example query mixed

#################################
Get the world bound for the stage
#################################

An additional API exists that leverages world extent data in Fabric set by
Fabric Scene Delegate or the RtBoundable schema to compute the bounding
extent for the stage: 

``GfRange3d UsdStage::GetStageExtent()``

If no world extent data exists in Fabric, this API will populate it from
USD using a multi-threaded compute and Fabric queries to target
only Boundable prims directly.

.. literalinclude::  test_example_code/test_stage.py
    :language: python
    :dedent:
    :start-after: Begin example stage extent
    :end-before: End example stage extent

###########################################
Using stage queries for optimal performance
###########################################

The key benefit of these query APIs is that they only
populate Fabric with the minimal set of data from the underlying
USD stage required for each query, and once populated,
querying Fabric is extremely fast. Fabric queries are performed
in constant time, and unlike stage traversal, do not increase
relative to prim count on the USD stage.

This performance characteristic is beneficial for modular software
architectures where each module may require independent inquiries
into the USD stage. For example, consider a hypothetical suite of Kit extensions
where each extension needs to do one of the following inquiries into
the USD stage in response to a stage-opened event:

* A BackupLight extension checks if there are any lights on the USD stage, and if not, creates a default light
* A CharacterAnimator extension finds all of the UsdSkel prims on the USD stage and populates a menu with their names
* A FastRender extension checks if any Mesh prim names end with the string "_glass" to optimize render settings
* A ForkliftSimulator extension finds all prims with the PhysicsDriveAPI schema applied to prepare a simulation context

Accomplishing these tasks with the conventional USD API requires
each extension to independently perform a complete traversal of the USD stage. However, with
the USDRT stage query APIs and underlying Fabric data, *at most* one USD stage
traversal is required for lightweight Fabric population, and subsequent queries
after the first leverage the data that has already been populated into Fabric.
This makes stage inspection fast and lightweight, and modularity straightforward.
