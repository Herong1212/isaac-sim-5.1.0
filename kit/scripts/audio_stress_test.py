import pathlib
import random
import carb.tokens
import omni.usd
import omni.usd.audio
import omni.timeline
import pxr.Sdf
import pxr.Gf

context = omni.usd.get_context()

context.new_stage()
stage = context.get_stage()

omni.timeline.get_timeline_interface().set_end_time(10)

audio = omni.usd.audio.get_stage_audio_interface()

audio.set_concurrent_voices(1024);

extension_path = carb.tokens.get_tokens_interface().resolve("${omni.kit.audio.test.usd}")
test_path = pathlib.Path(extension_path).joinpath("data").joinpath("tests").absolute()

test_sound_1ch_path = test_path.joinpath("short-1ch.oga").absolute()

N = 1<< 12
T = 1 << 12

random.seed(0xBEEF);
for i in range (0, N):
    prim_path = "/sound_" + str(i)
    prim = stage.DefinePrim(prim_path, "OmniSound")
    prim.GetAttribute("filePath").Set(str(test_sound_1ch_path))
    prim.GetAttribute("startTime").Set(random.randint(0, N) / (N / 10.0))
    prim.GetAttribute("gain").Set(random.randint(1, N) / (N * 20.0))
    prim.GetAttribute("timeScale").Set(random.randint(1, N) / (N  / 10))
    prim.GetAttribute("enableInterauralDelay").Set("on")
    # this seems to get some prims stuck looping
    #prim.GetAttribute("loopCount").Set(random.randint(0, 1))
    prim.GetAttribute("priority").Set(random.randint(0, 63))
    prim.CreateAttribute("xformOp:translate", pxr.Sdf.ValueTypeNames.Double3, False).Set(pxr.Gf.Vec3d(random.randint(-T, T), random.randint(-T, T), random.randint(-T, T)))
    prim.CreateAttribute("xformOpOrder", pxr.Sdf.ValueTypeNames.String, False).Set(["xformOp:translate"])

