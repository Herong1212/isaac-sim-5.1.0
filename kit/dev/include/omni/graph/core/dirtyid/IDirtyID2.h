// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IDirtyID1.h"

#include <omni/core/IObject.h>
#include <omni/graph/core/Handle.h>

#include <type_traits>

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{

OMNI_DECLARE_INTERFACE(IDirtyID2);

// ====================================================================================================
/*
     _____          _   _       _     _    _
    |  __ \        | \ | |     | |   | |  | |
    | |  | | ___   |  \| | ___ | |_  | |  | |___  ___
    | |  | |/ _ \  | . ` |/ _ \| __| | |  | / __|/ _ \
    | |__| | (_) | | |\  | (_) | |_  | |__| \__ \  __/
    |_____/ \___/  |_| \_|\___/ \__|  \____/|___/\___|
*/
// The DirtyId interface exposes the implementation details of change tracking system for bundles.
// This functionality is exposed to allow old interfaces such as BundlePrims to function.
// Eventually this interface is going to be removed, once BundlePrims is fully deprecated.
// ====================================================================================================

class IDirtyID2_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.graph.core.IDirtyID2")>
{
protected:
    //! @brief Activate or deactivate dirty id tracking for specific bundle on its attributes and children.
    //! @param handle to dirty id track.
    //! @param isActive Bool flag indicating if tracking is on or off.
    //! @return An omni::core::Result indicating the success of the operation.
    OMNI_ATTR("no_py")
    virtual omni::core::Result setup_abi(BundleHandle handle, bool isActive) noexcept = 0;

    //! @brief Get dirty id values for bundles.
    //!
    //! The output array for dirty id values needs to be at least size of input
    //! array of bundle handles.
    //!
    //! @param bundles      Input bundles to get dirty ids for.
    //! @param bundleCount  Size of input bundles.
    //! @param ids          Output dirty id values for requested bundles.
    //!
    //! @returns Success if operation was successful.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getForBundles_abi(
        ConstBundleHandle const* const bundles OMNI_ATTR("in, throw_if_null, count=bundleCount"),
        size_t bundleCount OMNI_ATTR("in"),
        DirtyIDType* const ids OMNI_ATTR("out, throw_if_null, count=bundleCount")) noexcept = 0;

    //! @brief Get dirty id values for attributes.
    //!
    //! The output array for dirty id values needs to be at least size of input
    //! array of attribute handles.
    //!
    //! @param attributes       Input attributes to get dirty ids for.
    //! @param attributeCount   Size of input attributes.
    //! @param ids              Output dirty id values for requested attributes.
    //!
    //! @returns Success if operation was successful.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getForAttributes_abi(
        ConstAttributeDataHandle const* const attributes OMNI_ATTR("in, throw_if_null, count=attributeCount"),
        size_t attributeCount OMNI_ATTR("in"),
        DirtyIDType* const ids OMNI_ATTR("out, throw_if_null, count=attributeCount")) noexcept = 0;
};

}
}
}
}

#include "IDirtyID2.gen.h"

OMNI_DEFINE_INTERFACE_API(omni::graph::core::unstable::IDirtyID2)
{
public:

    using DirtyIDType = omni::graph::core::DirtyIDType;
    using BundleHandle = omni::graph::core::BundleHandle;
    using ConstBundleHandle = omni::graph::core::ConstBundleHandle;
    using AttributeDataHandle = omni::graph::core::AttributeDataHandle;
    using ConstAttributeDataHandle = omni::graph::core::ConstAttributeDataHandle;

    //! @return Get invalid dirty id value.
    static DirtyIDType getInvalid() noexcept
    {
        return omni::graph::core::kInvalidDirtyID;
    }

    //! @brief Checks if given dirty id is valid dirty id.
    static bool isValid(DirtyIDType value) noexcept
    {
        return value != getInvalid();
    }

    //! @brief Get array of dirty id values for array of bundles.
    //!
    //! The output array for dirty id values needs to be at least size of input
    //! array of bundle handles.
    //!
    //! @param bundles      Input array bundle handles to get dirty ids for.
    //! @param bundleCount  Size of input array of bundle handles.
    //! @param ids          Output array of dirty id values for requested bundles.
    //!
    //! @returns Success if operation was successful.
    template <typename BUNDLE_HANDLE>
    omni::core::Result getForBundles(BUNDLE_HANDLE* const bundles,
                                     size_t bundleCount,
                                     DirtyIDType* const ids)
    {
        using BundleHandle_t = typename std::remove_cv<BUNDLE_HANDLE>::type;
        static_assert(std::is_same<BundleHandle_t, BundleHandle>::value ||
                      std::is_same<BundleHandle_t, ConstBundleHandle>::value);
        return getForBundles_abi(reinterpret_cast<ConstBundleHandle const* const>(bundles), bundleCount, ids);
    }

    //! @brief Get dirty id value for a bundle.
    //!
    //! @param handle Input bundle handle to get dirty id for.
    //!
    //! @returns A valid dirty id if success, invalid dirty id if failure.
    DirtyIDType getForBundle(ConstBundleHandle handle)
    {
        DirtyIDType value = getInvalid();
        auto const result = getForBundles_abi(&handle, 1, &value);
        return result == kResultSuccess ? value : getInvalid();
    }

    //! @brief Get array of dirty id values for array of attributes.
    //!
    //! The output array for dirty id values needs to be at least size of input
    //! array of attribute handles.
    //!
    //! @param attributes       Input array attribute handles to get dirty ids for.
    //! @param attributeCount   Size of input array of attribute handles.
    //! @param ids              Output array of dirty id values for requested attributes.
    //!
    //! @returns Success if operation was successful.
    template <typename ATTRIBUTE_HANDLE>
    omni::core::Result getForAttributes(ATTRIBUTE_HANDLE* const attributes,
                                        size_t attributeCount,
                                        DirtyIDType* const ids)
    {
        using AttributeDataHandle_t = typename std::remove_cv<ATTRIBUTE_HANDLE>::type;
        static_assert(std::is_same<AttributeDataHandle_t, AttributeDataHandle>::value ||
                      std::is_same<AttributeDataHandle_t, ConstAttributeDataHandle>::value);
        return getForAttributes_abi(
            reinterpret_cast<ConstAttributeDataHandle const* const>(attributes), attributeCount, ids);
    }

    //! @brief Get dirty id value for an attribute.
    //!
    //! @param handle Input attribute handle to get dirty id for.
    //!
    //! @returns A valid dirty id if success, invalid dirty id if failure.
    DirtyIDType getForAttribute(ConstAttributeDataHandle handle)
    {
        DirtyIDType value = getInvalid();
        auto const result = getForAttributes_abi(&handle, 1, &value);
        return result == kResultSuccess ? value : getInvalid();
    }
};
