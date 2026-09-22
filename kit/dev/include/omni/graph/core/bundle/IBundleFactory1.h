// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/IBundle.h>

namespace omni
{
namespace graph
{
namespace core
{

OMNI_DECLARE_INTERFACE(IBundleFactory);

//! Interface to create new bundles
class IBundleFactory_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.graph.core.IBundleFactory")>
{
protected:
    //! Create bundles at given paths and acquire instances of IBundle2 interface.
    //!
    //! @param contextObj The context where bundles are created.
    //! @param paths Locations for new bundles.
    //! @param pathCount Length of paths array.
    //! @param createdBundles Output instances of IBundle2 interface.
    //!
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //! invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result createBundles_abi(GraphContextObj const* const contextObj OMNI_ATTR("in, not_null"),
                                                 fabric::PathC const* const paths OMNI_ATTR("in, not_null"),
                                                 size_t pathCount,
                                                 IBundle2** const createdBundles
                                                     OMNI_ATTR("out, *not_null, count=pathCount")) noexcept = 0;

    //! Acquire instances of IConstBundle2 interface from const bundle handles.
    //!
    //! @param contextObj The context where bundles belong to.
    //! @param bundleHandles The bundle handles.
    //! @param bundleCount Length of bundleHandles array.
    //! @param bundles Output instances of IConstBundle2 interface.
    //!
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //! invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getConstBundles_abi(
        GraphContextObj const* const contextObj OMNI_ATTR("in, not_null"),
        ConstBundleHandle const* const bundleHandles OMNI_ATTR("in, not_null"),
        size_t bundleCount,
        IConstBundle2** const bundles OMNI_ATTR("out, *not_null, count=bundleCount")) noexcept = 0;

    //! Acquire instances of IBundle2 interface from bundle handles.
    //!
    //! @param contextObj The context where bundles belong to.
    //! @param bundleHandles The bundle handles.
    //! @param bundleCount Length of bundleHandles array.
    //! @param bundles Output instances of IConstBundle2 interface.
    //!
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //! invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getBundles_abi(
        GraphContextObj const* const contextObj OMNI_ATTR("in, not_null"),
        BundleHandle const* const bundleHandles OMNI_ATTR("in, not_null"),
        size_t bundleCount,
        IBundle2** const bundles OMNI_ATTR("out, *not_null, count=bundleCount")) noexcept = 0;
};
} // namespace core
} // namespace graph
} // namespace omni

#include "IBundleFactory1.gen.h"

//! @cond Doxygen_Suppress
//!
//! API part of the bundle factory interface
OMNI_DEFINE_INTERFACE_API(omni::graph::core::IBundleFactory)
//! @endcond
{
public:
    //! @brief Create a list of Bundle objects.
    //! Creates new bundle instances at specified paths within the given context.
    //!
    //! @param contextObj The graph context where the bundles will be created.
    //! @param paths Array of paths specifying locations for new bundles.
    //! @param pathCount Number of elements in the paths array.
    //! @param createdBundles Output array of smart pointers managing IBundle2 instances.
    //!
    //! @return true if all bundles were successfully created, false if any creation failed or if arguments were invalid.
    bool createBundles(
        omni::graph::core::GraphContextObj const& contextObj,
        omni::fabric::PathC const* const paths,
        size_t pathCount,
        omni::core::ObjectPtr<omni::graph::core::IBundle2>* const createdBundles) noexcept;
    
    //! @brief Create a single bundle at the given path and acquire an IBundle2 interface instance.
    //! This function is a convenience wrapper for creating individual bundles.
    //!
    //! @param contextObj The graph context where the bundle will be created.
    //! @param path Location for the new bundle.
    //!
    //! @return Smart pointer managing the lifetime of the IBundle2 instance.
    omni::core::ObjectPtr<omni::graph::core::IBundle2> createBundle(
        omni::graph::core::GraphContextObj const& contextObj,
        omni::fabric::PathC path) noexcept;
    
    //! @brief Acquire IConstBundle2 interface instances from constant bundle handles.
    //! This function retrieves read-only bundle interfaces from the provided handles.
    //!
    //! @param contextObj The graph context to which the bundles belong.
    //! @param bundleHandles Array of constant bundle handles.
    //! @param bundleCount Number of elements in the bundleHandles array.
    //! @param bundles Output array of smart pointers managing IConstBundle2 instances.
    //!
    //! @return true if interfaces were successfully acquired for all bundles, false otherwise.
    template <typename BUNDLE_HANDLE>
    bool getConstBundles(
        omni::graph::core::GraphContextObj const& contextObj,
        BUNDLE_HANDLE const* const bundleHandles,
        size_t bundleCount,
        omni::core::ObjectPtr<omni::graph::core::IConstBundle2>* const bundles) noexcept;
    
    //! @brief Acquire a single IConstBundle2 interface instance from a constant bundle handle.
    //! This function retrieves a read-only interface for a specific bundle.
    //!
    //! @param contextObj The graph context to which the bundle belongs.
    //! @param bundleHandle The immutable bundle handle.
    //!
    //! @return Smart pointer managing the lifetime of the IConstBundle2 instance.
    omni::core::ObjectPtr<omni::graph::core::IConstBundle2> getConstBundle(
        omni::graph::core::GraphContextObj const& contextObj,
        omni::graph::core::ConstBundleHandle const& bundleHandle) noexcept;
    
    //! @brief Acquire IBundle2 interface instances from bundle handles.
    //! This overloaded function retrieves writable bundle interfaces for the provided handles.
    //!
    //! @param contextObj The graph context to which the bundles belong.
    //! @param bundleHandles Array of bundle handles.
    //! @param bundleCount Number of elements in the bundleHandles array.
    //! @param bundles Output array of smart pointers managing IBundle2 instances.
    //!
    //! @return true if interfaces were successfully acquired for all bundles, false otherwise.
    bool getBundles(
        omni::graph::core::GraphContextObj const& contextObj,
        omni::graph::core::BundleHandle const* const bundleHandles,
        size_t bundleCount,
        omni::core::ObjectPtr<omni::graph::core::IBundle2>* const bundles) noexcept;
    
    //! @brief Acquire IConstBundle2 interface instances from constant bundle handles.
    //! This overloaded function retrieves read-only interfaces for constant bundles.
    //!
    //! @param contextObj The graph context to which the bundles belong.
    //! @param bundleHandles Array of constant bundle handles.
    //! @param bundleCount Number of elements in the bundleHandles array.
    //! @param bundles Output array of smart pointers managing IConstBundle2 instances.
    //!
    //! @return true if interfaces were successfully acquired for all bundles, false otherwise.
    bool getBundles(
        omni::graph::core::GraphContextObj const& contextObj,
        omni::graph::core::ConstBundleHandle const* const bundleHandles,
        size_t bundleCount,
        omni::core::ObjectPtr<omni::graph::core::IConstBundle2>* const bundles) noexcept;

    //! @brief Acquire a single IBundle2 interface instance from a bundle handle.
    //! This function retrieves a writable interface for a specific bundle.
    //!
    //! @param contextObj The graph context to which the bundle belongs.
    //! @param bundleHandle The bundle handle.
    //!
    //! @return Smart pointer managing the lifetime of the IBundle2 instance.
    omni::core::ObjectPtr<omni::graph::core::IBundle2> getBundle(
        omni::graph::core::GraphContextObj const& contextObj,
        omni::graph::core::BundleHandle const& bundleHandle) noexcept;
    
    //! @brief Acquire a single IConstBundle2 interface instance from a constant bundle handle.
    //! This function retrieves a read-only interface for a specific immutable bundle.
    //!
    //! @param contextObj The graph context to which the bundle belongs.
    //! @param bundleHandle The immutable bundle handle.
    //!
    //! @return Smart pointer managing the lifetime of the IConstBundle2 instance.
    omni::core::ObjectPtr<omni::graph::core::IConstBundle2> getBundle(
        omni::graph::core::GraphContextObj const& contextObj,
        omni::graph::core::ConstBundleHandle const& bundleHandle) noexcept;
};

//
// inline implementation
//

inline bool omni::graph::core::IBundleFactory::createBundles(
    omni::graph::core::GraphContextObj const& contextObj,
    omni::fabric::PathC const* const paths,
    size_t pathCount,
    omni::core::ObjectPtr<omni::graph::core::IBundle2>* const createdBundles) noexcept
{
    static_assert(sizeof(omni::core::ObjectPtr<omni::graph::core::IBundle2>) == sizeof(omni::graph::core::IBundle2*),
                  "ObjectPtr and IBundle2 pointer requires to be the same size!");

    auto result = createBundles_abi(
        &contextObj, paths, pathCount, reinterpret_cast<omni::graph::core::IBundle2**>(createdBundles));
    if (OMNI_FAILED(result))
    {
        OMNI_LOG_ERROR("unable to create bundles: 0x%08X", result);
        return false;
    }
    return true;
}


inline omni::core::ObjectPtr<omni::graph::core::IBundle2> omni::graph::core::IBundleFactory::createBundle(
    omni::graph::core::GraphContextObj const& contextObj,
omni::fabric::PathC path) noexcept
{
    omni::core::ObjectPtr<omni::graph::core::IBundle2> out;
    createBundles(contextObj, &path, 1, &out);
    return out;
}

template <typename BUNDLE_HANDLE>
bool omni::graph::core::IBundleFactory::getConstBundles(
    omni::graph::core::GraphContextObj const& contextObj,
    BUNDLE_HANDLE const* const bundleHandles,
    size_t bundleCount,
    omni::core::ObjectPtr<omni::graph::core::IConstBundle2>* const bundles) noexcept
{
    using namespace omni::graph::core;

    static_assert(sizeof(omni::core::ObjectPtr<IConstBundle2>) == sizeof(IConstBundle2*),
                  "ObjectPtr and IBundle2 pointer requires to be the same size!");

    auto result =
        getConstBundles_abi(&contextObj, bundleHandles, bundleCount, reinterpret_cast<IConstBundle2**>(bundles));
    if (OMNI_FAILED(result))
    {
        OMNI_LOG_ERROR("unable to get bundles: 0x%08X", result);
        return false;
    }
    return true;
}

inline omni::core::ObjectPtr<omni::graph::core::IConstBundle2> omni::graph::core::IBundleFactory::getConstBundle(
    omni::graph::core::GraphContextObj const& contextObj,
    omni::graph::core::ConstBundleHandle const& bundleHandle) noexcept
{
    omni::core::ObjectPtr<omni::graph::core::IConstBundle2> out;
    getConstBundles(contextObj, &bundleHandle, 1, &out);
    return out;
}

inline bool omni::graph::core::IBundleFactory::getBundles(
    graph::core::GraphContextObj const& contextObj,
    graph::core::BundleHandle const* const bundleHandles,
    size_t bundleCount,
    omni::core::ObjectPtr<graph::core::IBundle2>* const bundles) noexcept
{
    static_assert(sizeof(omni::core::ObjectPtr<omni::graph::core::IBundle2>) == sizeof(omni::graph::core::IBundle2*),
                  "ObjectPtr and IBundle2 pointer requires to be the same size!");

    auto result = getBundles_abi(
        &contextObj, bundleHandles, bundleCount, reinterpret_cast<omni::graph::core::IBundle2**>(bundles));
    if (OMNI_FAILED(result))
    {
        OMNI_LOG_ERROR("unable to get bundles: 0x%08X", result);
        return false;
    }
    return true;
}

inline bool omni::graph::core::IBundleFactory::getBundles(
    omni::graph::core::GraphContextObj const& contextObj,
    omni::graph::core::ConstBundleHandle const* const bundleHandles,
    size_t bundleCount,
    omni::core::ObjectPtr<omni::graph::core::IConstBundle2>* const bundles) noexcept
{
    static_assert(sizeof(ObjectPtr<omni::graph::core::IConstBundle2>) == sizeof(omni::graph::core::IConstBundle2*),
                  "ObjectPtr and IConstBundle2 pointer requires to be the same size!");

    auto result = getConstBundles_abi(
        &contextObj, bundleHandles, bundleCount, reinterpret_cast<omni::graph::core::IConstBundle2**>(bundles));
    if (OMNI_FAILED(result))
    {
        OMNI_LOG_ERROR("unable to get bundles: 0x%08X", result);
        return false;
    }
    return true;
}

inline omni::core::ObjectPtr<omni::graph::core::IBundle2> omni::graph::core::IBundleFactory::getBundle(
    omni::graph::core::GraphContextObj const& contextObj,
    omni::graph::core::BundleHandle const& bundleHandle) noexcept
{
    omni::core::ObjectPtr<omni::graph::core::IBundle2> out;
    getBundles(contextObj, &bundleHandle, 1, &out);
    return out;
}

inline omni::core::ObjectPtr<omni::graph::core::IConstBundle2> omni::graph::core::IBundleFactory::getBundle(
    omni::graph::core::GraphContextObj const& contextObj,
    omni::graph::core::ConstBundleHandle const& bundleHandle) noexcept
{
    ObjectPtr<omni::graph::core::IConstBundle2> out;
    getConstBundles(contextObj, &bundleHandle, 1, &out);
    return out;
}
