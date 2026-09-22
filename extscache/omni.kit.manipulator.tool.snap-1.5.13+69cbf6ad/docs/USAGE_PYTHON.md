```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Snap Object To Grid

```python
import asyncio
import carb.settings
from omni.kit.manipulator.tool.snap import SnapProviderManager, GRID_SNAP_NAME
from omni.kit.manipulator.tool.snap import settings_constants as c
from omni.kit.viewport.utility import get_active_viewport
from pxr import Gf

# Create and await an async method to perform snapping logic
async def snap_object_to_grid():
    # Get the active viewport API for snapping
    viewport_api = get_active_viewport()

    # Create an instance of SnapProviderManager with the viewport API
    snap_manager = SnapProviderManager(viewport_api=viewport_api)

    # set the snap provider name to GRID_SNAP_NAME
    settings = carb.settings.get_settings()
    settings.set(c.SNAP_PROVIDER_NAME_SETTING_PATH, GRID_SNAP_NAME)

    # Define a callback function to handle the snap results
    def on_snap_result(position, keep_spacing):
        print(f"Snapped position: {position}, Keep spacing: {keep_spacing}")

    # Start snap operation
    snap_manager.on_began(excluded_paths=[])

    # Perform snapping to grid at the center of the viewport (NDC coordinates (0, 0))
    snap_manager.get_snap_pos(
        xform=Gf.Matrix4d(1.0),  # Identity matrix for the object's current transform
        ndc_location=(0, 0, 0),  # NDC location at the center of the viewport
        scene_view=None,         # Scene view is not needed in this context
        on_snapped=on_snap_result # The callback function to handle snap results
    )

    # End snap operation
    snap_manager.on_ended()

# Run the async method
asyncio.ensure_future(snap_object_to_grid())
```

## Implement a custom snap provider, Register and Unregister the snap provider

```python
from typing import List, Sequence, Union, Callable
from omni.kit.manipulator.tool.snap import SnapProvider
from omni.kit.manipulator.tool.snap.registry import SnapProviderRegistry
import omni.kit.mesh.raycast
import omni.timeline
from pxr import Gf, Sdf, Usd

class MyPrimSnap(SnapProvider):
    """implement a customized prim snap provider that allows snapping objects to the closest primitive based on provided NDC position."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._raycast = omni.kit.mesh.raycast.acquire_mesh_raycast_interface()
        self._raycast_context = self._raycast.create_context()
        self._timeline = omni.timeline.get_timeline_interface()

    def destroy(self):
        if self._raycast_context:
            self._raycast.destroy_context(self._raycast_context)
            self._raycast_context = None

    def on_began(self, excluded_paths: List[Union[str, Sdf.Path]], **kwargs):
        """Initializes the snap operation with a list of paths to exclude from snapping."""
        self._excluded_paths = excluded_paths
        self._prev_refresh_rate = self._raycast.get_bvh_refresh_rate()

        self._raycast.set_bvh_refresh_rate(omni.kit.mesh.raycast.BvhRefreshRate.FAST, True)
        self._raycast.set_disallowed_mesh_paths(
            [str(path) for path in self._excluded_paths], True, self._raycast_context
        )

    def on_ended(self, **kwargs):
        """Resets the state of the provider when the snap operation ends."""
        self._excluded_paths = []
        self._raycast.set_disallowed_mesh_paths([], True, self._raycast_context)
        self._raycast.set_bvh_refresh_rate(self._prev_refresh_rate, True)

    def _get_current_timecode(self) -> Usd.TimeCode:
        return Usd.TimeCode(self._timeline.get_current_time() * self._timeline.get_time_codes_per_seconds())

    def on_snap(
        self,
        xform: Gf.Matrix4d,
        ndc_location: Sequence[float],
        want_orient: bool,
        want_keep_spacing: bool,
        on_snapped: Callable,
        *args,
        **kwargs,
    ) -> bool:
        """Attempts to snap to the closest prim"""
        # generate picking ray from ndc cursor location.
        (origin, dir, dist) = self._generate_picking_ray(ndc_location)
        # find the closest prim
        result = self._raycast.closestRaycast(origin, dir, dist, self._raycast_context)
        if result.meshIndex >= 0:
            path = self._raycast.get_mesh_path_from_index(result.meshIndex)
            if path:
                payload = {}
                payload["keep_spacing"] = want_keep_spacing
                payload["path"] = path
                transform = self._viewport_api.usd_context.compute_path_world_transform(path)
                payload["position"] = (transform[12], transform[13], transform[14])
                if want_orient:
                    rotation = Gf.Matrix3d(
                        transform[0],
                        transform[1],
                        transform[2],
                        transform[4],
                        transform[5],
                        transform[6],
                        transform[8],
                        transform[9],
                        transform[10],
                    )
                    rotation.Orthonormalize()
                    payload["orient"] = rotation.ExtractRotation()
                on_snapped(**payload)
                return True

        return False

    @staticmethod
    def get_name() -> str:
        """Returns the unique name of this snap provider."""
        return "My Prim (Mesh Based)"

    @classmethod
    def get_display_name(cls) -> str:
        """Returns the display name of this snap provider."""
        return "My Prim"

    @staticmethod
    def can_orient() -> bool:
        """Indicates if this snap provider can orient objects."""
        return True

# Get the singleton instance of SnapProviderRegistry
registry = SnapProviderRegistry.get_instance()

# Register a new MyPrimSnap provider
registry.register_provider(MyPrimSnap)

# Unregister the MyPrimSnap provider
registry.unregister_provider(MyPrimSnap)

```