// Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/core/IObject.h>
#include <omni/graph/core/Handle.h>

namespace omni
{
namespace graph
{
namespace core
{

//! Enumeration representing the type of change that occurred in a bundle.
//!
//! This enumeration is used to identify the kind of modification that has taken place in a bundle or attribute.
//! It's used as the return type for functions that check bundles and attributes, signaling whether those have been
//! modified or not.
enum class BundleChangeType : uint64_t
{
    None = 0 << 0, //!< Indicates that no change has occurred in the bundle.
    Modified = 1 << 0, //!< Indicates that the bundle has been modified.
};

OMNI_DECLARE_INTERFACE(IBundleChanges);

//! Interface for monitoring and handling changes in bundles and attributes.
//!
//! The IBundleChanges_abi is an interface that provides methods for checking whether bundles and attributes
//! have been modified, and cleaning them if they have been modified. This is particularly useful in scenarios
//! where it's crucial to track changes and maintain the state of bundles and attributes.
//!
//! This interface provides several methods for checking and cleaning modifications, each catering to different
//! use cases such as handling single bundles, multiple bundles, attributes, or specific attributes of a single bundle.
//!
//! The methods of this interface return a BundleChangeType enumeration that indicates whether the checked entity
//! (bundle or attribute) has been modified.
class IBundleChanges_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.graph.core.IBundleChanges")>
{
protected:
    //! @brief Activate tracking for specific bundle on its attributes and children.
    //! @param handle to the specific bundles to enable change tracking.
    //! @return An omni::core::Result indicating the success of the operation.
    virtual omni::core::Result activateChangeTracking_abi(BundleHandle handle) noexcept = 0;

    //! @brief Deactivate tracking for specific bundle on its attributes and children.
    //! @param handle to the specific bundles to enable change tracking.
    //! @return An omni::core::Result indicating the success of the operation.
    virtual omni::core::Result deactivateChangeTracking_abi(BundleHandle handle) noexcept = 0;

    //! @brief Retrieves the change status of an array of bundles.
    //!
    //! This method is used to check if any of the bundles in the provided array have been modified.
    //!
    //! The count parameter indicates the size of the bundles array, as well as the changes output array.
    //!
    //! @param bundles An array of handles to the specific bundles to check for modifications.
    //! @param count The number of bundle handles in the array.
    //! @param changes An array that will be filled with BundleChangeType values for each bundle.
    //!
    //! @returns An omni::core::Result indicating the success of the operation.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getChangesForBundles_abi(
        ConstBundleHandle const* const bundles OMNI_ATTR("in, throw_if_null, count=count"),
        size_t count,
        BundleChangeType* const changes OMNI_ATTR("out, throw_if_null, count=count")) noexcept = 0;

    //! @brief Retrieves the change status of an array of attributes.
    //!
    //! This method is used to check if any of the attributes in the provided array have been modified.
    //!
    //! The count parameter indicates the size of the attributes array, as well as the changes output array.
    //!
    //! @param attributes An array of handles to the attributes to check for modifications.
    //! @param count The number of attribute handles in the array.
    //! @param changes An array that will be filled with BundleChangeType values for each attribute.
    //!
    //! @returns An omni::core::Result indicating the success of the operation.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getChangesForAttributes_abi(
        ConstAttributeDataHandle const* const attributes OMNI_ATTR("in, throw_if_null, count=count"),
        size_t count,
        BundleChangeType* const changes OMNI_ATTR("out, throw_if_null, count=count")) noexcept = 0;

    //! @brief Retrieves the change status of specific attributes within a bundle.
    //!
    //! This method is used to check if any of the specified attributes within a bundle have been modified.
    //! It operates by providing a handle to the bundle and an array of attribute names to check for modifications.
    //!
    //! The count parameter indicates the number of attribute names in the array, as well as the size of the changes
    //! output array.
    //!
    //! @param bundle A handle to the specific bundle for which attribute changes are being checked.
    //! @param attributes An array of attribute names (Tokens) to check for modifications.
    //! @param count The number of attribute names in the array.
    //! @param changes An array that will be filled with BundleChangeType values for each attribute.
    //!
    //! @returns An omni::core::Result indicating the success of the operation.
    OMNI_ATTR("no_py, no_api")
    virtual omni::core::Result getChangesForAttributesInBundle_abi(
        ConstBundleHandle const bundle,
        fabric::TokenC const* const attributes OMNI_ATTR("in, throw_if_null, count=count"),
        size_t count,
        BundleChangeType* const changes OMNI_ATTR("out, throw_if_null, count=count")) noexcept = 0;

    //! Clears all recorded changes.
    //!
    //! This method is used to clear or reset all the recorded changes of the bundles and attributes.
    //! It can be used when the changes have been processed and need to be discarded.
    //!
    //! An omni::core::Result indicating the success of the operation.
    virtual omni::core::Result clearChanges_abi() noexcept = 0;
};

}
}
}

#include "IBundleChanges1.gen.h"

OMNI_DEFINE_INTERFACE_API(omni::graph::core::IBundleChanges)
{
public:
    using BundleChangeType = omni::graph::core::BundleChangeType;
    using ConstBundleHandle = omni::graph::core::ConstBundleHandle;
    using ConstAttributeDataHandle = omni::graph::core::ConstAttributeDataHandle;

    //! @brief Retrieves the change status of a specific bundle.
    //!
    //! This method is used to check if a specific bundle or its contents have been modified.
    //!
    //! @param bundle The handle to the specific bundle to check for modifications.
    //!
    //! @returns A BundleChangeType value indicating the type of change (if any) that has occurred to the bundle.
    BundleChangeType getChange(ConstBundleHandle bundle)
    {
        BundleChangeType change;
        auto const result = getChangesForBundles_abi(&bundle, 1, &change);
        return OMNI_SUCCEEDED(result) ? change : BundleChangeType::None;
    }

    //! @brief Retrieves the change status of a specific attribute.
    //!
    //! This method is used to check if a specific attribute has been modified.
    //!
    //! @param attribute The handle to the specific attribute to check for modifications.
    //!
    //! @returns A BundleChangeType value indicating the type of change (if any) that has occurred to the attribute.
    BundleChangeType getChange(ConstAttributeDataHandle attribute)
    {
        BundleChangeType change;
        auto const result = getChangesForAttributes_abi(&attribute, 1, &change);
        return OMNI_SUCCEEDED(result) ? change : BundleChangeType::None;
    }

    //! @brief Retrieves the change status of multiple bundles.
    //!
    //! This method is used to check if any of the provided bundles or their contents have been modified.
    //!
    //! @param bundles An array of handles to the bundles to check for modifications.
    //! @param size The number of bundle handles in the array.
    //! @param changes An array that will be filled with BundleChangeType values for each bundle.
    //!
    //! @returns An omni::core::Result indicating the success of the operation.
    omni::core::Result getChanges(ConstBundleHandle const* bundles, size_t size, BundleChangeType* changes)
    {
        return getChangesForBundles_abi(bundles, size, changes);
    }

    //! @brief Retrieves the change status of multiple attributes.
    //!
    //! This method is used to check if any of the provided attributes have been modified.
    //!
    //! @param attributes An array of handles to the attributes to check for modifications.
    //! @param size The number of attribute handles in the array.
    //! @param changes An array that will be filled with BundleChangeType values for each attribute.
    //!
    //! @returns An omni::core::Result indicating the success of the operation.
    omni::core::Result getChanges(ConstAttributeDataHandle const* attributes, size_t size, BundleChangeType* changes)
    {
        return getChangesForAttributes_abi(attributes, size, changes);
    }

    //! @brief Retrieves the change status of multiple attributes within a specific bundle.
    //!
    //! This method is used to check if any of the specified attributes within a particular bundle have been modified.
    //!
    //! @param bundle The handle to the specific bundle whose attributes are to be checked for modifications.
    //! @param attributes An array of Tokens representing the attributes to check for modifications.
    //! @param size The number of attribute tokens in the array.
    //! @param changes An array that will be filled with BundleChangeType values for each attribute.
    //!
    //! @returns An omni::core::Result indicating the success of the operation.
    omni::core::Result getChanges(ConstBundleHandle bundle, fabric::TokenC const* attributes, size_t size, BundleChangeType* changes)
    {
        return getChangesForAttributesInBundle_abi(bundle, attributes, size, changes);
    }
};
