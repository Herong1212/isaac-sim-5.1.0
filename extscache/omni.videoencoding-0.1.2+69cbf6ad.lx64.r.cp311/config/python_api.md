# Public API for module video_encoding:

## Classes

- class IVideoEncoding
  - def encode_next_frame_from_buffer(self, buffer_rgba8: buffer, width: int = 0, height: int = 0) -> bool
  - def encode_next_frame_from_file(self, frame_filename: str)
  - def finalize_encoding(self)
  - def start_encoding(self, video_filename: str, framerate: float, nframes: int, overwrite_video: bool) -> bool

## Functions

- def encode_image_file_sequence(filename_pattern, start_number, frame_rate, output_file, overwrite_existing) -> bool
- def get_video_encoding_interface() -> IVideoEncoding
