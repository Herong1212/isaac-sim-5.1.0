import carb
import carb.settings
import omni.ext
import omni.kit.livestream.bind


class Extension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        self._qos_status_callback_id = None
        pass

    def qos_status_callback(self, qos_status): # pragma: no cover
        carb.log_info(f"Livestreaming Quality of Service (qos) Status:")
        carb.log_info(f"   stream_index: {qos_status.stream_index}")
        carb.log_info(f"   qos_bitrate: {qos_status.qos_bitrate}")
        carb.log_info(f"   fec_percent: {qos_status.fec_percent}")
        carb.log_info(f"   recommended_mode:")
        carb.log_info(f"       width: {qos_status.recommended_mode.width}")
        carb.log_info(f"       height: {qos_status.recommended_mode.height}")
        carb.log_info(f"       actual_streaming_fps: {qos_status.recommended_mode.actual_streaming_fps}")
        carb.log_info(
            f"       sync_captured_and_streaming_fps: {qos_status.recommended_mode.sync_captured_and_streaming_fps}"
        )
        carb.log_info(f"   target_streaming_fps: {qos_status.target_streaming_fps}")
        carb.log_info(f"   pixel_alignment: {qos_status.pixel_alignment}")
        carb.log_info(f"   reference_aspect_ratio: {qos_status.reference_aspect_ratio}")
        carb.log_info(f"   preferred_width: {qos_status.preferred_width}")
        carb.log_info(f"   preferred_height: {qos_status.preferred_height}")
        carb.log_info(f"   preferred_height: {qos_status.preferred_height}")
        carb.log_info(f"   average_rtd_ms: {qos_status.average_rtd_ms}")
        carb.log_info(f"   encode_width: {qos_status.encode_width}")
        carb.log_info(f"   encode_height: {qos_status.encode_height}")

    def on_startup(self):
        self._kit_livestream = omni.kit.livestream.bind.acquire_livestream_interface()
        self._kit_livestream.startup()

        LOG_QOS_STATUS_SETTING = "/app/livestream/webrtc/logQosStatus"
        settings = carb.settings.get_settings()
        settings.set_default(LOG_QOS_STATUS_SETTING, False)
        log_qos_status = settings.get_as_bool(LOG_QOS_STATUS_SETTING)
        if log_qos_status:
            self._qos_status_callback_id = self._kit_livestream.register_qos_status_callback(self.qos_status_callback)
        else:
            self._qos_status_callback_id = None

    def on_shutdown(self):
        if self._qos_status_callback_id != None:
            self._kit_livestream.deregister_qos_status_callback(self._qos_status_callback_id)
            self._qos_status_callback_id = None
        self._kit_livestream.shutdown()
        self._kit_livestream = None
