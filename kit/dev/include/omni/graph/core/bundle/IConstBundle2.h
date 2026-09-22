// Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
//! @file IConstBundle.h
//!
//! @brief Defines Read only interfaces for recursive bundles.
#pragma once

#include <omni/core/IObject.h>
#include <omni/graph/core/Handle.h>
#include <omni/graph/core/Type.h>
#include <omni/log/ILog.h>

OMNI_LOG_DECLARE_CHANNEL(kBundleChannel)

namespace omni
{
namespace graph
{
namespace core
{

//! Declare the interface definition
OMNI_DECLARE_INTERFACE(IConstBundle2);

//! Provide read only access to recursive bundles.
class IConstBundle2_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.graph.core.IConstBundle2")>
{
protected:
    //! Return true if this bundle is valid, false otherwise.
    virtual bool isValid_abi() noexcept = 0;

    //! Return the context of this bundle.
    OMNI_ATTR("no_py")
    virtual GraphContextObj getContext_abi() noexcept = 0;

    //! Return Handle to this bundle. Invalid handle is returned if this bundle is invalid.
    OMNI_ATTR("no_py")
    virtual ConstBundleHandle getConstHandle_abi() noexcept = 0;

    //! Return full path of this bundle.
    OMNI_ATTR("no_py")
    virtual omni::fabric::PathC getPath_abi() noexcept = 0;

    //! Return name of this bundle
     OMNI_ATTR("no_py")
     virtual NameToken getName_abi() noexcept = 0;

    //! Return handle to the parent of this bundle. Invalid handle is returned if bundle has no parent.
    OMNI_ATTR("no_py")
    virtual ConstBundleHandle getConstParentBundle_abi() noexcept = 0;

    //! @brief Get the names and types of all attributes in this bundle.
    //!
    //! This method operates in two modes: **query mode** or **get mode**.
    //!
    //! **Query mode** is enabled when names and types are `nullptr`. When in this mode, *nameAndTypeCount
    //! will be populated with the number of attributes in the bundle.
    //!
    //! **Get mode** is enabled when names or types is not `nullptr`. Upon entering the function, *nameAndTypeCount
    //! stores the number of entries in names and types. In **Get mode** names are not nullptr, names array is populated
    //! with attribute names. In **Get mode** types are not nullptr, types array is populated with attribute types.
    //!
    //! @param names The names of the attributes.
    //! @param types The types of the attributes.
    //! @param nameAndTypeCount must not be `nullptr` in both modes.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getAttributeNamesAndTypes_abi(
        NameToken* const names OMNI_ATTR("out, count=*nameAndTypeCount"),
        Type* const types OMNI_ATTR("out, count=*nameAndTypeCount"),
        size_t* const nameAndTypeCount OMNI_ATTR("in, out, not_null")) noexcept = 0;

    //! @brief Get read only handles to all attributes in this bundle.
    //!
    //! This method operates in two modes: **query mode** or **get mode**.
    //!
    //! **Query mode** is enabled when attributes is `nullptr`. When in this mode, *attributeCount
    //! will be populated with the number of attributes in the bundle.
    //!
    //! **Get mode** is enabled when attributes is not `nullptr`. Upon entering the function, *attributeCount
    //! stores the number of entries in attributes.
    //! In **Get mode** attributes are not nullptr, attributes array is populated with attribute handles in the bundle.
    //!
    //! @param attributes The buffer to store handles of the attributes in this bundle.
    //! @param attributeCount Size of attributes buffer. Must not be `nullptr` in both modes.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getConstAttributes_abi(
        ConstAttributeDataHandle* const attributes OMNI_ATTR("out, not_null, count=*attributeCount"),
        size_t* const attributeCount OMNI_ATTR("in, out, not_null")) noexcept = 0;

    //! @brief Search for read only handles of the attribute in this bundle by using attribute names.
    //!
    //! @param names The name of the attributes to be searched for.
    //! @param nameCount Size of names buffer.
    //! @param attributes The buffer to store handles of the attributes.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getConstAttributesByName_abi(
        NameToken const* const names OMNI_ATTR("in, not_null, count=nameCount"),
        size_t nameCount,
        ConstAttributeDataHandle* const attributes OMNI_ATTR("out, not_null, count=nameCount")) noexcept = 0;

    //! @brief Get read only handles to all child bundles in this bundle.
    //!
    //! This method operates in two modes: **query mode** or **get mode**.
    //!
    //! **Query mode** is enabled when bundles is `nullptr`. When in this mode, *bundleCount
    //! will be populated with the number of bundles in the bundle.
    //!
    //! **Get mode** is enabled when bundles is not `nullptr`. Upon entering the function, *bundleCount
    //! stores the number of entries in bundles.
    //! In **Get mode** bundles are not nullptr, bundles array is populated with bundle handles in the bundle.
    //!
    //! @param bundles The buffer to save child bundle handles.
    //! @param bundleCount Size of the bundles buffer. Must not be `nullptr` in both modes.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getConstChildBundles_abi(
        ConstBundleHandle* const bundles OMNI_ATTR("out, not_null, count=*bundleCount"),
        size_t* const bundleCount OMNI_ATTR("in, out, not_null")) noexcept = 0;

    //! @brief Get read only handle to child bundle by index.
    //!
    //! @param bundleIndex Bundle index in range [0, childBundleCount).
    //! @param bundle Handle under the index. If bundle index is out of range, then invalid handle is returned.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py, no_api")
    virtual omni::core::Result getConstChildBundle_abi(
        size_t bundleIndex, ConstBundleHandle* const bundle OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief Lookup for read only handles to child bundles under specified names.
    //!
    //! For children that are not found invalid handles are returned.
    //!
    //! @param names The names of the child bundles in this bundle.
    //! @param nameCount The number of child bundles to be searched.
    //! @param foundBundles Output handles to the found bundles.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getConstChildBundlesByName_abi(
        NameToken const* const names OMNI_ATTR("in, not_null, count=nameCount"),
        size_t nameCount,
        ConstBundleHandle* const foundBundles OMNI_ATTR("out, not_null, count=nameCount")) noexcept = 0;

    //! @deprecated Metadata storage is deprecated and invalid handle is returned.
    OMNI_ATTR("no_py")
    virtual ConstBundleHandle getConstMetadataStorage_abi() noexcept = 0;

    //! @brief Get the names and types of all bundle metadata fields in this bundle.
    //!
    //! This method operates in two modes: **query mode** or **get mode**.
    //!
    //! **Query mode** is enabled when fieldNames and fieldTypes are `nullptr`. When in this mode, *fieldCount
    //! will be populated with the number of metadata fields in this bundle.
    //!
    //! **Get mode** is enabled when fieldNames or fieldTypes is not `nullptr`. Upon entering the function,
    //! *fieldCount stores the number of entries in fieldNames and @p fieldTypes.
    //!
    //! In **Get mode** fieldNames are not `nullptr`, fieldNames array is populated with field names.
    //! In **Get mode** fieldTypes are not `nullptr`, fieldTypes array is populated with field types.
    //!
    //! @param fieldNames Output field names in this bundle.
    //! @param fieldTypes Output field types in this bundle.
    //! @param fieldCount must not be `nullptr` in both modes.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getBundleMetadataNamesAndTypes_abi(
        NameToken* const fieldNames OMNI_ATTR("out, count=*fieldCount"),
        Type* const fieldTypes OMNI_ATTR("out, count=*fieldCount"),
        size_t* const fieldCount OMNI_ATTR("in, out, not_null")) noexcept = 0;

    //! @brief Search for field handles in this bundle by using field names.
    //!
    //!@param fieldNames Name of bundle metadata fields to be searched for.
    //!@param fieldCount Size of fieldNames and bundleMetadata arrays.
    //!@param bundleMetadata Handle to metadata fields in this bundle.
    //!@return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!        invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getConstBundleMetadataByName_abi(
        NameToken const* const fieldNames OMNI_ATTR("in, count=fieldCount"),
        size_t fieldCount,
        ConstAttributeDataHandle* const bundleMetadata OMNI_ATTR("out, count=fieldCount")) noexcept = 0;

    //! @brief Get the names and types of all attribute metadata fields in the attribute.
    //!
    //! This method operates in two modes: **query mode** or **get mode**.
    //!
    //! **Query mode** is enabled when fieldNames and @p fieldTypes are `nullptr`. When in this mode, *fieldCount
    //! will be populated with the number of metadata fields in the attribute.
    //!
    //! **Get mode** is enabled when fieldNames or fieldTypes is not `nullptr`. Upon entering the function,
    //! *fieldCount stores the number of entries in fieldNames and fieldTypes.
    //!
    //! In **Get mode** fieldNames are not `nullptr`, fieldNames array is populated with field names.
    //! In **Get mode** fieldTypes are not `nullptr`, fieldTypes array is populated with field types.
    //!
    //! @param attribute Name of the attribute.
    //! @param fieldNames Output field names in the attribute.
    //! @param fieldTypes Output field types in the attribute.
    //! @param fieldCount must not be `nullptr` in both modes.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getAttributeMetadataNamesAndTypes_abi(
        NameToken attribute,
        NameToken* const fieldNames OMNI_ATTR("out, count=*fieldCount"),
        Type* const fieldTypes OMNI_ATTR("out, count=*fieldCount"),
        size_t* const fieldCount OMNI_ATTR("in, out, not_null")) noexcept = 0;

    //! @brief Search for read only field handles in the attribute by using field names.
    //!
    //! @param attribute The name of the attribute.
    //! @param fieldNames The names of attribute metadata fields to be searched for.
    //! @param fieldCount Size of fieldNames and attributeMetadata arrays.
    //! @param attributeMetadata Handles to attribute metadata fields in the attribute.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getConstAttributeMetadataByName_abi(
        NameToken attribute,
        NameToken const* const fieldNames OMNI_ATTR("in, count=fieldCount"),
        size_t fieldCount,
        ConstAttributeDataHandle* const attributeMetadata OMNI_ATTR("out, count=fieldCount")) noexcept = 0;
};

} // namespace core
} // namespace graph
} // namespace omni

#include "IConstBundle2.gen.h"

//! @cond Doxygen_Suppress
//!
//! API part of the bundle factory interface
//! @copydoc omni::graph::core::IConstBundle2_abi
OMNI_DEFINE_INTERFACE_API(omni::graph::core::IConstBundle2)
//! @endcond
{
public:
    //! Return number of attributes in this bundle.
    size_t getAttributeCount() noexcept
    {
        size_t attributeCount = 0;
        auto result = getConstAttributes_abi(nullptr, &attributeCount);
        return OMNI_SUCCEEDED(result) ? attributeCount : 0;
    }

    //! Return number of child bundles in this bundle.
    size_t getChildBundleCount() noexcept
    {
        size_t bundleCount = 0;
        auto result = getConstChildBundles_abi(nullptr, &bundleCount);
        return OMNI_SUCCEEDED(result) ? bundleCount : 0;
    }

    //! @brief Get the names of all attributes in this bundle.
    //!
    //! @param names Output array of attribute names. Size must be at least nameCount.
    //! @param nameCount Length of names array.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    omni::core::Result getAttributeNames(omni::graph::core::NameToken* const names, size_t nameCount) noexcept
    {
        return getAttributeNamesAndTypes_abi(names, nullptr, &nameCount);
    }

    //! @brief Get the types of all attributes in this bundle.
    //!
    //! @param types Output array of attribute types. Size must be at least typeCount.
    //! @param typeCount Length of types array.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    omni::core::Result getAttributeTypes(omni::graph::core::Type* const types, size_t typeCount) noexcept
    {
        return getAttributeNamesAndTypes_abi(nullptr, types, &typeCount);
    }

    //! @copydoc omni::graph::core::IConstBundle2_abi::getConstAttributes_abi
    omni::core::Result getConstAttributes(
        omni::graph::core::ConstAttributeDataHandle* const attributes, size_t attributeCount) noexcept
    {
        return getConstAttributes_abi(attributes, &attributeCount);
    }

    //! @brief Search for attribute handle in this bundle by using attribute name.
    //!
    //! @param name The name of the attribute to search for.
    //! @return Valid attribute handle if attribute if found, invalid handle otherwise.
    omni::graph::core::ConstAttributeDataHandle getConstAttributeByName(omni::graph::core::NameToken name) noexcept
    {
        using namespace omni::graph::core;
        ConstAttributeDataHandle out{ ConstAttributeDataHandle::invalidValue() };
        auto result = getConstAttributesByName_abi(&name, 1, &out);
        return OMNI_SUCCEEDED(result) ? out : ConstAttributeDataHandle{ ConstAttributeDataHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IConstBundle2_abi::getConstChildBundles_abi
    omni::core::Result getConstChildBundles(omni::graph::core::ConstBundleHandle* const bundles, size_t bundleCount) noexcept
    {
        return getConstChildBundles_abi(bundles, &bundleCount);
    }

    //! @brief @copybrief omni::graph::core::IConstBundle2_abi::getConstChildBundle_abi
    //!
    //! @param bundleIndex Bundle index in range [0, childBundleCount).
    //! @return Valid bundle handle if child bundle is found, invalid handle otherwise.
    omni::graph::core::ConstBundleHandle getConstChildBundle(size_t bundleIndex) noexcept
    {
        using namespace omni::graph::core;
        ConstBundleHandle out{ ConstBundleHandle::invalidValue() };
        auto result = getConstChildBundle_abi(bundleIndex, &out);
        return OMNI_SUCCEEDED(result) ? out : ConstBundleHandle{ ConstBundleHandle::invalidValue() };
    }

    //! @brief @copybrief omni::graph::core::IConstBundle2_abi::getConstChildBundlesByName_abi
    //!
    //! @param name The name of the child bundle.
    //! @return Valid bundle handle if child bundle is found, invalid handle otherwise.
    omni::graph::core::ConstBundleHandle getConstChildBundleByName(omni::graph::core::NameToken name) noexcept
    {
        using namespace omni::graph::core;
        ConstBundleHandle out{ ConstBundleHandle::invalidValue() };
        auto result = getConstChildBundlesByName_abi(&name, 1, &out);
        return OMNI_SUCCEEDED(result) ? out : ConstBundleHandle{ ConstBundleHandle::invalidValue() };
    }

    //! Return number of metadata fields in this bundle.
    size_t getBundleMetadataCount() noexcept
    {
        size_t bundleMetadataCount = 0;
        auto result = getBundleMetadataNamesAndTypes_abi(nullptr, nullptr, &bundleMetadataCount);
        return OMNI_SUCCEEDED(result) ? bundleMetadataCount : 0;
    }

    //! @copydoc omni::graph::core::IConstBundle2_abi::getBundleMetadataNamesAndTypes_abi
    omni::core::Result getBundleMetadataNamesAndTypes(omni::graph::core::NameToken* const fieldNames,
                                                      omni::graph::core::Type* const fieldTypes, size_t fieldCount) noexcept
    {
        return getBundleMetadataNamesAndTypes_abi(fieldNames, fieldTypes, &fieldCount);
    }

    //! @copydoc omni::graph::core::IConstBundle2_abi::getConstBundleMetadataByName_abi
    using omni::core::Generated<IConstBundle2_abi>::getConstBundleMetadataByName;

    //! @brief @copybrief omni::graph::core::IConstBundle2_abi::getConstBundleMetadataByName_abi
    //!
    //! @param fieldName The name of the bundle metadata field.
    //! @return Valid attribute handle if bundle metadata is found, invalid handle otherwise.
    omni::graph::core::ConstAttributeDataHandle getConstBundleMetadataByName(omni::graph::core::NameToken fieldName) noexcept
    {
        using namespace omni::graph::core;
        ConstAttributeDataHandle out{ ConstAttributeDataHandle::invalidValue() };
        Result result = getConstBundleMetadataByName_abi(&fieldName, 1, &out);
        return OMNI_SUCCEEDED(result) ? out : ConstAttributeDataHandle{ ConstAttributeDataHandle::invalidValue() };
    }

    //! @brief Return Number of metadata fields in the attribute.
    //!
    //! @param attribute The name of the attribute.
    size_t getAttributeMetadataCount(omni::graph::core::NameToken attribute) noexcept
    {
        size_t attributeMetadataCount = 0;
        auto result = getAttributeMetadataNamesAndTypes_abi(attribute, nullptr, nullptr, &attributeMetadataCount);
        return OMNI_SUCCEEDED(result) ? attributeMetadataCount : 0;
    }

    //! @copydoc omni::graph::core::IConstBundle2_abi::getAttributeMetadataNamesAndTypes_abi
    omni::core::Result getAttributeMetadataNamesAndTypes(
        omni::graph::core::NameToken attribute, omni::graph::core::NameToken* const fieldNames,
        omni::graph::core::Type* const fieldTypes, size_t fieldCount) noexcept
    {
        return getAttributeMetadataNamesAndTypes_abi(attribute, fieldNames, fieldTypes, &fieldCount);
    }

    //! @copydoc omni::graph::core::IConstBundle2_abi::getConstAttributeMetadataByName_abi
    using omni::core::Generated<IConstBundle2_abi>::getConstAttributeMetadataByName;

    //! @brief @copybrief omni::graph::core::IConstBundle2_abi::getConstAttributeMetadataByName_abi
    //!
    //! @param attribute The name of the attribute.
    //! @param fieldName The name of the field.
    //! @return Valid attribute handle if bundle metadata is found, invalid handle otherwise.
    omni::graph::core::ConstAttributeDataHandle getConstAttributeMetadataByName(
        omni::graph::core::NameToken attribute, omni::graph::core::NameToken fieldName) noexcept
    {
        using namespace omni::graph::core;
        ConstAttributeDataHandle out{ ConstAttributeDataHandle::invalidValue() };
        auto result = getConstAttributeMetadataByName_abi(attribute, &fieldName, 1, &out);
        return OMNI_SUCCEEDED(result) ? out : ConstAttributeDataHandle{ ConstAttributeDataHandle::invalidValue() };
    }

    CARB_DEPRECATED("Accessing child bundles by index is deprecated, look up children by name")
    omni::core::Result getConstChildBundle(
        size_t bundleIndex, omni::graph::core::ConstBundleHandle* const bundle) noexcept
    {
        return getConstChildBundle_abi(bundleIndex, bundle);
    }

}; // IConstBundle2
