import time
import carb
import asyncio
import argparse
import omni.usd
from pxr import Sdf
from enum import Enum   
from copy import deepcopy
from omni.kit import viewport_legacy

gpus = carb.settings.get_settings().get("/renderer/multiGpu/currentGpuCount")
viewportFactory = viewport_legacy.get_viewport_interface()
# defaultWindow = viewportFactory.get_viewport_window()

for i in range(gpus - 1):
    handle = viewportFactory.create_instance()
    win = viewportFactory.get_viewport_window(handle)
    win.set_window_size(400, 400)
    win.set_window_pos(100 + 20 * i, 150 + 20 * i)
