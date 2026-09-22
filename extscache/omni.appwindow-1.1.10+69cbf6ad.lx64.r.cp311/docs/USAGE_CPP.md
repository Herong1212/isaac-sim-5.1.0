# C++ Usage Examples

## Get default application window

```
#include <omni/kit/IAppWindow.h>

omni::kit::IAppWindowFactory* factory = carb::getCachedInterface<omni::kit::IAppWindowFactory>();

omni::kit::IAppWindow* defaultAppWindow = factory->getDefaultWindow();
size_t num_windows = factory->getWindowCount();
```

## Create application window

```
#include <omni/kit/IAppWindow.h>

omni::kit::IAppWindowFactory* factory = carb::getCachedInterface<omni::kit::IAppWindowFactory>();

constexpr char title[] = "My new application window";
uint64_t x = 0;
uint64_t y = 0;
uint64_t width = 100;
uint64_t height = 100;

omni::kit::IAppWindow* newOsWindow = appWindowFactory->createWindowPtrFromSettings();
if (newOsWindow != nullptr)
{
    // Create application window.
    omni::kit::WindowDesc windowDesc = omni::kit::getDefaultWindowDesc();

    windowDesc.width = width;
    windowDesc.height = height;
    windowDesc.title = title;
    windowDesc.decorations = omni::kit::Decorations::eNone;
    windowDesc.x = x;
    windowDesc.y = y;

    newOsWindow->startupWithDesc(title, windowDesc);
}
```

## Application window settings
```
#include <omni/kit/IAppWindow.h>

constexpr char kAutocreateAppWindowSettingsPath[] = "/exts/omni.appwindow/autocreateAppWindow";
constexpr char kWindowWidthPathp[] = "/app/window/width";
constexpr char kWindowHeightPath[] = "/app/window/height";
constexpr char kpWindowWidthPath[] = "/persistent/app/window/width";

carb::settings::ISettings* settings= carb::getCachedInterface<carb::settings::ISettings>();

# set auto create app window to be true
if (settings)
{
    settings->setDefaultBool(kAutocreateAppWindowSettingsPath, true);
}

# get information from settings about the app window
int32_t width = settings->getAsInt(kWindowWidthPath);
int32_t height = settings->getAsInt(kWindowHeightPath);
bool maximized = settings->getAsBool(kWindowMaximizedPath);
```