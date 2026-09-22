from __future__ import annotations

import carb
import omni.usd
from omni.metropolis.utils.simulation_util import SimulationUtil
from pxr import Tf, Usd, UsdGeom
from ..utils import CameraGeneralUtil
from ..settings import CameraCalibrationSettings, GeneralSetting
from .calibration_utils import CameraRayCastUtils, CameraFovUtils


class CameraInfo:
    """simple data structure to record camera related information"""

    def __init__(self, prim_path: str):
        self.camera_name = str(prim_path).split("/")[-1]  # record camera name
        self.contours = None  # record outline vertex and holes vertex of the entire FOV
        self.calibration_dots = None  # record calibration dot lists


class CameraInfoManager:
    __instance: CameraInfoManager = None

    def __init__(self):
        if self.__instance is not None:
            raise RuntimeError("Only one instance of CameraInfoManager is allowed")

        # build a camera info dict to store all camera related information.
        self.camera_info_dict: dict[str, CameraInfo | None] = {}
        stage = self._get_context().get_stage()
        # listen to the update of camera prims in the stage.
        self._stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._notice_changed, stage)
        usd_context = self._get_context()
        self._events = usd_context.get_stage_event_stream()

        # subscribe the open and close of the stage
        self._stage_close_event_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            observer_name="isaacsim/sensors/rtx/placement/stage_close",
            event_name= str(usd_context.stage_event_name(omni.usd.StageEventType.CLOSING)),
            on_event = self._on_stage_refresh)


        self._stage_open_event_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            observer_name="isaacsim/sensors/rtx/placement/stage_open",
            event_name= str(usd_context.stage_event_name(omni.usd.StageEventType.OPENING)),
            on_event = self._on_stage_refresh)


        # push event when the camera information get updated
        CameraInfoManager.__instance = self

    def _get_context(self) -> Usd.Stage:
        # Get the UsdContext we are attached to
        return omni.usd.get_context()

    def clean_event_attributes(self):
        """clean all events related attributes"""
        self._stage_listener = None

        self._stage_close_event_sub = None
        self._stage_open_event_sub = None

        pass

    def destroy(self):
        self.clean_camera_data()
        self.clean_event_attributes()
        CameraInfoManager.__instance = None

    def __del__(self):
        self.destroy()

    @classmethod
    def get_instance(cls) -> CameraInfoManager:
        if cls.__instance is None:
            CameraInfoManager()
        return cls.__instance

    def clean_camera_data(self):
        """clean current camera data"""
        self.camera_info_dict.clear()

    def get_camera_info_dict(self) -> dict[str, CameraInfo]:
        """get current camera information dict"""
        return self.camera_info_dict

    def get_camera_info(self, camera_prim_path: str) -> CameraInfo | None:
        """get camera info if target camera prim not in the dict, return None"""
        camera_info = self.camera_info_dict.get(camera_prim_path, None)
        return camera_info

    def add_camera_item(self, camera_path):
        """store camera information such sa prim_path, raycast hit result"""
        self.camera_info_dict[str(camera_path)] = CameraInfo(camera_path)
        pass

    def _notice_changed(self, notice: Usd.Notice, stage: Usd.Stage) -> None:
        """Called by Tf.Notice.  Used when the current selected object changes in some way."""
        for p in notice.GetChangedInfoOnlyPaths():
            if str(p.GetPrimPath()) in self.camera_info_dict.keys():
                # if camera information is chanaged,remove the contour and calibration info stored in the camera item
                self.refresh_camera_info(None)

    def _on_stage_refresh(self, event):
        """Called by stage_event_stream. clean the camera information when the stage has been changed."""
        carb.log_info("Scene refreshed. Clean camera cache")
        self.refresh_camera_info(None)

    def set_camera_info(self, camera_path):
        """set camera information"""                
        # add camera data to current camera dict
        self.add_camera_item(camera_path)

    def set_camera_fov_info(self, camera_path):
        """set fov contour info for target camera"""

        recommended_calibration_seed = CameraCalibrationSettings.recommended_calibration_seed
        # get current setting values
        calibration_seed = CameraCalibrationSettings.raycast_seed
        contour_index = CameraCalibrationSettings.fov_contour_simplification_threshold
        size_threshold = CameraCalibrationSettings.fov_area_filter_threshold

        # check whether current calibration seed is less than the threshold value
        if int(calibration_seed) < int(recommended_calibration_seed):
            carb.log_warn(
                "Warning as Message :: Current calibration seed {calibration_seed} is too sparse, to draw detail calibration, adjust calibration seed to {recommended_calibration_seed}.".format(
                    calibration_seed=str(calibration_seed),
                    recommended_calibration_seed=str(recommended_calibration_seed),
                )
            )
            calibration_seed = recommended_calibration_seed
        # calculate camera's fov contour information
        contours = CameraFovUtils.get_camera_fov_contours(
            camera_path=camera_path,
            calibration_seed=calibration_seed,
            contour_index=contour_index,
            size_threshold=size_threshold,
        )
        # store camera's fov contour info to camera item
        self.camera_info_dict[str(camera_path)].contours = contours

    def refresh_camera_fov(self):
        """reset all camera's fov"""
        for camera_prim_path in self.camera_info_dict.keys():
            self.set_camera_fov_info(camera_prim_path)

    def refresh_camera_info(self, reset_camera_info: bool = False):
        """refresh all camera data stored in the camera_info_dict
        return whether camera info is refreshed successfully,
        if there is no valid camera within the stage, return false"""
        # clean all stored data
        self.clean_camera_data()
        # check whether the camera information need to be regenerate
        if reset_camera_info:
            # get activated camera prim list
            activated_camera_prim_list = CameraGeneralUtil.get_target_camera_prims_under_root()
            if not activated_camera_prim_list:
                # get current camera parent prim:
                camera_parent_path = GeneralSetting.camera_parent_prim_path
                carb.log_warn(
                    "Warning:: There is no valid camera prim under {camera_path}".format(
                        camera_path=str(camera_parent_path)
                    )
                )
                return False
            for camera_prim in activated_camera_prim_list:
                # add renewed camera data to the dict
                camera_path = camera_prim.GetPrimPath()
                self.set_camera_info(camera_path=camera_path)

        self.camera_update_subscription()

        return True

    def camera_update_subscription(self):
        """
        broadcast the camera information update event.
        """
        carb.log_info("camera info has been updated: Camera Updated Event is pushed")
        camera_info_update_event = CameraCalibrationSettings.Camera_Info_Updated_Event
        omni.kit.app.queue_event(camera_info_update_event, payload={"camera_info_updated": True})

    def get_stored_camera_list(self):
        """return the camera path list of current camera info dict"""
        return self.camera_info_dict.keys()
