// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "Widget.h"

#include <carb/eventdispatcher/EventDispatcherTypes.h>

#include <functional>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

namespace carb
{
namespace imgui
{
struct ImGui;
}
}

namespace omni
{
namespace kit
{
namespace ui
{


struct MenuItemImpl;


enum class MenuEventType : uint32_t
{
    eActivate,
};


/**
 * Menu System allows to register menu items based on path like: "File/Preferences/Foo".
 * The item can be either a toggle (2 state, with a check) or just a command.
 * Menu items in the same sub menu a sorted based on priority value. If priority differs more than 10 inbetween items -
 * separator is added.
 */
class OMNI_KIT_UI_CLASS_API Menu : public Widget
{
public:
    OMNI_KIT_UI_API Menu();

    OMNI_KIT_UI_API ~Menu() override;

    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::Menu);

    WidgetType getType() override
    {
        return kType;
    }

    /**
     * Checks if a menu item is already registered.
     *
     * @param menuPath The path to the menu (e.g. "File/Open").
     * @return true if it's existed, or false otherwise.
     */
    OMNI_KIT_UI_API bool hasItem(const char* menuPath);

    /**
     * Adds a menu item.
     *
     * @param menuPath The path to the menu (e.g. "File/Open").
     * @param onMenuItemClicked The callback function called when menu item is clicked.
     * @param toggle If the menu item is a toggle (i.e. checkable).
     * @param priority Priority of the menu. Menu with smaller priority will be placed at top. If priority differs more
     * @param toggle value (if toggle).
     * @param enabled.
     * @param draw glyph char with origin color defined in svg.
     * then 10 in between items separator is added.
     */
    OMNI_KIT_UI_API bool addItem(const char* menuPath,
                                 const std::function<void(const char* menuPath, bool value)>& onClick,
                                 bool toggle,
                                 int priority,
                                 bool value,
                                 bool enabled,
                                 bool originSvgColor = false);

    OMNI_KIT_UI_API void setOnClick(const char* menuPath,
                                    const std::function<void(const char* menuPath, bool value)>& onClick);

    OMNI_KIT_UI_API void setOnRightClick(const char* menuPath,
                                         const std::function<void(const char* menuPath, bool value)>& onClick);

    /**
     * Removes a menu item.
     *
     * @param menuPath The path of the menu item to be removed.
     */
    OMNI_KIT_UI_API void removeItem(const char* menuPath);

    OMNI_KIT_UI_API size_t getItemCount() const;

    OMNI_KIT_UI_API std::vector<std::string> getItems() const;

    /**
     * Sets the priority of a menu item.
     *
     * @param menuPath The path of the menu to set priority.
     * @param priority The priority to be set to.
     */
    OMNI_KIT_UI_API void setPriority(const char* menuPath, int priority);

    /**
     * Sets the hotkey for a menu item.
     *
     * @param menuPath The path of the menu to set hotkey to.
     * @param mod The modifier key flags for the hotkey.
     * @param key The key for the hotkey.
     */
    OMNI_KIT_UI_API void setHotkey(const char* menuPath,
                                   carb::input::KeyboardModifierFlags mod,
                                   carb::input::KeyboardInput key);

    /**
     * Sets the input action for a menu item.
     *
     * @param menuPath The path of the menu to set hotkey to.
     * @param actionName The action name.
     */
    OMNI_KIT_UI_API void setActionName(const char* menuPath, const char* actionMappingSetPath, const char* actionPath);

    /**
     * Sets the toggle value for a menu item. The menu must be a "toggle" when being created.
     *
     * @param value The toggle value of the menu item.
     */
    OMNI_KIT_UI_API void setValue(const char* menuPath, bool value);

    /**
     * Gets the toggle value for a menu item. The menu must be a "toggle" when being created.
     *
     * @return The toggle value of the menu item.
     */
    OMNI_KIT_UI_API bool getValue(const char* menuPath) const;

    /**
     * Sets the enabled state of a menu item.
     *
     * @param menuPath The path of the menu to set enabled state to.
     * @param enabled true to enabled the menu. false to disable it.
     */
    OMNI_KIT_UI_API void setEnabled(const char* menuPath, bool value);

    /**
     * For non "toggle" menu items, invoke the onClick function handler
     *
     * @param menuPath The path of the menu to activate.
     */
    OMNI_KIT_UI_API void executeOnClick(const char* menuPath);

    void draw(float elapsedTime) override;

private:
    void _update(float elapsedTime);

    std::unique_ptr<MenuItemImpl> m_root;
    std::unordered_map<std::string, MenuItemImpl*> m_pathToMenu;
    carb::eventdispatcher::ObserverGuard m_updateEvtSub;
    bool m_needUpdate = false;
    carb::input::Keyboard* m_keyboard = nullptr;
    bool m_warning_silence = false;
};

// Temporary hook up to the Editor main menu bar
OMNI_KIT_UI_API std::shared_ptr<Menu> getEditorMainMenu();

// Temporary hook to enable scripting a menu item via python
OMNI_KIT_UI_API void activateMenuItem(const char* menuPath);

}
}
}
