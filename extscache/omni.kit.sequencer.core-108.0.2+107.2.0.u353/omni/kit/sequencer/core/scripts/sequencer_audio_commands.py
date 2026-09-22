import asyncio

import carb
import carb.events
import omni.kit.commands
import omni.kit.notification_manager as nm
import omni.timeline
import omni.usd.audio

from .progress_popup import ProgressPopup


class SequencerUIStreamAudioCommand(omni.kit.commands.Command):
    """Command to record stage audio to file."""

    def __init__(self, audio_path: str):
        """
        Args:
            audio_path (str): Audio path to write.
        """
        super().__init__()
        self._audio_streamer = None
        self._timeline_interface = omni.timeline.get_timeline_interface()
        self._audio_interface = omni.usd.audio.get_stage_audio_interface()
        self._sub = None
        self._is_playing = False
        self._is_recording = False
        self._audio_path = audio_path

    def do(self):
        if not self._audio_path.endswith(".wav"):
            self._audio_path += ".wav"

        self._audio_streamer = self._audio_interface.create_capture_streamer()

        def on_cancel():
            asyncio.ensure_future(self._on_stream_audio_click_cancel())

        self._progress_popup = ProgressPopup(f"Streaming audio to {self._audio_path}", cancel_button_fn=on_cancel)

        success = self._audio_interface.start_capture(self._audio_streamer, str(self._audio_path))
        self._was_looping = self._timeline_interface.is_looping()
        self._was_time = self._timeline_interface.get_current_time()
        self._timeline_interface.set_looping(False)
        self._timeline_interface.set_current_time(self._timeline_interface.get_start_time())
        if success is True:
            # Start playing the level.
            self._progress_popup.show()
            self._progress_popup.progress = 0
            self._is_recording = True
            stream = self._timeline_interface.get_timeline_event_stream()
            self._sub = stream.create_subscription_to_pop(self._on_timeline_event)
            if not self._timeline_interface.is_playing():
                self._timeline_interface.play()
        else:
            nm.post_notification(
                "Audio stream capture failed! Check log for more info.", status=nm.NotificationStatus.WARNING
            )
        return self._audio_streamer

    @property
    def recording(self):
        return self._is_recording

    def _on_timeline_event(self, event: carb.events.IEvent):
        if event.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
            start = self._timeline_interface.get_start_time()
            end = self._timeline_interface.get_end_time()
            now = self._timeline_interface.get_current_time()
            length = end - start
            if length <= 0:
                return
            percent = (now - start) / length
            if self._progress_popup is not None:
                self._progress_popup.progress = percent
        if event.type == int(omni.timeline.TimelineEventType.PAUSE) or event.type == int(
            omni.timeline.TimelineEventType.STOP
        ):
            self._on_capture_finished()
            return

    def _on_capture_finished(self):
        success = self.stop_audio_capture()
        if success:
            nm.post_notification(f"Audio stream saved:\n{self._audio_path}.", status=nm.NotificationStatus.INFO)
            carb.log_info(f"Audio stream saved: {self._audio_path}.")
        else:
            nm.post_notification("Audio stream not saved.", status=nm.NotificationStatus.INFO)

    async def _on_stream_audio_click_cancel(self):
        nm.post_notification("Audio stream cancelled.", status=nm.NotificationStatus.INFO)
        self.stop_audio_capture()

    def stop_audio_capture(self):
        success = False
        if self._audio_streamer:
            success = self._audio_interface.stop_capture(self._audio_streamer)
            self._audio_streamer = None
            self._progress_popup.hide()
            self._progress_popup = None
        self._is_recording = False
        self._sub = None
        self._timeline_interface.set_looping(self._was_looping)
        self._timeline_interface.set_current_time(self._was_time)
        return success
