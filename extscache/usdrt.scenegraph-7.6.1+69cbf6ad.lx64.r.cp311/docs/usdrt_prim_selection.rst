##############################################################
Efficiently processing sets of prims with USDRT Scenegraph API
##############################################################

*****
About
*****

Usdrt has new APIs for efficiently processing sets of prims selected 
from the stage according to some criteria. The APIs support processing on CPU 
and GPU, in C++ and Python (using NVIDIA Warp). Possible uses include:

* A physics system updating all physics meshes.
* A clash detector finding collisions between all tagged meshes.
* A renderer rendering all meshes.
* An animation system updating all skeletons.
* A shader compiler compiling all materials.
* A procedural mesh system generating meshes for all prims containing input 
  parameters.

Using the new APIs has the following advantages compared to the standard USDRT 
APIs for finding and iterating over prims.

* By leveraging Fabric's stage index, the new APIs find the set of prims in
  constant time, as opposed to visiting every prim on the stage using a 
  traversal. For example, if you want to select 1000 prims from a stage of 
  1000000, the search cost is some constant k, not k*1000000 or even k*1000.
* The new APIs give access to Fabric's vectorized memory representation of the 
  selected prims' attributes, which allows fast, parallelizable access on CPU 
  or GPU.
* Accessing the N selected prims using the new APIs is faster than calling the 
  existing APIs N times, as it allows USDRT to amortize overheads. This gives 
  significant performance benefit with N as low as 100.

This document reviews these APIs, their behavior, and how you can leverage them
to increase performance in your own application or extension. It first describes 
how to use the new APIs to select which prims and attributes to process, and 
then how to use a new iterator (on CPU or GPU) to get fast access to the 
attribute data as we process it.

***********************************************
Selecting which prims and attributes to process
***********************************************
API
===
The UsdStage has a new API, SelectPrims, that we use to select the subset of 
the stage's prims that we want to work on. We can select prims according to 
their type and/or what applied schemas they have. Additionally, SelectPrims 
has a parameter that we use to select the subset of the prims' attributes that
we want to access or modify, and the prim selection will only include prims that 
have them. Although maybe less useful, it's also possible to leave prim type 
and applied schema unspecified, and just find all prims that have particular 
attributes. SelectPrims is defined as follows.

C++
---
.. code:: c++

    RtPrimSelection UsdStage::SelectPrims(std::vector<TfToken> requireAppliedSchema, 
                                          std::vector<AttrSpec> requireAttrs, 
                                          carb::cpp::optional<TfToken> requirePrimType = {},
                                          uint32_t device = kDeviceCPU)

The Device parameter is an integer that specifies whether to make the 
RtPrimSelection on CPU or GPU, and specifies a particular GPU on multiple GPU 
systems. Set device to kDeviceCPU to run on CPU, or 0 to run on CUDA GPU 0. 
Running on other GPUs in multi GPU systems is not currently supported.

Python
------
.. code:: python

  Usd.Stage.SelectPrims(device: str, 
                        require_applied_schemas=None: list(str), 
                        require_attrs=None: list(tuple),
                        require_prim_type=None: str)

In Python the device is specified by a string, set device to "cpu" to use the 
CPU, or "cuda:0" to run on CUDA GPU 0. Running on other GPUs in multi GPU systems 
is not currently supported.

In both C++ and Python, SelectPrims returns an object of a new type, 
RtPrimSelection, described in a later section, `Processing prims by iterating over the selection`_. 

Populating the stage into Fabric
================================
Unlike the USDRT query APIs, SelectPrims searches only USD prims that are 
present in Fabric, not the whole USD stage. For the examples in this document 
we want to search USD stages loaded from files, so we need the following code 
to populate Fabric.

C++
---
.. literalinclude::  test_example_code/TestExampleCode.cpp
    :language: c++
    :dedent:
    :start-after: Begin populate cornell.usda for examples
    :end-before: End populate cornell.usda for examples

Python
------
.. literalinclude::  test_example_code/test_examples.py
    :language: python
    :dedent:
    :start-after: Begin populate cornell.usda for examples
    :end-before: End populate cornell.usda for examples

Example 1: Selecting prims by type
==================================
The following example shows how to select all the meshes on the stage using
C++ and Python.

C++
---
.. literalinclude::  test_example_code/TestExampleCode.cpp
    :language: c++
    :dedent:
    :start-after: Begin example making a prim selection by prim type
    :end-before: End example making a prim selection by prim type

Python
------

.. literalinclude::  test_example_code/test_examples.py
    :language: python
    :dedent:
    :start-after: Begin example making a prim selection by prim type
    :end-before: End example making a prim selection by prim type

Example 2: Selecting prims by applied schema
============================================
With SelectPrims we can also select prims according to which applied schemas 
they have. The following example shows how to select all physics meshes, which 
are prims that have type "Mesh" and applied schema "PhysicsRigidBodyAPI".

C++
---

.. literalinclude::  test_example_code/TestExampleCode.cpp
    :language: c++
    :dedent:
    :start-after: Begin example making a prim selection by prim type and applied schema
    :end-before: End example making a prim selection by prim type and applied schema

Python
------

.. literalinclude::  test_example_code/test_examples.py
    :language: python
    :dedent:
    :start-after: Begin example making a prim selection by prim type and applied schema
    :end-before: End example making a prim selection by prim type and applied schema


Example 3: Specifying which attributes to access or modify
==========================================================
So far we've selected a subset of the stage's prims, next we need to specify 
which of their attributes we want to access. The following example selects all 
meshes that have a displayColor, and specifies that we want read/write access to 
it. 

C++
---
.. literalinclude::  test_example_code/TestExampleCode.cpp
    :language: c++
    :dedent:
    :start-after: Begin example making a prim selection by prim type and attributes
    :end-before: End example making a prim selection by prim type and attributes

Python
------

.. literalinclude::  test_example_code/test_examples.py
    :language: python
    :dedent:
    :start-after: Begin example setting array-valued attribute, select prims
    :end-before: End example setting array-valued attribute, select prims   

This example requests read-write access to displayColor. Other options
for access type are read-only and overwrite. Read/write and write access cause
Fabric's change tracker to log the access, and this has a cost. So it's best to
use read-only access for attributes that we only read. Overwrite tells 
USDRT that we will overwrite any existing data. This allows a performance 
optimization, because USDRT doesn't need to initialize data that it knows is 
about to be overwritten. This is even more important for GPU, because Fabric 
doesn't need to send arrays from CPU to GPU or vice versa when it knows they 
are about to be overwritten.

************************************************
Processing prims by iterating over the selection
************************************************
Once we've made a prim selection we can iterate over it and do some 
computation. We'll look at how to do that first in Python, then in C++.

Python
======
To process the selected prims in Python we use NVIDIA warp to iterate over the 
prims and apply a kernel function to each. The advantage of using NVIDIA warp 
is that it allows us to iterate and apply the python kernel on either CPU or 
GPU. To pass attributes to the kernel function we need to wrap each with 
warp.fabricarray, and then launch the function using warp.launch. The 
definitions of warp.fabricarray and warp.launch are as follows.

.. code:: python

  warp.fabricarray(view: dict, attrib: str)
  warp.launch(kernel, dim, inputs, device)

Example 4: Setting world position
---------------------------------
In this example we'll select all the physics meshes on the stage and change 
their world position. We'll select the prims for processing on CUDA GPU 0, but 
if we wanted to use the CPU instead the only change we'd need to make would be
to set the device parameter to "cpu". 

.. literalinclude::  test_example_code/test_examples.py
    :language: python
    :dedent:
    :start-after: Begin example setting world position, select prims
    :end-before: End example setting world position, select prims

Next we define the kernel function we want to apply to the selected prims.

.. literalinclude::  test_example_code/test_examples.py
    :language: python
    :dedent:
    :start-after: Begin example setting world position, kernel
    :end-before: End example setting world position, kernel

Finally we run the kernel on the selection using warp.

.. literalinclude::  test_example_code/test_examples.py
    :language: python
    :dedent:
    :start-after: Begin example setting world position, apply kernel
    :end-before: End example setting world position, apply kernel

Example 5: Setting an array-valued attribute
--------------------------------------------
In this example we'll select all the meshes on the stage and change their color 
to red. A quirk of USD is that displayColor is an array-valued attribute, even 
when one color is applied to the whole mesh. We'll use this example to 
demonstrate the use of array-valued attributes, even though in this case the 
array has size one. First we select all the meshes on the stage.

.. literalinclude::  test_example_code/test_examples.py
    :language: python
    :dedent:
    :start-after: Begin example setting array-valued attribute, select prims
    :end-before: End example setting array-valued attribute, select prims

Next we define the kernel function we want to apply to the selected prims. The 
main difference compared to the last example is that the type of the colors 
parameter is fabricarrayarray instead of fabricarray. The parameter is an 
array-of-arrays, because the selection contains multiple prims, each with an 
array of colors. We index the array using `colors[i, 0]` to access color 0 of 
selected prim i.

.. literalinclude::  test_example_code/test_examples.py
    :language: python
    :dedent:
    :start-after: Begin example setting array-valued attribute, kernel
    :end-before: End example setting array-valued attribute, kernel

Finally we make a warp.fabricarray for the attribute we want to pass to the 
kernel, and then launch it using warp. Note that here the array is a 
fabricarray, not a fabricarrayarray.

.. literalinclude::  test_example_code/test_examples.py
    :language: python
    :dedent:
    :start-after: Begin example setting array-valued attribute, apply kernel
    :end-before: End example setting array-valued attribute, apply kernel

C++
===
SelectPrims returns an RtPrimSelection, which has the following methods in C++.

.. code:: c++

    AttributeRef GetRef(SdfValueTypeName type, const TfToken& name) const;
    omni::fabric::batch::View GetBatchView() const;
    size_t GetCount() const;

To iterate over the prim selection's data on CPU or GPU we need to construct a 
batch::ViewIterator, using GetBatchView as follows.

.. code:: c++

    batch::ViewIterator iter(selection.GetBatchView());

batch::ViewIterator has the following methods:

.. code:: c++

    ViewIterator(const batch::View& view, const size_t index = 0)
    bool peek();
    bool advance(const size_t stride = 1);
    template<typename T> const T& getAttributeRd(const AttributeRef& attributeRef) const;
    template<typename T> T& getAttributeWr(const AttributeRef& attributeRef) const;
    template<typename T> SpanOf<const T> getArrayAttributeRd(const AttributeRef& attributeRef) const;
    template<typename T> SpanOf<T> getArrayAttributeWr(const AttributeRef& attributeRef) const;
    size_t getGlobalIndex() const;
    size_t getElementRangesIndex() const;
    size_t getElementIndex() const;
    size_t getElementCount(const AttributeRef& attributeRef) const;
    uint64_t getPath() const;

Example 6: Setting an array-valued attribute in C++ on CPU
----------------------------------------------------------
As in the Python example, we'll select all the meshes on the stage and make 
them red. First we make a prim selection, get an AttributeRef for displayColor,
make an RTiterator, then iterate over the data using a while loop.

.. literalinclude::  test_example_code/TestExampleCode.cpp
    :language: c++
    :dedent:
    :start-after: Begin example processing prims by iterating over the prim selection on CPU
    :end-before: End example processing prims by iterating over the prim selection on CPU

Example 7: Setting an array-valued attribute in C++ on GPU
----------------------------------------------------------
Now we'll port the previous example to the GPU. First we will define a CUDA kernel to change the colors.

.. literalinclude::  test_example_code/TestExampleCodeCuda.cu
    :language: c++
    :dedent:
    :start-after: Begin CUDA code for prim processing on GPU example
    :end-before: End CUDA code for prim processing on GPU example

Next we make a prim selection and AttributeRef as before, then launch the CUDA kernel.

.. literalinclude::  test_example_code/TestExampleCode.cpp
    :language: c++
    :dedent:
    :start-after: Begin example processing prims by iterating over the prim selection on GPU
    :end-before: End example processing prims by iterating over the prim selection on GPU

**********************************
Re-using a selection across frames
**********************************

It is possible to safely re-use a selection across frames using the `PrepareForReuse`
API introduced in Kit SDK 106.5.

Under the hood, the selection generated by `SelectPrims` holds a Fabric Batch View -
this object is valid as long as there are no structural changes to Fabric,
like adding or removing prims or attributes. The writeable attributes in the Batch View
are also marked dirty in Fabric at the time of View creation.

`PrepareForReuse` checks if any structural changes have been made to Fabric since the last
call to this API - if there have been, the internally held Batch View is re-created,
which implicitly dirties the writable attributes in the selection in Fabric. `PrepareForReuse` will
return `true` in this case.

If there have not been any structural changes to Fabric, then `PrepareForReuse` will
simple mark all writable attributes in the selection as dirty in Fabric again (so that
downstream watchers of Fabric change tracking know that your forthcoming usage of the
selection potentially modified those attributes). In this case, `PrepareForReuse` will
return `false`.
