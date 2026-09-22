// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// =================================================================================================================
// This file contains simple interface classes which wrap data in the OGN database for easier use.
//
//    ArrayInput       Read-only wrapper for attributes that are arrays of values on CPU or GPU
//    ArrayOutput      Writable wrapper for attributes that are arrays of values on CPU or GPU
//
// WARNING: These interfaces are subject to change without warning and are only meant to be used by generated code.
//          If you call them directly you may have to modify your code when they change.
// =================================================================================================================

#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/ogn/Types.h>
#include <omni/graph/core/ogn/array.h>
#include <omni/graph/core/ogn/string.h>
#include <omni/fabric/Enums.h>
using omni::fabric::PtrToPtrKind;

namespace omni {
namespace graph {
namespace core {
namespace ogn {

// ==============================================================================================================
/** House the shared data types that will be used by all array type accessors.
 * Provides typedefs for data access with similar but subtly different types, e.g. const versus non-const
 * Its unowned data points to the real data in the fabric. It provides a consistent interface to the data,
 * with an isValid() method to use for compute validation and an appropriate operator() for data extraction.
 */
template <typename DataType, eAttributeType AttributeType, eMemoryType MemoryType = kCpu, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
struct ArrayAttribute
{
    // Make const-ness aware at compile time so that this class be used in const and non-const contexts
    static constexpr bool readOnly = (AttributeType == ogn::kOgnInput);

    using this_t = ArrayAttribute<DataType, AttributeType, MemoryType, GpuPtrType>;
    using data_t = DataType;
    using array_t = std::conditional_t<
        readOnly,
        std::conditional_t<std::is_same<const char, DataType>::value, const_string, const_array<std::remove_const_t<DataType>>>,
        std::conditional_t<std::is_same<char, DataType>::value, string, array<DataType>>
    >;
    using handle_t = std::conditional_t<readOnly, ConstAttributeDataHandle, AttributeDataHandle>;

    /**
     * Set up the accessor for attributes with array data
     *
     * @param[in] offset: A reference to the instance offset currently pointed by owning database
     * @param[in] role Attribute's role
     */
    ArrayAttribute(size_t const& offset, AttributeRole role = AttributeRole::eNone)
        : m_role(role),
          m_offset(offset),
          m_currentOffset(offset)
    {
        static_assert(readOnly == std::is_const<DataType>::value, "Cannot construct input attributes from non-const types");
    }

    /**
     * @return Role of the managed attribute
     */
    AttributeRole role() const
    {
        return m_role;
    }

    /**
     * Set the context. This is done to allow the same wrapper class to be used for
     * multiple evaluations in different contexts.
     *
     * @param[in] context The graph context to which the array belongs
     */
    void setContext(const GraphContextObj& context)
    {
        m_arrayData.setContext(context);
    }

    /**
     * Set the attribute handle. This is done to allow the same wrapper class to be used for
     * multiple evaluations in different contexts.
     *
     * @param[in] handle Handle to the attribute to which the array belongs
     */
    void setHandle(handle_t handle)
    {
        m_arrayData.setHandle(handle);
    }

    /**
     * Forces the array to re-fetch its pointers
     */
    void invalidateCachedPointer()
    {
        //array data needs to be re-fetched every frame,
        //  as any external change of the value might have invalidated the pointers
        m_arrayData.setDirty();
    }

    /**
     * @param[in] index: For vectorized compute, the instance index relative to the one currently pointed by the owning database
     * @return Reference to an array wrapper around the raw fabric CPU data
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type == kCpu>::type>
    const array_t& operator()(size_t index = 0) const
    {
        return cpu(index);
    }

    /**
     * @param[in] index: For vectorized compute, the instance index relative to the one currently pointed by the owning database
     * @return Reference to an array wrapper around the raw fabric GPU data
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type == kCuda>::type>
    const DataType** operator()(size_t index = 0) const
    {
        return gpu(index);
    }

    /**
     * @param[in] index: For vectorized compute, the instance index relative to the one currently pointed by the owning database
     * @return Reference to an array wrapper around the raw fabric CPU data
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type != kCuda>::type>
    const array_t& cpu(size_t index = 0) const
    {
        adjustHandle(index);
        return m_arrayData;
    }

    /**
     * @param[in] index: For vectorized compute, the instance index relative to the one currently pointed by the owning database
     * @return Reference to GPU data
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type != kCpu>::type>
    auto gpu(size_t index = 0) const
    {
        return gpuGet(abi_handle(index), context());
    }

    /**
     * Query the size of the underlying array
     * @param[in] index: For vectorized compute, the instance index relative to the one currently pointed by the owning database
     * @return the size of the underlying array
     */
    const size_t size(size_t index = 0) const
    {
        size_t count = 0;
        ConstAttributeDataHandle chdl = abi_handle(index);
        context()->iAttributeData->getElementCount(&count, *context(), &chdl, 1);
        return count;
    }

    /**
     * @return True if the underlying attribute data is valid for accessing
     */
    bool isValid() const
    {
        return m_arrayData.isValid();
    }

    /**
     * @param[in] index: For vectorized compute, the instance index relative to the one currently pointed by the owning database
     * @return A copy of the underlying ABI data handle for the attribute
     */
    handle_t abi_handle(size_t index = 0) const
    {
        adjustHandle(index);
        return m_arrayData.m_handle;
    }

    //@deprecated use abi_handle instead
    [[deprecated("Calling handle() is deprecated. Use abi_handle() instead")]]
    inline handle_t handle(size_t index = 0) const { return abi_handle(index);}

    /**
     * @return A copy of the underlying ABI data handle for the attribute
     */
    GraphContextObj const* context() const
    {
        return m_arrayData.m_context;
    }

    /**
     * @param[in] index: For vectorized compute, the instance index relative to the one currently pointed by the owning database
     * @param[in] defValue: The default value to return if the array is empty
     * @return the first item in the array, or the default value if the array is empty
     */
    const DataType& firstOrDefault(size_t index = 0,
                            const DataType& defValue = DataType())
    {
        return size(index) ? (*this)(index)[0] : defValue;
    }

protected:
    /**
     * Make the handle point to the proper instance, referred by its index, in a vectorized context
     * @param[in] index: For vectorized compute, the instance index relative to the one currently pointed by the owning database
     */
    void adjustHandle(size_t index) const
    {
        if (m_arrayData.isValid())
        {
            size_t wantedIndex = m_offset + index;
            if (m_currentOffset != wantedIndex)
            {
                const_cast<array_t&>(m_arrayData).adjustHandle(wantedIndex - m_currentOffset);
                m_currentOffset = wantedIndex;
            }
        }
    }

protected:
    //! Role interpretation for the attribute this struct manages
    AttributeRole m_role{ AttributeRole::eNone };

    //! Helper for accessing array data (last as it uses the others in initializing)
    array_t m_arrayData;

    //! Offset (in terms of objects) to apply to the fabric pointer to access the current object
    size_t const& m_offset;

    //! Offset at which the array data is currently configured
    size_t mutable m_currentOffset{ 0 };

private:
    //select appropriate ABI function based on handle type
    static const DataType** gpuGet(ConstAttributeDataHandle const& hdl, GraphContextObj const* ctx)
    {
        const DataType** ptrToData{ nullptr };
        ctx->iAttributeData->getDataRGpuAt((const void**)&ptrToData, *ctx, &hdl, 1, GpuPtrType);
        return ptrToData;
    }
    static DataType** gpuGet(AttributeDataHandle const& hdl, GraphContextObj const* ctx)
    {
        DataType** ptrToData{ nullptr };
        ctx->iAttributeData->getDataWGpuAt((void**)&ptrToData, *ctx, &hdl, 1, GpuPtrType);
        return ptrToData;
    }

};

// ======================================================================
/**
 * Wrapper template that handles arrays of input attribute values.
 */
template <typename DataType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
using ArrayInput = ArrayAttribute<std::add_const_t<DataType>, kOgnInput, MemoryType, GpuPtrType>;

// ======================================================================
/**
 * Handle arrays of output attribute values.
 * It adds methods that provide write access to the underlying attribute data onto the functionality of ArrayInput.
 */
template <typename DataType, eAttributeType AttributeType, eMemoryType MemoryType = kCpu, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
struct ArrayWritableAttribute : public ArrayAttribute<DataType, AttributeType, MemoryType, GpuPtrType>
{
    // Make const-ness aware at compile time so that this class be used in const and non-const contexts
    static constexpr bool readOnly = (AttributeType == ogn::kOgnInput);

    using parent_t = ArrayAttribute<DataType, AttributeType, MemoryType, GpuPtrType>;
    using data_t = typename parent_t::data_t;
    using handle_t = typename parent_t::handle_t;
    using array_t = typename parent_t::array_t;
    using this_t  = ArrayWritableAttribute<DataType, AttributeType, MemoryType, GpuPtrType>;

    /**
     * Set up the accessor for output attributes with array data
     *
     * @param[in] offset: A reference to the instance offset currently pointed by owning database
     * @param[in] role Attribute's role
     */
    ArrayWritableAttribute(size_t const& offset, AttributeRole role = AttributeRole::eNone)
        : parent_t(offset, role)
    {
    }

    /**
     * @param[in] offset: A reference to the instance offset currently pointed by owning database
     * @return Reference to an array wrapper around the raw fabric CPU data
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type == kCpu>::type>
    array_t& operator()(size_t index = 0)
    {
        //always go through fetch for array as it has special treatment in datamodel
        return cpu(index);
    }

    /**
     * @param[in] offset: A reference to the instance offset currently pointed by owning database
     * @return Reference to an array wrapper around the raw fabric GPU data
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type == kCuda>::type>
    data_t** operator()(size_t index = 0)
    {
        // always go through fetch for array as it has special treatment in datamodel
        return gpu(index);
    }

    /**
     * @param[in] offset: A reference to the instance offset currently pointed by owning database
     * @return Reference to an array wrapper around the raw fabric CPU data
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type != kCuda>::type>
    array_t& cpu(size_t index = 0)
    {
        auto const* const_this = this;
        auto const& ret = const_this->parent_t::cpu(index);
        return const_cast<array_t&>(ret);
    }

    /**
     * @param[in] offset: A reference to the instance offset currently pointed by owning database
     * @return Reference to an array wrapper around the raw fabric GPU data
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type != kCpu>::type>
    data_t** gpu(size_t index = 0)
    {
        auto const* const_this = this;
        auto ret = const_this->parent_t::gpu(index);
        return const_cast<data_t**>(ret);
    }


    /**
     * Resize of the underlying array
     * @input newSize: the size to set for the underlying array
     * @input index: the index of the instance to query in a vectorized context
     */
    const void resize(size_t newSize, size_t index = 0)
    {
        auto& ctx = *this->context();
        ctx.iAttributeData->setElementCount(ctx, this->abi_handle(index), newSize);
        this->m_arrayData.setDirty();
    }

    /**
    * Copy some array data to another through the ABI
    * Will handle all the underlying optimizations (such as CoW or DataStealing)
    *
    * @return Reference to itself
    */
    this_t& operator=(const ArrayInput<DataType, MemoryType, GpuPtrType>& toBeCopied) { return shallowCopy(toBeCopied);}

    // @param[in] index: For vectorized compute, the instance index relative to the one currently pointed by the owning database
    this_t& shallowCopy(const ArrayInput<DataType, MemoryType, GpuPtrType>& toBeCopied, size_t index = 0)
    {
        const IAttributeData& iData = *(this->context()->iAttributeData);
        iData.copyData(this->abi_handle(index), *this->context(), toBeCopied.abi_handle(index));

        this->m_arrayData.setDirty();

        return *this;
    }
};

// Convenience types for distinguishing output and state attributes
template <typename DataType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
using ArrayOutput = ArrayWritableAttribute<DataType, kOgnOutput, MemoryType, GpuPtrType>;
template <typename DataType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
using ArrayState = ArrayWritableAttribute<DataType, kOgnState, MemoryType, GpuPtrType>;


// Backward compatibility for previously existing data types
template <typename DataType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
using DualArrayInput = ArrayInput<DataType, kAny, GpuPtrType>;
template <typename DataType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
using DualArrayOutput = ArrayOutput<DataType, kAny, GpuPtrType>;

} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
