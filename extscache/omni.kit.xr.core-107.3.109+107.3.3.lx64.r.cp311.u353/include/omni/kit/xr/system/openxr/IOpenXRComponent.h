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

#include <omni/kit/xr/XRAbi.h>
#include <omni/kit/xr/system/openxr/IOpenXRComponentBase.h>
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
OMNI_DECLARE_INTERFACE(IOpenXRComponent_EventHandler_v1);
OMNI_DECLARE_INTERFACE(IOpenXRComponent_UpdateTracking_v1);
OMNI_DECLARE_INTERFACE(IOpenXRComponent_UpdateTracking_v2);
OMNI_DECLARE_INTERFACE(IOpenXRComponent_CompositionLayerModifier_v1);
OMNI_DECLARE_INTERFACE(IOpenXRComponent_PreEndFrame_v1);
OMNI_DECLARE_INTERFACE(IOpenXRComponent_UsdStage_v1);

/**
 * @brief Optional additional interface to allow an IOpenXRComponent to handle OpenXR events
 *
 * This interface can be optionally implemented by a component to receive callbacks from the event handling loop
 * to let the component handle OpenXR events.
 */
class IOpenXRComponent_EventHandler_v1_abi
    : public omni::core::Inherits<omni::kit::xr::openxr::IOpenXRComponent_v1,
                                  OMNI_TYPE_ID("omni.kit.xr.openxr.IOpenXRComponent_EventHandler_v1")>
{
protected:
    /**
     * @brief Called from the event loop to let the component handle any OpenXR events
     *
     * @param event the current event to be handled
     * @param consumed the component can set this to true to consume the event and prevent it from being handled by
     * anything else after
     *
     * @throw XRException upon error
     */
    virtual XRResult handleEvent_abi(OMNI_ATTR("in") const XrEventDataBuffer* event,
                                     OMNI_ATTR("out") bool& consumed) noexcept = 0;
};

/**
 * @brief Tracking data needed for some interfaces' update functions
 */
struct UpdateTrackingFrameData_v1
{
    /** @brief the OpenXR frame time for the current frame */
    XrTime frameTime;
    /** @brief the amount of scene units for each meter */
    double metersPerUnit;
    /** @brief which axis points up */
    XRUpAxis upAxis;
    /** @brief the current physical world to world anchor transform */
    OMNI_ATTR("no_py") double physicalWorldToWorldAnchor[16];
    /** @brief the current world anchor to virtual world transform */
    OMNI_ATTR("no_py") double worldAnchorToVirtualWorld[16];
};

struct UpdateTrackingFrameData_v2
{
    /** @brief the OpenXR frame time for the current frame */
    XrTime frameTime;
    /** @brief the amount of scene units for each meter */
    double metersPerUnit;
    /** @brief which axis points up */
    XRUpAxis upAxis;
    /** @brief the current physical world to world anchor transform */
    OMNI_ATTR("no_py") double physicalWorldToWorldAnchor[16];
    /** @brief the current world anchor to virtual world transform */
    OMNI_ATTR("no_py") double worldAnchorToVirtualWorld[16];
    /** @brief the current stage space */
    XrSpace stageSpace;
};


/**
 * @brief Optional additional interface to allow an IOpenXRComponent to update custom tracking objects (ie, for hand or
 * marker tracking) during the frame update
 *
 * This interface can be optionally implemented by a component to receive callbacks from the frame tracking update loop
 * to let the component update tracking of objects.
 */
class IOpenXRComponent_UpdateTracking_v1_abi
    : public omni::core::Inherits<omni::kit::xr::openxr::IOpenXRComponent_v1,
                                  OMNI_TYPE_ID("omni.kit.xr.openxr.IOpenXRComponent_UpdateTracking_v1")>
{
protected:
    /**
     * @brief Called from the frame tracking update loop to let the component update custom tracking objects
     *
     * @param frameData tracking data for the current frame
     *
     * @throw XRException upon error
     */
    virtual XRResult updateTracking_abi(const UpdateTrackingFrameData_v1& frameData) noexcept = 0;
};

/**
 * @brief Optional additional interface to allow an IOpenXRComponent to update custom tracking objects (ie, for hand or
 * marker tracking) during the frame update
 *
 * This interface can be optionally implemented by a component to receive callbacks from the frame tracking update loop
 * to let the component update tracking of objects.
 */
class IOpenXRComponent_UpdateTracking_v2_abi
    : public omni::core::Inherits<omni::kit::xr::openxr::IOpenXRComponent_v1,
                                  OMNI_TYPE_ID("omni.kit.xr.openxr.IOpenXRComponent_UpdateTracking_v2")>
{
protected:
    /**
     * @brief Called from the frame tracking update loop to let the component update custom tracking objects
     *
     * @param frameData tracking data for the current frame
     *
     * @throw XRException upon error
     */
    virtual XRResult updateTracking_abi(const UpdateTrackingFrameData_v2& frameData) noexcept = 0;
};


/**
 * @brief Optional additional interface to allow an IOpenXRComponent to update the composition layer stack before
 * ending the frame
 *
 * This interface can be optionally implemented by a component to receive a callback before the OpenXR xrEndFrame
 * function is called, allowing the component to modify the composition layer stack.  This is useful for components
 * that need to add additional layers into the stack for the extensions they use.
 */
class IOpenXRComponent_CompositionLayerModifier_v1_abi
    : public omni::core::Inherits<omni::kit::xr::openxr::IOpenXRComponent_v1,
                                  OMNI_TYPE_ID("omni.kit.xr.openxr.IOpenXRComponent_CompositionLayerModifier_v1")>
{
protected:
    /**
     * @brief Called just before xrEndFrame to let the component modify the composition layer stack
     *
     * @param inLayers the current layer stack
     * @param inLayersCount the number of layers in inLayers
     * @param outLayers the modified layer stack
     *
     * @throw XRException upon error
     *
     * TODO - this will be modified shortly
     */
    virtual XRResult modifyCompositionLayers_abi(OMNI_ATTR("in, *in, count=inLayersCount")
                                                     XrCompositionLayerBaseHeader** inLayers,
                                                 size_t inLayersCount,
                                                 XR_ONI_ABI_OUT_STD_VECTOR(XrCompositionLayerBaseHeader*)
                                                     outLayers) noexcept = 0;
};

/**
 * @brief Optional additional interface to allow an IOpenXRComponent to modify the XrFrameEndInfo about to be passed to
 * xrEndFrame
 *
 * This interface can be optionally implemented by a component to receive a callback before the OpenXR xrEndFrame
 * function is called, allowing the component to modify the XrFrameEndInfo struct that will be passed to xrEndFrame.
 * This is useful for components that may need to attach additional data to this struct for the extensions they use.
 */
class IOpenXRComponent_PreEndFrame_v1_abi
    : public omni::core::Inherits<omni::kit::xr::openxr::IOpenXRComponent_v1,
                                  OMNI_TYPE_ID("omni.kit.xr.openxr.IOpenXRComponent_PreEndFrame_v1")>
{
protected:
    /**
     * @brief Called just before xrEndFrame to let the component modify the XrFrameEndInfo struct
     *
     * @param endFrameInfo pointer to the XrFrameEndInfo about to be passed to xrEndFrame
     *
     * @throw XRException upon error
     */
    virtual XRResult preEndFrame_abi(OMNI_ATTR("in") XrFrameEndInfo* endFrameInfo) noexcept = 0;
};


/**
 * @brief Optional additional interface to allow an IOpenXRComponent to leverage newly activated USD stage
 *
 * This interface can be optionally implemented by a component to receive new USD Stage ID when new stage was opened.
 */
class IOpenXRComponent_UsdStage_v1_abi
    : public omni::core::Inherits<omni::kit::xr::openxr::IOpenXRComponent_v1,
                                  OMNI_TYPE_ID("omni.kit.xr.openxr.IOpenXRComponent_UsdStage_v1")>
{
protected:
    /**
     * @brief Called when new USD stage is active
     *
     * @param usdStageId id of current USD Stage
     *
     * @throw XRException upon error
     */
    virtual XRResult updateActiveUsdStageId_abi(uint64_t usdStageId) noexcept = 0;
};


} // namespace openxr
} // namespace xr
} // namespace kit
} // namespace omni


#ifndef OMNI_BIND
#    include "generated/omni/kit/xr/system/openxr/IOpenXRComponent.gen.h"
#endif

namespace omni
{
namespace kit
{
namespace xr
{
namespace openxr
{

using IOpenXRComponent_EventHandlerPtr = omni::core::ObjectPtr<omni::kit::xr::openxr::IOpenXRComponent_EventHandler_v1>;
using IOpenXRComponent_CompositionLayerModifierPtr =
    omni::core::ObjectPtr<omni::kit::xr::openxr::IOpenXRComponent_CompositionLayerModifier_v1>;
using IOpenXRComponent_UpdateTrackingPtr =
    omni::core::ObjectPtr<omni::kit::xr::openxr::IOpenXRComponent_UpdateTracking_v1>;
using IOpenXRComponent_UsdStagePtr = omni::core::ObjectPtr<omni::kit::xr::openxr::IOpenXRComponent_UsdStage_v1>;
using IOpenXRComponent_PreEndFramePtr = omni::core::ObjectPtr<omni::kit::xr::openxr::IOpenXRComponent_PreEndFrame_v1>;


class OpenXRComponentBase : public IOpenXRComponentBase<IOpenXRComponent_v1>
{
};

class OpenXRComponentBase_EventHandler : public IOpenXRComponentBase<IOpenXRComponent_EventHandler_v1>
{
protected:
    virtual XRResult handleEvent_abi(OMNI_ATTR("in") const XrEventDataBuffer* event,
                                     OMNI_ATTR("out") bool& consumed) noexcept override
    {
        try
        {
            consumed = handleEvent(event);
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR();

        return XRResult::eSuccess;
    }

    virtual bool handleEvent(const XrEventDataBuffer* event) = 0;
};

class OpenXRComponentBase_UpdateTracking : public IOpenXRComponentBase<IOpenXRComponent_UpdateTracking_v2>
{
protected:
    virtual XRResult updateTracking_abi(const UpdateTrackingFrameData_v2& frameData) noexcept override
    {
        try
        {
            updateTracking(frameData);
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR();

        return XRResult::eSuccess;
    }

    virtual void updateTracking(const UpdateTrackingFrameData_v2& frameData) = 0;
};

class OpenXRComponentBase_CompositionLayerModifier
    : public IOpenXRComponentBase<IOpenXRComponent_CompositionLayerModifier_v1>
{
protected:
    virtual XRResult modifyCompositionLayers_abi(OMNI_ATTR("in, *in, count=inLayersCount")
                                                     XrCompositionLayerBaseHeader** inLayers,
                                                 size_t inLayersCount,
                                                 XR_ONI_ABI_OUT_STD_VECTOR(XrCompositionLayerBaseHeader*)
                                                     outLayers) noexcept override
    {
        try
        {
            std::vector<XrCompositionLayerBaseHeader*> layers;

            for (size_t i = 0; i < inLayersCount; i++)
            {
                layers.push_back(inLayers[i]);
            }

            modifyCompositionLayers(layers);

            outLayers = omni::container::ReadOnlyTypedArray<XrCompositionLayerBaseHeader*>::create(layers).detach();
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR();

        return XRResult::eSuccess;
    }

    virtual void modifyCompositionLayers(std::vector<XrCompositionLayerBaseHeader*>& layers) = 0;
};

class OpenXRComponentBase_PreEndFrame : public IOpenXRComponentBase<IOpenXRComponent_PreEndFrame_v1>
{
protected:
    virtual XRResult preEndFrame_abi(OMNI_ATTR("in") XrFrameEndInfo* endFrameInfo) noexcept override
    {
        try
        {
            preEndFrame(endFrameInfo);
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR();

        return XRResult::eSuccess;
    }

    virtual void preEndFrame(XrFrameEndInfo* endFrameInfo) = 0;
};

class OpenXRComponentBase_UsdStage : public IOpenXRComponentBase<IOpenXRComponent_UsdStage_v1>
{
protected:
    virtual XRResult updateActiveUsdStageId_abi(uint64_t usdStageId) noexcept override
    {
        try
        {
            updateActiveUsdStageId(usdStageId);
        }
        CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR();

        return XRResult::eSuccess;
    }

    virtual void updateActiveUsdStageId(uint64_t usdStageId) = 0;
};

}
}
}
}
