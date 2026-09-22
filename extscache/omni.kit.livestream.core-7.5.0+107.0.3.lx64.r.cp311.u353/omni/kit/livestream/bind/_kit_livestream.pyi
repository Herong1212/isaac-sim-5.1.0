from __future__ import annotations
import omni.kit.livestream.bind._kit_livestream
import typing

__all__ = [
    "AudioSampleFormat",
    "AudioSamplesDesc",
    "ILivestream",
    "NvstQosStatus",
    "NvstStreamingMode",
    "acquire_livestream_interface"
]


class AudioSampleFormat():
    """
    Members:

      SIGNED_FLOAT

      UNSIGNED_FLOAT

      SIGNED_INT_16

      UNSIGNED_INT_16
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    SIGNED_FLOAT: omni.kit.livestream.bind._kit_livestream.AudioSampleFormat # value = <AudioSampleFormat.SIGNED_FLOAT: 0>
    SIGNED_INT_16: omni.kit.livestream.bind._kit_livestream.AudioSampleFormat # value = <AudioSampleFormat.SIGNED_INT_16: 2>
    UNSIGNED_FLOAT: omni.kit.livestream.bind._kit_livestream.AudioSampleFormat # value = <AudioSampleFormat.UNSIGNED_FLOAT: 1>
    UNSIGNED_INT_16: omni.kit.livestream.bind._kit_livestream.AudioSampleFormat # value = <AudioSampleFormat.UNSIGNED_INT_16: 3>
    __members__: dict # value = {'SIGNED_FLOAT': <AudioSampleFormat.SIGNED_FLOAT: 0>, 'UNSIGNED_FLOAT': <AudioSampleFormat.UNSIGNED_FLOAT: 1>, 'SIGNED_INT_16': <AudioSampleFormat.SIGNED_INT_16: 2>, 'UNSIGNED_INT_16': <AudioSampleFormat.UNSIGNED_INT_16: 3>}
    pass
class AudioSamplesDesc():
    def __init__(self) -> None: ...
    @property
    def channel_count(self) -> int:
        """
        :type: int
        """
    @channel_count.setter
    def channel_count(self, arg0: int) -> None:
        pass
    @property
    def channel_mask(self) -> int:
        """
        :type: int
        """
    @channel_mask.setter
    def channel_mask(self, arg0: int) -> None:
        pass
    @property
    def sample_format(self) -> AudioSampleFormat:
        """
        :type: AudioSampleFormat
        """
    @sample_format.setter
    def sample_format(self, arg0: AudioSampleFormat) -> None:
        pass
    @property
    def sampling_rate(self) -> int:
        """
        :type: int
        """
    @sampling_rate.setter
    def sampling_rate(self, arg0: int) -> None:
        pass
    pass
class ILivestream():
    def deregister_qos_status_callback(self, arg0: int) -> bool: ...
    def enable_livestream(self, arg0: bool) -> bool: ...
    def register_qos_status_callback(self, arg0: typing.Callable[[NvstQosStatus], None]) -> int: ...
    def send_audio_samples(self, arg0: numpy.ndarray, arg1: int, arg2: int, arg3: AudioSamplesDesc) -> None: ...
    @staticmethod
    def set_stun_credentials(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def set_stun_credentials_with_shared_port(*args, **kwargs) -> typing.Any: ...
    def shutdown(self) -> bool: ...
    def startup(self) -> bool: ...
    pass
class NvstQosStatus():
    @property
    def average_rtd_ms(self) -> int:
        """
                     Average round trip delay in ms

                     Return:
                         int: Average round trip delay in ms.
                     

        :type: int
        """
    @property
    def encode_height(self) -> int:
        """
                     The encode resolution height the frame provider should use for future frames.

                     Return:
                         int: The encode resolution height the frame provider should use for future frames.
                     

        :type: int
        """
    @property
    def encode_width(self) -> int:
        """
                     The encode resolution width the frame provider should use for future frames.

                     Return:
                         int: The encode resolution width the frame provider should use for future frames.
                     

        :type: int
        """
    @property
    def fec_percent(self) -> int:
        """
                     FEC repair percent.

                     Return:
                         int: FEC repair percent.
                     

        :type: int
        """
    @property
    def pixel_alignment(self) -> int:
        """
                     Resolution pixel alignment recommendation, as configured by upper layers or client directly.

                     Return:
                         int: Resolution pixel alignment recommendation, as configured by upper layers or client directly.
                     

        :type: int
        """
    @property
    def preferred_height(self) -> int:
        """
                     The preferred streaming resolution height, before any pixel alignment adjustments.

                     Return:
                         int: The preferred streaming resolution height, before any pixel alignment adjustments.
                     

        :type: int
        """
    @property
    def preferred_width(self) -> int:
        """
                     The preferred streaming resolution width, before any pixel alignment adjustments.

                     Return:
                         int: The preferred streaming resolution width, before any pixel alignment adjustments.
                     

        :type: int
        """
    @property
    def qos_bitrate(self) -> int:
        """
                     Bitrate bps to be used for the next frame.

                     Return:
                         int: Bitrate bps to be used for the next frame.
                     

        :type: int
        """
    @property
    def recommended_mode(self) -> NvstStreamingMode:
        """
                     SDK's recommended resolution/FPS for the application to render at.

                     Return:
                         NvstStreamingMode: SDK's recommended resolution/FPS for the application to render at.
                     

        :type: NvstStreamingMode
        """
    @property
    def reference_aspect_ratio(self) -> float:
        """
                     If pixel alignment takes place, round in favor of values close to this reference aspect ratio.

                     Return:
                         float: If pixel alignment takes place, round in favor of values close to this reference aspect ratio.
                     

        :type: float
        """
    @property
    def stream_index(self) -> int:
        """
                     Index of the video stream in the multi-monitor use case.

                     Return:
                         int: Index of the video stream in the multi-monitor use case.
                     

        :type: int
        """
    @property
    def target_streaming_fps(self) -> int:
        """
                     This param represents the desired streaming FPS and it is used to control capture thread timing.

                     Return:
                         int: This param represents the desired streaming FPS and it is used to control capture thread timing.
                     

        :type: int
        """
    pass
class NvstStreamingMode():
    @property
    def actual_streaming_fps(self) -> int:
        """
                     Estimate of the actual streaming fps used for configuring the encoder.

                     Return:
                         int: Estimate of the actual streaming fps.
                     

        :type: int
        """
    @property
    def height(self) -> int:
        """
                     Height of the stream.

                     Return:
                         int: Height of the stream.
                     

        :type: int
        """
    @property
    def sync_captured_and_streaming_fps(self) -> bool:
        """
                     When set to true, streaming FPS will sync to captured FPS which will avoid capturing and streaming the duplicate (repeat) frames.

                     Return:
                         bool: Sync captured FPS and streaming FPS.
                     

        :type: bool
        """
    @property
    def width(self) -> int:
        """
                     Width of the stream.

                     Return:
                         int: Width of the stream.
                     

        :type: int
        """
    pass
def acquire_livestream_interface(*args, **kwargs) -> typing.Any:
    pass
