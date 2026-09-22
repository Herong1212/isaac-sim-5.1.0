import os
import sys
from pathlib import Path
from unittest import skipIf

import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.kit.undo
import omni.usd
import omni.usd.audio
from omni.ui.tests.compare_utils import OUTPUTS_DIR
from omni.kit.sequencer.core.scripts.sequencer_audio_commands import SequencerUIStreamAudioCommand


TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "data")
TEST_AUDIO_STREAM_LAYER = os.path.join(TEST_DATA_PATH, "audio_stream_test.usda")


class TestSequencerUIStreamAudioCommand(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        usd_context = omni.usd.get_context()
        usd_context.open_stage(TEST_AUDIO_STREAM_LAYER)
        await omni.kit.app.get_app().next_update_async()

    @skipIf(sys.platform.startswith("linux"), "No audio stream test on Linux.")
    async def test_stream_audio_command(self):
        audio_interface = omni.usd.audio.get_stage_audio_interface()
        self.assertTrue(os.path.exists(TEST_AUDIO_STREAM_LAYER))
        audio_path = Path(OUTPUTS_DIR) / "TEST_SequencerUIStreamAudioCommand"
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        command = SequencerUIStreamAudioCommand(audio_path=str(audio_path))
        capture_id = command.do()
        self.assertIsInstance(capture_id, int)
        self.assertTrue(command.recording)

        while command.recording:
            await omni.kit.app.get_app().next_update_async()

        # wait for the audio interface to be complete
        success = audio_interface.wait_for_capture(capture_id, 300)
        self.assertTrue(success)

        expected_path = audio_path.with_suffix(".wav")
        self.assertTrue(expected_path.exists(), f"Expected file does not exist: {expected_path}")
        # Don't know exact size, output not deterministic
        expected_path.stat().st_size >= 370000
