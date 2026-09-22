// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>
#include <carb/InterfaceUtils.h>
#include <carb/Types.h>
#include <omni/fabric/FabricUSD.h>
#include <omni/fabric/IPath.h>

#include <iostream>
#include <vector>

namespace omni
{
namespace fabric
{

// A TfNotice sent with a vector of paths for attribute that
// have changed. Sent by StageReaderWriter upon request, contains
// the paths of attributes that the StageReaderWriter has flagged
// as modified during it's lifetime, which is typically one frame.
//
// primPaths and attributeNames are required to the same length,
// the prim and attribute name within that prim whose value
// changed
class AttributeValuesChangedNotice : public pxr::TfNotice
{
public:
    AttributeValuesChangedNotice(const std::vector<pxr::SdfPath>& primPaths,
                                 const std::vector<pxr::TfToken>& attributeNames)
        : _primPaths(primPaths), _attributeNames(attributeNames)
    {
    }

    ~AttributeValuesChangedNotice()
    {
    }

    const std::vector<pxr::SdfPath>& GetPrimPaths() const
    {
        return _primPaths;
    }

    const std::vector<pxr::TfToken>& GetAttributeNames() const
    {
        return _attributeNames;
    }

private:
    const std::vector<pxr::SdfPath> _primPaths;
    const std::vector<pxr::TfToken> _attributeNames;
};

void broadcastTfNoticeForAttributesChanged(StageReaderWriterId stageId);

template <typename T>
T getValue(const pxr::UsdAttribute& attribute, const pxr::UsdTimeCode& timeCode)
{
    // First, look in fabric to see if a value is present. If not, fall back
    // to read USD's composed attribute value.

    {
        // read from fabric via StageReaderWriter, this is called during a run
        // loop where extensions are modifying one timeslice within StageWithHisotry

        // Look up the long int identifier for the attribute's UsdStage
        auto usdStageId = PXR_NS::UsdUtilsStageCache::Get().GetId(attribute.GetStage()).ToLongInt();

        // grab the carb interface for StageReaderWriter and use it to access the
        // (potentially NULL) current StageReaderWriter for the UsdStage
        auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
        auto stageReaderWriter = iStageReaderWriter->get(usdStageId);

        if (stageReaderWriter.id)
        {
            // Grab a pointer to in-memory representation for the attribute value, in this
            // case a pointer to a T. Will be NULL if attribute doesn't exist in fabric
            auto valueSpan =
                iStageReaderWriter->getAttribute(stageReaderWriter, omni::fabric::asInt(attribute.GetPrimPath()),
                                                 omni::fabric::asInt(attribute.GetName()));

            T* valuePtr = (T*)valueSpan.ptr;

            if (valuePtr)
            {
                // We have a value stored for this attribute in fabric, return it
                return *valuePtr;
            }
        }
    }

    // If we get here we didn't find a value stored for this attribute in fabric,
    // so call USD API
    pxr::VtValue val;
    attribute.Get(&val, timeCode);
    return val.UncheckedGet<T>();
}


template <typename T_VALUETYPE>
void setFabricValue(const pxr::UsdAttribute& attribute, T_VALUETYPE value, bool writeToUSD)
{
    if (writeToUSD)
    {
        // write to the USD layer
        attribute.Set(value);
    }
    else
    {
        // write to fabric, via StageReaderWriter

        // grab const references to the path of the attribute's parent
        // prim and the name of the attribute. Avoid copies here.
        const pxr::SdfPath& path = attribute.GetPrimPath();
        const pxr::TfToken& name = attribute.GetName();
        const pxr::SdfPath& attrPath = attribute.GetPath();

        // Convert the bits into a carb-safe value
        auto pathId = omni::fabric::asInt(path);
        auto nameId = omni::fabric::asInt(name);

        // Look up the long int identifier for the attribute's UsdSage
        auto usdStageId = PXR_NS::UsdUtilsStageCache::Get().GetId(attribute.GetStage()).ToLongInt();

        // grab the carb interface for StageReaderWriter and use it to access the
        // (potentially NULL) current StageReaderWriter for the UsdStage
        auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
        auto stageReaderWriter = iStageReaderWriter->get(usdStageId);

        if (!stageReaderWriter.id)
        {
            // No one created a StageReaderWriter, we're expecting this
            // to be created by another extension or run loop
            //
            // XXX: warn, or return false?
            return;
        }

        // Grab a pointer to in-memory representation for the attribute value, in this
        // case a pointer to a float
        auto valuePtr = iStageReaderWriter->getAttribute(stageReaderWriter, pathId, nameId);

        // Set the value within StageReaderWriter
        ((T_VALUETYPE*)valuePtr.ptr)[0] = value;
    }
}

// This should be in UsdValueAccessors.cpp, but when it goes there
// clients in DriveSim can't find the symbol. Needs fixing.
inline void setFabricValueFloat(const pxr::UsdAttribute& attribute, float value, bool writeToUSD)
{
    setFabricValue<float>(attribute, value, writeToUSD);
}

} // namespace fabric
} // namespace omni
