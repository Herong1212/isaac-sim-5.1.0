import omni.kit.test

import carb.settings

import os
import tempfile

import numpy as np

from video_encoding import get_video_encoding_interface

VIDEO_FULL_RANGE_PATH = "/exts/omni.videoencoding/vui/videoFullRangeFlag"

class Test(omni.kit.test.AsyncTestCase):
    def get_next_frame(self, shape=(480,640,4)):
        values = self._rng.random(shape)
        result = (values * 255.).astype(np.uint8)
        return result

    async def setUp(self):
        self._rng = np.random.default_rng(seed=1234)
        self._settings = carb.settings.acquire_settings_interface()
        self._encoding_interface = get_video_encoding_interface()


    async def tearDown(self):
        self._rng = None

    def _encode_test_sequence(self, n_frames=10):
        n_frames = 10

        with tempfile.TemporaryDirectory() as tmpdirname:
            video_filename = os.path.join(tmpdirname,'output.mp4')
            self.assertTrue(self._encoding_interface.start_encoding(video_filename, 24, n_frames, True),
                msg="Failed to initialize encoding interface.")
            for i_frame in range(n_frames):
                frame_data = self.get_next_frame()
                self._encoding_interface.encode_next_frame_from_buffer(frame_data)
            self._encoding_interface.finalize_encoding()

            encoded_size = os.path.getsize(video_filename)
        return encoded_size

    async def test_encoding_interface(self):
        self.assertTrue(self._encoding_interface is not None)
        self._settings.set(VIDEO_FULL_RANGE_PATH, False)

        encoded_size = self._encode_test_sequence(n_frames=10)
        expected_encoded_size = 721879

        self.assertAlmostEqual(encoded_size / expected_encoded_size, 1., places=1,
            msg=f"Expected encoded video size {expected_encoded_size}; got: {encoded_size}")

    async def test_encoding_interface_with_full_range(self):
        self._settings.set(VIDEO_FULL_RANGE_PATH, True)

        encoded_size = self._encode_test_sequence(n_frames=10)
        expected_encoded_size = 1081165

        self.assertAlmostEqual(encoded_size / expected_encoded_size, 1., places=1,
            msg=f"Expected encoded video size {expected_encoded_size}; got: {encoded_size}")
