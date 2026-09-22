import omni.kit.test

import omni.kit.audiodeviceenum


def get_name_from_sample_type(sample_type):  # pragma: no cover
    if sample_type == omni.kit.audiodeviceenum.SampleType.UNKNOWN:
        return "UNKNOWN"

    if sample_type == omni.kit.audiodeviceenum.SampleType.PCM_SIGNED_INTEGER:
        return "INT PCM"

    if sample_type == omni.kit.audiodeviceenum.SampleType.PCM_UNSIGNED_INTEGER:
        return "UINT PCM"

    if sample_type == omni.kit.audiodeviceenum.SampleType.PCM_FLOAT:
        return "FLOAT PCM"

    if sample_type == omni.kit.audiodeviceenum.SampleType.COMPRESSED:
        return "COMPRESSED"


class TestAudio(omni.kit.test.AsyncTestCase):  # pragma: no cover
    async def test_audio_device(self):
        audio = omni.kit.audiodeviceenum.get_audio_device_enum_interface()
        self.assertIsNotNone(audio)

        count = audio.get_device_count(omni.kit.audiodeviceenum.Direction.PLAYBACK)
        self.assertGreaterEqual(count, 0)

        printDevices = 0

        if printDevices != 0:
            print("Found ", count, " Available Playback Devices:")

        if count > 0:
            for i in range(0, count):
                desc = audio.get_device_description(omni.kit.audiodeviceenum.Direction.PLAYBACK, i)
                self.assertIsNotNone(desc)

                name = audio.get_device_name(omni.kit.audiodeviceenum.Direction.PLAYBACK, i)
                self.assertIsNotNone(name)

                uniqueId = audio.get_device_id(omni.kit.audiodeviceenum.Direction.PLAYBACK, i)
                self.assertIsNotNone(uniqueId)

                if not audio.is_direct_hardware_backend():
                    frame_rate = audio.get_device_frame_rate(omni.kit.audiodeviceenum.Direction.PLAYBACK, i)
                    self.assertGreater(frame_rate, 0)

                    channel_count = audio.get_device_channel_count(omni.kit.audiodeviceenum.Direction.PLAYBACK, i)
                    self.assertGreater(channel_count, 0)

                    sample_size = audio.get_device_sample_size(omni.kit.audiodeviceenum.Direction.PLAYBACK, i)
                    self.assertGreater(sample_size, 0)

                    sample_type = audio.get_device_sample_type(omni.kit.audiodeviceenum.Direction.PLAYBACK, i)

                    if printDevices != 0:
                        str_desc = "    found the device '" + name + "' "
                        str_desc += "{" + str(channel_count) + " channels "
                        str_desc += "@ " + str(frame_rate) + "Hz "
                        str_desc += str(sample_size) + "-bit " + get_name_from_sample_type(sample_type)
                        print(str_desc)
                        print("        " + desc)

                else:
                    if printDevices != 0:
                        print("    found the device '" + name + "' ")
                        print("        " + desc)

        # make sure out of range values fail.
        desc = audio.get_device_description(omni.kit.audiodeviceenum.Direction.PLAYBACK, count)
        self.assertIsNone(desc)
        name = audio.get_device_name(omni.kit.audiodeviceenum.Direction.PLAYBACK, count)
        self.assertIsNone(name)
        uniqueId = audio.get_device_id(omni.kit.audiodeviceenum.Direction.PLAYBACK, count)
        self.assertIsNone(uniqueId)
        frame_rate = audio.get_device_frame_rate(omni.kit.audiodeviceenum.Direction.PLAYBACK, count)
        self.assertEqual(frame_rate, 0)
        channel_count = audio.get_device_channel_count(omni.kit.audiodeviceenum.Direction.PLAYBACK, count)
        self.assertEqual(channel_count, 0)
        sample_size = audio.get_device_sample_size(omni.kit.audiodeviceenum.Direction.PLAYBACK, count)
        self.assertEqual(sample_size, 0)
        sample_type = audio.get_device_sample_type(omni.kit.audiodeviceenum.Direction.PLAYBACK, count)
        self.assertEqual(sample_type, omni.kit.audiodeviceenum.SampleType.UNKNOWN)

        count = audio.get_device_count(omni.kit.audiodeviceenum.Direction.CAPTURE)
        self.assertGreaterEqual(count, 0)

        if printDevices != 0:
            print("\nFound ", count, " Available Capture Devices:")

        if count > 0:
            for i in range(0, count):
                desc = audio.get_device_description(omni.kit.audiodeviceenum.Direction.CAPTURE, i)
                self.assertIsNotNone(desc)

                name = audio.get_device_name(omni.kit.audiodeviceenum.Direction.CAPTURE, i)
                self.assertIsNotNone(name)

                uniqueId = audio.get_device_id(omni.kit.audiodeviceenum.Direction.CAPTURE, i)
                self.assertIsNotNone(uniqueId)

                if not audio.is_direct_hardware_backend():
                    frame_rate = audio.get_device_frame_rate(omni.kit.audiodeviceenum.Direction.CAPTURE, i)
                    self.assertGreater(frame_rate, 0)

                    channel_count = audio.get_device_channel_count(omni.kit.audiodeviceenum.Direction.CAPTURE, i)
                    self.assertGreater(channel_count, 0)

                    sample_size = audio.get_device_sample_size(omni.kit.audiodeviceenum.Direction.CAPTURE, i)
                    self.assertGreater(sample_size, 0)

                    sample_type = audio.get_device_sample_type(omni.kit.audiodeviceenum.Direction.CAPTURE, i)

                    if printDevices != 0:
                        str_desc = "    found the device '" + name + "' "
                        str_desc += "{" + str(channel_count) + " channels "
                        str_desc += "@ " + str(frame_rate) + "Hz "
                        str_desc += str(sample_size) + "-bit " + get_name_from_sample_type(sample_type)
                        print(str_desc)
                        print("        " + desc)

                else:
                    if printDevices != 0:
                        print("    found the device '" + name + "' ")
                        print("        " + desc)

        # make sure out of range values fail.
        desc = audio.get_device_description(omni.kit.audiodeviceenum.Direction.CAPTURE, count)
        self.assertIsNone(desc)
        name = audio.get_device_name(omni.kit.audiodeviceenum.Direction.CAPTURE, count)
        self.assertIsNone(name)
        uniqueId = audio.get_device_id(omni.kit.audiodeviceenum.Direction.CAPTURE, count)
        self.assertIsNone(uniqueId)
        frame_rate = audio.get_device_frame_rate(omni.kit.audiodeviceenum.Direction.CAPTURE, count)
        self.assertEqual(frame_rate, 0)
        channel_count = audio.get_device_channel_count(omni.kit.audiodeviceenum.Direction.CAPTURE, count)
        self.assertEqual(channel_count, 0)
        sample_size = audio.get_device_sample_size(omni.kit.audiodeviceenum.Direction.CAPTURE, count)
        self.assertEqual(sample_size, 0)
        sample_type = audio.get_device_sample_type(omni.kit.audiodeviceenum.Direction.CAPTURE, count)
        self.assertEqual(sample_type, omni.kit.audiodeviceenum.SampleType.UNKNOWN)
