import sys
import time
import carb
import carb.eventdispatcher
import asyncio
import argparse
import omni.usd
from pxr import Sdf
from enum import Enum   
from copy import deepcopy

loopCnt = 0
eventSubscription = None

def on_rendering_event(e: carb.eventdispatcher.Event):
    global loopCnt
    frameNo = e["frame_number"]
    print(f"Exec python frame:{frameNo} completed loop:{loopCnt} ")

async def script_loop():
    global loopCnt
    print(f"Beginning script_loop {loopCnt}")
    while True:
        print(f"Exec python before waitBeginFrame: loop {loopCnt}")
        await omni.kit.app.get_app().pre_update_async()
        print(f"Exec python after waitBeginFrame: loop {loopCnt}")
        print(f"Exec python before waitEndFrame: loop {loopCnt}")
        await omni.kit.app.get_app().post_update_async()
        print(f"Exec python bafterefore waitEndFrame: loop {loopCnt}")
        loopCnt = loopCnt + 1

def main():
    global loopCnt
    global eventSubscription

    print(f"Exec python: create eventSubscription loop:{loopCnt} ")
    usd_context = omni.usd.get_context()
    eventSubscription = carb.eventdispatcher.get_eventdispatcher().observe_event(
        event_name=usd_context.stage_rendering_event_name(omni.usd.StageRenderingEventType.NEW_FRAME, True),
        on_event=on_rendering_event,
        observer_name="test_exec_order"
    )
    print(f"Exec python: script execution begin, ensure_future pre loop:{loopCnt} ")
    asyncio.ensure_future(script_loop())
    print(f"Exec python: script execution begin, ensure_future post loop:{loopCnt} ")

main()
