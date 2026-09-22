// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include <carb/ObjectUtils.h>
#include <carb/container/LocklessQueue.h>
#include <carb/eventdispatcher/IEventDispatcher.h>
#include <carb/events/IEvents.h>

#include <omni/ui/Object.h>
#include <omni/ui/scene/SceneView.h>

namespace omni
{
namespace kit
{
namespace xr
{
namespace scene_view
{
namespace core
{

enum class InputType : carb::events::EventType
{
    eScreenSpaceMovement = CARB_EVENTS_TYPE_FROM_STR("XR_INPUT_MOVE_SCREENSPACE"),
    eWorldSpaceMovement = CARB_EVENTS_TYPE_FROM_STR("XR_INPUT_MOVE_WORLDSPACE"),
    eToggleActivated = CARB_EVENTS_TYPE_FROM_STR("XR_INPUT_TOGGLE_ACTIVATE"),
    eToggleDeactivated = CARB_EVENTS_TYPE_FROM_STR("XR_INPUT_TOGGLE_DEACTIVATE"),
};

enum class InputButtonMap : uint64_t
{
    eButton0 = 0x1 << 0,
    eLeftButton = 0x1 << 0,

    eButton1 = 0x1 << 1,
    eRightButton = 0x1 << 1,

    eButton2 = 0x1 << 2,
    eMiddleButton = 0x1 << 2,

    eButton3 = 0x1 << 3,
    eBackButton = 0x1 << 3,

    eButton4 = 0x1 << 4,
    eForwardButton = 0x1 << 4,
};

//
// CLASS XRSceneView
//
class OMNIUI_SCENE_CLASS_API XRSceneView : public omni::ui::scene::SceneView
{
    OMNIUI_OBJECT(XRSceneView)

public:
    OMNIUI_SCENE_API
    XRSceneView(const std::shared_ptr<omni::ui::scene::AbstractManipulatorModel>& model = nullptr,
                const std::string& customBasePath = "");

    OMNIUI_SCENE_API
    ~XRSceneView() override;

    OMNIUI_SCENE_API
    carb::events::IEventStreamPtr getInputEventStream();

    OMNIUI_SCENE_API
    std::string getSystemUsdPath();

    OMNIUI_SCENE_API
    static std::string getBaseUsdPath();

    OMNIUI_SCENE_API
    void updateTransforms();

    OMNIUI_SCENE_API
    void runUpdate();

protected:
    OMNIUI_SCENE_API
    virtual std::unique_ptr<omni::ui::scene::AbstractDrawSystem> _createDrawSystem() const override;

    OMNIUI_SCENE_API
    virtual omni::ui::scene::MouseInput _captureInput(float width,
                                                      float height,
                                                      const omni::ui::scene::Matrix44& view,
                                                      const omni::ui::scene::Matrix44& projection) const override;

    OMNIUI_SCENE_API
    TextureOptions getTextureOptions() const override;

private:
    carb::eventdispatcher::ObserverGuard m_updateEventSub;
    carb::events::ISubscriptionPtr m_inputEventSub;
    carb::dictionary::IDictionary* m_dictionary;

    enum class MovementType
    {
        eScreenSpacePix,
        eScreenSpaceNorm,
        eWorldSpace,
    };

    struct MouseState
    {
        MovementType movementType;

        struct WorldMovementInfo
        {
            carb::Float3 origin;
            carb::Float3 direction;
        };
        union
        {
            carb::Float2 posPix;
            carb::Float2 posNorm;
            WorldMovementInfo worldPos;
        };

        uint32_t pressedMap;
        uint32_t releasedMap;
        uint32_t toggleMap;
    };
    MouseState _mouseState;

    carb::events::IEventStreamPtr m_inputEventStream;
    std::string m_id;
    std::string m_usdBasePath;

    void _handleInput(const carb::events::IEvent* evt);
    void _onPostUpdateEvent(float dt);
};

} // namespace core
} // namespace scene_view
} // namespace xr
} // namespace kit
} // namespace omni
