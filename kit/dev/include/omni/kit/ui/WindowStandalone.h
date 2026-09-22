// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/kit/KitTypes.h>
#include <omni/kit/ui/Common.h>
#include <omni/kit/ui/Container.h>
#include <omni/kit/ui/Menu.h>
#include <omni/ui/windowmanager/IWindowCallbackManager.h>

#include <cstdint>
#include <functional>
#include <memory>
#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

class OMNI_KIT_UI_CLASS_API WindowMainStandalone : public Container
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::WindowMainStandalone);
    WidgetType getType() override
    {
        return kType;
    }

protected:
    omni::ui::windowmanager::IWindowCallbackPtr m_uiWindow;
};

class OMNI_KIT_UI_CLASS_API WindowStandalone : public ContainerBase
{
public:
    typedef uint32_t Flags;

    static constexpr Flags kWindowFlagNone = 0;
    static constexpr Flags kWindowFlagNoTitleBar = (1 << 0);
    static constexpr Flags kWindowFlagNoResize = (1 << 1);
    static constexpr Flags kWindowFlagNoMove = (1 << 2);
    static constexpr Flags kWindowFlagNoScrollbar = (1 << 3);
    static constexpr Flags kWindowFlagNoCollapse = (1 << 4);
    static constexpr Flags kWindowFlagNoSavedSettings = (1 << 5);
    static constexpr Flags kWindowFlagShowHorizontalScrollbar = (1 << 7);
    static constexpr Flags kWindowFlagForceVerticalScrollbar = (1 << 8);
    static constexpr Flags kWindowFlagForceHorizontalScrollbar = (1 << 9);
    static constexpr Flags kWindowFlagNoClose = (1 << 10);

    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::WindowStandalone);
    WidgetType getType() override
    {
        return kType;
    }

    /**
     * Constructor.
     *
     * @param title The window title.
     * @param width The window default width.
     * @param height The window default height.
     */
    OMNI_KIT_UI_API explicit WindowStandalone(
        const char* title,
        uint32_t width = 640,
        uint32_t height = 480,
        bool open = true,
        bool addToMenu = true,
        const std::string& menuPath = "",
        bool isToggleMenu = true,
        omni::ui::windowmanager::DockPreference dockPreference = omni::ui::windowmanager::DockPreference::eLeftBottom,
        Flags flags = kWindowFlagNone);

    /**
     * Destructor.
     */
    OMNI_KIT_UI_API ~WindowStandalone();

    /**
     * Gets the title of the window.
     *
     * @return The title of the window.
     */
    OMNI_KIT_UI_API const char* getTitle() const;

    /**
     * Sets the title for the window.
     *
     * @param title The title of the window.
     */
    OMNI_KIT_UI_API void setTitle(const char* title);

    /**
     * Gets the width of the window.
     *
     * @return The width of the window.
     */
    OMNI_KIT_UI_API uint32_t getWidth() const;

    /**
     * Sets the width of the window.
     *
     * @param width The width of the window.
     */
    OMNI_KIT_UI_API void setWidth(uint32_t width);

    /**
     * Gets the height of the window.
     *
     * @return The height of the window.
     */
    OMNI_KIT_UI_API uint32_t getHeight() const;

    /**
     * Sets the height of the window.
     *
     * @param height The height of the window.
     */
    OMNI_KIT_UI_API void setHeight(uint32_t height);

    /**
     * Sets the size of the window.
     *
     * @param width The width of the window.
     * @param height The height of the window.
     */
    OMNI_KIT_UI_API void setSize(uint32_t width, uint32_t height);

    /**
     * Sets the flags for the window.
     *
     * @param fkags The flags for the window.
     */
    OMNI_KIT_UI_API void setFlags(Flags flags)
    {
        m_flags = flags;
    }

    /**
     * Gets the flags for the window
     *
     * @param flags The flags for the window.
     */
    OMNI_KIT_UI_API Flags getFlags() const
    {
        return m_flags;
    }

    /**
     * Sets the alpha value (transparency) of the window.
     *
     * @param alpha  The alpha value of the window.
     */
    OMNI_KIT_UI_API void setAlpha(float alpha);

    /**
     * Gets the layout for the window.
     *
     * @return The layout for the window.
     */
    OMNI_KIT_UI_API std::shared_ptr<Container> getLayout() const;

    /**
     * Sets the layout for the window.
     *
     * @return The layout for the window.
     */
    OMNI_KIT_UI_API void setLayout(std::shared_ptr<Container> layout);

    /**
     * Determines if the window is visible.
     *
     * @return true if the window is visible.
     */
    OMNI_KIT_UI_API bool isVisible() const;

    /**
     * Shows a window and sets it to visible.
     */
    OMNI_KIT_UI_API void show();

    /**
     * Hides a window and sets it to not visible.
     */
    OMNI_KIT_UI_API void hide();

    void draw(float elapsedTime) override;

    /**
     *
     */
    OMNI_KIT_UI_API void setUpdateFn(const std::function<void(float)>& fn);

    OMNI_KIT_UI_API void setVisibilityChangedFn(const std::function<void(bool)>& fn);

    OMNI_KIT_UI_API void setVisible(bool visible);

    carb::events::IEventStream* getEventStream() const
    {
        return m_stream.get();
    }

    std::shared_ptr<Menu> menu;

    carb::Float2 currentMousePos;
    carb::Float2 windowPos;

private:
    WindowStandalone() = default;

    carb::events::IEventStreamPtr m_stream;
    omni::kit::Window* m_handle = nullptr;
    omni::kit::SubscriptionId m_updateSubId;
    std::string m_title;
    std::string m_menuPath;
    uint32_t m_width = 0;
    uint32_t m_height = 0;
    float m_alpha = 1.0f;
    bool m_visible = false;
    std::shared_ptr<Container> m_layout = nullptr;
    std::function<void(float)> m_updateFn;
    std::function<void(bool)> m_visibilityChangedFn;
    omni::ui::windowmanager::IWindowCallbackPtr m_uiWindow;
    bool m_addToMenu;
    bool m_menuTogglable;
    bool m_autoResize = false;
    omni::ui::windowmanager::DockPreference m_dock;
    Flags m_flags;
};

}
}
}
