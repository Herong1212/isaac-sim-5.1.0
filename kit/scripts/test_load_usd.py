# loads a USD file and plays its timeline after load.
import argparse
import time
import threading
import omni.usd
import omni.timeline
import omni.kit.app

parser = argparse.ArgumentParser()
parser.add_argument("path", help="Path to USD stage.")

options = parser.parse_args()


def on_open(*_):
    omni.timeline.get_timeline_interface().play()


omni.usd.get_context().open_stage_with_callback(options.path, on_open)
