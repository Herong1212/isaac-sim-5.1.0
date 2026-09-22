// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/extras/Hash.h>

#include <omni/core/IObject.h>
#include <omni/fabric/SimStageWithHistory.h>
#include <pxr/pxr.h>
#include <usdrt/gf/matrix.h>
#include <usdrt/gf/quat.h>
#include <usdrt/gf/range.h>
#include <usdrt/gf/vec.h>

PXR_NAMESPACE_OPEN_SCOPE
class UsdProperty;
class VtValue;
class TfToken;
PXR_NAMESPACE_CLOSE_SCOPE

namespace carb
{
    namespace datastore
    {
        class IDataStore;
    }
}

namespace usdrt
{
namespace population
{

struct DerivedDataInValue
{
    omni::fabric::Type type;
    omni::fabric::Span<const uint8_t> data;
};
// TODO: look for ABI safe alternatives for passing data ownership and ref counting
using DerivedDataOutValue = PXR_NS::VtValue;

using HashType = carb::extras::hash128_t;

struct UsdPropertyType
{
    const PXR_NS::UsdProperty* propPtr;
};
using UsdTokenType = PXR_NS::TfToken;

struct ContentHashMetaData
{
    size_t elementCount;
    omni::fabric::Type type;
    uint64_t generationContext; // context to re-generate the associated data, should it be missing
};

// The DerivedDataLookup can be used to communicate pre-computed values (e.g. loaded from a side-car cache) that
// are then used during FSD population to skip accessing actual USD values
// This can reduce the network/disk/memory usage during population, if later consumers of the USD data also only operate
// on cached data. E.g. During FSD population fabric is only populated with content hashes of the authored USD geometry.
// The RenderDelegate then only uses those content hashes to access the GPU-ready geometry from a cache.
// This means that the authored USD geometry data never needs to be downloaded/loaded from disk/stored in memory.
class IDerivedDataLookup
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("usdrt.population.IDerivedDataLookup")>
{
public:
    // Set a vector of values in the Derived data lookup that will be used during FSD population
    // layerFilenameHash - hash of the layer file name string
    // derivedDataKey - identifier of the type of derived data, e.g. "ContentHash" or "BoundingBox" for other derived
    // data attributeSpecPathHashes - array of hashes of the attribute path. This is computed as the compound hash of
    // the tokens of the
    //                       attribute spec path. computeAttributePathHash performs this computation for an array of
    //                       given paths.
    // valueKeyHashes - array of tokens that describe the specific value for each attribute. E.g. "default" or a
    // timesample values - array of derived data value to store for the given layer, attributepath, derived data key and
    // value key numPathCs - number of attributePathHashes, valueKeyHashes and values
    virtual void set(const HashType& layerFilenameHash,
                     const omni::fabric::TokenC& derivedDataKey,
                     const HashType* attributeSpecPathHashes,
                     const HashType* valueKeyHashes,
                     const DerivedDataInValue* values,
                     size_t numPathCs) noexcept = 0;

    // Retrieves derived data for a given UsdProperty
    // derivedDataKey - identifier of the type of derived data, e.g. "ContentHash" or "BoundingBox" for other derived
    // data valueKey - token that describes the derived data value. E.g. "default" or a timesample outValue - value to
    // be filled with the retrieved value if they exist
    virtual bool get(const UsdPropertyType& prop,
                     const UsdTokenType& derivedDataKey,
                     const UsdTokenType& valueKey,
                     DerivedDataOutValue& outValue) noexcept = 0;

    // clears the whole DerivedDataLookup
    virtual void clear() noexcept = 0;

    // computes the attribute path hash for an attribute spec path to be used with the above set() function
    virtual void computeAttributePathHash(const PXR_NS::SdfPath* paths,
                                          size_t numPaths,
                                          HashType* outAttributePathHashes) noexcept = 0;

    // Set metadata for contenthashes to be retrieved by content hash later
    // contentHashes - array of attribute content hashes
    // numContentHashes - number of content hashes in the array
    // sizeOfContentHashMetaData - size in bytes of the content hash meta data holding the return values
    // metaData - metadata to store
    virtual void setMetaDataForHash(const HashType* contentHashes, size_t numContentHashes, size_t sizeOfContentHashMetaData, const ContentHashMetaData* metaData) noexcept = 0;

    // Fetch metadata for a given array of content hashes
    // contentHashes - array of attribute content hashes
    // numContentHashes - number of content hashes in the array
    // sizeOfContentHashMetaData - size in bytes of the content hash meta data holding the return values
    // outMetaData - array of ContentHashMetaData (or a larger or smaller structure of the same layout) of size numContentHashes
    //               ContentHashMetaData::Type is unknown basetype if a content hash is not found
    virtual void getMetaDataFromHash(const HashType* contentHashes, size_t numContentHashes, size_t sizeOfContentHashMetaData, ContentHashMetaData* outMetaData) noexcept = 0;

    // Fetch data for a given array of content hashes
    // store - the data store to retrieve cached data
    // contentHashes - array of attribute content hashes
    // numContentHashes - number of content hashes in the array
    // outMetaData - array of DerivedDataOutValue to fill with the derived data. Must have length numContentHashes
    //               the outValue[i] is not changed if the content hash for contentHashes[i] is not found
    virtual void getDataFromHash(carb::datastore::IDataStore* store, const HashType* contentHashes, size_t numContentHashes, DerivedDataOutValue* outValues) noexcept = 0;

    // Sets the usd stage id associated with this derived data lookup. this has to be called before any lookup operation is performed
    // stageid - the usd stage associated with this lookup interface
    virtual void setUsdStageId(const omni::fabric::UsdStageId stageId) noexcept = 0;
};

// Structure used to store array data information inside the IDerivedDataLookup
struct ArrayDataDesc
{
    HashType contentHash;
    uint64_t elementCount;
    uint32_t type;
    uint32_t padding;
};

inline bool operator==(const ArrayDataDesc& a, const ArrayDataDesc& b)
{
    return (a.contentHash.d[0] == b.contentHash.d[0])
        && (a.contentHash.d[1] == b.contentHash.d[1])
        && (a.elementCount == b.elementCount)
        && (a.type == b.type);
}

} // namespace population
} // namespace usdrt
