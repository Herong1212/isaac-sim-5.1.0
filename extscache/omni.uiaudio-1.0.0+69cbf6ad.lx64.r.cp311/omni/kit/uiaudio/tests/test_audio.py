
import omni.kit.test
import omni.kit.uiaudio


class TestAudio(omni.kit.test.AsyncTestCase):  # pragma: no cover
    async def test_ui_audio(self):
        audio = omni.kit.uiaudio.get_ui_audio_interface()
        self.assertIsNotNone(audio)

        # try to load a sound to test with.
        sound = audio.create_sound("${sounds}/stop.wav")

        if sound == None:
            # still try to play the null sound.
            audio.play_sound(sound)

            # verify the sound's length is zero.
            length = audio.get_sound_length(sound)
            self.assertEqual(length, 0.0)

            # make sure querying whether the null sound is playing fails.
            playing = audio.is_sound_playing(sound)
            self.assertFalse(playing)

        else:
            # play the sound.
            audio.play_sound(sound)

            # verify that it is playing.
            playing = audio.is_sound_playing(sound)
            self.assertTrue(playing)

            # verify the sound's length is non-zero.
            length = audio.get_sound_length(sound)
            self.assertGreater(length, 0.0)

            # wait so that a user can hear that sound is playing.
            time.sleep(min(length, 5.0))

            # clean up the local reference to the sound.
            sound = None
