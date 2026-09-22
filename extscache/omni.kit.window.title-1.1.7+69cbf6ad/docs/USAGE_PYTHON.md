# Usage Examples

## Get the Current Window Title

```python
import omni.kit.window.title

# Get the window title instance
window_title = omni.kit.window.title.get_main_window_title()

# Get the current title as a string
current_title = window_title.get_full_title()
print(f"Current window title: {current_title}")
```
---

## Customize the Window Title Components

```python
import omni.kit.window.title

# Get the window title instance
window_title = omni.kit.window.title.get_main_window_title()

# Set application name (first part of the title)
window_title.set_app_name("My Custom App")

# Set application version (second part of the title)
window_title.set_app_version("2.0")

# Set the title text (third part of the title)
window_title.set_title("Custom Project")

# Set additional decorative text (at the end of the title)
window_title.set_title_decor("- Debug Mode")

# Get the updated full title
updated_title = window_title.get_full_title()
print(f"Updated window title: {updated_title}")
```
---

## Set Title Based on Stage URL

```python
import omni.kit.window.title

# Get the window title instance
window_title = omni.kit.window.title.get_main_window_title()

# Set the title using the current stage URL
# This will include read-only status if applicable
window_title.set_title_url()

# Get the updated title
updated_title = window_title.get_full_title()
print(f"Title with stage URL: {updated_title}")
```
---

## Reset to Default Title Values

```python
import omni.kit.window.title
import carb.settings
import carb.tokens

# Get the window title instance
window_title = omni.kit.window.title.get_main_window_title()

# Get default values from settings and tokens
settings = carb.settings.get_settings()
tokens = carb.tokens.get_tokens_interface()

default_app_name = settings.get("/app/window/title")
default_app_version = tokens.resolve("${app_version}")

# Reset the title components to defaults
window_title.set_app_name(default_app_name)
window_title.set_app_version(default_app_version)
window_title.set_title("")
window_title.set_title_decor("")

# Get the reset title
reset_title = window_title.get_full_title()
print(f"Reset window title: {reset_title}")
```
