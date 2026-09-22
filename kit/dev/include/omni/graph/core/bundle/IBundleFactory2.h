// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IBundleFactory1.h"

namespace omni
{
namespace graph
{
namespace core
{

OMNI_DECLARE_INTERFACE(IBundleFactory2);

//! IBundleFactory version 2.
//!
//! The version 2 allows to retrieve instances of IBundle instances from paths.
class IBundleFactory2_abi
    : public omni::core::Inherits<omni::graph::core::IBundleFactory, OMNI_TYPE_ID("omni.graph.core.IBundleFactory2")>
{
protected:
    //! Get read only IBundle interface from path.
    //!
    //! @param contextObj The context where bundles belong to.
    //! @param paths Input paths.
    //! @param pathCount Length of paths array.
    //! @param bundles Output instances of IConstBundle2 interface.
    //!
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //! invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getConstBundlesFromPaths_abi(
        GraphContextObj const* const contextObj OMNI_ATTR("in, not_null"),
        omni::fabric::PathC const* const paths OMNI_ATTR("in, not_null"),
        size_t pathCount,
        IConstBundle2** const bundles OMNI_ATTR("out, *not_null, count=pathCount")) noexcept = 0;

    //! Get read write IBundle interface from path.
    //!
    //! @param contextObj The context where bundles belong to.
    //! @param paths Input paths.
    //! @param pathCount Length of paths array.
    //! @param bundles Output instances of IBundle2 interface.
    //!
    //! @return Success if executed successfully, Fail for unsuccessful execution, InvalidArgument if arguments are
    //! invalid.
    OMNI_ATTR("no_py")
    virtual omni::core::Result getBundlesFromPaths_abi(
        GraphContextObj const* const contextObj OMNI_ATTR("in, not_null"),
        omni::fabric::PathC const* const paths OMNI_ATTR("in, not_null"),
        size_t pathCount,
        IBundle2** const bundles OMNI_ATTR("out, *not_null, count=pathCount")) noexcept = 0;
};

}
}
}

#include "IBundleFactory2.gen.h"

//! @cond Doxygen_Suppress
//!
//! API part of the bundle factory interface
OMNI_DEFINE_INTERFACE_API(omni::graph::core::IBundleFactory2)
//! @endcond
{
public:
    //! Get read only IBundle interface from path.
    //!
    //! @param contextObj The context where bundles belong to.
    //! @param path Input path.
    //!
    //! @return Instance of IConstBundle interface.
    omni::core::ObjectPtr<omni::graph::core::IConstBundle2> getConstBundleFromPath(
        omni::graph::core::GraphContextObj const& contextObj, omni::fabric::PathC path) noexcept
    {
        omni::core::ObjectPtr<omni::graph::core::IConstBundle2> out;
        auto const outPtr = reinterpret_cast<omni::graph::core::IConstBundle2**>(&out);
        auto const result = getConstBundlesFromPaths_abi(&contextObj, &path, 1, outPtr);
        if (OMNI_FAILED(result))
        {
            OMNI_LOG_ERROR("unable to get bundle at path: 0x%08X", result);
        }
        return out;
    }

    //! Get read write IBundle interface from path.
    //!
    //! @param contextObj The context where bundles belong to.
    //! @param path Input path.
    //!
    //! @return Instance of IBundle interface.
    omni::core::ObjectPtr<omni::graph::core::IBundle2> getBundleFromPath(
        omni::graph::core::GraphContextObj const& contextObj, omni::fabric::PathC path) noexcept
    {
        omni::core::ObjectPtr<omni::graph::core::IBundle2> out;
        auto const outPtr = reinterpret_cast<omni::graph::core::IBundle2**>(&out);
        auto const result = getBundlesFromPaths_abi(&contextObj, &path, 1, outPtr);
        if (OMNI_FAILED(result))
        {
            OMNI_LOG_ERROR("unable to get bundle at path: 0x%08X", result);
        }
        return out;
    }

    //! Get read only IConstBundle2 interfaces from an array of paths.
    //!
    //! @param contextObj The context where bundles belong to.
    //! @param paths Input paths.
    //! @param pathCount Length of paths array.
    //! @param createdBundles Smart pointers that manage lifetime of IConstBundle2 instances.
    //!
    //! @return false on failure, true on success.
    bool getConstBundlesFromPaths(
        omni::graph::core::GraphContextObj const& contextObj,
        omni::fabric::PathC const* const paths,
        size_t const pathCount,
        omni::core::ObjectPtr<omni::graph::core::IConstBundle2>* createdBundles) noexcept
    {
        static_assert(sizeof(ObjectPtr<omni::graph::core::IConstBundle2>) == sizeof(omni::graph::core::IConstBundle2*),
                      "ObjectPtr and IConstBundle2 pointer requires to be the same size!");

        auto const result = getConstBundlesFromPaths_abi(&contextObj, paths, pathCount, reinterpret_cast<omni::graph::core::IConstBundle2**>(createdBundles));
        if (OMNI_FAILED(result))
        {
            OMNI_LOG_ERROR("unable to get const bundles from path: 0x%08X", result);
            return false;
        }
        return true;
    }

};
