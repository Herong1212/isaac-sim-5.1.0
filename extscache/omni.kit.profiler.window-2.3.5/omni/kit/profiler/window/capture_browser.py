import glob
import importlib
import io
import os
import pstats
import sys
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

import carb
import omni.ui as ui
from omni.kit.profiler.window import logger


@contextmanager
def _change_envvar(name: str, value: str):
    old_value = os.environ.get(name, None)
    os.environ[name] = value
    try:
        yield
    finally:
        os.environ[name] = old_value


@lru_cache()
def is_external_build():
    return carb.settings.get_settings().get("/privacy/externalBuild") == True


def get_tracy_module():
    try:
        import omni.kit.profiler.tracy

        return omni.kit.profiler.tracy
    except ImportError:
        return None


def try_remove(p):
    if os.path.exists(p):
        os.remove(p)


class TraceFile:
    def __init__(self, path):
        self._path = path
        self.unzipped_path = os.path.splitext(self._path)[0] + ".json"
        self.tracy_path = os.path.splitext(self._path)[0] + ".tracy"
        self.is_unzipped = os.path.exists(self.unzipped_path)

    def unzip(self):
        if self.is_unzipped:
            return
        import gzip
        import shutil

        with gzip.open(self._path, "rb") as f_in:
            with open(self.unzipped_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
                self.is_unzipped = True

    def remove(self):
        try_remove(self._path)
        try_remove(self.unzipped_path)
        try_remove(self.tracy_path)

    def launch_in_tracy(self):
        tracy_module = get_tracy_module()
        if not tracy_module:
            return
        if not os.path.exists(self.tracy_path):
            self.unzip()
            tracy_module.convert_json_to_tracy(self.unzipped_path, self.tracy_path)
        tracy_module.launch_tracy(self.tracy_path)


class CaptureBrowserWindow:
    def __init__(self, path):
        self._path = path
        self._last_capture_paths = []
        self._window = ui.Window("Captured Traces Browser", width=800, height=710, flags=ui.WINDOW_FLAGS_NO_DOCKING)
        self._window.visible = False
        self._proc = None

    def destroy(self):
        self._window = None
        if self._proc:
            self._proc.kill()
            self._proc = None
        pass

    def show(self):
        if not self._window.visible:
            self._window.visible = True
            self.refresh()

    def set_last_capture_paths(self, paths):
        self._last_capture_paths = paths
        if self._window.visible:
            self.refresh()

    def is_last_capture(self, path):
        for last in self._last_capture_paths:
            if os.path.exists(last) and os.path.samefile(last, path):
                return True
        return False

    def _build_carb_profiler_list(self):
        ui.Label("List of Traces (carb.profiler):", style={"color": 0xFFB7F222, "font_size": 16})
        ui.Spacer(height=5)

        is_tracy_available = get_tracy_module() is not None

        traces = list(glob.glob(f"{self._path}/*.gz"))
        if len(traces) == 0:
            ui.Label("Empty. Capture traces: enable using CPU Profiler -> Press Capture.")
        for p in traces:
            ui.Spacer(height=5)
            trace = TraceFile(p)
            with ui.HStack():
                name = os.path.basename(trace.unzipped_path if trace.is_unzipped else p)
                if self.is_last_capture(p):
                    name += " (new)"
                ui.Label(name, style={"color": 0xFFFFFFFF})

                if not trace.is_unzipped:

                    def unzip(t=trace):
                        t.unzip()
                        self.refresh()

                    ui.Button("unzip", width=100, clicked_fn=unzip)

                if is_tracy_available:

                    def on_tracy(t=trace):
                        t.launch_in_tracy()

                    ui.Button("tracy", width=100, clicked_fn=on_tracy)

                def remove(t=trace):
                    t.remove()
                    self.refresh()

                ui.Button("remove", width=100, clicked_fn=remove)

    def _open_with_snakeviz(self, path):
        import subprocess

        # OMFP-1886: Cease use of pip-install, and use pre bundled packages.
        try:
            import snakeviz
        except ImportError:
            carb.log_error("Cannot import snakeviz. Filed to open with snakeviz.")
            return

        packages_path = str(Path(snakeviz.__file__).parent.parent)
        with _change_envvar("PYTHONPATH", packages_path):
            python_exe = "python.exe" if sys.platform == "win32" else "bin/python3"
            args = [path]
            cmd = [sys.prefix + "/" + python_exe, "-m", "snakeviz"] + args
            logger.info("run process: %s", cmd)
            if self._proc:
                self._proc.kill()
                self._proc = None
            self._proc = subprocess.Popen(cmd)

    def _build_cprofile_list(self):
        ui.Label("List of Traces (cProfile):", style={"color": 0xFFB7F222, "font_size": 16})
        ui.Spacer(height=5)

        traces = list(glob.glob(f"{self._path}/*.prof"))
        if len(traces) == 0:
            ui.Label("Empty. Capture traces: enable using Profile Python (cProfile) -> Press Capture.")
        for p in traces:
            print(self._last_capture_paths)
            ui.Spacer(height=5)
            with ui.HStack():
                name = os.path.basename(p)
                if self.is_last_capture(p):
                    name += " (new)"
                ui.Label(name, style={"color": 0xFFFFFFFF})

                # That functionality for internal builds only. To avoid automatic pip install on public builds.
                if not is_external_build():

                    def snakeviz(p_=p):
                        self._open_with_snakeviz(p_)

                    ui.Button("snakeviz", width=100, clicked_fn=snakeviz)

                def stats(p_=p):
                    import webbrowser

                    s = io.StringIO()
                    pstats.Stats(p_, stream=s).strip_dirs().sort_stats("tottime").print_stats()
                    outp = p_ + ".txt"
                    with open(outp, "w") as f:
                        f.write(s.getvalue())
                    print(s.getvalue())
                    webbrowser.open(outp)

                ui.Button("stats", width=100, clicked_fn=stats)

    def refresh(self):
        def add_open_button(text, url):
            def open(url_=url):
                import webbrowser

                webbrowser.open(url_)

            ui.Button(text, width=100, clicked_fn=open, tooltip=url)

        def add_clean_button(text, path):
            def clean(path_=path):
                for f in glob.glob(f"{path_}/*"):
                    os.remove(f)
                self.refresh()

            ui.Button(text, width=100, clicked_fn=clean, tooltip="Remove all traces (!)")

        with self._window.frame:
            with ui.VStack(height=0):
                ui.Button("Refresh", width=100, clicked_fn=lambda: self.refresh())

                ui.Spacer(height=10)
                ui.Label("Trace Folder:", style={"color": 0xFFB7F222, "font_size": 16})
                ui.Spacer(height=5)

                with ui.HStack():
                    add_open_button("Open", self._path)
                    add_clean_button("Remove All", self._path)
                    ui.Label(f"Path: {self._path}")

                ui.Spacer(height=10)
                ui.Label("View Methods:", style={"color": 0xFFB7F222, "font_size": 16})
                ui.Spacer(height=5)
                with ui.HStack():
                    ui.Label("1. Open Chrome -> 'chrome://tracing' -> drag unzipped trace (json file)")
                if get_tracy_module():
                    ui.Spacer(height=5)
                    with ui.HStack():
                        ui.Label("2. Tracy (Button)")
                ui.Spacer(height=20)

                self._build_carb_profiler_list()
                ui.Spacer(height=20)
                self._build_cprofile_list()
