"""
        Bindings for the omni::IVideoEncoding interface.
    """
from __future__ import annotations
import video_encoding._video_encoding
import typing

__all__ = [
    "IVideoEncoding",
    "acquire_video_encoding_interface",
    "release_video_encoding_interface"
]


class IVideoEncoding():
    def encode_next_frame_from_buffer(self, buffer_rgba8: buffer, width: int = 0, height: int = 0) -> bool: 
        """
        Encode a frame and write the result to disk.

        Args:
            buffer_rgba8 raw frame image data; format: R8G8B8A8; size: width * height * 4
            width frame width; can be inferred from shape of buffer_rgba8 if set appropriately
            height frame height; can be inferred from shape of buffer_rgba8 if set appropriately
        Returns:
            True if successful, else False.
        """
    def encode_next_frame_from_file(self, frame_filename: str) -> None: 
        """
        Read a frame from an image file, encode, and write to disk. Warning: pixel formats other than RGBA8 will probably not work (yet).

        Args:
            frame_filename name of the file to read. Supported file formats: see carb::imaging
        """
    def finalize_encoding(self) -> None: 
        """
        Indicate that all frames have been encoded. This will ensure that writing to the output video file is done, and close it.
        """
    def start_encoding(self, video_filename: str, framerate: float, nframes: int, overwrite_video: bool) -> bool: 
        """
        Prepare the encoding plugin to process frames.

        Args:
            video_filename name of the MP4 file where the encoded video will be written
            framerate number of frames per second
            nframes total number of frames; if unknown, set to 0
            overwrite_video if set, overwrite existing MP4 file; otherwise, refuse to do anything if the file specified in video_filename exists.

        Returns:
            True if preparation succeeded and the encoding plugin is ready; False otherwise.
        """
    pass
def acquire_video_encoding_interface(plugin_name: str = None, library_path: str = None) -> IVideoEncoding:
    pass
def release_video_encoding_interface(arg0: IVideoEncoding) -> None:
    pass
