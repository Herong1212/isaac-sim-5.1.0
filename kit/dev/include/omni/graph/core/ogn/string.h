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
//    ogn::const_string  Read-only access to a string in fabric
//    ogn::string        Writable access to a string in fabric, with resizing and reallocation wrapped in
//                       string-like functions
//
// WARNING: These interfaces are subject to change without warning and are only meant to be used by generated code.
//          If you call them directly you may have to modify your code when they change.
// =================================================================================================================

#include <gsl/string_span>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/ogn/Types.h>

#include <algorithm>
#include <string>

namespace omni {
namespace graph {
namespace core {
namespace ogn {

/**
 * std::string_view-like wrapper class for string attribute data in the Ogn Database.
 * As of this writing OGN is built on C++14 and std::string_view requires C++17 so the Microsoft forward
 * compatible implementaton of gsl::string_span<> is used.
 * *
 * This wrapper operates by using the Fabric interface to interact with string data it has stored.
 * The base string class provides common operations common to both const and non-const data.
 */
template <typename CharType, typename HandleType>
class base_string : public base_array<CharType, HandleType>
{
public:
    /**
     * @return The number of elements in the currently managed array
     */
    size_t length() const
    {
        return this->size();
    }

    /**
     * Cast the string data to a std::string.
     *
     * After you do this the string data is now a copy of the original so you can manipulate it without
     * affecting the original, however it means you must reassign it back to a writable ogn::string if you
     * do want to change the string.
     *
     * @return String containing a copy of the internal raw string data
     */
    operator std::string() const
    {
        auto const& spanObj = this->span();
        if (spanObj.data())
        {
            return std::string{ spanObj.data(), spanObj.size() };
        }
        return std::string{};
    }

    /**
     * See if two strings are equal.
     *
     * These simple comparison operators avoid extra conversions to std::string, to help minimize allocations
     *
     * @tparam IterableStringType String variant that supports iteration for comparison
     * @param[in] rhs String to compare against - just requires iterability
     * @return True if the strings have the same contents
     */
    template <typename IterableStringType>
    bool operator==(const IterableStringType& rhs) const
    {
        return this->data() ? std::equal(this->begin(), this->end(), rhs.begin(), rhs.end()) : (rhs.begin() == rhs.end());
    }

    /**
     * See if two strings are not equal.
     *
     * These simple comparison operators avoid extra conversions to std::string, to help minimize allocations
     *
     * @tparam IterableStringType String variant that supports iteration for comparison
     * @param[in] rhs String to compare against - just requires iterability
     * @return True if the strings do not have the same contents
     */
    template <typename IterableStringType>
    bool operator!=(const IterableStringType& rhs) const
    {
        return this->data() ? !std::equal(this->begin(), this->end(), rhs.begin(), rhs.end()) :
                              (rhs.begin() != rhs.end());
    }

    /**
     * See if this string is lexicographically less than the provided one.
     *
     * These simple comparison operators avoid extra conversions to std::string, to help minimize allocations
     *
     * @tparam IterableStringType String variant that supports iteration for comparison
     * @param[in] rhs String to compare against - just requires iterability
     * @return True if this string is lexicographically less than the provided one
     */
    template <typename IterableStringType>
    bool operator<(const IterableStringType& rhs) const
    {
        return std::lexicographical_compare(this->begin(), this->end(), rhs.begin(), rhs.end());
    }

    /**
     * See if this string is lexicographically greater than the provided one.
     *
     * These simple comparison operators avoid extra conversions to std::string, to help minimize allocations
     *
     * @tparam IterableStringType String variant that supports iteration for comparison
     * @param[in] rhs String to compare against - just requires iterability
     * @return True if this string is lexicographically greater than the provided one
     */
    template <typename IterableStringType>
    bool operator>(const IterableStringType& rhs) const
    {
        return std::lexicographical_compare(rhs.begin(), rhs.end(), this->begin(), this->end());
    }

    /**
     * See if this string is lexicographically less than or equal to the provided one.
     *
     * These simple comparison operators avoid extra conversions to std::string, to help minimize allocations
     *
     * @tparam IterableStringType String variant that supports iteration for comparison
     * @param[in] rhs String to compare against - just requires iterability
     * @return True if this string is lexicographically less than or equal to the provided one
     */
    template <typename IterableStringType>
    bool operator<=(const IterableStringType& rhs) const
    {
        return operator<(rhs) || operator==(rhs);
    }

    /**
     * See if this string is lexicographically greater than or equal to the provided one.
     *
     * These simple comparison operators avoid extra conversions to std::string, to help minimize allocations
     *
     * @tparam IterableStringType String variant that supports iteration for comparison
     * @param[in] rhs String to compare against - just requires iterability
     * @return True if this string is lexicographically greater than or equal to the provided one
     */
    template <typename IterableStringType>
    bool operator>=(const IterableStringType& rhs) const
    {
        return operator>(rhs) || operator==(rhs);
    }
};

/**
 * std::string_view-like wrapper class for constant string attribute data in the Ogn Database.
 * It operates by using the Fabric interface to interact with string data it has stored.
 * This const version of the string wrapper should be used for input attributes, whose data cannot be changed.
 *
 */
class const_string : public base_string<const char, ConstAttributeDataHandle>
{
    // from regular attributes
    template <typename, eAttributeType, eMemoryType, PtrToPtrKind>
    friend struct ArrayAttribute;

    // from runtime attributes
    template <typename, bool, eMemoryType, PtrToPtrKind>
    friend struct ArrayData;


public:
    /**
     * Default constructor to start pointing to nothing.
     */
    const_string() = default;
};

/**
 * std::string_view-like class for string output attribute data in the Ogn Database.
 * It operates by using the Fabric interface to interact with string data it has stored.
 * This non-const version of the string wrapper should be used for output attributes, whose data will be changed.
 *
 */
class string : public base_string<char, AttributeDataHandle>
{
public:
    /** Type of the parent class */
    using parent_t = base_string<char, AttributeDataHandle>;
    // Make non-templated functions available to pass 1 of template resolution
    // http://www.gotw.ca/gotw/087.htm
    using base_string::data;
    using base_string::size;
    using base_string::reset;

    /**
     * Default constructor to start pointing to nothing.
     */
    string() = default;

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
        CUDA_SAFE_ASSERT(isValid());
        const IAttributeData& iData = *(this->context()->iAttributeData);
        iData.setElementCount(*this->context(), this->handle(), newCount);
        this->setDirty();
    }

    /**
     * @return Non-const pointer to the raw string data
     */
    char* data()
    {
        return const_cast<char*>(this->span().data());
    }

    /**
     * Access a specific character in the string. No bounds checking is performed.
     *
     * @param[in] index Element index into the string
     * @return Reference to the index'th character of the string
     */
    char& operator[](size_t index)
    {
        return const_cast<char&>(this->operator[](index));
    }

    /**
     * Access a specific character in the string. Bounds checking is performed.
     *
     * @param[in] index Element index into the string
     * @return Reference to the index'th character of the string
     */
    char& at(size_t index)
    {
        return const_cast<char&>(this->at(index));
    }


    /**
     * Assignment of a raw sized string to this object, used by all variations.
     *
     * This will create a duplicate of all string members and reset the references into the Fabric, leaving the
     * context and the handle unchanged.
     *
     * @param[in] dataToCopy The string being copied in
     * @param[in] charCount The number of characters in the string being copied
     * @return Pointer to this
     */
    string& assign(char const* dataToCopy, size_t charCount)
    {
        CUDA_SAFE_ASSERT(isValid());

        // Resize this string first so that it has the proper space to receive the new data
        resize(charCount);
        if (charCount == 0)
        {
            // No work to do when the new string is empty
            return *this;
        }
        std::memcpy(data(), dataToCopy, charCount);
        return *this;
    }

    /**
     * Generic string assignment operator
     *
     * This template handles all compatible string types with a data() and size() method. At minimum
     * ogn::string, ogn::const_string, std::string, const std::string
     *
     * @param[in] rhs The string being copied in
     * @return Pointer to this
     */
    template <typename StringType>
    string& operator=(StringType& rhs)
    {
        return assign(rhs.data(), rhs.size());
    }

    /**
     * const char* assignment operator (avoids alloc, and disambiguates between std::string and ogn::const_string)
     *
     * This will create a duplicate of all string members and reset the references into the Fabric, leaving the
     * context and the handle unchanged.
     *
     * @param[in] rhs The string being copied in
     * @return Pointer to this
     */
    string& operator=(const char* rhs)
    {
        const size_t MAX_SIZE = 1024*1024; // bound buffer to an arbitrary large size to avoid buffer overflow attacks
        size_t length = rhs ? strnlen(rhs, MAX_SIZE) : 0;
        bool overflow = length == MAX_SIZE;
        CUDA_SAFE_ASSERT(!overflow);
        return assign(rhs, !overflow ? length : 0);
    }

    /**
     * Standard method to clear a string, i.e. assign the empty string to it.
     * Since the null terminator is not needed in fabric the string truly is empty
     */
    void clear()
    {
        resize(0);
    }
};

} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
