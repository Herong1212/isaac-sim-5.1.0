"""
This is the implementation of the OGN node defined in OgnGetActiveViewportCamera.ogn
"""

from omni.kit.viewport.utility import get_viewport_window_camera_string


class OgnGetActiveViewportCamera:
    """
    Gets a viewport's actively bound camera
    """

    @staticmethod
    def compute(db) -> bool:
        """Compute the outputs from the current input"""
        try:
            viewport_name = db.inputs.viewport
            active_camera = get_viewport_window_camera_string(viewport_name)
            db.outputs.camera = active_camera
            db.outputs.cameraPrim = [active_camera]

        except Exception as error:  # pylint: disable=broad-except
            db.log_error(str(error))
            return False
        return True
