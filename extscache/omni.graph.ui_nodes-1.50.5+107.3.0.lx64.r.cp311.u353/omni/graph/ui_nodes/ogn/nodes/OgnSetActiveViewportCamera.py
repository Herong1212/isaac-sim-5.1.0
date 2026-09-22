"""
This is the implementation of the OGN node defined in OgnSetActiveViewportCamera.ogn
"""

import omni.graph.core as og
from omni.kit.viewport.utility import get_viewport_from_window_name
from pxr import Sdf, UsdGeom


class OgnSetActiveViewportCamera:
    """
    Sets a viewport's actively bound camera to a free camera
    """

    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current input"""
        db.outputs.execOut = og.ExecutionAttributeState.DISABLED
        try:
            new_camera_path = db.inputs.primPath
            if not Sdf.Path.IsValidPathString(new_camera_path):
                return True

            viewport_name = db.inputs.viewport
            viewport_api = get_viewport_from_window_name(viewport_name)
            if not viewport_api:
                return True

            stage = viewport_api.stage
            new_camera_prim = stage.GetPrimAtPath(new_camera_path) if stage else False
            if not new_camera_prim:
                return True
            if not new_camera_prim.IsA(UsdGeom.Camera):
                return True

            new_camera_path = Sdf.Path(new_camera_path)
            if viewport_api.camera_path != new_camera_path:
                viewport_api.camera_path = new_camera_path

        except Exception as error:  # pylint: disable=broad-except
            db.log_error(str(error))
            return False

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
