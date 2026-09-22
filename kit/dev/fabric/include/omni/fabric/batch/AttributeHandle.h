// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "BatchFilter.h"
#include "View.h"
#include "Types.h"

namespace omni
{
namespace fabric
{
namespace batch
{

template<typename T>
struct AttributeReadHandle
{
    inline AttributeReadHandle()
    : ref(0)
    {
    }

    inline AttributeReadHandle(BatchFilter& filter, const omni::fabric::AttrNameAndType& nameAndType)
    {
        assign(filter, nameAndType);
    }

    inline ~AttributeReadHandle(){}

    inline void assign(BatchFilter& filter, const omni::fabric::AttrNameAndType& nameAndType)
    {
        ref = filter.readAttribute(nameAndType);
    }

    inline const T& operator()(const ViewIterator& iter) const
    {
        return iter.getAttributeRd<T>(ref);
    }

    AttributeRef ref;
};

template<typename T>
struct AttributeWriteHandle
{
    inline AttributeWriteHandle()
    : ref(0)
    {
    }

    inline AttributeWriteHandle(BatchFilter& filter, const omni::fabric::AttrNameAndType& nameAndType)
    {
        assign(filter, nameAndType);
    }

    inline ~AttributeWriteHandle(){}

    inline void assign(BatchFilter& filter, const omni::fabric::AttrNameAndType& nameAndType)
    {
        ref = filter.writeAttribute(nameAndType);
    }

    inline T& operator()(const ViewIterator& iter) const
    {
        return iter.getAttributeWr<T>(ref);
    }

    AttributeRef ref;
};

template<typename T>
struct AttributeReadWriteHandle
{
    inline AttributeReadWriteHandle()
    : ref(0)
    {
    }

    inline AttributeReadWriteHandle(BatchFilter& filter, const omni::fabric::AttrNameAndType& nameAndType)
    {
        assign(filter, nameAndType);
    }

    inline ~AttributeReadWriteHandle(){}

    inline void assign(BatchFilter& filter, const omni::fabric::AttrNameAndType& nameAndType)
    {
        ref = filter.readWriteAttribute(nameAndType);
    }

    inline T& operator()(const ViewIterator& iter) const
    {
        return iter.getAttributeWr<T>(ref);
    }

    AttributeRef ref;
};

} // namespace batch
} // namespace fabric
} // namespace omni
