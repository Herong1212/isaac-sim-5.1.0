// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "GpuArray.h"

#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/Accessors.h>

namespace omni {
namespace graph {
namespace core {

template <typename T>
struct GpuArray;

template <typename T>
struct ConstGpuArray;

// Convenience function to retrieve an attribute data handle given the attribute.  The
// attribute data handle is needed to retrieve the data of the attribute.  This is the read only version.
inline ConstAttributeDataHandle getAttributeHandleR(const AttributeObj& attrObj, InstanceIndex instIndex)
{
    return attrObj.iAttribute->getConstAttributeDataHandle(attrObj, instIndex);
}

// Convenience function to retrieve an attribute data handle given the attribute.  The
// attribute data handle is needed to retrieve the data of the attribute.  This is the writable version.
inline AttributeDataHandle getAttributeHandleW(const AttributeObj& attrObj, InstanceIndex instIndex)
{
    return attrObj.iAttribute->getAttributeDataHandle(attrObj, instIndex);
}

template <typename T>
class ArrayWrapper
{
    const GraphContextObj m_context = {};
    const AttributeObj m_attrObj = {};
    const InstanceIndex m_instIdx{ kAccordingToContextIndex };

public:
    ArrayWrapper(const GraphContextObj& context,
                 const AttributeObj& attrObj,
                 InstanceIndex instanceIdx = kAccordingToContextIndex)
        : m_context(context), m_attrObj(attrObj), m_instIdx(instanceIdx)
    {
    }

    ArrayWrapper()
    {
    }

    bool isValid(DataAccessFlags access) const
    {
        if (!m_context.iContext)
            return false;

        // for outputs it's okay for the size to be 0.  So we only check for inputs here.
        return access == kReadOnly ? getArrayRd() != nullptr : true;
    }

    // CPU buffer accessors
    T* getArray()
    {
        return getArrayWr();
    }

    const T* getArrayRd() const
    {
        ConstAttributeDataHandle attrDataHandle = getAttributeHandleR(m_attrObj, m_instIdx);
        // Technically this is a void*** at this point.  Fabric stores arrays as a pointer to the actual
        // buffer.  The getDataR interface requires a void** , so we are forcing it to be that here.
        // At the end of the call, out contains the address to the buffer, which we then dereference to
        // get at the array buffer
        const void** out = nullptr;
        void** outPtr = reinterpret_cast<void**>(&out);
        m_context.iAttributeData->getDataR((const void**)outPtr, m_context, &attrDataHandle, 1);
        if (out == nullptr)
            return nullptr;
        return reinterpret_cast<T*>(const_cast<void*>(*out));
    }

    T* getArrayWr()
    {
        AttributeDataHandle attrDataHandle = getAttributeHandleW(m_attrObj, m_instIdx);
        void** out;
        // see note above about void*** forced to void**
        void** outPtr = reinterpret_cast<void**>(&out);
        m_context.iAttributeData->getDataW(outPtr, m_context, &attrDataHandle, 1);
        if (out == nullptr)
            return nullptr;
        return reinterpret_cast<T*>(*out);
    }

    void resize(size_t newCount)
    {
        AttributeDataHandle attrDataHandle = getAttributeHandleW(m_attrObj, m_instIdx);
        m_context.iAttributeData->setElementCount(m_context, attrDataHandle, newCount);
    }

    size_t size() const
    {
        ConstAttributeDataHandle attrDataHandle = getAttributeHandleR(m_attrObj, m_instIdx);
        size_t elemCount = 0;
        m_context.iAttributeData->getElementCount(&elemCount, m_context, &attrDataHandle, 1);
        return elemCount;
    }

    bool empty() const
    {
        return size() == 0;
    }

    // GPU buffer accessors
    GpuArray<T> getArrayGPU()
    {
        return getArrayWrGPU();
    }

    ConstGpuArray<T> getArrayRdGPU() const
    {
        ConstAttributeDataHandle attrDataHandle = getAttributeHandleR(m_attrObj, m_instIdx);
        const void** out = nullptr;
        void** outPtr = reinterpret_cast<void**>(&out);
        m_context.iAttributeData->getDataRGPU((const void**)outPtr, m_context, &attrDataHandle, 1);
        auto array = (T* const*)(out);
        return ConstGpuArray<T>{ array, sizeGPU() };
    }

    GpuArray<T> getArrayWrGPU()
    {

        AttributeDataHandle attrDataHandle = getAttributeHandleW(m_attrObj, m_instIdx);
        void** out;
        void** outPtr = reinterpret_cast<void**>(&out);
        m_context.iAttributeData->getDataWGPU(outPtr, m_context, &attrDataHandle, 1);
        auto array = (T* const*)(out);
        return GpuArray<T>{ array, sizeGPU() };
    }

    // GPU size accessor
    const size_t* sizeGPU() const
    {
        // We don't support GPU resizing array
        return nullptr;
    }
};
}
}
}
