import asyncio
import os
import platform
import subprocess
import sys
import time
import uuid
import webbrowser
from datetime import datetime
from functools import lru_cache
from typing import Optional

import carb
import omni.kit.app
import omni.ui as ui

from . import logger
from .chrome_trace import ChromeTrace
from .nvdf import nvdf_send_batched


def get_local_timestamp():
    return (
        # ':' is not path-friendly on windows
        datetime.now()
        .isoformat(timespec="seconds")
        .replace(":", "-")
    )


@lru_cache()
def is_windows():
    return platform.system().lower() == "windows"


def run_process(args):
    print(f"running process: {args}")
    kwargs = {"close_fds": False}
    if is_windows():
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(args, **kwargs)


def profile_startup(output):
    ts = get_local_timestamp()

    # Open output dir
    webbrowser.open(output)

    # Run new app with profiling
    args = list(sys.argv)
    args += [
        "--/plugins/carb.profiler-cpu.plugin/saveProfile=1",
        "--/plugins/carb.profiler-cpu.plugin/compressProfile=1",
        "--/app/profileFromStart=1",
        f"--/plugins/carb.profiler-cpu.plugin/filePath='{output}/ct_startup_profile_{ts}.gz'",
        "--/app/quitAfter=10",
    ]
    run_process(args)

    # Kill itself
    carb.settings.get_settings().set("/crashreporter/enabled", False)
    os._exit(0)


async def export_trace_to_nvdf(
    chrometrace_filepath: str, nvdf_endpoint: str, extra_kwargs: Optional[dict] = None, ts_created: Optional[int] = None
):
    """Export trace data to nvdf

    Args:
        chrometrace_filepath: Path to json chrome format tracefile
        nvdf_endpoint: Endpoint to publish profile data to
        extra_kwargs: Arbitrary extra fields added to every elasticsearch doc
        ts_created: Time (linux epoch time in milliseconds) to set on every doc (defaults to now)
    """

    def _fn():
        asyncio.run(_export_trace_to_nvdf(chrometrace_filepath, nvdf_endpoint, extra_kwargs, ts_created))

    await asyncio.get_running_loop().run_in_executor(None, _fn)


async def _export_trace_to_nvdf(chrometrace_filepath, nvdf_endpoint, extra_kwargs, ts_created):
    trace_uuid = uuid.uuid4().hex  # a unique id to group all docs in this trace
    ts_created = ts_created or int(time.time() * 1000)
    docs = []

    # TODO this should be impl in omni.kit.app
    app = omni.kit.app.get_app()
    ver = app.get_build_version()  # eg 103.1+release.10030.f5f9dcab.tc
    kit_ver = ver.split("+", 1)[0]  # 103.1
    kit_build_number = int(ver.rsplit(".", 3)[1])  # 10030

    doc_base = {
        "ts_created": ts_created,
        "trace_uuid": trace_uuid,
        "kit_version": kit_ver,
        "kit_build_number": kit_build_number,
        "platform": app.get_platform_info()["platform"],
    }

    if extra_kwargs:
        doc_base.update(extra_kwargs)

    # load the chrometrace
    chrometrace = await ChromeTrace.create(chrometrace_filepath)

    # calc and export collapsed span info (raw span data is far too large, ~2s == 400k+ spans)
    """
    span_totals = chrometrace.get_span_totals()

    for span_doc in span_totals:
        span_doc.update(doc_base)
        span_doc["objtype"] = "span_total"
        docs.append(span_doc)
    """

    # calc and export avg walltime per span. Note that this is different to span_dur below, which reports a total
    # walltime that takes recursion into account (ie does not re-count time spent in recursed spans). This doesn't
    # make sense when calculating an avg walltime per span.
    #
    for span_name, avg_walltime in chrometrace.get_avg_walltime_per_span().items():
        doc = {"objtype": "span_walltime_avg", "span_name": span_name, "avg_walltime": avg_walltime}
        doc.update(doc_base)
        docs.append(doc)

    """
    def _export_durs(objtype, durs):

        for durs_doc in durs:
            durs_doc.update(doc_base)

            # we break nonlocal-dur and self-dur into separate docs so a stacked chart can be shown in kibana
            self_doc = {
                "objtype": objtype,
                "dur_type": "self",
                "dur_total": durs_doc["self_dur_total"]
            }
            self_doc.update(durs_doc)
            docs.append(self_doc)

            nonself_dur_total = durs_doc["wall_dur_total"] - durs_doc["self_dur_total"]
            nonself_doc = {
                "objtype": objtype,
                "dur_type": "nonself",
                "dur_total": nonself_dur_total
            }
            nonself_doc.update(durs_doc)
            docs.append(nonself_doc)

    # calc and export wall duration per span name
    span_wall_durs = chrometrace.get_span_wall_durs()
    _export_durs("span_dur", span_wall_durs)

    # calc and export wall duration per category
    cat_wall_durs = chrometrace.get_cat_wall_durs()
    _export_durs("cat_dur", cat_wall_durs)
    """

    logger.info("%d raw events converted to %d elastic docs", chrometrace.raw_event_count, len(docs))
    await nvdf_send_batched(docs, nvdf_endpoint)


def create_label_checkbox(
    text: str,
    enabled: Optional[bool] = None,
    change_fn=None,
    tooltip=None,
    model: Optional[ui.AbstractValueModel] = None,
):
    with ui.HStack(width=0, height=0):
        ui.Label(text)
        ui.Spacer(width=5)
        with ui.VStack():
            ui.Spacer(height=4)
            checkbox = ui.CheckBox(model=model)
        ui.Spacer(width=10)
        if tooltip:
            checkbox.tooltip = tooltip
        if not model:
            checkbox.model.set_value(enabled)
            if change_fn:
                checkbox.model.add_value_changed_fn(change_fn)
        return checkbox


from typing import Union


def create_label_slider(text: str, min: Union[int, float], max: Union[int, float], tooltip: str):
    with ui.HStack(width=0, height=0):
        ui.Label(text)
        ui.Spacer(width=10)
        with ui.VStack():
            ui.Spacer(height=3)
            slider = ui.IntSlider(
                min=min, max=max, width=60, height=18, style_type_name_override="Drag", tooltip=tooltip
            )
        ui.Spacer(width=10)

    return slider


def create_label_drag(
    text: str,
    drag_type: Union[ui.IntDrag, ui.FloatDrag],
    min: Union[int, float],
    max: Union[int, float],
    step: Union[int, float],
    tooltip: str,
):
    with ui.HStack(width=0, height=0):
        ui.Label(text)
        ui.Spacer(width=5)
        with ui.VStack():
            ui.Spacer(height=3)
            drag = drag_type(
                min=min,
                max=max,
                step=step,
                style_type_name_override="Drag",
                format="%.3f",
                width=60,
                height=18,
                tooltip=tooltip,
            )
        ui.Spacer(width=10)
    return drag
