from typing import Any, Callable, Dict, List, Optional

import carb
import carb.tokens
import omni.usd
from omni.kit.viewport.utility import get_active_viewport
from pxr import Usd, UsdGeom

from .constant import PLAYLISTS_ROOT

DEFAULT_VIEWS = {
    "OmniverseKit_Persp": "Perspective",
    # "OmniverseKit_Top": "Top",
    # "OmniverseKit_Front": "Front",
    # "OmniverseKit_Right": "Right",
}


class PlaylistCard:
    CAMERA = "camera"
    PLAYLIST = "playlist"
    WAYPOINT = "waypoint"

    # Registered card
    __g_registered: Dict[str, Any] = {}

    @staticmethod
    def register(type: str, cls) -> bool:
        """
        Registery a new type of playlist card.
        Args:
            type (str): Type name.
            cls: Class for new Type
        """
        if type in PlaylistCard.__g_registered:
            return False

        PlaylistCard.__g_registered[type] = cls
        carb.log_info(f"[Playlist] registered playlist card: {type} {cls}")
        return True

    @staticmethod
    def deregister(type: str):
        """
        Deregister a type of playlist card.
        Args:
            type (str): Type name
        """
        PlaylistCard.__g_registered.pop(type, None)
        carb.log_info(f"[Playlist] deregistered playlist card: {type}")

    @classmethod
    def accept(camera_path: str) -> bool:
        """
        Check if camera path belongs to the playlist card.
        Args:
            camera_path (str): Path to camera.
        Returns True if it belongs to the playlist card Otherwise False.
        """
        return False  # pragma: no cover

    @staticmethod
    def create(
        type: Optional[str] = None,
        camera_prim: Optional[Usd.Prim] = None,
        name: Optional[str] = None,
        path: Optional[str] = None,
    ):
        if camera_prim:
            path = camera_prim.GetPath().pathString
            if name is None:
                name = camera_prim.GetName()

        if path is None:
            carb.log_error(f"[playlist] No camera path defined!")
            return None

        if type is None:
            for t, cls in PlaylistCard.__g_registered.items():
                if cls.accept(path):
                    type = t
                    break
            else:
                if camera_prim:
                    if camera_prim.IsA(UsdGeom.Camera):
                        type = PlaylistCard.CAMERA
                elif path:
                    type = PlaylistCard.CAMERA

        if type in PlaylistCard.__g_registered:
            return PlaylistCard.__g_registered[type](type, name=name, path=path)
        elif type == PlaylistCard.CAMERA:
            return CameraCard(type, name=name, path=path)
        else:
            carb.log_info(f"[playlist] Unknown playlist card type: {type} from {path}")
            return None

    def __init__(self, type: str, path: str, name: Optional[str] = None):
        self.type = type
        self.path = path
        self.name = name if name else "Unknown"

    @property
    def camera_prim(self) -> Optional[Usd.Prim]:
        stage = omni.usd.get_context().get_stage()
        if stage:
            return stage.GetPrimAtPath(self.path)
        else:
            return None

    @property
    def menu_text(self) -> str:
        """
        Menu text to group the playlist card
        """
        return ""  # pragma: no cover

    @property
    def icon(self) -> str:
        return ""  # pragma: no cover

    # In animation mode, active card without active camera
    def active(self, without_camera=False):
        pass  # pragma: no cover

    def clean(self, without_camera=False):
        pass  # pragma: no cover


class CameraCard(PlaylistCard):
    def __init__(self, type: str, path: str, name=None):
        super().__init__(type, path, name=name)

        if self.name in DEFAULT_VIEWS:
            self.name = DEFAULT_VIEWS[self.name]

    @property
    def icon(self) -> str:
        return carb.tokens.get_tokens_interface().resolve("${omni.kit.playlist.core}/icons/Camera.png")

    @property
    def menu_text(self) -> str:
        return "Cameras"

    def active(self, without_camera=False):
        if not without_camera:
            viewport_api = get_active_viewport()
            viewport_api.camera_path = self.path


def enum_playlist_cards() -> List[PlaylistCard]:
    HIDDEN_CAMERAS = ["OmniverseKit_Top", "OmniverseKit_Front", "OmniverseKit_Right"]
    stage = omni.usd.get_context().get_stage()
    if stage is None:
        return []

    cards = []
    for prim in Usd.PrimRange(stage.GetPseudoRoot()):
        if prim.IsA(UsdGeom.Camera):
            path = prim.GetPath().pathString
            if path.startswith(PLAYLISTS_ROOT):
                continue
            else:
                card = PlaylistCard.create(camera_prim=prim)
                if card and card.name not in HIDDEN_CAMERAS:
                    cards.append(card)

    return cards
