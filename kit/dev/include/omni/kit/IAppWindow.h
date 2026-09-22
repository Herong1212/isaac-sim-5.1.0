// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/IObject.h>
#include <carb/Interface.h>
#include <carb/events/EventsUtils.h>
#include <carb/events/IEvents.h>
#include <carb/input/IInput.h>
#include <carb/windowing/IWindowing.h>

namespace omni
{
namespace kit
{

constexpr char kWindowEnabledPath[] = "/app/window/enabled"; //!< Whether application window is enabled.
constexpr char kWindowWidthPath[] = "/app/window/width"; //!< Width of application window.
constexpr char kWindowHeightPath[] = "/app/window/height"; //!< Height of application window.
constexpr char kpWindowWidthPath[] = "/persistent/app/window/width"; //!< previous saved width of application window.
constexpr char kpWindowHeightPath[] = "/persistent/app/window/height"; //!< previous saved height of application window.
constexpr char kWindowMaximizedPath[] = "/app/window/maximized"; //!< Whether application window is maximized.
constexpr char kpWindowMaximizedPath[] = "/persistent/app/window/maximized"; //!< previous saved state of whether application window is maximized.
constexpr char kWindowXPath[] = "/app/window/x"; //!< The x coordinate of the window.
constexpr char kWindowYPath[] = "/app/window/y"; //!< The y coordinate of the window.
constexpr char kWindowTitlePath[] = "/app/window/title"; //!< Title of the application window.
constexpr char kWindowFullscreenPath[] = "/app/window/fullscreen"; //!< Whether application window is fullscreen.
constexpr char kWindowNoResizePath[] = "/app/window/noResize"; //!< Whether application window not allows resize.
constexpr char kWindowScaleToMonitorPath[] = "/app/window/scaleToMonitor"; //!< Whether application window DPI is scaled with monitor DPI.
constexpr char kWindowAlwaysOnTopPath[] = "/app/window/alwaysOnTop"; //!< Whether application window is always on top.
constexpr char kWindowNoDecorationsPath[] = "/app/window/noDecorations"; //!< Whether application window has no decorations.
constexpr char kWindowHideMouseInFullscreenPath[] = "/app/window/hideMouseInFullscreen"; //!< Whether application window hides mouse in fullscreen mode.
constexpr char kWindowDpiScaleOverridePath[] = "/app/window/dpiScaleOverride"; //!< DPI scale overrides value.
constexpr char kWindowBlockAllInputPath[] = "/app/window/blockAllInput"; //!< If application window blocks all input device.
constexpr char kWindowIconPath[] = "/app/window/iconPath"; //!< Icon path of the application window.
constexpr char kWindowChildWindowsOnTopPath[] = "/app/window/childWindowsOnTop"; //!< Whether child windows are on top.
constexpr char kWindowCursorBlinkPath[] = "/app/window/cursorBlink"; //!< If cursor blinks.

constexpr const uint64_t kPositionCentered = (uint64_t)-1;
constexpr const uint64_t kPositionUnset = (uint64_t)-2;

//! Whether window has decorations
enum class Decorations
{
    eFull, //!< window has full decorations
    eNone  //!< window has no decorations
};

//! Whether window resize is allowed
enum class Resize
{
    eAllowed, //!< window resize is allowed
    eNotAllowed //!< window resize is not allowed
};

//! Whether window is always on top
enum class Floating
{
    eRegular, //!< regular window
    eAlwaysOnTop //!< window is always on top
};

//! Whether window DPI is scaled to monitor DPI
enum class Scaling
{
    eScaleToMonitor, //!< window DPI is scaled with monitor DPI
    eNotScaled //!< window DPI is not scaled with monitor DPI
};

//! Window fullscreen state
enum class Fullscreen
{
    eWindowed, //!< window is not fullscreen
    eFullscreen, //!< window is fullscreen
};

//! Window state
enum class WindowState
{
    eNormal, //!< normal window
    eMaximized, //!< maximized window
    eMinimized, //!< minimized window
};

//! Window cursor blink
enum class CursorBlink
{
    eBlink, //!< Cursor blinks
    eNoBlink //!< Cursor doesn't blink
};

//! Window description
struct WindowDesc
{
    size_t structSize; //!< This field is needed to maintain ABI stability

    uint64_t width; //!< Window width.
    uint64_t height; //!< Window height.
    uint64_t x; //!< The x coordinate of the window.
    uint64_t y; //!< The Y coordinate of the window.
    const char* title; //!< The window title.
    Fullscreen fullscreen; //!< If window is fullscreen.
    Decorations decorations; //!< If window has full decorations.
    Resize resize; //!< If allows window resize.
    Floating floating; //!< If window is floating.
    Scaling scaling; //!< If window is scaled to monitor.
    float dpiScaleOverride; //!< DPI scale overrides value.
    CursorBlink cursorBlink; //!< If cursor (caret) blinks in input fields or not.
    WindowState windowState; //!< window state: normal, minimized or maximized.
};

/**
 * @brief Get default application window description.
 *
 * @return default application window description.
 */
inline WindowDesc getDefaultWindowDesc()
{
    WindowDesc windowDesc;
    windowDesc.structSize = sizeof(WindowDesc);
    windowDesc.width = 1440;
    windowDesc.height = 900;
    windowDesc.x = kPositionUnset;
    windowDesc.y = kPositionUnset;
    windowDesc.title = "Application Window";
    windowDesc.fullscreen = Fullscreen::eWindowed;
    windowDesc.windowState = WindowState::eNormal;
    windowDesc.decorations = Decorations::eFull;
    windowDesc.resize = Resize::eAllowed;
    windowDesc.floating = Floating::eRegular;
    windowDesc.scaling = Scaling::eScaleToMonitor;
    windowDesc.dpiScaleOverride = -1.0f;
    windowDesc.cursorBlink = CursorBlink::eBlink;
    return windowDesc;
}

const carb::events::EventType kEventTypeWindowCreated = 1; // Application window created event type
const carb::events::EventType kEventTypeWindowDestroyed = 2; // Application window destroyed event type
const carb::events::EventType kEventTypeWindowStartup = 3; // Application window startup event type
const carb::events::EventType kEventTypeWindowShutdown = 4; // Application window shutdown event type

//! Window Type
enum class WindowType
{
    eVirtual, //!< Virtual window, for headless application
    eOs, //!< OS window, for application with graphical user interface
};

//! Application window
class IAppWindow : public carb::IObject
{
public:
    /**
     * Initializes the window taking parameters from carb::settings.
     * @param name Name that identifies the window, can be nullptr.
     * @return Whether the startup operation was completed successfully.
     */
    virtual bool startup(const char* name) = 0;

    /**
     * Initializes the window with custom description.
     * @return Whether the startup operation was completed successfully.
     */
    virtual bool startupWithDesc(const char* name, const WindowDesc& desc) = 0;

    /**
     * Deinitializes the window.
     * @return Whether the shutdown operation was completed successfully.
     */
    virtual bool shutdown() = 0;

    /**
     * Call one update loop iteration on application.
     *
     * Normally, explicitly calling update is not required, as in presence of IApp interface,
     * a subscription will be created that will be this function automatically.
     *
     * @param dt Time elapsed since previous call. If <0 application ignores passed value and measures elapsed time
     * automatically.
     */
    virtual void update(float dt = -1.0f) = 0;

    /**
     * Returns the Carbonite window the editor is working with, or nullptr if headless.
     * @return Carbonite window the editor is working with, or nullptr if headless.
     */
    virtual carb::windowing::Window* getWindow() = 0;

    /**
     * @return The event stream that fires events on window resize.
     */
    virtual carb::events::IEventStream* getWindowResizeEventStream() = 0;
    /**
     * @return The event stream that fires events on window close.
     */
    virtual carb::events::IEventStream* getWindowCloseEventStream() = 0;
    /**
     * @return The event stream that fires events on window move.
     */
    virtual carb::events::IEventStream* getWindowMoveEventStream() = 0;
    /**
     * @return The event stream that fires events on window DPI scale change.
     * Content scale event stream provides DPI and "real DPI". The first one is affected by the DPI override, while
     * the second one is raw hardware DPI induced this event.
     */
    virtual carb::events::IEventStream* getWindowContentScaleEventStream() = 0;

    /**
     * @return The event stream that fires events on window drag-n-drop events.
     */
    virtual carb::events::IEventStream* getWindowDropEventStream() = 0;
    /**
     * @return The event stream that fires events on window focus change.
     */
    virtual carb::events::IEventStream* getWindowFocusEventStream() = 0;
    /**
     * @return The event stream that fires events on window minimize events.
     */
    virtual carb::events::IEventStream* getWindowMinimizeEventStream() = 0;

    /**
     * Sets fullscreen state of editor Window.
     *
     * @param fullscreen true to set Editor Window to fullscreen.
     */
    virtual void setFullscreen(bool fullscreen) = 0;

    /**
     * Gets the fullscreen state of editor Window.
     *
     * @return true if Editor is fullscreen.
     */
    virtual bool isFullscreen() = 0;

    /**
     * Resizes the window.
     *
     * @param width The width of the window.
     * @param height The height of the window.
     */
    virtual void resize(uint32_t width, uint32_t height) = 0;

    /**
     * @return window width.
     */
    virtual uint32_t getWidth() = 0;

    /**
     * @return window height.
     */
    virtual uint32_t getHeight() = 0;

    /**
     * @return window size.
     */
    virtual carb::Uint2 getSize() = 0;

    /**
     * Moves the window.
     *
     * @param x The x coordinate of the window.
     * @param y The y coordinate of the window.
     */
    virtual void move(int x, int y) = 0;

    /**
     * @return window position.
     */
    virtual carb::Int2 getPosition() = 0;

    /**
     * @return UI scale multiplier that is applied on top of the OS DPI scale.
     */
    virtual float getUiScaleMultiplier() const = 0;

    /**
     * Sets the UI scale multiplier that is applied on top of OS DPI scale.
     *
     * @param uiScaleCoeff UI scale coefficient.
     */
    virtual void setUiScaleMultiplier(float uiScaleMultiplier) = 0;

    /**
     * @return UI scale. Includes UI scale multiplier and OS DPI scale.
     */
    virtual float getUiScale() const = 0;


    /**
     * Gets current action mapping set settings path.
     *
     * @return action mapping set settings path.
     */
    virtual const char* getActionMappingSetPath() = 0;

    /**
     * Gets the keyboard associated with the window.
     *
     * @return The window keyboard.
     */
    virtual carb::input::Keyboard* getKeyboard() = 0;

    /**
     * Gets the mouse associated with the window.
     *
     * @return The window mouse.
     */
    virtual carb::input::Mouse* getMouse() = 0;

    /**
     * Gets one of the gamepads available.
     *
     * @return The window gamepad or nullptr if index is invalid.
     */
    virtual carb::input::Gamepad* getGamepad(size_t index) = 0;

    /**
     * @return Window title.
     */
    virtual const char* getTitle() = 0;

    /**
     * @return DPI scale.
     */
    virtual float getDpiScale() const = 0;

    /**
     * Sets the DPI scale override. Negative value means no override.
     *
     * @param dpiScaleOverride DPI scale overrides.
     */
    virtual void setDpiScaleOverride(float dpiScaleOverride) = 0;

    /**
     * Gets DPI scale override.
     *
     * @return DPI scale override.
     */
    virtual float getDpiScaleOverride() const = 0;

    /**
     * Sets the forced rejecting of all input events from a certain device type.
     *
     * @param deviceType The input device type, e.g. keyboard, mouse or gamepad.
     * @param shouldBlock Whether we should block the device input or not.
     */
    virtual void setInputBlockingState(carb::input::DeviceType deviceType, bool shouldBlock) = 0;

    /**
     * Gets whether the input for a certain device types is being blocked.
     *
     * @param deviceType The input device type, e.g. keyboard, mouse or gamepad.
     *
     * @return whether the input for a certain device types is being blocked.
     */
    virtual bool getInputBlockingState(carb::input::DeviceType deviceType) const = 0;

    /**
     * Sets the forced rejecting of all input events for all device types.
     *
     * @param shouldBlock Whether we should block the device input or not.
     */
    void broadcastInputBlockingState(bool shouldBlock)
    {
        for (size_t i = 0; i < (size_t)carb::input::DeviceType::eCount; ++i)
        {
            setInputBlockingState((carb::input::DeviceType)i, shouldBlock);
        }
    }

    /**
     * @brief Gets the window type: Virtual/OS window
     *
     * @return Window Type: Virtual/OS window
     */
    virtual WindowType getWindowType() const = 0;

    /**
     * @return True if cursor (caret) blinks in input fields.
     */
    virtual bool getCursorBlink() const = 0;

    /**
     * Gets the text from the clipboard associated with the window.
     *
     * @return The text in the window's clipboard.
     */
    virtual const char* getClipboard() = 0;

    /**
     * Sets the text in the clipboard associated with the window.
     *
     * @param text The text in the window's clipboard.
     */
    virtual void setClipboard(const char* text) = 0;

    /**
     * Maximize the editor window.
     */
    virtual void maximizeWindow() = 0;

    /**
     * Restore the editor window (exit maximize/minimize).
     */
    virtual void restoreWindow() = 0;

    /**
     * Gets the maxinized state of editor Window.
     *
     * @return true if Editor is maximized.
     */
    virtual bool isMaximized() = 0;

    /**
     * @brief Allows to replace the keyboard.
     *
     * @param keyboard the keyboard this AppWindow should follow.
     */
    virtual void setKeyboard(carb::input::Keyboard* keyboard) = 0;

    /**
     * Focus the window and bring to front, if applicable.
     */
    virtual void focusWindow() = 0;


};

using IAppWindowPtr = carb::ObjectPtr<IAppWindow>;


//! Application window creation factory
class IAppWindowFactory
{
public:
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::kit::IAppWindowFactory", 2, 4);

    /**
     * Create new application window.
     *
     * @return The application window carb object pointer.
     */
    IAppWindowPtr createWindowFromSettings();

    /**
     * Create new application window.
     *
     * @return application window pointer.
     */
    virtual IAppWindow* createWindowPtrFromSettings() = 0;

    /**
     * Destroy the input application window.
     *
     * @param appWindow input application window pointer.
     */
    virtual void destroyWindowPtr(IAppWindow* appWindow) = 0;

    /**
     * Get default application window.
     *
     * @return application window pointer.
     */
    virtual IAppWindow* getDefaultWindow() = 0;

    /**
     * Set default application window.
     *
     * @param{unnamed} input application window pointer.
     */
    virtual void setDefaultWindow(IAppWindow*) = 0;

    /**
     * Get the number of application windows.
     *
     * @return The number of application windows.
     */
    virtual size_t getWindowCount() = 0;

    /**
     * Get application window by index.
     * @param index window index
     */
    virtual IAppWindow* getWindowAt(size_t index) = 0;

    /**
     * Start up action mapping set.
     */
    virtual void startupActionMappingSet() = 0;

    /**
     * Shutdown action mapping set.
     */
    virtual void shutdownActionMappingSet() = 0;

    /**
     * @brief Get window action mapping set.
     *
     * @return Window action mapping set.
     */
    virtual carb::input::ActionMappingSet* getActionMappingSet() const = 0;

    /**
     * Application window startup.
     *
     * @return Whether the startup operation was completed successfully.
     */
    virtual bool startup() = 0;

    /**
     * Application window shutdown.
     *
     * @return Whether the shutdown operation was completed successfully.
     */
    virtual bool shutdown() = 0;

    /**
     * @brief Get event stream of application window creation.
     *
     * @return Event stream pointer of application window creation.
     */
    virtual carb::events::IEventStream* getWindowCreationEventStream() = 0;

    /**
     * @brief Get application window from handle.
     *
     * @param appWindowHandle Application window handle.
     *
     * @return application window pointer.
     */
    virtual IAppWindow* getAppWindowFromHandle(int64_t appWindowHandle) = 0;

    /**
     * @brief Create window according to the input window type.
     *
     * @param windowType Type of the window: virtual or OS.
     *
     * @return application window carb object pointer.
     */
    IAppWindowPtr createWindowByType(WindowType windowType);

    /**
     * @brief Create window according to the input window type.
     *
     * @param windowType Type of the window: virtual or OS.
     *
     * @return application window pointer.
     */
    virtual IAppWindow* createWindowPtrByType(WindowType windowType) = 0;
};

inline IAppWindowPtr IAppWindowFactory::createWindowFromSettings()
{
    return carb::stealObject(this->createWindowPtrFromSettings());
}

inline IAppWindowPtr IAppWindowFactory::createWindowByType(WindowType windowType)
{
    return carb::stealObject(this->createWindowPtrByType(windowType));
}

/**
 * @brief Get default application window.
 *
 * @return application window pointer, return bullptr if factory is nullptr.
 */
inline IAppWindow* getDefaultAppWindow()
{
    IAppWindowFactory* factory = carb::getCachedInterface<IAppWindowFactory>();
    return factory ? factory->getDefaultWindow() : nullptr;
}

}
}
