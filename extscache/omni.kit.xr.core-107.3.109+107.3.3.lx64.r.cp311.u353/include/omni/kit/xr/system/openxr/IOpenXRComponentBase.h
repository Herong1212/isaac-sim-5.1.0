// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

// An OpenXRComponent lets extensions augment OpenXR functionality by providing some custom callbacks

#include <carb/Interface.h>
#include <carb/Types.h>

#include <omni/core/IWeakObject.h>
#include <omni/kit/xr/XRAbi.h>
#include <openxr/openxr.h>

namespace omni
{
namespace kit
{
namespace xr
{
namespace openxr
{

// declared below
OMNI_DECLARE_INTERFACE(IOpenXRComponent_v1);
OMNI_DECLARE_INTERFACE(IOpenXRComponentRegistry_v1);

using LayerPriority OMNI_ATTR("constant, prefix=kLayerPriority") = int32_t;
constexpr LayerPriority kLayerPriorityValidation = -10;
constexpr LayerPriority kLayerPriorityDefault = 0;

/**
 * @brief Info about a required layer (name and order priority)
 */

struct RequiredLayerInfo_v1
{
    omni::str::IReadOnlyCString* layerName; // name of the layer
    LayerPriority priority; // priority used to sort the layers
};

/**
 * @brief An OpenXR component
 *
 * Base functionality for extension requirements, session start/stop callbacks, init, teardown
 *
 * Initialization flow when a session is started looks like this:
 *      - check setting for the component ID to see if we try to enable
 *      - checkSupported is called with available extensions and layers. If it returns false, then we skip this
 *        component
 *      - getComponentRequiredExtensions/Layers get called by the system.  OpenXRExtension again checks if those are
 *         available and recreates the instance if it needs to
 *      - initialize is called with the instance, xrGetInstanceProcAddr, and system ID. The component can again decide
 *         to be disabled by returning false
 *      - finally, onSessionStart is called with the session and mode token
 */
class IOpenXRComponent_v1_abi
    : public omni::core::Inherits<omni::core::IWeakObject, OMNI_TYPE_ID("omni.kit.xr.openxr.IOpenXRComponent_v1")>
{
protected:
    /**
     * @brief Gets the displayable name of this component
     *
     * @throw XRException upon error
     */
    virtual XRResult getDisplayName_abi(XR_ONI_ABI_OUT_STD_STRING() outName) noexcept = 0;

    /**
     * @brief Gets the unique ID of this component.
     *
     * This ID is used to uniquely identify the component and for the name of the setting that controls whether the
     * component is enabled.
     *
     * @throw XRException upon error
     */
    virtual XRResult getOpenXRComponentId_abi(XR_ONI_ABI_OUT_STD_STRING() outId) noexcept = 0;

    /**
     * @brief Gets the list of OpenXR layers required to be enabled for this component to be used.
     *
     * @throw XRException upon error
     */
    virtual XRResult getRequiredLayers_abi(XR_ONI_ABI_OUT_STD_VECTOR(omni::kit::xr::openxr::RequiredLayerInfo_v1)
                                               layers) noexcept = 0;

    /**
     * @brief Gets the list of OpenXR extensions required to be enabled for this component to be used.
     *
     * @throw XRException upon error
     */
    virtual XRResult getRequiredExtensions_abi(XR_ONI_ABI_OUT_STD_STRING_VECTOR() extensions) noexcept = 0;

    /**
     * @brief Checks whether this component is supported with the list of currently available OpenXR layers and
     * extensions.  Returns true if the component is supported, false if not.
     *
     * @param availableLayers  string array of layers available in the current OpenXR runtime
     * @param availableExtensions  string array of extensions available in the current OpenXR runtime
     *
     * @throw XRException upon error
     */
    virtual XRResult checkSupported_abi(omni::container::IReadOnlyArray* availableLayers,
                                        omni::container::IReadOnlyArray* availableExtensions,
                                        OMNI_ATTR("out") bool& supported) noexcept = 0;

    /**
     * @brief Initializes the component with the current OpenXR instance.  Returns true if the component was
     * enabled, false if not.
     *
     * @param instance  the current OpenXR instance handle
     * @param xrGetInstanceProcAddr  the current OpenXR instance's xrGetInstanceProcAddr function (useful to load
     * required OpenXR functions)
     * @param xrSystemId  the ID of the active OpenXR system
     *
     * @throw XRException upon error
     */
    virtual XRResult initialize_abi(XrInstance instance,
                                    OMNI_ATTR("in, not_null") PFN_xrGetInstanceProcAddr xrGetInstanceProcAddr,
                                    XrSystemId xrSystemId,
                                    XrVersion openXRVersion,
                                    OMNI_ATTR("out") bool& initialized) noexcept = 0;

    /**
     * @brief Cleans up the component during session shutdown
     *
     * @param instance  the current OpenXR instance handle
     *
     * @throw XRException upon error
     */
    virtual XRResult shutdown_abi(XrInstance instance) noexcept = 0;

    /**
     * @brief Called to notify the component that a session has started.
     *
     * @param session  the OpenXR session handle for the session that just started
     *
     * @throw XRException upon error
     */
    virtual XRResult onSessionStart_abi(XrSession session, XRToken mode) noexcept = 0;

    /**
     * @brief Called to notify the component that a session is about to end
     *
     * @param session the OpenXR session handle for the session that is about to end
     *
     * @throw XRException upon error
     */
    virtual XRResult onSessionStop_abi(XrSession session) noexcept = 0;
};

/**
 * @brief A registry for tracking enabled OpenXR components
 */
class IOpenXRComponentRegistry_v1_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.kit.xr.openxr.IOpenXRComponentRegistry_v1")>
{
protected:
    /**
     * @brief Registers a component
     *
     * @param xrComponent component to be registered
     *
     * @throw XRException upon error
     */
    virtual XRResult registerOpenXRComponent_abi(OMNI_ATTR("throw_if_null")
                                                     omni::kit::xr::openxr::IOpenXRComponent_v1* xrComponent) noexcept = 0;

    /**
     * @brief Unregisters a component
     *
     * @param xrComponent component to be unregistered
     *
     * @throw XRException upon error
     */
    virtual XRResult unregisterOpenXRComponent_abi(
        OMNI_ATTR("throw_if_null") omni::kit::xr::openxr::IOpenXRComponent_v1* xrComponent) noexcept = 0;

    /**
     * @brief Gets a list of the currently registered components
     *
     * @throw XRException upon error
     */
    virtual XRResult getAvailableComponents_abi(XR_ONI_ABI_OUT_STD_VECTOR(omni::kit::xr::openxr::IOpenXRComponent_v1*)
                                                    outComponents) noexcept = 0;
};


} // namespace openxr
} // namespace xr
} // namespace kit
} // namespace omni


#ifndef OMNI_BIND
#    include "generated/omni/kit/xr/system/openxr/IOpenXRComponentBase.gen.h"
#endif

namespace omni
{
namespace kit
{
namespace xr
{
namespace openxr
{

using IOpenXRComponentPtr = omni::core::ObjectPtr<omni::kit::xr::openxr::IOpenXRComponent_v1>;
using IOpenXRComponentRegistryPtr = omni::core::ObjectPtr<omni::kit::xr::openxr::IOpenXRComponentRegistry_v1>;


// boilerplate for IOpenXRComponent objects
template <typename T>
class IOpenXRComponentBase : public T
{
protected:
    static_assert(std::is_convertible<T*, IOpenXRComponent_v1*>::value, "T must be an IOpenXRComponent");

    /// ==== Internal API base functions to (optionally) override ====

    virtual std::string getDisplayName() = 0;
    virtual std::string getOpenXRComponentId() = 0;
    virtual void getRequiredLayers(std::vector<omni::kit::xr::openxr::RequiredLayerInfo_v1>& ret)
    {
    }
    virtual void getRequiredLayers(std::vector<std::string>& ret)
    {
    }
    virtual void getRequiredExtensions(std::vector<std::string>& ret)
    {
    }
    virtual bool checkSupported(const std::vector<std::string>& availableLayers,
                                const std::vector<std::string>& availableExtensions)
    {
        std::vector<std::string> requiredExtensions;
        std::vector<std::string> requiredLayers;
        getRequiredExtensions(requiredExtensions);
        getRequiredLayers(requiredLayers);

        return vectorContainsAll(availableExtensions, requiredExtensions) &&
               vectorContainsAll(availableLayers, requiredLayers);
    }
    virtual bool initialize(XrInstance instance,
                            PFN_xrGetInstanceProcAddr xrGetInstanceProcAddr,
                            XrSystemId xrSystemId,
                            XrVersion openXRVersion)
    {
        return true;
    }
    virtual void shutdown(XrInstance instance)
    {
    }

    virtual void onSessionStart(XrSession session, XRToken mode)
    {
    }

    virtual void onSessionStop(XrSession session)
    {
    }


    /// ==== ABI overrides ====

    virtual XRResult getDisplayName_abi(XR_ONI_ABI_OUT_STD_STRING() outName) noexcept override
    {
        try
        {
            outName = omni::str::ReadOnlyCString::create(getDisplayName().c_str()).detach();
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR();
        return XRResult::eSuccess;
    }

    virtual XRResult getOpenXRComponentId_abi(XR_ONI_ABI_OUT_STD_STRING() outId) noexcept override
    {
        try
        {
            outId = omni::str::ReadOnlyCString::create(getOpenXRComponentId().c_str()).detach();
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR();
        return XRResult::eSuccess;
    }

    virtual XRResult getRequiredLayers_abi(XR_ONI_ABI_OUT_STD_VECTOR(omni::kit::xr::openxr::RequiredLayerInfo_v1)
                                               layers) noexcept override
    {
        try
        {
            std::vector<omni::kit::xr::openxr::RequiredLayerInfo_v1> ret;
            getRequiredLayers(ret);
            layers =
                omni::container::ReadOnlyTypedArray<omni::kit::xr::openxr::RequiredLayerInfo_v1>::create(ret).detach();
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR();
        return XRResult::eSuccess;
    }

    virtual XRResult getRequiredExtensions_abi(XR_ONI_ABI_OUT_STD_STRING_VECTOR() extensions) noexcept override
    {
        try
        {
            std::vector<std::string> ret;
            getRequiredExtensions(ret);
            extensions = omni::container::ReadOnlyStringArray::create(ret).detach();
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR();
        return XRResult::eSuccess;
    }

    virtual XRResult checkSupported_abi(omni::container::IReadOnlyArray* availableLayers,
                                        omni::container::IReadOnlyArray* availableExtensions,
                                        OMNI_ATTR("out") bool& supported) noexcept override
    {
        try
        {
            std::vector<std::string> stl_availableLayers = omni::container::convertReadOnlyStringArray(availableLayers);
            std::vector<std::string> stl_availableExtensions =
                omni::container::convertReadOnlyStringArray(availableExtensions);
            supported = checkSupported(stl_availableLayers, stl_availableExtensions);
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR();
        return XRResult::eSuccess;
    }

    virtual XRResult initialize_abi(XrInstance instance,
                                    OMNI_ATTR("in, not_null") PFN_xrGetInstanceProcAddr xrGetInstanceProcAddr,
                                    XrSystemId xrSystemId,
                                    XrVersion openXRVersion,
                                    OMNI_ATTR("out") bool& initialized) noexcept override
    {
        try
        {
            m_instance = instance;
            m_xrGetInstanceProcAddr = xrGetInstanceProcAddr;
            initialized = initialize(instance, xrGetInstanceProcAddr, xrSystemId, openXRVersion);
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR_WITH_HOOK_ON_ERROR(m_instance = nullptr;
                                                                    m_xrGetInstanceProcAddr = nullptr;);
        return XRResult::eSuccess;
    }

    virtual XRResult shutdown_abi(XrInstance instance) noexcept override
    {
        try
        {
            shutdown(instance);
            m_instance = nullptr;
            m_xrGetInstanceProcAddr = nullptr;
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR_WITH_HOOK_ON_ERROR(m_instance = nullptr;
                                                                    m_xrGetInstanceProcAddr = nullptr;)
        return XRResult::eSuccess;
    }

    virtual XRResult onSessionStart_abi(XrSession session, XRToken mode) noexcept override
    {
        try
        {
            onSessionStart(session, mode);
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR()
        return XRResult::eSuccess;
    }

    virtual XRResult onSessionStop_abi(XrSession session) noexcept override
    {
        try
        {
            onSessionStop(session);
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR()
        return XRResult::eSuccess;
    }

    /// ==== Helper functions ====

    bool vectorContainsAll(const std::vector<std::string>& fullList, const std::vector<std::string>& requiredItems)
    {
        return std::all_of(requiredItems.begin(), requiredItems.end(),
                           [fullList](const std::string& item)
                           { return std::find(fullList.begin(), fullList.end(), item) != fullList.end(); });
    }

    /// ==== Base member variables ====

    std::string m_componentName;
    std::string m_componentId;
    XrInstance m_instance;
    PFN_xrGetInstanceProcAddr m_xrGetInstanceProcAddr;
};

}
}
}
}
