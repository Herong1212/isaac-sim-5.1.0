from typing import Optional

import omni.usd
from pxr import Sdf, Usd

SESSION_CAMERAS = {
    "/OmniverseKit_Persp": "Perspective",
    "/OmniverseKit_Top": "Top",
    "/OmniverseKit_Front": "Front",
    "/OmniverseKit_Right": "Right",
}


def get_camera_display(path: Sdf.Path, stage: Optional[Usd.Stage] = None):
    name = SESSION_CAMERAS.get(path.pathString, None)
    if name:
        return name

    if stage:
        camera_prim = stage.GetPrimAtPath(path)
        if camera_prim:
            display_name = omni.usd.editor.get_display_name(camera_prim)
            if display_name:
                return display_name

    return path.name
