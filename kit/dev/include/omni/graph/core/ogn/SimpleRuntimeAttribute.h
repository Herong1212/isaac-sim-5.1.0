// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/ogn/RuntimeAttribute.h>
#include <omni/graph/core/ogn/SimpleAttribute.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace ogn
{


template <typename RTAttrib>
struct SimpleRTAttrib
{
    using dataHandle_t = typename RTAttrib::dataHandle_t;
    using attrib_t = typename std::remove_const<RTAttrib>::type;
    using this_t = SimpleRTAttrib<RTAttrib>;

private:
    size_t const& m_offset;
    attrib_t m_attrib;
    size_t m_rootHandleOffset{0};
    bool m_dirty{ false };
    AttributeObj m_dirtyPendingObj;
    
public:
    SimpleRTAttrib(size_t const& offset)
        : m_offset(offset)
    {}

    SimpleRTAttrib(SimpleRTAttrib const& other) = default;
    SimpleRTAttrib(SimpleRTAttrib&&) = default;
    SimpleRTAttrib& operator=(SimpleRTAttrib const& other)
    {
        const_cast<size_t&>(m_offset) = other.m_offset;
        m_attrib = other.m_attrib;
        m_rootHandleOffset = other.m_rootHandleOffset;
        m_dirty = other.m_dirty;
        m_dirtyPendingObj = other.m_dirtyPendingObj;
        return *this;
    }
    SimpleRTAttrib& operator=(SimpleRTAttrib&&) = default;

    /**
     * @return Reference to the inner runtime attribute
     */
    RTAttrib& operator()(size_t index = 0)
    {
        static const dataHandle_t kInvalidHandle = dataHandle_t{ dataHandle_t::invalidValue() };

        if (m_dirty)
        {
            auto hdl = m_dirtyPendingObj.iAttribute->getAttributeDataHandle(m_dirtyPendingObj, { m_rootHandleOffset });
            m_attrib.reset(m_attrib.abi_context(), hdl, m_dirtyPendingObj);
            m_dirtyPendingObj = { nullptr, kInvalidAttributeHandle };
            m_dirty = false;
        }

        //if our attrib already points to something...
        if (m_attrib.abi_handle() != kInvalidHandle)
        {
            //check that this something is actually the asked instance
            auto offset = index + m_offset;
            if (offset != m_rootHandleOffset)
            {
                //if not, make it point to the proper instance
                m_attrib.adjustHandle(offset - m_rootHandleOffset);
                //... and keep trace of which instance is currently pointed
                m_rootHandleOffset = offset;
            }
        }
        return m_attrib;
    }
    RTAttrib const& operator()(size_t index = 0) const
    {
        return const_cast<this_t*>(this)->operator()(index);
    }

    /**
     * Forces the wrapper to re-fetch the data pointer on next access.
     */
    void invalidateCachedPointer()
    {
        m_attrib.invalidateCachedPointer();
    }

    /**
     * @return True if the attribute can be accessed for vectorized compute
     */
    bool const canVectorize() const
    {
        return m_attrib.canVectorize();
    }
    
    void const fetchDetails(const AttributeObj& attr)
    {
        //This is called on type resolution changes, lots of other changes are probably going to happen on the graph
        // So do not fetch anything right away at this would force a useless graph bucket creation,
        // and just defer the fetch on first access
        m_dirty = true;
        m_dirtyPendingObj = attr;
    }
};


template <eAttributeType AttributeType, eMemoryType MemoryType, eMemoryType DUMMY, PtrToPtrKind GpuPtrType>
struct SimpleInput<const RuntimeAttribute<AttributeType, MemoryType, GpuPtrType>, DUMMY>
    : public SimpleRTAttrib< const RuntimeAttribute<AttributeType, MemoryType, GpuPtrType> >
{
    using super = SimpleRTAttrib< const RuntimeAttribute<AttributeType, MemoryType, GpuPtrType> >;
    SimpleInput(size_t const& offset) : super(offset) {}
};

template <eAttributeType AttributeType, eMemoryType MemoryType, eMemoryType DUMMY, PtrToPtrKind GpuPtrType>
struct SimpleWritableAttribute<RuntimeAttribute<AttributeType, MemoryType, GpuPtrType>, AttributeType, DUMMY>
    : public SimpleRTAttrib< RuntimeAttribute<AttributeType, MemoryType, GpuPtrType> >
{
    using super = SimpleRTAttrib< RuntimeAttribute<AttributeType, MemoryType, GpuPtrType> >;
    SimpleWritableAttribute(size_t const& offset) : super(offset) {}
};


} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
