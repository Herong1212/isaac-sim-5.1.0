// Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file IBundle.h
//!
//! @brief Defines Read Write interfaces for recursive bundles.
#pragma once

#include "IConstBundle2.h"

namespace omni
{
namespace graph
{
namespace core
{

//! Declare the IBundle2 interface definition
OMNI_DECLARE_INTERFACE(IBundle2);

//! Provide read write access to recursive bundles.
class IBundle2_abi : public omni::core::Inherits<IConstBundle2, OMNI_TYPE_ID("omni.graph.core.IBundle2")>
{
protected:
    //! Return handle to this bundle. Invalid handle is returned if this bundle is invalid.
    OMNI_ATTR("no_py")
    virtual BundleHandle getHandle_abi() noexcept = 0;

    //! Return parent of this bundle, or invalid handle if there is no parent.
    OMNI_ATTR("no_py")
    virtual BundleHandle getParentBundle_abi() noexcept = 0;

    //! @brief Get read-write handles to all attributes in this bundle.
    //!
    //! @copydetails IConstBundle2_abi::getConstAttributes_abi
    OMNI_ATTR("no_py")
    virtual omni::core::Result getAttributes_abi(
        AttributeDataHandle* const attributes OMNI_ATTR("out, not_null, count=*attributeCount"),
        size_t* const attributeCount OMNI_ATTR("in, out, not_null")) noexcept = 0;

    //! @brief Searches for read-write handles of the attribute in this bundle by using attribute names.
    //!
    //! @copydetails IConstBundle2_abi::getConstAttributesByName_abi
    OMNI_ATTR("no_py")
    virtual omni::core::Result getAttributesByName_abi(
        NameToken const* const names OMNI_ATTR("in, not_null, count=nameCount"),
        size_t nameCount,
        AttributeDataHandle* const attributes OMNI_ATTR("out, not_null, count=nameCount")) noexcept = 0;

    //! @brief Get read write handles to all child bundles in this bundle.
    //!
    //! @copydetails IConstBundle2_abi::getConstChildBundles_abi
    OMNI_ATTR("no_py")
    virtual omni::core::Result getChildBundles_abi(BundleHandle* const bundles OMNI_ATTR("out, not_null, count=bundleCount"),
                                                   size_t* const bundleCount OMNI_ATTR("in, out, not_null")) noexcept = 0;

    //! @brief Get read write handle to child bundle by index.
    //!
    //! @copydetails IConstBundle2_abi::getConstChildBundle_abi
    OMNI_ATTR("no_py, no_api")
    virtual omni::core::Result getChildBundle_abi(size_t bundleIndex,
                                                  BundleHandle* const bundle OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief Lookup for read write handles to child bundles under specified names.
    //!
    //! @copydetails IConstBundle2_abi::getConstChildBundlesByName_abi
    OMNI_ATTR("no_py")
    virtual omni::core::Result getChildBundlesByName_abi(
        NameToken const* const names OMNI_ATTR("in, not_null, count=nameCount"),
        size_t nameCount,
        BundleHandle* const foundBundles OMNI_ATTR("out, not_null, count=nameCount")) noexcept = 0;

    //! @brief Create new attributes by copying existing.
    //!
    //! Source attribute handles' data and metadata are copied. If a handle is invalid,
    //! then its source is ignored.
    //! Created attributes are owned by this bundle.
    //!
    //! @param newNames The names for the new attributes, if `nullptr` then names are taken from the source attributes.
    //! @param sourceAttributes Handles to attributes whose data type is to be copied.
    //! @param attributeCount Number of attributes to be copied.
    //! @param overwrite An option to overwrite existing attributes.
    //! @param copiedAttributes Output handles to the newly copied attributes. Can be `nullptr` if no output is
    //!        required.
    //! @param copiedCount Number of successfully copied attributes.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result copyAttributes_abi(
        NameToken const* const newNames OMNI_ATTR("in, count=attributeCount"),
        ConstAttributeDataHandle const* const sourceAttributes OMNI_ATTR("in, not_null, count=attributeCount"),
        size_t attributeCount,
        bool overwrite,
        AttributeDataHandle* const copiedAttributes OMNI_ATTR("out, count=attributeCount"),
        size_t* const copiedCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief Create attributes based on provided names and types.
    //!
    //! Created attributes are owned by this bundle.
    //!
    //! @param names The names of the attributes.
    //! @param types The types of the attributes.
    //! @param elementCount Number of elements in the array, can be `nullptr` if attribute is not an array.
    //! @param attributeCount Number of attributes to be created.
    //! @param createdAttributes Output handles to the newly created attributes. Can be nullptr if no output is
    //!        required.
    //! @param createdCount Number of successfully created attributes.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result createAttributes_abi(
        NameToken const* const names OMNI_ATTR("in, not_null, count=attributeCount"),
        Type const* const types OMNI_ATTR("in, not_null, count=attributeCount"),
        size_t const* const elementCount OMNI_ATTR("in, not_null, count=attributeCount"),
        size_t attributeCount,
        AttributeDataHandle* const createdAttributes OMNI_ATTR("out, count=attributeCount"),
        size_t* const createdCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief Use attribute handles as pattern to create new attributes.
    //!
    //! The name and type for new attributes are taken from pattern attributes, data and metadata is not copied.
    //! If pattern handle is invalid, then attribute creation is skipped.
    //! Created attributes are owned by this bundle.
    //!
    //! @param patternAttributes Attributes whose name and type is to be used to create new attributes.
    //! @param patternCount Number of attributes to be created.
    //! @param createdAttributes Output handles to the newly created attributes. Can be nullptr if no output is
    //! required.
    //! @param createdCount Number of successfully created attributes.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result createAttributesLike_abi(
        ConstAttributeDataHandle const* const patternAttributes OMNI_ATTR("in, not_null, count=patternCount"),
        size_t patternCount,
        AttributeDataHandle* const createdAttributes OMNI_ATTR("out, count=patternCount"),
        size_t* const createdCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief Create immediate child bundles under specified names in this bundle.
    //!
    //! Only immediate children are created. This method does not work recursively.
    //! If name token is invalid, then child bundle creation is skipped.
    //! Created bundles are owned by this bundle.
    //!
    //! @param names New children names in this bundle.
    //! @param nameCount Number of bundles to be created.
    //! @param createdBundles Output handles to the newly created bundles. Can be nullptr if no output is required.
    //! @param createdCount Number of successfully created child bundles.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result createChildBundles_abi(
        NameToken const* const names OMNI_ATTR("in, not_null, count=nameCount"),
        size_t nameCount,
        BundleHandle* const createdBundles OMNI_ATTR("out, count=nameCount"),
        size_t* const createdCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! <b>Feature not implemented yet.</b>
    //!
    //! @brief Add a set of attributes to this bundle as links.
    //!
    //! Added attributes are links to other attributes that are part of another bundle.
    //! If target handle is invalid, then linking is skipped.
    //! The links are owned by this bundle, but targets of the links are not.
    //! Removing links from this bundle does not destroy the data links point to.
    //!
    //! @param linkNames The names for new links.
    //! @param targetAttributes Handles to attributes whose data is to be added.
    //! @param attributeCount Number of attributes to be added.
    //! @param linkedAttributes Output handles to linked attributes. Can be nullptr if no output is required.
    //! @param linkedCount Number of attributes successfully linked.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result linkAttributes_abi(
        NameToken const* const linkNames OMNI_ATTR("in, count=attributeCount"),
        ConstAttributeDataHandle const* const targetAttributes OMNI_ATTR("in, not_null, count=attributeCount"),
        size_t attributeCount,
        AttributeDataHandle* const linkedAttributes OMNI_ATTR("out, count=attributeCount"),
        size_t* const linkedCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief Copy bundle data and metadata from the source bundle to this bundle.
    //!
    //! If source handle is invalid, then operation is skipped.
    //!
    //! @param sourceBundle Handle to bundle whose data is to be copied.
    //! @param overwrite An option to overwrite existing content of the bundle.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //! invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result copyBundle_abi(ConstBundleHandle sourceBundle, bool overwrite) noexcept = 0;

    //! @brief Create new child bundles by copying existing.
    //!
    //! Source bundle handles' data and metadata are copied. If a handle is invalid,
    //! then its source is ignored.
    //! Created bundles are owned by this bundle.
    //!
    //! @param newNames Names for new children, if `nullptr` then names are taken from the source bundles.
    //! @param sourceBundles Handles to bundles whose data is to be copied.
    //! @param bundleCount Number of bundles to be copied.
    //! @param overwrite An option to overwrite existing child bundles.
    //! @param copiedBundles Output handles to the newly copied bundles. Can be `nullptr` if no output is required.
    //! @param copiedCount Number of successfully copied child bundles.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result copyChildBundles_abi(
        NameToken const* const newNames OMNI_ATTR("in, count=bundleCount"),
        ConstBundleHandle const* const sourceBundles OMNI_ATTR("in, not_null, count=bundleCount"),
        size_t bundleCount,
        bool overwrite,
        BundleHandle* const copiedBundles OMNI_ATTR("out, count=bundleCount"),
        size_t* const copiedCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! <b>Feature not implemented yet.</b>
    //!
    //! @brief Link content from the source bundle to this bundle.
    //!
    //! If source handle is invalid, then operation is skipped.
    //!
    //! @param sourceBundle Handle to bundle whose data is to be linked.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result linkBundle_abi(
        ConstBundleHandle const* const sourceBundle OMNI_ATTR("in, not_null")) noexcept = 0;

    //! @brief Add a set of bundles as children to this bundle as links.
    //!
    //! Created bundles are links to other bundles that are part of another bundle.
    //! If target handle is invalid, then operation is skipped.
    //! The links are owned by this bundle, but targets of the links are not.
    //! Removing links from this bundle does not destroy the targets data.
    //!
    //! @param linkNames Names for new links.
    //! @param targetBundles Handles to bundles whose data is to be added.
    //! @param bundleCount Number of bundles to be added.
    //! @param linkedBundles Handles to linked bundles. Can be nullptr if no output is required.
    //! @param linkedCount Number of child bundles successfully linked.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result linkChildBundles_abi(
        NameToken const* const linkNames OMNI_ATTR("in, count=bundleCount"),
        ConstBundleHandle const* const targetBundles OMNI_ATTR("in, not_null, count=bundleCount"),
        size_t bundleCount,
        BundleHandle* const linkedBundles OMNI_ATTR("out, count=bundleCount"),
        size_t* const linkedCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief Remove attributes based on provided handles.
    //!
    //! Lookup the attribute handles and if they are part of this bundle then remove attributes' data and
    //! metadata. Attribute handles that are not part of this bundle are ignored.
    //!
    //! @param attributes Handles to attributes whose data is to be removed
    //! @param attributeCount Number of attributes to be removed.
    //! @param removedCount Number of attributes successfully removed.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result removeAttributes_abi(ConstAttributeDataHandle const* const attributes
                                                        OMNI_ATTR("in, not_null, count=attributeCount"),
                                                    size_t attributeCount,
                                                    size_t* const removedCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief  Remove attributes based on provided names.
    //!
    //! Lookup the attribute names and if they are part of this bundle then remove attributes' data and
    //! metadata. Attribute names that are not part of this bundle are ignored.
    //!
    //! @param names The names of the attributes whose data is to be removed.
    //! @param nameCount Number of attributes to be removed.
    //! @param removedCount Number of attributes successfully removed.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result removeAttributesByName_abi(
        NameToken const* const names OMNI_ATTR("in, not_null, count=nameCount"),
        size_t nameCount,
        size_t* const removedCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief Remove child bundles based on provided handles.
    //!
    //! Lookup the bundle handles and if they are children of the bundle then remove them and their metadata.
    //! Bundle handles that are not children of this bundle are ignored.
    //! Only empty child bundles can be removed.
    //!
    //! @param childHandles Handles to bundles to be removed.
    //! @param childCount Number of child bundles to be removed.
    //! @param removedCount Number of child bundles successfully removed.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result removeChildBundles_abi(
        ConstBundleHandle const* const childHandles OMNI_ATTR("in, not_null, count=bundleCount"),
        size_t childCount,
        size_t* const removedCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief  Remove child bundles based on provided names.
    //!
    //! Lookup the bundle names and if the are children of the bundle then remove them and their metadata.
    //! Bundle names that are not children of this bundle are ignored.
    //! Only empty child bundles can be removed.
    //!
    //! @param names The names of the child bundles to be removed.
    //! @param nameCount Number of child bundles to be removed.
    //! @param removedCount Number of child bundles successfully removed.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result removeChildBundlesByName_abi(
        NameToken const* const names OMNI_ATTR("in, not_null, count=nameCount"),
        size_t nameCount,
        size_t* const removedCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @deprecated Metadata storage is deprecated and invalid handle is returned.
    OMNI_ATTR("no_py")
    virtual BundleHandle getMetadataStorage_abi() noexcept = 0;

    //! @brief Search for bundle metadata fields based on provided names.
    //!
    //! Invalid attribute handles are returned for not existing names.
    //!
    //! @param fieldNames Bundle metadata field names to be searched for.
    //! @param fieldCount Size of fieldNames and bundleMetadata arrays.
    //! @param bundleMetadata Handles to bundle metadata fields in this bundle.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getBundleMetadataByName_abi(
        NameToken const* const fieldNames OMNI_ATTR("in, count=fieldCount"),
        size_t fieldCount,
        AttributeDataHandle* const bundleMetadata OMNI_ATTR("out, count=fieldCount")) noexcept = 0;

    //! @brief Create bundle metadata fields in this bundle.
    //!
    //! @param fieldNames Names of new bundle metadata fields.
    //! @param fieldTypes Types of new bundle metadata fields.
    //! @param elementCount Number of elements in the array, can be `nullptr` if field is not an array.
    //! @param fieldCount Size of fieldNames and fieldTypes arrays.
    //! @param bundleMetadata Handles to the newly created bundle metadata fields. Can be `nullptr` if no output is
    //! required.
    //! @param createdCount Number of child bundles successfully created.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result createBundleMetadata_abi(
        NameToken const* const fieldNames OMNI_ATTR("in, count=fieldCount"),
        Type const* const fieldTypes OMNI_ATTR("in, count=fieldCount"),
        size_t const* const elementCount OMNI_ATTR("in, count=fieldCount"),
        size_t fieldCount,
        AttributeDataHandle* const bundleMetadata OMNI_ATTR("out, count=fieldCount"),
        size_t* const createdCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief Remove bundle metadata based on provided field names.
    //!
    //! @param fieldNames Names of the bundle metadata fields whose data is to be removed.
    //! @param fieldCount Number of the bundle metadata fields to be removed.
    //! @param removedCount Number of bundle metadata fields successfully removed.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result removeBundleMetadata_abi(
        NameToken const* const fieldNames OMNI_ATTR("in, not_null, count=fieldCount"),
        size_t fieldCount,
        size_t* const removedCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief Search for read write field handles in the attribute by using field names.
    //!
    //! @copydetails IConstBundle2_abi::getConstAttributeMetadataByName_abi
    OMNI_ATTR("no_py")
    virtual omni::core::Result getAttributeMetadataByName_abi(
        NameToken attribute,
        NameToken const* const fieldNames OMNI_ATTR("in, count=fieldCount"),
        size_t fieldCount,
        AttributeDataHandle* const attributeMetadata OMNI_ATTR("out, count=fieldCount")) noexcept = 0;

    //! @brief Create attribute metadata fields.
    //!
    //! @param attribute Name of the attribute.
    //! @param fieldNames Names of new attribute metadata fields.
    //! @param fieldTypes Types of new attribute metadata fields.
    //! @param elementCount Number of elements in the array, can be `nullptr` if field is not an array.
    //! @param fieldCount Size of fieldNames and fieldTypes arrays.
    //! @param attributeMetadata Handles to the newly created attribute metadata. Can be `nullptr` if no output is
    //! required.
    //! @param createdCount Number of attribute metadata fields successfully created.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result createAttributeMetadata_abi(
        NameToken attribute,
        NameToken const* const fieldNames OMNI_ATTR("in, count=fieldCount"),
        Type const* const fieldTypes OMNI_ATTR("in, count=fieldCount"),
        size_t const* const elementCount OMNI_ATTR("in, count=fieldCount"),
        size_t fieldCount,
        AttributeDataHandle* const attributeMetadata OMNI_ATTR("out, count=fieldCount"),
        size_t* const createdCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief Remove attribute metadata fields.
    //!
    //! @param attribute Name of the attribute.
    //! @param fieldNames Names of the attribute metadata fields to be removed.
    //! @param fieldCount Size of fieldNames array.
    //! @param removedCount Number of attribute metadata fields successfully removed.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result removeAttributeMetadata_abi(
        NameToken attribute,
        NameToken const* const fieldNames OMNI_ATTR("in, count=fieldCount"),
        size_t fieldCount,
        size_t* const removedCount OMNI_ATTR("out, not_null")) noexcept = 0;

    //! @brief Remove all attributes, child bundles and metadata from this bundle, but keep the bundle itself.
    //!
    //! @param bundleMetadata Clears bundle metadata in this bundle.
    //! @param attributes Clears attributes in this bundle.
    //! @param childBundles Clears child bundles in this bundle.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result clearContents_abi(bool bundleMetadata, bool attributes, bool childBundles) noexcept = 0;
};

} // namespace core
} // namespace graph
} // namespace omni

#include "IBundle2.gen.h"

//! @cond Doxygen_Suppress
//!
//! API part of the bundle factory interface
//! @copydoc omni::graph::core::IBundle2_abi
OMNI_DEFINE_INTERFACE_API(omni::graph::core::IBundle2)
//! @endcond
{
public:
    //! @copydoc omni::graph::core::IBundle2::getAttributes_abi
    omni::core::Result getAttributes(
        omni::graph::core::AttributeDataHandle* const attributes, size_t attributeCount) noexcept
    {
        return getAttributes_abi(attributes, &attributeCount);
    }

    //! @brief Searches for read-write handle of the attribute in this bundle by using attribute name.
    //!
    //! @param name The name of the attribute to search for.
    //! @return Valid attribute handle if attribute if found, invalid handle otherwise.
    omni::graph::core::AttributeDataHandle getAttributeByName(omni::graph::core::NameToken name) noexcept
    {
        using namespace omni::graph::core;
        AttributeDataHandle out{ AttributeDataHandle::invalidValue() };
        auto result = getAttributesByName_abi(&name, 1, &out);
        return OMNI_SUCCEEDED(result) ? out : AttributeDataHandle{ AttributeDataHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::getChildBundles_abi
    omni::core::Result getChildBundles(omni::graph::core::BundleHandle* const bundles, size_t bundleCount) noexcept
    {
        return getChildBundles_abi(bundles, &bundleCount);
    }

    //! @brief Get the child bundle handle by index.
    //!
    //! If bundle index is out of range, then invalid handle is returned.
    //!
    //! @param bundleIndex Bundle index in range [0, childBundleCount).
    //! @return Bundle handle under the index.
    omni::graph::core::BundleHandle getChildBundle(size_t bundleIndex) noexcept
    {
        using namespace omni::graph::core;
        BundleHandle out{ BundleHandle::invalidValue() };
        auto result = getChildBundle_abi(bundleIndex, &out);
        return OMNI_SUCCEEDED(result) ? out : BundleHandle{ BundleHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::copyAttributes_abi
    template <typename HANDLE>
    omni::core::Result copyAttributes(HANDLE const* const sourceAttributes, size_t attributeCount, bool overwrite = true,
                                      omni::graph::core::NameToken const* const newNames = nullptr,
                                      omni::graph::core::AttributeDataHandle* const copiedAttributes = nullptr,
                                      size_t* const copiedCount = nullptr) noexcept
    {
        using namespace omni::graph::core;
        static_assert(
            std::is_same<HANDLE, AttributeDataHandle>::value || std::is_same<HANDLE, ConstAttributeDataHandle>::value,
            "Only AttributeDataHandle and ConstAttributeDataHandle can be copied");

        return copyAttributes_abi(newNames, reinterpret_cast<ConstAttributeDataHandle const* const>(sourceAttributes),
                                  attributeCount, overwrite, copiedAttributes, copiedCount);
    }

    //! @brief Create new attribute by copying existing attribute's data and metadata.
    //!
    //! Created attribute is owned by this bundle.
    //!
    //! @param sourceAttribute Handle to attribute whose data type is to be copied.
    //! @param overwrite Overwrites existing attributes.
    //! @param newName The new name for copied attribute.
    //! @return Output handle to the newly copied attribute.
    omni::graph::core::AttributeDataHandle copyAttribute(
        omni::graph::core::ConstAttributeDataHandle const& sourceAttribute, bool overwrite = true,
        omni::graph::core::NameToken newName = omni::fabric::kUninitializedToken) noexcept
    {
        using namespace omni::graph::core;
        AttributeDataHandle out{ AttributeDataHandle::invalidValue() };
        NameToken* newNamePtr = newName == omni::fabric::kUninitializedToken ? nullptr : &newName;
        auto result = copyAttributes_abi(newNamePtr, &sourceAttribute, 1, overwrite, &out, nullptr);
        return OMNI_SUCCEEDED(result) ? out : AttributeDataHandle{ AttributeDataHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::createAttributes_abi
    omni::core::Result createAttributes(omni::graph::core::NameToken const* const names,
                                        omni::graph::core::Type const* const types, size_t attributeCount,
                                        size_t const* const elementCount = nullptr,
                                        omni::graph::core::AttributeDataHandle* const createdAttributes = nullptr,
                                        size_t* const createdCount = nullptr) noexcept
    {
        return createAttributes_abi(names, types, elementCount, attributeCount, createdAttributes, createdCount);
    }

    //! @brief Create attribute based on provided name and type.
    //!
    //! Created attribute is owned by this bundle.
    //!
    //! @param name The name of the attribute.
    //! @param type The type of the attribute.
    //! @param elementCount Number of elements in the array.
    //! @return Output handle to the newly created attribute.
    omni::graph::core::AttributeDataHandle createAttribute(
        omni::graph::core::NameToken name, omni::graph::core::Type const& type, size_t elementCount = 0) noexcept
    {
        using namespace omni::graph::core;
        omni::core::Result result = kResultFail;
        AttributeDataHandle out{ AttributeDataHandle::invalidValue() };
        size_t* elementCountPtr = type.arrayDepth == 0 ? nullptr : &elementCount;
        result = createAttributes_abi(&name, &type, elementCountPtr, 1, &out, nullptr);
        return OMNI_SUCCEEDED(result) ? out : AttributeDataHandle{ AttributeDataHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::createAttributesLike_abi
    omni::core::Result createAttributesLike(omni::graph::core::ConstAttributeDataHandle const* const patternAttributes,
                                            size_t patternCount,
                                            omni::graph::core::AttributeDataHandle* const createdAttributes = nullptr,
                                            size_t* const createdCount = nullptr) noexcept
    {
        return createAttributesLike_abi(patternAttributes, patternCount, createdAttributes, createdCount);
    }

    //! @brief Use input attribute handle as pattern to create attribute in this bundle.
    //!
    //! The name and type are taken from pattern attribute, data is not copied.
    //! Created attribute is owned by this bundle.
    //!
    //! @param patternAttribute Attribute whose name and type is to be used to create new attribute.
    //! @return Output handle to the newly created attribute.
    omni::graph::core::AttributeDataHandle createAttributeLike(
        omni::graph::core::ConstAttributeDataHandle const& patternAttribute) noexcept
    {
        using namespace omni::graph::core;
        AttributeDataHandle out{ AttributeDataHandle::invalidValue() };
        auto result = createAttributesLike_abi(&patternAttribute, 1, &out, nullptr);
        return OMNI_SUCCEEDED(result) ? out : AttributeDataHandle{ AttributeDataHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::createChildBundles_abi
    omni::core::Result createChildBundles(omni::graph::core::NameToken const* const names, size_t nameCount,
                                          omni::graph::core::BundleHandle* const createdBundles = nullptr,
                                          size_t* const createdCount = nullptr) noexcept
    {
        return createChildBundles_abi(names, nameCount, createdBundles, createdCount);
    }

    //! @brief Create immediate child bundle under specified name.
    //!
    //! Created bundle is owned by this bundle. This method does not work recursively. Only immediate child can be
    //! created.
    //!
    //! @param name New child name in this bundle.
    //! @return Output handle to the newly created bundle.
    omni::graph::core::BundleHandle createChildBundle(omni::graph::core::NameToken name) noexcept
    {
        using namespace omni::graph::core;
        BundleHandle out{ BundleHandle::invalidValue() };
        auto result = createChildBundles_abi(&name, 1, &out, nullptr);
        return OMNI_SUCCEEDED(result) ? out : BundleHandle{ BundleHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::linkAttributes_abi
    template <typename HANDLE>
    omni::core::Result linkAttributes(HANDLE const* const targetAttributes, size_t attributeCount,
                                      omni::graph::core::NameToken const* const linkNames = nullptr,
                                      omni::graph::core::AttributeDataHandle* const linkedAttributes = nullptr,
                                      size_t* const linkedCount = nullptr) noexcept
    {
        using namespace omni::graph::core;
        static_assert(
            std::is_same<HANDLE, AttributeDataHandle>::value || std::is_same<HANDLE, ConstAttributeDataHandle>::value,
            "Only AttributeDataHandle and ConstAttributeDataHandle can be copied");

        auto linkedAttributesPtr = reinterpret_cast<ConstAttributeDataHandle const* const>(targetAttributes);
        return linkAttributes_abi(linkNames, linkedAttributesPtr, attributeCount, linkedAttributes, linkedCount);
    }

    //! < b>Feature not implemented yet.< /b>
    //!
    //! @brief Add an attribute to this bundle as link with custom name.
    //!
    //! Added attribute is a link to other attribute that is part of another bundle.
    //! The link is owned by this bundle, but target of the link is not.
    //! Removing link from this bundle does not destroy the data link points to.
    //!
    //! @param linkName Name for new link.
    //! @param targetAttribute Handle to attribute whose data is to be added.
    //! @return Output handle to linked attributes.
    omni::graph::core::AttributeDataHandle linkAttribute(
        omni::graph::core::ConstAttributeDataHandle const& targetAttribute,
        omni::graph::core::NameToken linkName = omni::fabric::kUninitializedToken) noexcept
    {
        using namespace omni::graph::core;
        AttributeDataHandle out{ AttributeDataHandle::invalidValue() };
        auto result = linkAttributes_abi(&linkName, &targetAttribute, 1, &out, nullptr);
        return OMNI_SUCCEEDED(result) ? out : AttributeDataHandle{ AttributeDataHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::copyBundle_abi
    omni::core::Result copyBundle(omni::graph::core::ConstBundleHandle sourceBundle, bool overwrite = true) noexcept
    {
        return copyBundle_abi(sourceBundle, overwrite);
    }

    //! @copydoc omni::graph::core::IBundle2_abi::copyChildBundles_abi
    template <typename HANDLE>
    omni::core::Result copyChildBundles(HANDLE const* const sourceBundles, size_t bundleCount, bool overwrite = true,
                                        omni::graph::core::NameToken const* const newNames = nullptr,
                                        omni::graph::core::BundleHandle* const copiedBundles = nullptr,
                                        size_t* const copiedCount = nullptr) noexcept
    {
        using namespace omni::graph::core;
        static_assert(std::is_same<HANDLE, BundleHandle>::value || std::is_same<HANDLE, ConstBundleHandle>::value,
                      "Only BundleHandle and ConstBundleHandle can be copied");

        auto sourceBundlesPtr = reinterpret_cast<ConstBundleHandle const* const>(sourceBundles);
        return copyChildBundles_abi(newNames, sourceBundlesPtr, bundleCount, overwrite, copiedBundles, copiedCount);
    }

    //! @brief Create new child bundle by copying existing bundle's data and metadata, with possibility of giving child
    //! a new name.
    //!
    //! Created bundle is owned by this bundle.
    //!
    //! @param sourceBundle Handle to bundle whose data is to be copied.
    //! @param overwrite An option to overwrite child bundle.
    //! @param newName Name for new child.
    //! @return Output handles to the newly copied bundle.
    omni::graph::core::BundleHandle copyChildBundle(
        omni::graph::core::ConstBundleHandle const& sourceBundle, bool overwrite = true,
        omni::graph::core::NameToken newName = omni::fabric::kUninitializedToken) noexcept
    {
        using namespace omni::graph::core;
        BundleHandle out{ BundleHandle::invalidValue() };
        NameToken* newNamePtr = newName == omni::fabric::kUninitializedToken ? nullptr : &newName;
        auto result = copyChildBundles_abi(newNamePtr, &sourceBundle, 1, overwrite, &out, nullptr);
        return OMNI_SUCCEEDED(result) ? out : BundleHandle{ BundleHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::removeAttributes_abi
    template <typename HANDLE>
    omni::core::Result removeAttributes(
        HANDLE const* const attributes, size_t attributeCount, size_t* const removedCount = nullptr) noexcept
    {
        using namespace omni::graph::core;
        static_assert(
            std::is_same<HANDLE, AttributeDataHandle>::value || std::is_same<HANDLE, ConstAttributeDataHandle>::value,
            "Only AttributeDataHandle and ConstAttributeDataHandle can be copied");

        auto attributesPtr = reinterpret_cast<ConstAttributeDataHandle const* const>(attributes);
        return removeAttributes_abi(attributesPtr, attributeCount, removedCount);
    }

    //! @brief Lookup the attribute handle and if it is part of this bundle then remove attributes' data and
    //! metadata.
    //!
    //! Attribute handle that is not part of this bundle is ignored.
    //!
    //! @param attribute Handle to attribute whose data is to be removed.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    omni::core::Result removeAttribute(omni::graph::core::ConstAttributeDataHandle const& attribute) noexcept
    {
        return removeAttributes_abi(&attribute, 1, nullptr);
    }

    //! @copydoc omni::graph::core::IBundle2_abi::removeAttributesByName_abi
    omni::core::Result removeAttributesByName(omni::graph::core::NameToken const* const names, size_t nameCount,
                                              size_t* const removedCount = nullptr) noexcept
    {
        return removeAttributesByName_abi(names, nameCount, removedCount);
    }

    //! @brief Lookup the attribute by name and remove its data and metadata.
    //!
    //! @param name The name of the attribute whose data is to be removed.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    omni::core::Result removeAttributeByName(omni::graph::core::NameToken name) noexcept
    {
        return removeAttributesByName_abi(&name, 1, nullptr);
    }

    //! @copydoc omni::graph::core::IBundle2_abi::removeChildBundles_abi
    template <typename HANDLE>
    omni::core::Result removeChildBundles(
        HANDLE const* const bundles, size_t bundleCount, size_t* const removedCount = nullptr) noexcept
    {
        using namespace omni::graph::core;
        static_assert(std::is_same<HANDLE, BundleHandle>::value || std::is_same<HANDLE, ConstBundleHandle>::value,
                      "Only BundleHandle and ConstBundleHandle can be copied");

        auto bundlesPtr = reinterpret_cast<ConstBundleHandle const* const>(bundles);
        return removeChildBundles_abi(bundlesPtr, bundleCount, removedCount);
    }

    //! @brief Lookup the bundle handle and if it is child of the bundle then remove it and its metadata.
    //!
    //! Bundle handle that is not child of this bundle is ignored. Only empty bundle can be removed.
    //!
    //! @param bundle Handle to bundle to be removed.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    omni::core::Result removeChildBundle(omni::graph::core::ConstBundleHandle const& bundle) noexcept
    {
        return removeChildBundles_abi(&bundle, 1, nullptr);
    }

    //! @copydoc omni::graph::core::IBundle2_abi::removeChildBundlesByName_abi
    omni::core::Result removeChildBundlesByName(omni::graph::core::NameToken const* const names, size_t nameCount,
                                                size_t* const removedCount = nullptr) noexcept
    {
        return removeChildBundlesByName_abi(names, nameCount, removedCount);
    }

    //! @brief Lookup child bundle by name and remove its data and metadata.
    //!
    //! @param name The name of the child bundle to be removed.
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    omni::core::Result removeChildBundleByName(omni::graph::core::NameToken name) noexcept
    {
        return removeChildBundlesByName_abi(&name, 1, nullptr);
    }

    //! @brief Lookup for child under specified name.
    //!
    //! For child that is not found invalid handle is returned.
    //!
    //! @param name The name of bundle child in this bundle.
    //! @return Output handle to the found bundle.
    omni::graph::core::BundleHandle getChildBundleByName(omni::graph::core::NameToken name) noexcept
    {
        using namespace omni::graph::core;
        BundleHandle out{ BundleHandle::invalidValue() };
        auto result = getChildBundlesByName_abi(&name, 1, &out);
        return OMNI_SUCCEEDED(result) ? out : BundleHandle{ BundleHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::getBundleMetadataByName_abi
    using omni::core::Generated<omni::graph::core::IBundle2_abi>::getBundleMetadataByName;

    //! @brief Search for bundle metadata field based on provided name.
    //!
    //! Invalid attribute handle is returned for not existing name.
    //!
    //! @param fieldName Bundle metadata field name to be searched for.
    //!
    //! @return Valid metadata attribute handle for existing name, or Invalid handle for not existing.
    omni::graph::core::AttributeDataHandle getBundleMetadataByName(omni::graph::core::NameToken fieldName) noexcept
    {
        using namespace omni::graph::core;
        AttributeDataHandle out{ AttributeDataHandle::invalidValue() };
        auto result = getBundleMetadataByName_abi(&fieldName, 1, &out);
        return OMNI_SUCCEEDED(result) ? out : AttributeDataHandle{ AttributeDataHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::createBundleMetadata_abi
    omni::core::Result createBundleMetadata(omni::graph::core::NameToken const* const fieldNames,
                                            omni::graph::core::Type const* const fieldTypes, size_t fieldCount,
                                            size_t const* const elementCount = nullptr,
                                            omni::graph::core::AttributeDataHandle* const bundleMetadata = nullptr,
                                            size_t* const createdCount = nullptr) noexcept
    {
        return createBundleMetadata_abi(fieldNames, fieldTypes, elementCount, fieldCount, bundleMetadata, createdCount);
    }

    //! @brief Create bundle metadata field in this bundle.
    //!
    //! @param fieldName Name of new bundle metadata field.
    //! @param fieldType Type of new bundle metadata field.
    //! @param elementCount Number of elements in the array, if fieldType is an array type.
    //!
    //! @return Valid metadata attribute handle for existing name, or Invalid handle for not existing.
    omni::graph::core::AttributeDataHandle createBundleMetadata(
        omni::graph::core::NameToken fieldName, omni::graph::core::Type const& fieldType, size_t elementCount = 0) noexcept
    {
        using namespace omni::graph::core;
        AttributeDataHandle out{ AttributeDataHandle::invalidValue() };
        auto result = createBundleMetadata_abi(&fieldName, &fieldType, &elementCount, 1, &out, nullptr);
        return OMNI_SUCCEEDED(result) ? out : AttributeDataHandle{ AttributeDataHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::removeBundleMetadata_abi
    omni::core::Result removeBundleMetadata(omni::graph::core::NameToken const* const fieldNames, size_t fieldCount,
                                            size_t* const removedCount = nullptr) noexcept
    {
        return removeBundleMetadata_abi(fieldNames, fieldCount, removedCount);
    }

    //! @brief Remove bundle metadata based on provided field name.
    //!
    //! @param fieldName Name of the bundle metadata field whose data is to be removed.
    //!
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    omni::core::Result removeBundleMetadata(omni::graph::core::NameToken fieldName) noexcept
    {
        return removeBundleMetadata_abi(&fieldName, 1, nullptr);
    }

    //! @copydoc omni::graph::core::IBundle2_abi::getAttributeMetadataByName_abi
    using omni::core::Generated<omni::graph::core::IBundle2_abi>::getAttributeMetadataByName;

    //! @brief Search for read-write metadata field handle for the attribute by using field name.
    //!
    //! @param attribute The name of the attribute.
    //! @param fieldName The name of attribute metadata field to be searched for.
    //!
    //! @return Valid metadata attribute handle for existing name, or Invalid handle for not existing.
    omni::graph::core::AttributeDataHandle getAttributeMetadataByName(
        omni::graph::core::NameToken attribute, omni::graph::core::NameToken fieldName) noexcept
    {
        using namespace omni::graph::core;
        AttributeDataHandle out{ AttributeDataHandle::invalidValue() };
        auto result = getAttributeMetadataByName_abi(attribute, &fieldName, 1, &out);
        return OMNI_SUCCEEDED(result) ? out : AttributeDataHandle{ AttributeDataHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::createAttributeMetadata_abi
    omni::core::Result createAttributeMetadata(
        omni::graph::core::NameToken attribute, omni::graph::core::NameToken const* const fieldNames,
        omni::graph::core::Type const* const fieldTypes, size_t fieldCount, size_t const* const elementCount = nullptr,
        omni::graph::core::AttributeDataHandle* const attributeMetadata = nullptr,
        size_t* const createdCount = nullptr) noexcept
    {
        return createAttributeMetadata_abi(
            attribute, fieldNames, fieldTypes, elementCount, fieldCount, attributeMetadata, createdCount);
    }

    //! @brief Create attribute metadata field.
    //!
    //! @param attribute Name of the attribute.
    //! @param fieldName Name of new attribute metadata field.
    //! @param fieldType Type of new attribute metadata field.
    //! @param elementCount Number of elements in the array.
    //! @return Handle to the newly created attribute metadata field.
    omni::graph::core::AttributeDataHandle createAttributeMetadata(
        omni::graph::core::NameToken attribute, omni::graph::core::NameToken fieldName,
        omni::graph::core::Type const& fieldType, size_t elementCount = 0) noexcept
    {
        using namespace omni::graph::core;
        AttributeDataHandle out{ AttributeDataHandle::invalidValue() };
        size_t* elementCountPtr = fieldType.arrayDepth == 0 ? nullptr : &elementCount;
        auto result = createAttributeMetadata_abi(attribute, &fieldName, &fieldType, elementCountPtr, 1, &out, nullptr);
        return OMNI_SUCCEEDED(result) ? out : AttributeDataHandle{ AttributeDataHandle::invalidValue() };
    }

    //! @copydoc omni::graph::core::IBundle2_abi::removeAttributeMetadata_abi
    omni::core::Result removeAttributeMetadata(omni::graph::core::NameToken attribute,
                                               omni::graph::core::NameToken const* const fieldNames, size_t fieldCount,
                                               size_t* const removedCount = nullptr) noexcept
    {
        return removeAttributeMetadata_abi(attribute, fieldNames, fieldCount, removedCount);
    }

    //! @copydoc omni::graph::core::IBundle2_abi::removeAttributeMetadata_abi
    using omni::core::Generated<omni::graph::core::IBundle2_abi>::removeAttributeMetadata;

    //! @brief Remove attribute metadata field.
    //!
    //! @param attribute Name of the attribute.
    //! @param fieldName Name of the attribute metadata field to be removed.
    //!
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //!         invalid.
    omni::core::Result removeAttributeMetadata(
        omni::graph::core::NameToken attribute, omni::graph::core::NameToken fieldName) noexcept
    {
        return removeAttributeMetadata_abi(attribute, &fieldName, 1, nullptr);
    }

    //! @copydoc omni::graph::core::IBundle2_abi::clearContents_abi
    omni::core::Result clearContents(bool bundleMetadata = true, bool attributes = true, bool childBundles = true) noexcept
    {
        return clearContents_abi(bundleMetadata, attributes, childBundles);
    }

    CARB_DEPRECATED("Accessing child bundles by index is deprecated, look up children by name")
    omni::core::Result getChildBundle(size_t bundleIndex, omni::graph::core::BundleHandle* const bundle) noexcept
    {
        return getChildBundle_abi(bundleIndex, bundle);
    }
}; // IBundle2
