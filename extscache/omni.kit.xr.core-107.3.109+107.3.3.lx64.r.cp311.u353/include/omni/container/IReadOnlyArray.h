// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include <omni/core/IObject.h>

#include <set>
#include <string>
#include <vector>

namespace omni
{
namespace container
{

OMNI_DECLARE_INTERFACE(IReadOnlyArray);

class IReadOnlyArray_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.container.IReadOnlyArray")>
{
protected:
    /**
     * Get pointer to array of pointers
     */
    virtual void* getData_abi() noexcept = 0;

    /**
     * Get size of array
     */
    virtual size_t getSize_abi() noexcept = 0;

    /**
     * Get size of each element in the array
     */
    virtual size_t getElementSize_abi() noexcept = 0;
};

} // namespace container
} // namespace omni

template <>
class omni::core::Generated<omni::container::IReadOnlyArray_abi> : public omni::container::IReadOnlyArray_abi
{
public:
    inline void* getData() noexcept
    {
        return getData_abi();
    }

    inline size_t getSize() noexcept
    {
        return getSize_abi();
    }

    inline size_t getElementSize() noexcept
    {
        return getElementSize_abi();
    }

    inline void* get_data() noexcept
    {
        return getData_abi();
    }

    inline size_t get_size() noexcept
    {
        return getSize_abi();
    }

    inline size_t get_element_size() noexcept
    {
        return getElementSize_abi();
    }
};

namespace omni
{
namespace container
{
using IReadOnlyArrayPtr = omni::core::ObjectPtr<omni::container::IReadOnlyArray>;

// Convenience function that rebuilds a std::vector object from a ReadOnlyArray container
// Note: this function releases the array object at the end of the function

template <typename T>
inline std::vector<T> convertReadOnlyTypedArray(omni::container::IReadOnlyArray* arr)
{
    if (arr == nullptr)
    {
        return std::vector<T>();
    }

    // Sanity check Ensure that struct size is still the same
    CARB_ASSERT(arr->getElementSize() == sizeof(T));

    std::vector<T> result(reinterpret_cast<T*>(arr->getData()), reinterpret_cast<T*>(arr->getData()) + arr->getSize());
    arr->release();
    return result;
}

template <typename T>
inline std::set<T> convertReadOnlyTypedArrayToSet(omni::container::IReadOnlyArray* arr)
{
    if (arr == nullptr)
    {
        return std::set<T>();
    }
    // Sanity check Ensure that struct size is still the same
    CARB_ASSERT(arr->getElementSize() == sizeof(T));

    std::set<T> result(reinterpret_cast<T*>(arr->getData()), reinterpret_cast<T*>(arr->getData()) + arr->getSize());
    arr->release();
    return result;
}

// Convenience function that rebuilds a vector with strings
// Note: this function releases the array object at the end of the function

inline std::vector<std::string> convertReadOnlyStringArray(omni::container::IReadOnlyArray* arr)
{
    if (arr == nullptr)
    {
        return std::vector<std::string>();
    }

    // Sanity check Ensure that struct size is still the same
    CARB_ASSERT(arr->getElementSize() == sizeof(const char*));

    const char** data = reinterpret_cast<const char**>(arr->getData());
    size_t size = arr->getSize();
    std::vector<std::string> result(size);
    for (size_t idx = 0; idx < size; ++idx)
    {
        result[idx] = data[idx];
    }

    arr->release();
    return result;
}

// Convenience function that rebuilds a vector with strings
// Note: this function releases the array object at the end of the function

// TODO: Should deprecate this one
template <typename T, typename U>
inline std::vector<U> convertReadOnlyTypedStealObjectArray(omni::container::IReadOnlyArray* arr)
{
    if (arr == nullptr)
    {
        return std::vector<U>();
    }

    // Sanity check Ensure that struct size is still the same
    CARB_ASSERT(arr->getElementSize() == sizeof(T));

    size_t size = arr->getSize();
    std::vector<U> result(size);
    T* data = reinterpret_cast<T*>(arr->getData());

    for (size_t idx = 0; idx < size; ++idx)
    {
        result[idx] = omni::core::steal(data[idx]);
    }

    arr->release();

    return result;
}

// Convenience function that rebuilds a vector with strings
// Note: this function releases the array object at the end of the function

template <typename T, typename U>
inline std::vector<U> convertReadOnlyArrayToObjectArray(omni::container::IReadOnlyArray* arr)
{
    if (arr == nullptr)
    {
        return std::vector<U>();
    }

    // Sanity check Ensure that struct size is still the same
    CARB_ASSERT(arr->getElementSize() == sizeof(T));

    size_t size = arr->getSize();
    std::vector<U> result(size);
    T* data = reinterpret_cast<T*>(arr->getData());

    for (size_t idx = 0; idx < size; ++idx)
    {
        result[idx] = omni::core::borrow(data[idx]);
    }

    arr->release();

    return result;
}

}
}
