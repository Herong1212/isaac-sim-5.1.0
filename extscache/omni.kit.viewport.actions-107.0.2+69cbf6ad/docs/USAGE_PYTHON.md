```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Switch to Perspective Camera

```python
import omni.kit.actions.core
action_registry = omni.kit.actions.core.get_action_registry()
action = action_registry.get_action("omni.kit.viewport.actions", "perspective_camera")
action.execute()
```

## Toggle Camera Visibility

```python
import omni.kit.actions.core
action_registry = omni.kit.actions.core.get_action_registry()
action = action_registry.get_action("omni.kit.viewport.actions", "toggle_camera_visibility")
action.execute()
```

## Set Viewport Resolution to HD 1080P

```python
import omni.kit.actions.core
action_registry = omni.kit.actions.core.get_action_registry()
action = action_registry.get_action("omni.kit.viewport.actions", "set_viewport_resolution")
action.execute((1920, 1080))
```

## Toggle RTX render-mode between Realtime and Pathtracing

```python
import omni.kit.actions.core
action_registry = omni.kit.actions.core.get_action_registry()
action = action_registry.get_action("omni.kit.viewport.actions", "toggle_rtx_rendermode")
action.execute()
```

## Toggle HUD Memory Visibility

```python
import omni.kit.actions.core
action_registry = omni.kit.actions.core.get_action_registry()
action = action_registry.get_action("omni.kit.viewport.actions", "toggle_hud_memory_visibility")
action.execute()
```