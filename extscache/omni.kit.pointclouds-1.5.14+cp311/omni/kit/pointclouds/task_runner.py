# Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
from typing import Callable

import carb

FARM_QUEUE_URL = "/queue/management"

# Following functions serves for testing purposes and are enabled from the importer dialog with a setting:
# exts."omni.kit.pointclouds".local_cache_generation = true
# Not meant for production


def get_args(task_type: str, task_fn: str, fn_args: dict, task_comment: str):
    task_args = {
        "user": "omni.kit.pointclouds",
        "task_type": task_type,
        "task_args": {},
        "task_function": task_fn,
        "task_function_args": fn_args,
        "task_comment": task_comment,
        "priority": 65535,
        "metadata": {},
        "status": "submitted",
    }
    return task_args


def submit_task(
    farm_uri: str,
    task_type: str,
    task_fn: str,
    fn_args: dict,
    task_name="point cloud",
    task_comment="",
    next_fn: Callable = None,
):
    client = None
    try:
        import omni.services.client as services_client

        client = services_client.AsyncClient(uri=f"{farm_uri}{FARM_QUEUE_URL}")
    except Exception as error:
        carb.log_error(f"Can't create client: {error}")
        return False

    async def submit(args):
        task = await client.tasks.submit(**args)
        if task:
            info = await client.tasks.info.get(task["task_id"])
            status = info["status"]
            for i in range(360):
                carb.log_info(f"Converting '{task_name}' - {status} ({i * 10} s)...")
                await asyncio.sleep(10)
                info = await client.tasks.info.get(task["task_id"])
                status = info["status"]
                if status == "finished":
                    carb.log_info(f"Converting '{task_name}' finished")
                    if next_fn:
                        await next_fn()
                    return
                elif status == "errored" or status == "cancelled" or status == "archived":
                    carb.log_info(f"Converting '{task_name}' {status}")
                    return

    asyncio.ensure_future(submit(get_args(task_type, task_fn, fn_args, task_comment)))

    return True
