# Usage Examples

## Create and Use Viewport1WindowState

```python
from omni.kit.viewport.manipulator.transform import Viewport1WindowState

# Create an instance of Viewport1WindowState
viewport_state = Viewport1WindowState()

# Retrieve the picked world position from the focused window
picked_world_pos = viewport_state.get_picked_world_pos()
print("Picked World Position:", picked_world_pos)

# Retrieve the USD context name from the first focused window
usd_context_name = viewport_state.get_usd_context_name()
print("USD Context Name:", usd_context_name)

# Destroy the viewport state
viewport_state.destroy()
```
