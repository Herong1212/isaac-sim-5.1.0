import os

import carb
import omni.ext
from .._video_encoding import *

# Put interface object publicly to use in our API.
_video_encoding_api = None


def get_video_encoding_interface() -> IVideoEncoding:
    """Return the video encoding interface object.

    Returns:
        IVideoEncoding: The current video encoding interface object.
    """
    return _video_encoding_api


def encode_image_file_sequence(filename_pattern, start_number, frame_rate, output_file, overwrite_existing) -> bool:
    """Encode a sequence of image files into a video.

    Args:
        filename_pattern (str): File pattern to generate frame file names.
        start_number (int): Starting frame number for file sequence.
        frame_rate (int): Frame rate of the output video.
        output_file (str): Destination file for encoded video.
        overwrite_existing (bool): Flag indicating whether to overwrite the existing output file.

    Returns:
        bool: True if encoding succeeded, False otherwise.

    Raises:
        Exception: Propagates any exceptions encountered during frame encoding.
    """
    video_encoding_api = get_video_encoding_interface()
    if video_encoding_api is None:
        carb.log_warn("Video encoding api not available; cannot encode video.")
        return False

    # acquire list of available frame image files, based on start_number and filename_pattern
    next_frame = start_number
    frame_filenames = []
    while True:
        frame_filename = filename_pattern % (next_frame)

        if os.path.isfile(frame_filename) and os.access(frame_filename, os.R_OK):
            frame_filenames.append(frame_filename)
            next_frame += 1
        else:
            break

    carb.log_warn(f"Found {len(frame_filenames)} frames to encode.")
    if len(frame_filenames) == 0:
        carb.log_warn(f"No frames to encode.")
        return False

    if not video_encoding_api.start_encoding(output_file, frame_rate, len(frame_filenames), overwrite_existing):
        return

    try:
        for frame_filename in frame_filenames:
            video_encoding_api.encode_next_frame_from_file(frame_filename)
    except:
        raise
    finally:
        video_encoding_api.finalize_encoding()

    return True


# Use extension entry points to acquire and release interface.
class VideoEncodingExtension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        pass

    def on_startup(self, ext_id):
        global _video_encoding_api
        _video_encoding_api = acquire_video_encoding_interface()

    def on_shutdown(self):
        global _video_encoding_api
        release_video_encoding_interface(_video_encoding_api)
        _video_encoding_api = None
