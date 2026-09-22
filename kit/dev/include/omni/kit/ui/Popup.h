// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Api.h"

#include <omni/kit/KitTypes.h>
#include <omni/ui/windowmanager/IWindowCallbackManager.h>

#include <functional>
#include <memory>
#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

class Container;

/**
 * Defines a popup.
 */
class OMNI_KIT_UI_CLASS_API Popup
{
public:
    /**
     * Constructor
     */
    OMNI_KIT_UI_API explicit Popup(
        const std::string& title, bool modal = false, float width = 0, float height = 0, bool autoResize = false);

    /**
     * Destructor.
     */
    OMNI_KIT_UI_API ~Popup();

    OMNI_KIT_UI_API void show();

    OMNI_KIT_UI_API void hide();

    OMNI_KIT_UI_API bool isVisible() const;

    OMNI_KIT_UI_API void setVisible(bool visible);

    OMNI_KIT_UI_API const char* getTitle() const;

    OMNI_KIT_UI_API void setTitle(const char* title);

    OMNI_KIT_UI_API carb::Float2 getPos() const;

    OMNI_KIT_UI_API void setPos(const carb::Float2& pos);

    OMNI_KIT_UI_API float getWidth() const;

    OMNI_KIT_UI_API void setWidth(float width);

    OMNI_KIT_UI_API float getHeight() const;

    OMNI_KIT_UI_API void setHeight(float height);

    OMNI_KIT_UI_API std::shared_ptr<Container> getLayout() const;

    OMNI_KIT_UI_API void setLayout(std::shared_ptr<Container> layout);

    OMNI_KIT_UI_API void setUpdateFn(const std::function<void(float)>& fn);

    OMNI_KIT_UI_API void setCloseFn(const std::function<void()>& fn);

private:
    void _draw(float dt);

    std::string m_popupId;
    bool m_modal;
    bool m_autoResize;
    std::string m_title;
    float m_width;
    float m_height;
    carb::Float2 m_pos;
    std::shared_ptr<Container> m_layout;
    omni::ui::windowmanager::IWindowCallbackPtr m_handle;
    omni::kit::SubscriptionId m_updateSubId;
    bool m_visible = false;
    bool m_pendingVisiblityUpdate = false;
    bool m_pendingPositionUpdate = false;
    std::function<void(float)> m_updateFn;
    std::function<void()> m_closeFn;
};

}
}
}
