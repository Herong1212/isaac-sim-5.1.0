// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/CppWrappers.h>
#include <omni/graph/core/ogn/TypeConversion.h>
#include <omni/graph/core/ogn/Types.h>

// =================================================================================================================
// This file contains simple interface classes which wrap data in the OGN database for easier use.
//
//    SimpleInput    Read-only wrapper for simple (POD and tuple) attribute values on CPU or GPU
//    SimpleOutput   Writable data wrapper for simple (POD and tuple) attribute values on CPU or GPU
//
// WARNING: These interfaces are subject to change without warning and are only meant to be used by generated code.
//          If you call them directly you may have to modify your code when they change.
// =================================================================================================================

namespace omni {
namespace graph {
namespace core {
namespace ogn {


// ======================================================================
/**
 * Wrapper template that handles POD input attribute values.
 * Its unowned data points to the real data in the fabric. It provides
 * a consistent interface to the data with a isValid() method and an operator(),
 * as well as enforcing const-correctness with the values.
 *
 * Rather than split this into CPU and GPU versions some key methods are enabled by template based
 * on the template parameter. This avoids duplication of the common code and reduces clutter.
 *
 * The data in this class is owned by the OGN generated code, this class only maintains pointers to those references.
 * By doing this, those generated references can be updated from fabric and this class will automatically pick up
 * the change, avoiding the need for synchronization code.
 */

template <typename DataType, eAttributeType AttributeType, eMemoryType MemoryType = kCpu>
struct SimpleAttribute
{
    // Make const-ness aware at compile time so that this class be used in const and non-const contexts
    static constexpr bool readOnly = (AttributeType == ogn::kOgnInput);

    using data_t = DataType;
    using handle_t = std::conditional_t<readOnly, ConstAttributeDataHandle, AttributeDataHandle>;

    /**
     * Set up the accessor for input attributes with simple data
     *
     * @param[in] offset: A reference to the instance offset currently pointed by owning database
     * @param[in] role Attribute's role
     */
    SimpleAttribute(size_t const& offset, AttributeRole role = AttributeRole::eNone) : m_role(role), m_offset(offset)
    {
        static_assert(readOnly == std::is_const<DataType>::value, "Cannot construct input attributes from non-const types");
    }

    /**
     * Set up the accessor for input attributes with simple data where the data pointer is known at construction time
     *
     * @param[in] dataPtr Pointer to the attribute's data
     * @param[in] role Attribute's role
     */
    SimpleAttribute(size_t const& offset, data_t* dataPtr, AttributeRole role = AttributeRole::eNone)
        : m_ptrToData{ dataPtr }, m_role(role), m_offset(offset)
    {}

    /**
     * @param[in] idx: For vectorized compute, the instance index/offset relative to the one currently pointed by the owning database
     * @return Reference to the raw fabric data extracted for use on the CPU
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type != kCuda>::type>
    const DataType& cpu(size_t idx = 0) const
    {
        // Cast is necessary to generically handle both const and non-const internal data
        m_ptrToData = (data_t*)getDataR<DataType>(*m_context, m_handle);
        return m_ptrToData[m_offset+idx];
    }

    /**
     * @param[in] idx: For vectorized compute, the instance index/offset relative to the one currently pointed by the owning database
     * @return Pointer to the raw fabric data extracted for use on the GPU
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type != kCpu>::type>
    const DataType* gpu(size_t idx = 0) const
    {
        // Cast is necessary to generically handle both const and non-const internal data
        m_ptrToData = (data_t*)getDataRGPU<DataType>(*m_context, m_handle);
        return m_ptrToData + m_offset + idx;
    }

    /**
     * Set the context. This is done to allow the same wrapper class to be used for
     * multiple evaluations in different contexts.
     *
     * @param[in] context The graph context to which the attribute belongs
     */
    void setContext(const GraphContextObj& context)
    {
        m_context = &context;
    }

    /**
     * Set the attribute handle. This is done to allow the same wrapper class to be used for
     * multiple evaluations in different contexts.
     *
     * @param[in] handle Handle to the attribute to which the attribute belongs
     */
    void setHandle(handle_t handle)
    {
        m_handle = handle;
        m_ptrToData = nullptr;
    }

    /**
     * Forces the wrapper to re-fetch the dat apointer on next access.
     */
    void invalidateCachedPointer()
    {
        m_ptrToData = nullptr;
    }

    /**
     * @return Role of the managed attribute
     */
    AttributeRole role() const
    {
        return m_role;
    }

    /**
     * @return True if the underlying attribute data is valid for accessing
     */
    template <eMemoryType Type = MemoryType>
    bool isValid() const
    {
        return m_handle.isValid();
    }

protected:
    mutable data_t* m_ptrToData{ nullptr }; //!< Cached pointer to fabric data
    AttributeRole m_role{ AttributeRole::eNone }; //!< Role interpretation for the attribute this struct manages
    const GraphContextObj* m_context{ nullptr }; //!< ABI OmniGraph object, for JIT access to data
    handle_t m_handle{ handle_t::invalidValue() }; //!< Handle to this attribute's data, for JIT access to data
    mutable Type m_originalDataType{ BaseDataType::eUnknown }; //!< The actual type of the underlying data in fabric
                                                               //!< (used for auto conversion)
    size_t const& m_offset; //!< An offset (in terms of object count) to apply to the pointer to access the object
};

// ======================================================================
/**
 * Wrapper template that handles POD input attribute values.
 */
template <typename DataType, eMemoryType MemoryType = kCpu>
struct SimpleInput : public SimpleAttribute<std::add_const_t<DataType>, kOgnInput, MemoryType>
{
    using parent_t = SimpleAttribute<DataType, kOgnInput, MemoryType>;
    using data_t = typename parent_t::data_t;
    using handle_t = typename parent_t::handle_t;

    /**
     * Set up the accessor for input attributes with simple data
     *
     * @param[in] offset: A reference to the instance offset currently pointed by owning database
     * @param[in] role: Attribute's role
     */
    SimpleInput(size_t const& offset, AttributeRole role = AttributeRole::eNone) : parent_t(offset, role)
    {
    }

    /**
     * @param[in] idx: For vectorized compute, the instance index/offset relative to the one currently pointed by the owning database
     * @return Reference to the raw fabric data; only enabled when it lives on the CPU
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type == kCpu>::type>
    const DataType& operator()(size_t idx = 0) const
    {
        auto& data = this->m_ptrToData == nullptr ? this->template cpu<Type>(idx) : this->m_ptrToData[idx+this->m_offset];
        if (this->m_originalDataType.baseType == BaseDataType::eUnknown)
        {
            if (this->m_context)
                this->m_originalDataType = this->m_context->iAttributeData->getType(*this->m_context, this->m_handle);
            else
                return data;
        }
        return *converter.convertValue(&data, this->m_originalDataType);
    }

    /**
     * @param[in] idx: For vectorized compute, the instance index/offset relative to the one currently pointed by the owning database
     * @return Pointer to the raw flatcache data (or the converted value); only enabled when it lives on the GPU
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type == kCuda>::type>
    const DataType* operator()(size_t idx = 0) const
    {
        if (!this->m_context->iAttributeData->gpuValid(this->m_handle, *this->m_context))
            this->m_ptrToData = nullptr;

        return this->m_ptrToData == nullptr ? this->template gpu<Type>(idx) : (this->m_ptrToData + idx + this->m_offset);
    }

    /**
     * @return True if the attribute can be accessed for vectorized compute
     */
    bool const canVectorize() const
    {
        if (this->m_originalDataType.baseType == BaseDataType::eUnknown)
        {
            if (this->m_context)
                this->m_originalDataType = this->m_context->iAttributeData->getType(*this->m_context, this->m_handle);
            else
                return false;
        }
        return converter.willConvert(this->m_originalDataType) == false;
    }

    /**
     * @param[in] count: The number of instances available for vectorized access
     * @return A span for the vectorized range if available. If not available, user must call operator() in a loop with incremented indices instead
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type == kCpu>::type>
    gsl::span<DataType const> vectorized(size_t count) const
    {
        auto& data = this->m_ptrToData == nullptr ? this->template cpu<Type>() : this->m_ptrToData[this->m_offset];
        if (this->m_originalDataType.baseType == BaseDataType::eUnknown)
        {
            if (this->m_context)
                this->m_originalDataType = this->m_context->iAttributeData->getType(*this->m_context, this->m_handle);
            else
                return { &data, count };
        }
        if (converter.willConvert(this->m_originalDataType))
        {
            if (count != 1)
                return {};
            return { converter.convertValue(&data, this->m_originalDataType), count /*= 1*/ };
        }

        return { &data, count };
    }

    /**
     * @param[in] index: For vectorized compute, the instance index/offset relative to the one currently pointed by the owning database
     * @return A copy of the underlying ABI data handle for the attribute
     */
    handle_t abi_handle(size_t index = 0) const
    {
        size_t const idx = this->m_offset + index;
        return idx == 0 ? this->m_handle :
                   this->m_context->iAttributeData->moveToAnotherInstanceR(*this->m_context, this->m_handle, (int)idx);
    }

private:
    Converter<DataType> converter;
};

// ======================================================================
/**
 * Wrapper template that handles POD output attribute values.
 * It adds methods that provide write access to the underlying attribute data onto the functionality of SimpleInput.
 */
template <typename DataType, eAttributeType AttributeType, eMemoryType MemoryType = kCpu>
struct SimpleWritableAttribute : public SimpleAttribute<DataType, AttributeType, MemoryType>
{
    using parent_t = SimpleAttribute<DataType, AttributeType, MemoryType>;
    using data_t = typename parent_t::data_t;
    using handle_t = typename parent_t::handle_t;

    /**
     * Set up the accessor for output attributes with simple data
     *
     * @param[in] offset: A reference to the instance offset currently pointed by owning database
     * @param[in] Attribute's role
     */
    SimpleWritableAttribute(size_t const& offset, AttributeRole role = AttributeRole::eNone) : parent_t(offset, role)
    {
    }

    /**
     * Query if the attribute can be accessed in a vectorized manner
     * @return True: SimpleWritableAttribute can always vectorize
     */
    bool const canVectorize() const
    {
        return true;
    }

    /**
     * @return A span for the vectorized range
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type == kCpu>::type>
    gsl::span<DataType> vectorized(size_t count)
    {
        if (this->m_ptrToData)
            return { this->m_ptrToData + this->m_offset, count };
        return { &cpu(), count };
    }

    /**
     * @param[in] idx: For vectorized compute, the instance index/offset relative to the one currently pointed by the owning database
     * @return Reference to the raw fabric data; only enabled when it lives on the CPU
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type == kCpu>::type>
    DataType& operator()(size_t idx = 0) const
    {
        if (this->m_ptrToData)
            return this->m_ptrToData[idx+this->m_offset];
        return cpu(idx);
    }

    /**
     * @param[in] idx: For vectorized compute, the instance index/offset relative to the one currently pointed by the owning database
     * @return Pointer to the raw fabric data; only enabled when it lives on the GPU
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type == kCuda>::type>
    DataType* operator()(size_t idx = 0) const
    {
        if (!this->m_context->iAttributeData->gpuValid(this->m_handle, *this->m_context))
            this->m_ptrToData = nullptr;
        if (this->m_ptrToData)
            return this->m_ptrToData + idx + this->m_offset;
        return gpu(idx);
    }

    /**
     * @param[in] idx: For vectorized compute, the instance index/offset relative to the one currently pointed by the owning database
     * @return Reference to the raw fabric data extracted for use on the CPU
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type != kCuda>::type>
    DataType& cpu(size_t idx = 0) const
    {
        this->m_ptrToData = getDataW<DataType>(*this->m_context, this->m_handle);
        return this->m_ptrToData[idx+this->m_offset];
    }

    /**
     * @param[in] idx: For vectorized compute, the instance index/offset relative to the one currently pointed by the owning database
     * @return Pointer to the raw fabric data extracted for use on the GPU
     */
    template <eMemoryType Type = MemoryType, typename = typename std::enable_if<Type != kCpu>::type>
    DataType* gpu(size_t idx = 0) const
    {
        this->m_ptrToData = getDataWGPU<DataType>(*this->m_context, this->m_handle);
        return this->m_ptrToData + idx + this->m_offset;
    }

    /**
     * @param[in] index: For vectorized compute, the instance index/offset relative to the one currently pointed by the owning database
     * @return A copy of the underlying ABI data handle for the attribute
     */
    handle_t abi_handle(size_t index = 0) const
    {
        size_t const idx = this->m_offset + index;
        return idx == 0 ? this->m_handle :
                   this->m_context->iAttributeData->moveToAnotherInstanceW(*this->m_context, this->m_handle, (int)idx);
    }
};

// Typedefs to differentiate state from output types
template <typename DataType, eMemoryType MemoryType = kCpu>
using SimpleOutput = SimpleWritableAttribute<DataType, kOgnOutput, MemoryType>;
template <typename DataType, eMemoryType MemoryType = kCpu>
using SimpleState = SimpleWritableAttribute<DataType, kOgnState, MemoryType>;


// Backward compatibility for previously existing data types
template <typename DataType>
using DualInput = SimpleInput<DataType, kAny>;
template <typename DataType>
using DualOutput = SimpleOutput<DataType, kAny>;


} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
