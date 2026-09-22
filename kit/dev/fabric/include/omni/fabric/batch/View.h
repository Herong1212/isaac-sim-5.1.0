// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <cstddef>
#include <cstdint>

#include <omni/fabric/batch/forward.h>
#include <omni/fabric/batch/Defines.h>
#include <omni/fabric/batch/Types.h>

namespace omni
{
namespace fabric
{
namespace batch
{

// At the heart of Batch API's user model is the View. The View represents the results of a BatchFilter. It conceptually
// condenses all filtered prims into one location, even if Fabric internals have chosen to arrange data fragmented
// across multiple segments.
//
// Here are some key takeaways about the View model:
//
// * A View contains a single range of prim indices [0, N).
// * View indices are not synonymous with prim indices / elements of an Attribute span returned by IFabric APIs.
// * Views are cheap to copy. No deep copy of data will occur in doing so.
// * Views (and related support classes) are available in both CPU and GPU kernels.
//
// An initial glance of the public interface might surprise the reader that the View definition is mostly private. This
// is to allow development flexibility in case internal representation changes are needed. Don't worry, the data is
// still accessible.
//
// To interact with prims in a View, acquire a ViewIterator into it. The ViewIterator allows fast random- or
// forward-iterative access to prims within a View. See ViewIterator for more details.
//
struct View
{
    struct Attribute
    {
        static constexpr uintptr_t SCALAR_LENGTHS_SENTINEL_VALUE = 0u;
        uintptr_t values; // scalar attribute values require single dereference, array attribute values require double
                          // dereference, and should be length-checked
        uintptr_t lengths; // scalar attribute length a sentinel value of 0, array attribute length requires single
                           // dereference
    };

    //
    // [elementBegin, elementEnd) is the Fabric Bucket space element range
    // [indexBegin, indexEnd) is in Fabric Batch API View space index range
    //
    // [indexBegin, indexEnd) is a projection of [elementBegin, elementEnd) onto View index space.
    struct ElementRange
    {
        size_t elementBegin;
        size_t elementEnd;

        size_t indexBegin;
        size_t indexEnd;
    };

    // Returns true if this View's memory is Cpu-backed, false otherwise
    BATCH_SHARED_API bool isCpu() const;

    // Returns true if this View is Gpu-backed, false otherwise
    BATCH_SHARED_API bool isGpu() const;

    // Returns N, the length of the View's index range. I.e. a View represents prim indices [0, count()).
    BATCH_SHARED_API size_t count() const;

    // Access the elementSize for the given AttributeRef
    BATCH_SHARED_API size_t getElementSize(const AttributeRef& attributeRef) const;

    // Returns all Attributes contained within this View
    BATCH_SHARED_API SpanOf<const Attribute> getAttributes() const;

    // Returns all ElementRanges contained within this View
    BATCH_SHARED_API SpanOf<const ElementRange> getElementRanges() const;

    // Given the current View with indices [indexBegin, indexEnd), and some 'length', slice the View into two parts:
    //   * Left Slice  [indexBegin, indexBegin + length)
    //   * Right Slice [indexBegin + length, indexEnd)
    // Returns a pair of Views representing the Left and Right slice.
    // Each slice is internally organized to speed up in-kernel access given the new index restrictions
    // This is fairly cheap to do, no deep data copies are incurred.
    BATCH_SHARED_API void slice(View& outLeft, View& outRight, const size_t length) const;

private:
    friend struct omni::fabric::batch::detail::Batch;
    friend struct ViewBuffers;
    friend struct ViewIterator;

    static constexpr size_t kInvalidElement = SIZE_MAX;
    static constexpr size_t kInvalidSpanOffset = SIZE_MAX;

    struct Flags
    {
        bool isCpu : 1; // 1 == CPU compute, 0 == GPU compute
        bool isProvidingPaths : 1; // 1 == getPath() is supported
        bool unused : 6; // can add future flags here
    };

    struct DeviceDataBuffers
    {
        size_t* elementSizes; // 1 per attribute
        ElementRange* elementRanges; // 1 per bucket
        Attribute* attributes; // 1 per (bucket, attribute)
        uint64_t* fabricIds; // 1 per bucket
        uint64_t* paths; // 1 per index
    };

    BATCH_SHARED_API DeviceDataBuffers& deviceDataBuffers();
    BATCH_SHARED_API const DeviceDataBuffers& deviceDataBuffers() const;

    BATCH_SHARED_API bool findElementRange(size_t& inOutElementRangesIndex,
                                           const ElementRange*& outElementRange,
                                           const size_t index) const;

    size_t indexBegin;
    size_t indexEnd;
    size_t elementRangesCount;
    AttributeRef attributeCount;
    Flags flags;
    uint8_t padding[6]; // lost to alignment
    DeviceDataBuffers deviceDataBuffersCpu;
    DeviceDataBuffers deviceDataBuffersGpu; // TODO: MGPU support
    WriteMask writeMask;
};

// The ViewIterator allows fast random- or forward-iterative access to prims within a View.
//
// A ViewIterator can be initialized and used as a random-access iterator for any index within a View's range:
//
//     AttributeRef ref;
//     ...
//     ViewIterator iter(view, <random index>);
//     if (iter.peek())
//     {
//         const float& value = iter.getCpuRd(ref);
//     }
//
// The caller must always peek() before acquiring any data using the ViewIterator when using random-access patterns.
//
// A ViewIterator can be used to forward-iterate through prims in a View:
//
//    AttributeRef ref;
//    ...
//    omni::fabric::batch::ViewIterator iter(view);
//    while(iter.advance())
//    {
//         const float& value = iter.getCpuRd(ref);
//    }
//
// The caller must always advance() before acquiring any data using the ViewIterator when using forward-iterative-access
// patterns.
//
struct ViewIterator
{
    // Constructs a ViewIterator given a View and initial View index.
    // After construction, the caller MUST peek() or advance() before using any of the getXXX functions.
    BATCH_SHARED_API ViewIterator(const View& view, const size_t index = 0);

    // Peeks at the current index, and checks if it is valid within the View's index range.
    // Seeks internal state to point to Fabric data matching the current index.
    BATCH_SHARED_API bool peek();

    // Peeks at the current index, and checks if it is valid within the View's index range.
    // Seeks internal state to point to Fabric data matching the current index.
    // If the peek was successful, this advances the current index AFTER the seek.
    BATCH_SHARED_API bool advance(const size_t stride = 1);

    // Access read-only scalar data for the given AttributeRef
    template <typename T>
    BATCH_SHARED_API const T& getAttributeRd(const AttributeRef& attributeRef) const;

    // Access writable scalar data for the given AttributeRef
    template <typename T>
    BATCH_SHARED_API T& getAttributeWr(const AttributeRef& attributeRef) const;

    // Access read-only array data for the given AttributeRef
    template <typename T>
    BATCH_SHARED_API SpanOf<const T> getArrayAttributeRd(const AttributeRef& attributeRef) const;

    // Access writable array data for the given AttributeRef
    template <typename T>
    BATCH_SHARED_API SpanOf<T> getArrayAttributeWr(const AttributeRef& attributeRef) const;

    // Get the FabricId this View references
    BATCH_SHARED_API uint64_t getFabricId() const;

    // Get the current global index in View index space (all prims across many buckets)
    BATCH_SHARED_API size_t getGlobalIndex() const;

    // Get the current ElementRanges index.
    // This is unique, and typically 1:1 with buckets, but not guaranteed in the case of View splicing
    BATCH_SHARED_API size_t getElementRangesIndex() const;

    // Get the current element index in bucket index space (prim indices within a single bucket)
    BATCH_SHARED_API size_t getElementIndex() const;

    // Get the total number of elements in bucket index space (prim indices within a single bucket)
    BATCH_SHARED_API size_t getElementCount(const AttributeRef& attributeRef) const;

    // Returns the uint64_t encoding of a PathC for the current element index
    BATCH_SHARED_API uint64_t getPath() const;

private:
    BATCH_SHARED_API bool findIndex();

    BATCH_SHARED_API const View::Attribute& getAttribute(const AttributeRef& attributeRef) const;
    BATCH_SHARED_API const View::Attribute& readAttribute(const AttributeRef& attributeRef) const;
    BATCH_SHARED_API const View::Attribute& writeAttribute(const AttributeRef& attributeRef) const;

    template <typename T>
    BATCH_SHARED_API T& toScalar(const AttributeRef& attributeRef, const View::Attribute& attribute) const;

    template <typename T>
    BATCH_SHARED_API SpanOf<T> toArray(const AttributeRef& attributeRef, const View::Attribute& attribute) const;

    const View& m_view;

    size_t m_index;
    size_t m_elementRangesIndex;
    const View::ElementRange* m_elementRange;
    size_t m_element;
    size_t m_spanOffset;
};

} // namespace batch
} // namespace fabric
} // namespace omni

#include "impl/View.inl"
