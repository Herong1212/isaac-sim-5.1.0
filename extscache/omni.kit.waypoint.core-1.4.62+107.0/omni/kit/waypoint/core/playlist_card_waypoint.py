from pathlib import Path
from typing import Optional

import carb
from omni.kit.playlist.core import PlaylistCard
from pxr import Usd

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("icons")


class WaypointCard(PlaylistCard):
    PLAYLIST_CARD_TYPE_WAYPOINT = "waypoint"
    WAYPOINT_EXTENSION_INSTANCE = None

    # Waypoint playlist card
    def __init__(self, type: str, path: str, name: str = None):
        super().__init__(type, path, name=name)

        self._waypoint = WaypointCard.WAYPOINT_EXTENSION_INSTANCE.get_waypoint_from_prim_path(self.path)
        self.name = self._waypoint.name if self._waypoint else "(Unknown Waypoint)"
        self.path = self._waypoint.path if self._waypoint else self.path

    @classmethod
    def accept(cls, camera_path: str) -> bool:
        return WaypointCard.WAYPOINT_EXTENSION_INSTANCE.is_waypoint_prim(camera_path)

    @property
    def menu_text(self) -> str:
        return "Waypoints"

    @property
    def camera_prim(self):
        if self._waypoint is None:
            return None
        else:
            return self._waypoint.camera_prim

    @property
    def icon(self):
        return f"{ICON_PATH}/Waypoint_Light.svg"

    def active(self, without_camera=False):
        waypoint = WaypointCard.WAYPOINT_EXTENSION_INSTANCE.get_waypoint(self.name)
        if waypoint:
            # Use recall_waypoint instead of waypoint.recall to set active waypoint
            # When playing, first recall without camera, next recall to set camera
            # Here use force=True to make sure second recall work
            WaypointCard.WAYPOINT_EXTENSION_INSTANCE.recall_waypoint(
                waypoint, without_camera=without_camera, force=True, recall_timeline=False
            )
        else:
            carb.log_error(f'[Playlist] Invalid waypoint "{self.name}". It may be renamed or deleted.')

    def clean(self, without_camera=False):
        self.active(without_camera=without_camera)
