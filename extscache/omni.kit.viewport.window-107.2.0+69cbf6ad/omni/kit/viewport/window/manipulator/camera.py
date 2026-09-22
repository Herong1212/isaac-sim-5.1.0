# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['ViewportCameraManiulatorFactory']

from omni.kit.manipulator.camera import ViewportCameraManipulator
import omni.kit.app
import carb


class ViewportCameraManiulatorFactory:
    VP1_CAM_VELOCITY = '/persistent/app/viewport/camMoveVelocity'
    VP1_CAM_INERTIA_ENABLED = '/persistent/app/viewport/camInertiaEnabled'
    VP1_CAM_INERTIA_SEC = '/persistent/app/viewport/camInertiaAmount'
    VP1_CAM_ROTATIONAL_STEP = '/persistent/app/viewport/camFreeRotationStep'
    VP1_CAM_LOOK_SPEED = '/persistent/app/viewport/camYawPitchSpeed'

    VP2_FLY_ACCELERATION = '/persistent/app/viewport/manipulator/camera/flyAcceleration'
    VP2_FLY_DAMPENING = '/persistent/app/viewport/manipulator/camera/flyDampening'
    VP2_LOOK_ACCELERATION = '/persistent/app/viewport/manipulator/camera/lookAcceleration'
    VP2_LOOK_DAMPENING = '/persistent/app/viewport/manipulator/camera/lookDampening'

    def __init__(self, desc: dict, *args, **kwargs):
        self.__manipulator = ViewportCameraManipulator(desc.get('viewport_api'))

        def setting_changed(value, event_type, set_fn):
            if event_type != carb.settings.ChangeEventType.CHANGED:
                return
            set_fn(value.get('', None))

        self.__setting_subs = (
            omni.kit.app.SettingChangeSubscription(ViewportCameraManiulatorFactory.VP1_CAM_VELOCITY, lambda *args: setting_changed(*args, self.__set_flight_velocity)),
            omni.kit.app.SettingChangeSubscription(ViewportCameraManiulatorFactory.VP1_CAM_INERTIA_ENABLED, lambda *args: setting_changed(*args, self.__set_inertia_enabled)),
            omni.kit.app.SettingChangeSubscription(ViewportCameraManiulatorFactory.VP1_CAM_INERTIA_SEC, lambda *args: setting_changed(*args, self.__set_inertia_seconds)),

            omni.kit.app.SettingChangeSubscription(ViewportCameraManiulatorFactory.VP2_FLY_ACCELERATION, lambda *args: setting_changed(*args, self.__set_flight_acceleration)),
            omni.kit.app.SettingChangeSubscription(ViewportCameraManiulatorFactory.VP2_FLY_DAMPENING, lambda *args: setting_changed(*args, self.__set_flight_dampening)),
            omni.kit.app.SettingChangeSubscription(ViewportCameraManiulatorFactory.VP2_LOOK_ACCELERATION, lambda *args: setting_changed(*args, self.__set_look_acceleration)),
            omni.kit.app.SettingChangeSubscription(ViewportCameraManiulatorFactory.VP2_LOOK_DAMPENING, lambda *args: setting_changed(*args, self.__set_look_dampening))
        )
        settings = carb.settings.get_settings()
        settings.set_default(ViewportCameraManiulatorFactory.VP1_CAM_VELOCITY, 5.0)
        settings.set_default(ViewportCameraManiulatorFactory.VP1_CAM_INERTIA_ENABLED, False)
        settings.set_default(ViewportCameraManiulatorFactory.VP1_CAM_INERTIA_SEC, 0.55)

        settings.set_default(ViewportCameraManiulatorFactory.VP2_FLY_ACCELERATION, 1000.0)
        settings.set_default(ViewportCameraManiulatorFactory.VP2_FLY_DAMPENING, 10.0)
        settings.set_default(ViewportCameraManiulatorFactory.VP2_LOOK_ACCELERATION, 2000.0)
        settings.set_default(ViewportCameraManiulatorFactory.VP2_LOOK_DAMPENING, 20.0)

        self.__set_flight_velocity(settings.get(ViewportCameraManiulatorFactory.VP1_CAM_VELOCITY))
        self.__set_inertia_enabled(settings.get(ViewportCameraManiulatorFactory.VP1_CAM_INERTIA_ENABLED))
        self.__set_inertia_seconds(settings.get(ViewportCameraManiulatorFactory.VP1_CAM_INERTIA_SEC))

        self.__set_flight_acceleration(settings.get(ViewportCameraManiulatorFactory.VP2_FLY_ACCELERATION))
        self.__set_flight_dampening(settings.get(ViewportCameraManiulatorFactory.VP2_FLY_DAMPENING))
        self.__set_look_acceleration(settings.get(ViewportCameraManiulatorFactory.VP2_LOOK_ACCELERATION))
        self.__set_look_dampening(settings.get(ViewportCameraManiulatorFactory.VP2_LOOK_DAMPENING))

    def __set_inertia_enabled(self, value):
        if value is not None:
            self.__manipulator.model.set_ints('inertia_enabled', [1 if value else 0])

    def __set_inertia_seconds(self, value):
        if value is not None:
            self.__manipulator.model.set_floats('inertia_seconds', [value])

    def __set_flight_velocity(self, value):
        if value is not None:
            self.__manipulator.model.set_floats('fly_speed', [value])

    def __set_flight_acceleration(self, value):
        if value is not None:
            self.__manipulator.model.set_floats('fly_acceleration', [value, value, value])

    def __set_flight_dampening(self, value):
        if value is not None:
            self.__manipulator.model.set_floats('fly_dampening', [10, 10, 10])

    def __set_look_acceleration(self, value):
        if value is not None:
            self.__manipulator.model.set_floats('look_acceleration', [value, value, value])

    def __set_look_dampening(self, value):
        if value is not None:
            self.__manipulator.model.set_floats('look_dampening', [value, value, value])

    def __vel_changed(self, value, event_type):
        if event_type != carb.settings.ChangeEventType.CHANGED:
            return
        self.__set_flight_velocity(value.get('', None))

    def destroy(self):
        self.__setting_subs = None
        if self.__manipulator:
            self.__manipulator.destroy()
            self.__manipulator = None

    @property
    def categories(self):
        return ['manipulator']

    @property
    def name(self):
        return 'Camera'

    @property
    def visible(self):
        return self.__manipulator.visible

    @visible.setter
    def visible(self, value):
        self.__manipulator.visible = bool(value)

    @property
    def manipulator(self):
        return self.__manipulator
