// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
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
//    ogn::const_array  Read-only array of fabric data
//    ogn::array        Array of fabric data, with writing and resizing capabilities
//
// WARNING: These interfaces are subject to change without warning and are only meant to be used by generated code.
//          If you call them directly you may have to modify your code when they change.
// =================================================================================================================

#include <gsl/span>
#include <cstring>
#include <stdexcept>
#include <type_traits>

#include <omni/graph/core/Handle.h>
#include <omni/graph/core/CudaUtils.h>
#include <omni/graph/core/iAttributeData.h>
#include <omni/graph/core/ogn/Types.h>

using omni::fabric::PtrToPtrKind;

namespace omni {
namespace graph {
namespace core {
namespace ogn {

// =================================================================================================================
/**
 * std::span-like wrapper class for array attribute data in the Ogn Database.
 *
 * In attribute terms an array is a variable sized collection of data of a single type, not to be confused with
 * the C++ notion of an array, which is a fixed sized collection of data of a single type.
 *
 * This wrapper operates by using the Fabric interface to interact with array data it has stored.
 * The base array class provides common operations common to both const and non-const data.
 *
 * @tparam BaseDataType Type of data contained within the array
 * @tparam HandleType Attribute handle used to access the underlying Fabric copy of the data
 */
template <typename BaseDataType, typename HandleType>
class base_array
{
    //from regular attributes
    template <typename, eAttributeType, eMemoryType, PtrToPtrKind>
    friend struct ArrayAttribute;

    //from runtime attributes
    template <typename, bool, eMemoryType, PtrToPtrKind >
    friend struct ArrayData;

public:
    /** const version of the BaseDataType */
    using ConstBaseDataType = const typename std::remove_const<BaseDataType>::type;
    /** Type definition of this class */
    using this_t = base_array<BaseDataType, HandleType>;
    // Pass through the span iterator so that this class can iterate over it transparently
    /** Iterator over the array contents */
    using iterator = typename gsl::span<BaseDataType>::iterator;
    /** Reverse iterator over the array contents */
    using reverse_iterator = typename gsl::span<BaseDataType>::reverse_iterator;

    /**
     * Constructor
     */
    base_array() = default;

    /**
     * Confirm that the data values are safe for accessing
     *
     * @return true if the context and attribute handle values are both valid
     */
    bool isValid() const
    {
        return context() && (AttrKey)handle() != handle().invalidValue();
    }

    /**
     * @return The number of elements in the currently managed array
     */
    size_t size() const { return span().size();}

    /**
     * @return Is the currently managed array empty?
     */
    bool empty() const { return span().empty(); }

    /**
     * @return Pointer to the raw data in the array (first element)
     */
    ConstBaseDataType* data() const { return span().data();}

    /**
     * @return Iterator pointing to the beginning of the array
     */
    const iterator begin() const { return span().begin(); }

    /**
     * @return Iterator pointing past the end of the array
     */
    const iterator end() const { return span().end(); }

    /**
     * @return Iterator pointing to the end of the array
     */
    const reverse_iterator rbegin() const { return span().rbegin(); }

    /**
     * @return Iterator pointing before the beginning of the array
     */
    const reverse_iterator rend() const { return span().rend(); }

    /**
     * Access a specific element of the array. No bounds checking is performed.
     *
     * @param[in] index Element index into the array
     * @return Reference to the index'th element of the array
     */
    ConstBaseDataType& operator[](size_t index) const { return span()[index]; }

    /**
     * Access a specific element of the array with bounds checking.
     *
     * @param[in] index Element index into the array
     * @return Reference to the index'th element of the array
     * @exception std::out_of_range if there is no data for the given index
     */
    ConstBaseDataType& at(size_t index) const
    {
        auto const& spanObj = span();
        if (!spanObj.data() || (spanObj.size() <= index))
        {
            std::string rangeMessage("Attempt to access out of range index ");
            rangeMessage += std::to_string(index);
            throw std::out_of_range(rangeMessage);
        }
        return spanObj[index];
    }

    /**
     * Access the underlying span that allows to access the array data
     *
     * @return A reference to the underlying span
     */
    gsl::span<BaseDataType> const& span() const
    {
        if (m_dirty)
            const_cast<this_t*>(this)->reset();
        m_dirty = false;
        return m_span;
    }
    /**
     * @brief Access the context to which this array belongs
     *
     * @returns Pointer to the context to which this array belongs
     */
    GraphContextObj const* context() const { return m_context;}
    /**
     * @brief Access the attribute handle used to access the array data in Fabric
     *
     * @returns Pointer to the attribute handle used to access the array data in Fabric
     */
    HandleType const& handle() const { return m_handle;}

    /**
     * Flag the span data as not being up2Date
     *
     */
    void setDirty() const { m_dirty = true; }

    /**
     * In a vectorized context, move forward the current handle
     *
     * @param[in] idx The amount of instance(s) to offset the current handle
     */
    void adjustHandle(size_t idx)
    {
        const IAttributeData& iData = *(context()->iAttributeData);
        moveHdl(iData, idx, m_handle);
        setDirty();
    }

protected:
    /**
     * Reset the internal span to point to new data.
     *
     */
    void reset()
    {
        if (isValid())
        {
            const IAttributeData& iData = *(m_context->iAttributeData);
            size_t count = 0;
            ConstAttributeDataHandle chdl = m_handle;
            iData.getElementCount(&count, *m_context, &chdl, 1);
            BaseDataType** ptrToData = getData(iData, m_handle);
            this->m_span = gsl::span<BaseDataType>(*ptrToData, count);
        }
        else
        {
            this->m_span = gsl::span<BaseDataType>();
        }
    }

    /**
     * @brief Get a pointer to the array data from a specific const data handle
     *
     * @param iData Interface class containing the accessor functions
     * @param hdl Handle to the attribute data whose value is being retrieved
     * @return BaseDataType** Pointer to the array of retrieved data
     */
    BaseDataType** getData(const IAttributeData& iData, ConstAttributeDataHandle const& hdl)
    {
        BaseDataType** ptrToData = nullptr;
        iData.getDataR((const void**)&ptrToData, *m_context, &hdl, 1);
        return ptrToData;
    }
    /**
     * @brief Get a pointer to the array data from a specific mutable data handle
     *
     * @param iData Interface class containing the accessor functions
     * @param hdl Handle to the attribute data whose value is being retrieved
     * @return BaseDataType** Pointer to the array of retrieved data
     */
    BaseDataType** getData(const IAttributeData& iData, AttributeDataHandle const& hdl)
    {
        BaseDataType** ptrToData = nullptr;
        iData.getDataW((void**)&ptrToData, *m_context, &hdl, 1);
        return ptrToData;
    }

    /**
     * Set the context. This is done to allow the same wrapper class to be used for
     * multiple evaluations in different contexts.
     *
     * @param[in] context The graph context to which the array belongs
     */
    void setContext(const GraphContextObj& context)
    {
        m_context = &context;
        setDirty();
    }

    /**
     * Set the attribute handle. This is done to allow the same wrapper class to be used for
     * multiple evaluations in different contexts.
     *
     * @param[in] handle Handle to the attribute to which the array belongs
     */
    void setHandle(HandleType handle)
    {
        m_handle = handle;
        setDirty();
    }

private:

    /**
     * helper that allows to make the proper call depending on the type of the handle
     */
    void moveHdl(const IAttributeData& iData, size_t index, ConstAttributeDataHandle& hdl) const
    {
        hdl = iData.moveToAnotherInstanceR(*m_context, hdl, (int)index);
    }
    void moveHdl(const IAttributeData& iData, size_t index, AttributeDataHandle& hdl) const
    {
        hdl = iData.moveToAnotherInstanceW(*m_context, hdl, (int)index);
    }

    const GraphContextObj* m_context{ nullptr };        //!< The graph context to which the array belongs
    HandleType m_handle{ HandleType::invalidValue() };  //!< Handle to the attribute data
    bool mutable m_dirty { true };                      //!< whether the span is uptodate or not
    gsl::span<BaseDataType> m_span;                     //!< Iterable managed array data
};

// =================================================================================================================
/**
 * std::vector-like wrapper class for constant array attribute data in the Ogn Database.
 * It operates by using the Fabric interface to interact with array data it has stored.
 * This const version of the array wrapper should be used for input attributes, whose data cannot be changed.
 * (The naming is "array" for consistency with how attribute types are named, even though it doesn't
 * behave like a std::array, whose content size is determined at compile time.)
 *
 * @tparam BaseDataType Type of data contained within the array
 */
template <typename BaseDataType>
class const_array : public base_array<const BaseDataType, ConstAttributeDataHandle>
{
public:
    /**
     * Constructor
     */
    const_array() = default;
};

// =================================================================================================================
/**
 * std::vector-like wrapper class for array attribute data in the Ogn Database.
 * It operates by using the Fabric interface to interact with array data it has stored.
 * This non-const version of the array wrapper should be used for output attributes, whose data will be changed.
 * (The naming is "array" for consistency with how attribute types are named, even though it doesn't
 * behave like a std::array, whose content size is determined at compile time.)
 *
 * @tparam BaseDataType Type of data contained within the array
 */
template <typename BaseDataType>
class array : public base_array<BaseDataType, AttributeDataHandle>
{
public:
    /** The type of the parent class */
    using parent_t = base_array<BaseDataType, AttributeDataHandle>;
    // Make non-templated functions available to pass 1 of template resolution
    // http://www.gotw.ca/gotw/087.htm
    using parent_t::data;
    using parent_t::size;

    // Pass through the span iterator so that this class can iterate over it transparently
    /** Iterator over the array contents */
    using iterator = typename gsl::span<BaseDataType>::iterator;
    /** Reverse iterator over the array contents */
    using reverse_iterator = typename gsl::span<BaseDataType>::reverse_iterator;

    /**
     * Constructor
     */
    array() = default;

    /**
     * Assignment operator: performs a shallow copy
     *
     * @param[in] rhs The array being copied in
     * @return Reference to this
     */
    array& operator=(array<BaseDataType> const& rhs)
    {
        return shallowCopy(reinterpret_cast<const_array<BaseDataType> const&>(rhs));
    }
    /**
     * Assignment operator: performs a shallow copy of a const array of const data
     *
     * @param[in] rhs The array being copied in
     * @return Reference to this
     */
    array& operator=(const_array<const BaseDataType> const& rhs)
    {
        return shallowCopy(reinterpret_cast<const_array<BaseDataType> const&>(rhs));
    }
    /**
     * Assignment operator: performs a shallow copy of a const array of non-const data
     *
     * @param[in] rhs The array being copied in
     * @return Reference to this
     */
    array& operator=(const_array<BaseDataType> const& rhs)
    {
        return shallowCopy(rhs);
    }

    /**
     * Performs a shallow copy the provided object over this object
     *
     * This will create a reference for this object that points to the provided object
     *
     * @param[in] from The array being copied in
     * @return Reference to this
     */
    array& shallowCopy(const_array<BaseDataType> const& from)
    {
        this->context()->iAttributeData->copyData(this->handle(), *this->context(), from.handle());
        this->setDirty();

        return *this;
    }

    /**
     * Overwrite this object data with data from the provided object
     *
     * This will create a duplicate of all array members and reset the references
     *
     * @param[in] rhs The array being copied in
     * @return Reference to this
     */
    array& deepCopy(parent_t const& rhs)
    {
        // Resize this array first so that it has the proper space to receive the new data
        resize(rhs.size());
        if (rhs.size() == 0)
        {
            // No work to do when the new array is empty
            return *this;
        }

        // Get the raw arrays and walk them directly for the copy to minimize friction.
        rawCopyFrom(rhs.data(), std::conditional_t<std::is_assignable<BaseDataType, std::add_const_t<BaseDataType>>::value,
                                                   std::true_type, std::false_type>());

        return *this;
    }

    /**
     * Set the size of the array data to a new value.
     *
     * This may or may not relocate memory. If anything is holding a raw pointer from contents()
     * that pointer should be refreshed by calling contents() again when this method returns.
     *
     * @param[in] newCount New element count of the array.
     */
    void resize(size_t newCount)
    {
        CUDA_SAFE_ASSERT(this->isValid());
        const IAttributeData& iData = *(this->context()->iAttributeData);
        iData.setElementCount(*this->context(), this->handle(), newCount);
        this->setDirty();
    }

    /**
     * @return Non-const pointer to the raw data in the array (first element)
     */
    BaseDataType* data()
    {
        return const_cast<BaseDataType*>(this->parent_t::data());
    }

    /**
     * Access a specific element of the array. No bounds checking is performed.
     *
     * @param[in] index Element index into the array
     * @return Reference to the index'th element of the array
     */
    BaseDataType& operator[](size_t index)
    {
        return const_cast<BaseDataType&>(this->parent_t::operator[](index));
    }

    /**
     * Access a specific element of the array with bounds checking.
     *
     * @param[in] index Element index into the array
     * @return Reference to the index'th element of the array
     * @exception std::out_of_range if there is no data for the given index
     */
    BaseDataType& at(size_t index)
    {
        return const_cast<BaseDataType&>(this->parent_t::at(index));
    }

private:
    /**
     * Safe copy; one version for when the array members are assignable, the other as a fallback to do raw memcpy
     *
     * @param[in] srcArray The location of the raw data to be copied in (already vetted for size compatibility)
     * @param[in] assignable Overload selected when the base data type can or cannot be assigned
     */
    void rawCopyFrom(const BaseDataType* srcArray, std::true_type assignable)
    {
        auto dstArray = data();
        for (size_t i = 0; i < size(); ++i)
        {
            dstArray[i] = srcArray[i];
        }
    }
    void rawCopyFrom(const BaseDataType* srcArray, std::false_type assignable)
    {
        memcpy(data(), srcArray, sizeof(BaseDataType) * size());
    }
};

/** Default trait indicating if the class is one of our array types
 * @tparam T Class type to check for being an array
 */
template<class T>
struct is_array : std::false_type {};

/** Trait indicating that specific templated types are array types
 * @tparam T Class type to check for being an array
 * @tparam HandleType Attribute data handle type for the array
 */
template<class T, typename HandleType>
struct is_array<base_array<T, HandleType>> : std::true_type {};

/** Trait indicating that mutable templated types are array types
 * @tparam T Class type to check for being an array
 */
template<class T>
struct is_array<array<T>> : std::true_type {};

/** Trait indicating that constant templated types are array types
 * @tparam T Class type to check for being an array
 */
template<class T>
struct is_array<const_array<T>> : std::true_type {};

} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
