# Python Usage Examples

## Create OS window
```python
import carb.windowing
import omni.appwindow

# create app window from app window factory interface
app_window_factory = omni.appwindow.acquire_app_window_factory_interface()
app_window = app_window_factory.create_window_from_settings()

# config the app window
app_window.startup_with_desc(
    title="Test OS window",
    width=100,
    height=100,
    x=omni.appwindow.POSITION_CENTERED,
    y=omni.appwindow.POSITION_CENTERED,
    decorations=True,
    resize=True,
    always_on_top=False,
    scale_to_monitor=False,
    dpi_scale_override=-1.0
)

# show app window
windowing = carb.windowing.acquire_windowing_interface()
native_app_window = app_window.get_window()
windowing.show_window(native_app_window)

# shutdown app window
app_window.shutdown()
```

## Create virtual window
```python
import carb.settings
import omni.appwindow

WINDOW_ENABLED_PATH = "/app/window/enabled"

# create virtual app window from app window factory interface
settings = carb.settings.acquire_settings_interface()
is_window_enabled = settings.get(WINDOW_ENABLED_PATH)
settings.set(WINDOW_ENABLED_PATH, False)
app_window_factory = omni.appwindow.acquire_app_window_factory_interface()
app_window = app_window_factory.create_window_from_settings()

app_window.startup_with_desc(
    title="Test virtual window",
    width=100,
    height=100,
    x=omni.appwindow.POSITION_CENTERED,
    y=omni.appwindow.POSITION_CENTERED,
    decorations=True,
    resize=True,
    always_on_top=False,
    scale_to_monitor=False,
    dpi_scale_override=-1.0
)

native_app_window = app_window.get_window()

# shutdown app window and restore settings
app_window.shutdown()
settings.set(WINDOW_ENABLED_PATH, is_window_enabled)
```
