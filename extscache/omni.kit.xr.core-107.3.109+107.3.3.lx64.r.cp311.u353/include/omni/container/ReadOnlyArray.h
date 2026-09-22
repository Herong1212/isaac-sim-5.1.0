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

#include <omni/container/IReadOnlyArray.h>

#include <memory>
#include <set>
#include <vector>

namespace omni
{
namespace container
{

template <typename T>
class ReadOnlyTypedArray : public omni::core::Implements<omni::container::IReadOnlyArray>
{
public:
    ReadOnlyTypedArray(const std::vector<T>& data) : m_array(data)
    {
    }

    ReadOnlyTypedArray(const std::set<T>& data)
    {
        m_array.insert(m_array.begin(), data.begin(), data.end());
    }

    virtual void* getData_abi() noexcept override
    {
        return reinterpret_cast<void*>(m_array.data());
    }

    virtual size_t getSize_abi() noexcept override
    {
        return m_array.size();
    }

    virtual size_t getElementSize_abi() noexcept override
    {
        return sizeof(T);
    }

    static omni::core::ObjectPtr<IReadOnlyArray> create()
    {
        std::vector<T> data; // empty array
        return { new ReadOnlyTypedArray(data), omni::core::kSteal };
    }

    static omni::core::ObjectPtr<IReadOnlyArray> create(const std::vector<T>& data)
    {
        return { new ReadOnlyTypedArray(data), omni::core::kSteal };
    }

    static omni::core::ObjectPtr<IReadOnlyArray> create(const std::set<T>& data)
    {
        return { new ReadOnlyTypedArray(data), omni::core::kSteal };
    }

private:
    std::vector<T> m_array;
};


template <typename T, typename U>
class ReadOnlyTypedArrayWithInternalData : public omni::core::Implements<omni::container::IReadOnlyArray>
{
public:
    ReadOnlyTypedArrayWithInternalData(const std::vector<T>& data, std::shared_ptr<U> internalData)
        : m_array(data), m_internalData(internalData)
    {
    }

    ReadOnlyTypedArrayWithInternalData(const std::set<T>& data, std::shared_ptr<U> internalData)
    {
        m_array.insert(m_array.begin(), data.begin(), data.end());
        m_internalData = internalData;
    }

    virtual void* getData_abi() noexcept override
    {
        return reinterpret_cast<void*>(m_array.data());
    }

    virtual size_t getSize_abi() noexcept override
    {
        return m_array.size();
    }

    virtual size_t getElementSize_abi() noexcept override
    {
        return sizeof(T);
    }

    static omni::core::ObjectPtr<IReadOnlyArray> create()
    {
        std::vector<T> data; // empty array
        return { new ReadOnlyTypedArrayWithInternalData(data), omni::core::kSteal };
    }

    static omni::core::ObjectPtr<IReadOnlyArray> create(const std::vector<T>& data, std::shared_ptr<U> internalData)
    {
        return { new ReadOnlyTypedArrayWithInternalData(data, internalData), omni::core::kSteal };
    }

    static omni::core::ObjectPtr<IReadOnlyArray> create(const std::set<T>& data, std::shared_ptr<U> internalData)
    {
        return { new ReadOnlyTypedArrayWithInternalData(data, internalData), omni::core::kSteal };
    }

private:
    std::vector<T> m_array;
    std::shared_ptr<U> m_internalData;
};

template <typename T>
class ReadOnlyObjectArray : public omni::core::Implements<omni::container::IReadOnlyArray>
{
public:
    ReadOnlyObjectArray(const std::vector<omni::core::ObjectPtr<T>>& data) : m_array(data)
    {
        m_ptrArray.resize(m_array.size());
        for (size_t idx = 0; idx < m_array.size(); ++idx)
        {
            m_ptrArray[idx] = m_array[idx].get();
        }
    }

    virtual void* getData_abi() noexcept override
    {
        return reinterpret_cast<void*>(m_ptrArray.data());
    }

    virtual size_t getSize_abi() noexcept override
    {
        return m_ptrArray.size();
    }

    virtual size_t getElementSize_abi() noexcept override
    {
        return sizeof(T*);
    }

    static omni::core::ObjectPtr<IReadOnlyArray> create(const std::vector<omni::core::ObjectPtr<T>>& data)
    {
        return { new ReadOnlyObjectArray(data), omni::core::kSteal };
    }

    static omni::core::ObjectPtr<IReadOnlyArray> create()
    {
        std::vector<omni::core::ObjectPtr<T>> empty;
        return { new ReadOnlyObjectArray(empty), omni::core::kSteal };
    }

private:
    std::vector<omni::core::ObjectPtr<T>> m_array;
    std::vector<T*> m_ptrArray;
};

class ReadOnlyStringArray : public omni::core::Implements<omni::container::IReadOnlyArray>
{
public:
    ReadOnlyStringArray(const std::vector<std::string>& data) : m_string_array(data)
    {
        for (auto& str : m_string_array)
        {
            m_array.push_back(str.c_str());
        }
    }

    ReadOnlyStringArray(const std::set<std::string>& data)
    {
        for (auto& str : data)
        {
            m_string_array.push_back(str);
            // Add from the m_string_array here so the pointer stays valid
            m_array.push_back(m_string_array.back().c_str());
        }
    }

    virtual void* getData_abi() noexcept override
    {
        return reinterpret_cast<void*>(m_array.data());
    }

    virtual size_t getSize_abi() noexcept override
    {
        return m_array.size();
    }

    virtual size_t getElementSize_abi() noexcept override
    {
        return sizeof(const char*);
    }

    static omni::core::ObjectPtr<IReadOnlyArray> create(const std::vector<std::string>& data)
    {
        return { new ReadOnlyStringArray(data), omni::core::kSteal };
    }

    static omni::core::ObjectPtr<IReadOnlyArray> create(const std::set<std::string>& data)
    {
        return { new ReadOnlyStringArray(data), omni::core::kSteal };
    }

private:
    std::vector<const char*> m_array;
    std::vector<std::string> m_string_array;
};


} // namespace container
} // namespace omni
