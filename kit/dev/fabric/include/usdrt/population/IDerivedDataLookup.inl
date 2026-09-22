// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IDerivedDataLookup.h"

namespace usdrt
{
namespace population
{

// non ABI safe helpers
inline void setDerivedData(IDerivedDataLookup& lookup,
                           const HashType& layerFilenameHash,
                           const omni::fabric::TokenC& derivedDataKey,
                           const PXR_NS::SdfPath& attributeSpecPath,
                           const char* valueKey,
                           const usdrt::population::DerivedDataInValue& value)
{
    carb::extras::hash128_t valueHash = carb::extras::fnv128hashString(valueKey);
    carb::extras::hash128_t attributeHash;
    lookup.computeAttributePathHash(&attributeSpecPath, 1, &attributeHash);
    lookup.set(layerFilenameHash, derivedDataKey, &attributeHash, &valueHash, &value, 1);
}

inline void setDefaultDerivedData(IDerivedDataLookup& lookup,
                                  const HashType& layerFilenameHash,
                                  const omni::fabric::TokenC& derivedDataKey,
                                  const PXR_NS::SdfPath& attributeSpecPath,
                                  const usdrt::population::DerivedDataInValue& value)
{
    setDerivedData(lookup, layerFilenameHash, derivedDataKey, attributeSpecPath, "default", value);
}

inline void setDefaultContentHash(IDerivedDataLookup& lookup,
                                  const HashType& layerFilenameHash,
                                  const PXR_NS::SdfPath& attributeSpecPath,
                                  const usdrt::population::DerivedDataInValue& value)
{
    setDefaultDerivedData(
        lookup, layerFilenameHash, omni::fabric::Token("omni:array_content_hash").asTokenC(), attributeSpecPath, value);
}

template <typename ScalarType, typename FetchCallback>
static bool arrayWrite(uint64_t arraySize, PXR_NS::VtValue& outValue, FetchCallback callback)
{
    PXR_NS::VtArray<ScalarType> v;
    v.resize(arraySize);
    if (callback((uint8_t*)v.data(), arraySize * sizeof(ScalarType)))
    {
        outValue = v;
        return true;
    }
    return false;
}

template <typename ScalarType, typename FetchCallback>
static bool scalarWrite(PXR_NS::VtValue& outValue, FetchCallback callback)
{
    ScalarType v;
    if (callback((uint8_t*)&v, sizeof(ScalarType)))
    {
        outValue = v;
        return true;
    }
    return false;
}

template <typename FetchCallback>
bool vtValueWrite(const omni::fabric::Type& valueType, uint64_t dataSize, PXR_NS::VtValue& outValue, FetchCallback callback)
{
    using namespace pxr;
    using namespace omni::fabric;

    if (valueType.isArray())
    {
        CARB_ASSERT(valueType.arrayDepth == 1); // Must be array type;
        CARB_ASSERT(!dataSize || ((dataSize >= valueType.baseTypeSize()) && valueType.baseTypeSize()),
                    "Stripped array must be bigger than length 1, was: %zu", dataSize);
        uint64_t elementSize = valueType.baseTypeSize() * valueType.componentCount;
        uint64_t arraySize = dataSize / elementSize;
        CARB_ASSERT(arraySize * elementSize == dataSize,
                    "Stripped array data must fit into provided data size. DataSize: %zu, Element size: %zu", dataSize,
                    elementSize);
        switch (valueType.baseType)
        {
        case BaseDataType::eBool:
            return arrayWrite<bool>(arraySize, outValue, callback);
        case BaseDataType::eUChar:
            return arrayWrite<uint8_t>(arraySize, outValue, callback);
        case BaseDataType::eUInt:
            return arrayWrite<uint32_t>(arraySize, outValue, callback);
        case BaseDataType::eInt: {
            if (valueType.componentCount == 1)
                return arrayWrite<int32_t>(arraySize, outValue, callback);
            else if (valueType.componentCount == 2)
                return arrayWrite<PXR_NS::GfVec2i>(arraySize, outValue, callback);
            else if (valueType.componentCount == 3)
                return arrayWrite<PXR_NS::GfVec3i>(arraySize, outValue, callback);
            else if (valueType.componentCount == 4)
                return arrayWrite<PXR_NS::GfVec4i>(arraySize, outValue, callback);
        }
        break;
        case BaseDataType::eUInt64:
            return arrayWrite<uint64_t>(arraySize, outValue, callback);
        case BaseDataType::eInt64:
            return arrayWrite<int64_t>(arraySize, outValue, callback);
        case BaseDataType::eHalf: {
            if (valueType.componentCount == 1)
                return arrayWrite<PXR_NS::GfHalf>(arraySize, outValue, callback);
            else if (valueType.componentCount == 2)
                return arrayWrite<PXR_NS::GfVec2h>(arraySize, outValue, callback);
            else if (valueType.componentCount == 3)
                return arrayWrite<PXR_NS::GfVec3h>(arraySize, outValue, callback);
            else if (valueType.componentCount == 4)
                return arrayWrite<PXR_NS::GfVec4h>(arraySize, outValue, callback);
        }
        break;
        case BaseDataType::eFloat: {
            if (valueType.componentCount == 1)
                return arrayWrite<float>(arraySize, outValue, callback);
            else if (valueType.componentCount == 2)
                return arrayWrite<PXR_NS::GfVec2f>(arraySize, outValue, callback);
            else if (valueType.componentCount == 3)
                return arrayWrite<PXR_NS::GfVec3f>(arraySize, outValue, callback);
            else if (valueType.componentCount == 4)
                return arrayWrite<PXR_NS::GfVec4f>(arraySize, outValue, callback);
        }
        break;
        case BaseDataType::eDouble: {
            if (valueType.role == AttributeRole::eMatrix)
            {
                if (valueType.componentCount == 4)
                    return arrayWrite<PXR_NS::GfMatrix2d>(arraySize, outValue, callback);
                else if (valueType.componentCount == 9)
                    return arrayWrite<PXR_NS::GfMatrix3d>(arraySize, outValue, callback);
                else if (valueType.componentCount == 16)
                    return arrayWrite<PXR_NS::GfMatrix4d>(arraySize, outValue, callback);
            }
            else
            {
                if (valueType.componentCount == 1)
                    return arrayWrite<double>(arraySize, outValue, callback);
                else if (valueType.componentCount == 2)
                    return arrayWrite<PXR_NS::GfVec2d>(arraySize, outValue, callback);
                else if (valueType.componentCount == 3)
                    return arrayWrite<PXR_NS::GfVec3d>(arraySize, outValue, callback);
                else if (valueType.componentCount == 4)
                    return arrayWrite<PXR_NS::GfVec4d>(arraySize, outValue, callback);
            }
        }
        break;
        default:
            break;
        }
        CARB_ASSERT(false);
        return false;
    }
    else
    {
        switch (valueType.baseType)
        {
        case BaseDataType::eBool:
            return scalarWrite<bool>(outValue, callback);
        case BaseDataType::eUChar:
            return scalarWrite<uint8_t>(outValue, callback);
        case BaseDataType::eUInt:
            return scalarWrite<uint32_t>(outValue, callback);
        case BaseDataType::eInt: {
            if (valueType.componentCount == 1)
                return scalarWrite<int32_t>(outValue, callback);
            else if (valueType.componentCount == 2)
                return scalarWrite<PXR_NS::GfVec2i>(outValue, callback);
            else if (valueType.componentCount == 3)
                return scalarWrite<PXR_NS::GfVec3i>(outValue, callback);
            else if (valueType.componentCount == 4)
                return scalarWrite<PXR_NS::GfVec4i>(outValue, callback);
        }
        break;
        case BaseDataType::eUInt64:
            return scalarWrite<uint64_t>(outValue, callback);
        case BaseDataType::eInt64:
            return scalarWrite<int64_t>(outValue, callback);
        case BaseDataType::eHalf: {
            if (valueType.componentCount == 1)
                return scalarWrite<PXR_NS::GfHalf>(outValue, callback);
            else if (valueType.componentCount == 2)
                return scalarWrite<PXR_NS::GfVec2h>(outValue, callback);
            else if (valueType.componentCount == 3)
                return scalarWrite<PXR_NS::GfVec3h>(outValue, callback);
            else if (valueType.componentCount == 4)
                return scalarWrite<PXR_NS::GfVec4h>(outValue, callback);
        }
        break;
        case BaseDataType::eFloat: {
            if (valueType.componentCount == 1)
                return scalarWrite<float>(outValue, callback);
            else if (valueType.componentCount == 2)
                return scalarWrite<PXR_NS::GfVec2f>(outValue, callback);
            else if (valueType.componentCount == 3)
                return scalarWrite<PXR_NS::GfVec3f>(outValue, callback);
            else if (valueType.componentCount == 4)
                return scalarWrite<PXR_NS::GfVec4f>(outValue, callback);
        }
        break;
        case BaseDataType::eDouble: {
            if (valueType.role == AttributeRole::eMatrix)
            {
                if (valueType.componentCount == 4)
                    return scalarWrite<PXR_NS::GfMatrix2d>(outValue, callback);
                else if (valueType.componentCount == 9)
                    return scalarWrite<PXR_NS::GfMatrix3d>(outValue, callback);
                else if (valueType.componentCount == 16)
                    return scalarWrite<PXR_NS::GfMatrix4d>(outValue, callback);
            }
            else
            {
                if (valueType.componentCount == 1)
                    return scalarWrite<double>(outValue, callback);
                else if (valueType.componentCount == 2)
                    return scalarWrite<PXR_NS::GfVec2d>(outValue, callback);
                else if (valueType.componentCount == 3)
                    return scalarWrite<PXR_NS::GfVec3d>(outValue, callback);
                else if (valueType.componentCount == 4)
                    return scalarWrite<PXR_NS::GfVec4d>(outValue, callback);
            }
        }
        break;
        default:
            break;
        }
        CARB_ASSERT(false);
        return false;
    }
}

inline PXR_NS::VtValue rawDataToVtValue(const omni::fabric::Type& type,
                                        const omni::fabric::Span<const uint8_t>& data)
{
    PXR_NS::VtValue value;
    vtValueWrite(type, data.size(), value, [&data](uint8_t* dataPtr, uint64_t size) {
        if (size)
        {
            memcpy(dataPtr, data.data(), std::min(size, uint64_t(data.size())));
        }
        return true;
    });
    return value;
}

} // namespace population
} // namespace usdrt
