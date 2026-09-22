import argparse
import time
import threading
import omni.usd.audio
import omni.timeline
import omni.kit.app
import asyncio

parser = argparse.ArgumentParser()
parser.add_argument("path", help="Path to USD stage.")

options = parser.parse_args()

async def test():
    def finished():
        omni.kit.app.get_app().post_quit()

    omni.usd.get_context().open_stage(options.path)

    audio = omni.usd.audio.get_stage_audio_interface()

    prim = omni.usd.get_context().get_stage().GetPrimAtPath("/World/sample")
    while audio.get_sound_asset_status(prim) != omni.usd.audio.AssetLoadStatus.IN_PROGRESS:
        print("WAITING FOR ASSETS")
        time.sleep(0.1)

    omni.timeline.get_timeline_interface().play()

    threading.Timer(4.0, finished).start()

asyncio.ensure_future(test())
