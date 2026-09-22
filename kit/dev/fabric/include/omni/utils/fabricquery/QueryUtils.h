// Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "Query.h"

namespace query
{
    template<typename T, typename RowT>
    bool canRead(const RowT& row)
    {
        using Read = typename RowT::QueryT::Read;
        static constexpr const size_t I = Read::template getIdx<T>();
        return std::get<I>(row.read.refs).ptr != nullptr;
    }

    template<typename T, typename RowT>
    const auto& read(const RowT& row)
    {
        using Read = typename RowT::QueryT::Read;
        static constexpr const size_t I = Read::template getIdx<T>();
        return row.read.template get<I>();
    }

    template<typename T, typename RowT>
    bool canWrite(const RowT& row)
    {
        using Write = typename RowT::QueryT::Write;
        static constexpr const size_t I = Write::template getIdx<T>();
        return std::get<I>(row.write.refs).ptr != nullptr;
    }

    template<typename T, typename RowT>
    auto& write(RowT& row)
    {
        using Write = typename RowT::QueryT::Write;
        static constexpr const size_t I = Write::template getIdx<T>();
        return row.write.template get<I>();
    }

    template<typename T, typename RowT>
    auto& writeAdd(RowT& row)
    {
        using Add = typename RowT::QueryT::Add;
        static constexpr const size_t I = Add::template getIdx<T>();
        return row.add.template get<I>();
    }

    template<typename RowT>
    omni::fabric::PathC getPath(query::TransformContext& context, RowT& row)
    {
        return row.pathArray.ptr[row.row];
    }

    template<typename RowT>
    bool isNew(RowT& row)
    {
        return row.isNew;
    }

    template<typename T, typename RowT>
    void addDeferred(RowT& row, const Path& path, const typename T::ValueT& value)
    {
        using AddDeferred = typename RowT::QueryT::AddDeferred;
        static constexpr const size_t I = AddDeferred::template getIdx<T>();
        row.addDeferred.push_back({ path, I, value });
    }

    template<typename T, typename RowT>
    void addDeferred(query::TransformContext& context, RowT& row, const typename T::ValueT& value)
    {
        using AddDeferred = typename RowT::QueryT::AddDeferred;
        static constexpr const size_t I = AddDeferred::template getIdx<T>();
        addDeferred<T>(row, getPath(context, row), value);
    }

    template<typename T, typename RowT>
    void addDeferred(RowT& row, const Path& path, const typename T::ArrayT* value, size_t elemCount)
    {
        using AddDeferred = typename RowT::QueryT::AddDeferred;
        static constexpr const size_t I = AddDeferred::template getIdx<T>();

        size_t dataSize = (sizeof(typename T::ArrayT) * elemCount + sizeof(size_t) * 2 - 1) / sizeof(size_t);
        size_t* data = elemCount ? new size_t[dataSize] : nullptr;
        if (elemCount)
        {
            *data = elemCount;
            std::memcpy(data + 1, value, sizeof(typename T::ArrayT) * elemCount);
        }
        row.addDeferred.push_back({ path, I, data });
    }

    template<typename T, typename RowT>
    void addDeferred(query::TransformContext& context, RowT& row, const typename T::ArrayT* value, size_t elemCount)
    {
        addDeferred<T>(row, getPath(context, row), value, elemCount);
    }

    omni::fabric::PathC getParent(query::TransformContext& context, omni::fabric::PathC path)
    {
        return context.path ? context.path->getParent(path) : 0;
    }

    template<typename RowT>
    omni::fabric::PathC getParent(query::TransformContext& context, RowT& row)
    {
        return getParent(context, getPath(context, row));
    }

    template<typename RowT, typename... ArgTypes>
    void create(query::TransformContext& context, RowT& row, const omni::fabric::PathC& newPath, const ArgTypes&... args)
    {
        row.createRow(context.db, newPath, args...);
    }

    template<typename T>
    typename T::ValueT const* getRead(query::TransformContext& context, const omni::fabric::PathC& path)
    {
        return typename T::ValueT{};
        /*
        if (T::isElemCount)
        {
            return (typename T::ValueT const*)context.attributeMap.getArrayAttributeSizeRd(path, omni::fabric::Token(T::usdName)); // conversion to token here is slow
        }
        else
        {
            return context.attributeMap.getAttributeRd<typename T::ValueT>(path, omni::fabric::Token(T::usdName)); // conversion to token here is slow
        }
        */
    }

    template<typename T>
    size_t* getWriteCount(query::TransformContext& context, const omni::fabric::PathC& path)
    {
        CARB_CHECK(false);
        return nullptr;
        //return context.attributeMap.getArrayAttributeSizeWr(path, omni::fabric::Token(T::usdName)); // conversion to token here is slow
    }

    template<typename T>
    typename T::ValueT* getWrite(query::TransformContext& context, const omni::fabric::PathC& path)
    {
        CARB_CHECK(false);
        return nullptr;
        /*
        if (T::isElemCount)
        {
            return (typename T::ValueT*)context.attributeMap.getArrayAttributeSizeWr(path, omni::fabric::Token(T::usdName)); // conversion to token here is slow
        }
        else
        {
            return context.attributeMap.getAttributeWr<typename T::ValueT>(path, omni::fabric::Token(T::usdName)); // conversion to token here is slow
        }
        */
    }

    template<typename T>
    typename T::ValueT* getWriteNoAlloc(query::TransformContext& context, const omni::fabric::PathC& path)
    {
        CARB_CHECK(false);
        return nullptr;
        /*
        static_assert(!T::isElemCount, "Fast element count access not supported yet");
        return context.attributeMap.getAttributeWrFast<typename T::ValueT>(path, omni::fabric::Token(T::usdName), flatcache::NameSuffix::none); // conversion to token here is slow
        */
    }

    template<typename T>
    bool readArray(query::TransformContext& context, const omni::fabric::PathC& path, std::vector<typename T::ArrayT>& values)
    {
        CARB_CHECK(false);
        return false;
        /*
        if (typename T::ValueT const* source = getRead<T>(context, path))
        {
            size_t count = *context.attributeMap.getArrayAttributeSizeRd(path, omni::fabric::Token(T::usdName));
            values.resize(count);
            if (count)
            {
                memcpy(values.data(), *source, count * sizeof(T::ArrayT));
            }
            return true;
        }
        else
        {
            return false;
        }
        */
    }

    template<typename RowT>
    size_t getGatherIndex(RowT& row)
    {
        return row.gatherIdx;
    }

    template<typename RowT>
    size_t getGatherCount(RowT& row)
    {
        return row.gatherCount;
    }

    template<typename RowT>
    auto& getThreadStorage(RowT& row)
    {
        CARB_ASSERT(row.threadStorage);
        return *row.threadStorage;
    }
}
