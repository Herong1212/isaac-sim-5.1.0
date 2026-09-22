// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
namespace omni
{
namespace fabric
{
namespace batch
{

BATCH_SHARED_API inline bool View::isCpu() const
{
    return flags.isCpu;
}

BATCH_SHARED_API inline bool View::isGpu() const
{
    return !flags.isCpu;
}

BATCH_SHARED_API inline size_t View::count() const
{
    BATCH_ASSERT(indexEnd >= indexBegin);
    return indexEnd - indexBegin;
}

BATCH_SHARED_API inline size_t View::getElementSize(const AttributeRef& attributeRef) const
{
    BATCH_ASSERT(attributeRef < attributeCount);
    return deviceDataBuffers().elementSizes[attributeRef];
}

BATCH_SHARED_API inline SpanOf<const View::Attribute> View::getAttributes() const
{
    return SpanOf<const Attribute>{ deviceDataBuffers().attributes, elementRangesCount * attributeCount };
}

BATCH_SHARED_API inline SpanOf<const View::ElementRange> View::getElementRanges() const
{
    return SpanOf<const ElementRange>{ deviceDataBuffers().elementRanges, elementRangesCount };
}

BATCH_SHARED_API inline void View::slice(View& outLeft, View& outRight, const size_t length) const
{
    const size_t lengthAdjusted = length < count() ? length : count();
    const size_t sliceIndex = indexBegin + lengthAdjusted;

    static_assert(
        std::is_trivially_copy_assignable<View>::value, "expected std::is_trivially_copy_assignable<View>::value");
    View left = *this;
    View right = *this;

    {
        left.indexEnd = sliceIndex;
    }

    {
        size_t truncateCount = 0;
        const View::ElementRange* elementRange;
        if (!findElementRange(truncateCount, elementRange, sliceIndex))
        {
            static View::ElementRange __empty{};
            elementRange = &__empty;
        }
        BATCH_ASSERT(truncateCount <= elementRangesCount);

        right.indexBegin = sliceIndex;
        // right.elementSizes does not need to skip since it is defined per-attribute, not per-bucket
        right.deviceDataBuffers().elementRanges += truncateCount;
        right.deviceDataBuffers().attributes += (truncateCount * attributeCount);
        // right.paths does not need to skip since it is mapped to global indices, not view-space indices
        right.elementRangesCount -= truncateCount;
    }

    BATCH_ASSERT(left.count() + right.count() == count());
    outLeft = left;
    outRight = right;
}

BATCH_SHARED_API inline View::DeviceDataBuffers& View::deviceDataBuffers()
{
#if defined(__CUDACC__)
    return deviceDataBuffersGpu;
#else
    return deviceDataBuffersCpu;
#endif
}

BATCH_SHARED_API inline const View::DeviceDataBuffers& View::deviceDataBuffers() const
{
#if defined(__CUDACC__)
    return deviceDataBuffersGpu;
#else
    return deviceDataBuffersCpu;
#endif
}

BATCH_SHARED_API inline bool View::findElementRange(size_t& inOutElementRangesIndex,
                                                    const ElementRange*& outElementRange,
                                                    const size_t index) const
{
    static ElementRange __empty{};

    if (index < indexEnd)
    {
#if defined(__CUDACC__)
        // GPU uses a binary search to find the relevant View::ElementRange because access patterns
        // are effectively random access due to how GPU threads get mapped to View indices.
        {
            size_t l = inOutElementRangesIndex;
            size_t r = elementRangesCount - 1;
            while (l <= r)
            {
                const size_t elementRangesIndex = (l + r) / 2;
                const View::ElementRange& probe = deviceDataBuffers().elementRanges[elementRangesIndex];
                if (probe.indexEnd <= index)
                {
                    l = elementRangesIndex + 1;
                }
                else if (index < probe.indexBegin)
                {
                    r = elementRangesIndex - 1;
                }
                else
                {
                    inOutElementRangesIndex = elementRangesIndex;
                    outElementRange = &probe;
                    return true;
                }
            }
        }
#else // #if defined (__CUDACC__)
      // CPU uses a linear search to find the relevant View::ElementRange because access patterns
      // are effectively forward-access. There should be zero search misses on initialization because of a CPU-only
      // optimizations made during Batch::partitionView(...) where we artificially truncate the beginning of the
      // View::ElementRange* array to skip already-consumed ElementRanges used by previously sliced and enqueued Views.
        {
            size_t elementRangesIndex = inOutElementRangesIndex;
            while (1)
            {
                const View::ElementRange& probe = deviceDataBuffers().elementRanges[elementRangesIndex];
                if (index < probe.indexEnd)
                {
                    inOutElementRangesIndex = elementRangesIndex;
                    outElementRange = &probe;
                    return true;
                }

                ++elementRangesIndex;
            }
        }
#endif // #if defined (__CUDACC__)
    }

    inOutElementRangesIndex = 0;
    outElementRange = &__empty;
    return false;
}

BATCH_SHARED_API inline ViewIterator::ViewIterator(const View& view, const size_t index)
    : m_view(view),
      m_index(m_view.indexBegin + index),
      m_elementRangesIndex(0),
      m_elementRange(nullptr),
      m_element(View::kInvalidElement),
      m_spanOffset(View::kInvalidSpanOffset)
{
    // Note: We initialize m_index to m_view.indexBegin + index. This reads a bit obtuse, but it is correct.
    //
    // The user does not, and should not, know if the View they are using is the whole View or a slice of the View. For
    // CPU compute, it is likely they received a slice. For GPU compute, it is likely they received a whole View. For
    // slices, the m_view.indexBegin is shifted by Batch internals to restrict the View to a subrange of indices. If the
    // whole View represents [0, N), then the slice would be [i, j), where 0 <= i && i < j && j <= N. In other words,
    // there are two index spaces in play:
    //   - View space [0, N)
    //   - User space [i, j)
    // View::count() returns the length of user space indices. The addition above is effectively a shift from User space
    // to View space, which is necessary because View::ElementRange is all in View space.
}

BATCH_SHARED_API inline bool ViewIterator::peek()
{
    return findIndex();
}

BATCH_SHARED_API inline bool ViewIterator::advance(const size_t stride)
{
    if (findIndex())
    {
        m_index += stride;
        return true;
    }

    return false;
}

template <typename T>
BATCH_SHARED_API inline const T& ViewIterator::getAttributeRd(const AttributeRef& attributeRef) const
{
    return toScalar<const T>(attributeRef, readAttribute(attributeRef));
}

template <typename T>
BATCH_SHARED_API inline T& ViewIterator::getAttributeWr(const AttributeRef& attributeRef) const
{
    return toScalar<T>(attributeRef, writeAttribute(attributeRef));
}

template <typename T>
BATCH_SHARED_API SpanOf<const T> ViewIterator::getArrayAttributeRd(const AttributeRef& attributeRef) const
{
    return toArray<const T>(attributeRef, readAttribute(attributeRef));
}

template <typename T>
BATCH_SHARED_API SpanOf<T> ViewIterator::getArrayAttributeWr(const AttributeRef& attributeRef) const
{
    return toArray<T>(attributeRef, writeAttribute(attributeRef));
}

BATCH_SHARED_API inline size_t ViewIterator::getFabricId() const
{
    return m_view.deviceDataBuffers().fabricIds[m_elementRangesIndex];
}

BATCH_SHARED_API inline size_t ViewIterator::getGlobalIndex() const
{
    // We can't use m_index directly because depending on if the user did peek() or advance(),
    // the m_index might have advanced to the "next" index based on the given stride, whether
    // or not that "next" index is in bounds (handled by findIndex() for attribute data accessors).
    BATCH_ASSERT(m_element != View::kInvalidElement);
    BATCH_ASSERT(m_element >= m_elementRange->elementBegin);
    return m_element - m_elementRange->elementBegin + m_elementRange->indexBegin;
}

BATCH_SHARED_API inline size_t ViewIterator::getElementRangesIndex() const
{
    return m_elementRangesIndex;
}

BATCH_SHARED_API inline size_t ViewIterator::getElementIndex() const
{
    return m_element;
}

BATCH_SHARED_API inline size_t ViewIterator::getElementCount(const AttributeRef& attributeRef) const
{
    return m_elementRange->elementEnd - m_elementRange->elementBegin;
}

BATCH_SHARED_API inline uint64_t ViewIterator::getPath() const
{
    if (m_view.flags.isProvidingPaths)
    {
        const size_t idx = getGlobalIndex();
        BATCH_ASSERT(idx >= m_view.indexBegin);
        BATCH_ASSERT(idx < m_view.indexEnd);
        return m_view.deviceDataBuffers().paths[idx];
    }
    else
    {
        // I want to assert that 0 == kUninitializedPath here, but I can't because this file is included in CUDA code,
        // so I shoved this assert in Batch.cpp
        return 0;
    }
}

BATCH_SHARED_API inline bool ViewIterator::findIndex()
{
    if (!m_view.findElementRange(m_elementRangesIndex, m_elementRange, m_index))
    {
        return false;
    }

    m_spanOffset = m_elementRangesIndex * m_view.attributeCount;

    BATCH_ASSERT(m_elementRange);
    BATCH_ASSERT(m_elementRange->indexBegin <= m_index);
    BATCH_ASSERT(m_index < m_elementRange->indexEnd);
    const size_t offset = m_index - m_elementRange->indexBegin;
    m_element = m_elementRange->elementBegin + offset;

    return true;
}

BATCH_SHARED_API inline const View::Attribute& ViewIterator::getAttribute(const AttributeRef& attributeRef) const
{
    BATCH_ASSERT(attributeRef < m_view.attributeCount);
    BATCH_ASSERT(m_spanOffset != View::kInvalidSpanOffset);
    const size_t attributeIndex = m_spanOffset + attributeRef;
    BATCH_ASSERT(attributeIndex < m_view.elementRangesCount * m_view.attributeCount);
    return m_view.deviceDataBuffers().attributes[attributeIndex];
}

BATCH_SHARED_API inline const View::Attribute& ViewIterator::readAttribute(const AttributeRef& attributeRef) const
{
    return getAttribute(attributeRef);
}

BATCH_SHARED_API inline const View::Attribute& ViewIterator::writeAttribute(const AttributeRef& attributeRef) const
{
    BATCH_ASSERT(m_view.writeMask.test(attributeRef));
    return getAttribute(attributeRef);
}

template <typename T>
BATCH_SHARED_API inline T& ViewIterator::toScalar(const AttributeRef& attributeRef, const View::Attribute& attribute) const
{
    BATCH_ASSERT(sizeof(T) == m_view.deviceDataBuffers().elementSizes[attributeRef]);
    BATCH_ASSERT(m_element < m_elementRange->elementEnd);
    BATCH_ASSERT(attribute.lengths == View::Attribute::SCALAR_LENGTHS_SENTINEL_VALUE);
    return ((T*)attribute.values)[m_element];
}

template <typename T>
BATCH_SHARED_API inline SpanOf<T> ViewIterator::toArray(const AttributeRef& attributeRef,
                                                        const View::Attribute& attribute) const
{
    BATCH_ASSERT(sizeof(T) == m_view.deviceDataBuffers().elementSizes[attributeRef]);
    BATCH_ASSERT(m_element < m_elementRange->elementEnd);
    BATCH_ASSERT(attribute.lengths != View::Attribute::SCALAR_LENGTHS_SENTINEL_VALUE);
    return SpanOf<T>{ ((T**)attribute.values)[m_element], ((size_t*)attribute.lengths)[m_element] };
}

} // namespace batch
} // namespace fabric
} // namespace omni
