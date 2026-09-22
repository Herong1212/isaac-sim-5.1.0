# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import json
import platform
import subprocess
from io import BytesIO
from pathlib import Path
from queue import Empty, Queue
from threading import Thread

import carb
import carb.settings
import carb.tokens
import omni.client
import omni.kit.app
import omni.kit.converter.jt_core
import omni.kit.tool.asset_importer as ai
import omni.log
from omni import ui
from omni.kit.converter.common import ProgressLogConsumer, ProgressStepType, validate_file_path
from omni.kit.converter.common.ui import CadConverterOptionsBuilder, ConfirmDialogHelper, ProgressDialog
from omni.kit.notification_manager import NotificationStatus, post_notification

__all__ = ["JtConverterDelegate"]

APP_NAME = "omni.kit.converter.jt"
JT_LAUNCH_SCRIPT_PATH = "/omni/kit/converter/jt/process/launch_jt_app.py"


def enqueue_output(out: BytesIO, queue: Queue):
    """store output from subprocess in a queue for later"""
    for line in iter(out.readline, b""):
        queue.put(line)
    out.close()


class JtConverterOptionsBuilder(CadConverterOptionsBuilder):
    def __init__(self, options_model=None):
        super().__init__(options_model=options_model)

        self._override_tessellation_geometry = ui.SimpleBoolModel(default_value=False)
        self._override_tessellation_geometry_sub = self._override_tessellation_geometry.subscribe_value_changed_fn(
            self._override_tessellation_geometry_changed
        )

        self._override_tessellation_parameters = ui.SimpleBoolModel(default_value=False)
        self._override_tessellation_parameters_sub = self._override_tessellation_parameters.subscribe_value_changed_fn(
            self._override_tessellation_parameters_changed
        )

        # Tessellation Fallback Parameters
        self._override_fallbackTessParamChordal = ui.SimpleFloatModel(0.0)
        self._override_fallbackTessParamChordal_sub = (
            self._override_fallbackTessParamChordal.subscribe_value_changed_fn(
                self._override_fallbackTessParamChordal_changed
            )
        )
        self._override_fallbackTessParamAngular = ui.SimpleFloatModel(0.0)
        self._override_fallbackTessParamAngular_sub = (
            self._override_fallbackTessParamAngular.subscribe_value_changed_fn(
                self._override_fallbackTessParamAngular_changed
            )
        )
        self._override_fallbackTessParamLength = ui.SimpleFloatModel(0.0)
        self._override_fallbackTessParamLength_sub = self._override_fallbackTessParamLength.subscribe_value_changed_fn(
            self._override_fallbackTessParamLength_changed
        )
        self._override_fallbackTessParamMaxAspect = ui.SimpleFloatModel(0.0)
        self._override_fallbackTessParamMaxAspect_sub = (
            self._override_fallbackTessParamMaxAspect.subscribe_value_changed_fn(
                self._override_fallbackTessParamMaxAspect_changed
            )
        )
        self._override_fallbackTessParamMinEdgeLength = ui.SimpleFloatModel(0.0)
        self._override_fallbackTessParamMinEdgeLength_sub = (
            self._override_fallbackTessParamMinEdgeLength.subscribe_value_changed_fn(
                self._override_fallbackTessParamMinEdgeLength_changed
            )
        )

    def _override_tessellation_geometry_changed(self, model: ui.SimpleBoolModel):
        self._options_model.overrideTessellationGeometry = model.as_bool

    def _override_tessellation_parameters_changed(self, model: ui.SimpleBoolModel):
        self._options_model.overrideTessellationParameters = model.as_bool
        # Show or Hide the fallback parameters ui
        self._override_tessellation_fallback_parameters.collapsed = not model.as_bool

    def _override_fallbackTessParamChordal_changed(self, model: ui.SimpleFloatModel):
        self._options_model.fallbackTessParamChordal = model.as_float

    def _override_fallbackTessParamAngular_changed(self, model: ui.SimpleFloatModel):
        self._options_model.fallbackTessParamAngular = model.as_float

    def _override_fallbackTessParamLength_changed(self, model: ui.SimpleFloatModel):
        self._options_model.fallbackTessParamLength = model.as_float

    def _override_fallbackTessParamMaxAspect_changed(self, model: ui.SimpleFloatModel):
        self._options_model.fallbackTessParamMaxAspect = model.as_float

    def _override_fallbackTessParamMinEdgeLength_changed(self, model: ui.SimpleFloatModel):
        self._options_model.fallbackTessParamMinEdgeLength = model.as_float

    def _has_tessellation_options(self) -> bool:
        """Return True if the options include tessellation options"""
        return True

    def _build_tessellation_options(self) -> None:
        """Build tessellation options ui"""
        super()._build_tessellation_options()
        with ui.HStack(width=0, spacing=4):
            ui.CheckBox(
                model=self._override_tessellation_geometry,
                identifier="override_tessellation_geometry",
                tooltip="Override Tessellation Geometry -\nIf true, embedded tessellation geometry will be ignored in favour for explicit tessellation of surface geometry.",
            )
            ui.Label("Override Tessellation Geometry")

        with ui.VStack(spacing=4):
            with ui.HStack(width=0, spacing=4):
                ui.CheckBox(
                    model=self._override_tessellation_parameters,
                    identifier="override_tessellation_parameters",
                    tooltip="Override Tessellation Parameters -\nIf true, embedded tessellation parameters will be ignored in favour for explicit tessellation parameters.",
                )
                ui.Label("Override Tessellation Parameters")

            # Add hidden fallback parameters ui
            self._override_tessellation_fallback_parameters = ui.CollapsableFrame(title="Fallback Parameters")
            self._override_tessellation_fallback_parameters.collapsed = (
                not self._options_model.overrideTessellationParameters
            )
            tooltip_details = """Tessellation parameters to be used as a fallback in the absence of embedded tessellation parameters.
If Override Tessellation Parameters is set, these values will be used to override all tessellation parameters."""
            with self._override_tessellation_fallback_parameters:
                with ui.VStack(spacing=4):
                    with ui.HStack(spacing=4):
                        tooltip = f"Ignore Embedded Chordal Tolerance, the absolute or relative maximal chord height for a polygonal segment with respect to the model.\n\n{tooltip_details}"
                        ui.Spacer(width=10)
                        ui.Label(
                            "Chordal Tolerance: ",
                            alignment=ui.Alignment.RIGHT,
                            tooltip=tooltip,
                        )
                        ui.FloatField(
                            model=self._override_fallbackTessParamChordal,
                            identifier="_override_fallbackTessParamChordal",
                            tooltip=tooltip,
                            width=50,
                        )
                    with ui.HStack(spacing=4):
                        tooltip = f"Ignore Embedded Angular Tolerance, the maximum angle deviation between subsequent polygonal segments in an approximation of an edge.\n\n{tooltip_details}"
                        ui.Spacer(width=10)
                        ui.Label(
                            "Angular Tolerance: ",
                            alignment=ui.Alignment.RIGHT,
                            tooltip=tooltip,
                        )
                        ui.FloatField(
                            model=self._override_fallbackTessParamAngular,
                            identifier="_override_fallbackTessParamAngular",
                            tooltip=tooltip,
                            width=50,
                        )
                    with ui.HStack(spacing=4):
                        tooltip = f"Ignore Embedded Parameter Length Tolerance, the maximum polygonal segment length.\n\n{tooltip_details}"
                        ui.Spacer(width=10)
                        ui.Label(
                            "Parameter Length Tolerance: ",
                            alignment=ui.Alignment.RIGHT,
                            tooltip=tooltip,
                        )
                        ui.FloatField(
                            model=self._override_fallbackTessParamLength,
                            identifier="_override_fallbackTessParamLength",
                            tooltip=tooltip,
                            width=50,
                        )
                    with ui.HStack(spacing=4):
                        tooltip = f"Ignore Embedded Max Aspect, the maximum ratio of the longest side of a triangle to the shortest.\n\n{tooltip_details}"
                        ui.Spacer(width=10)
                        ui.Label(
                            "Max Aspect: ",
                            alignment=ui.Alignment.RIGHT,
                            tooltip=tooltip,
                        )
                        ui.FloatField(
                            model=self._override_fallbackTessParamMaxAspect,
                            identifier="_override_fallbackTessParamMaxAspect",
                            tooltip=tooltip,
                            width=50,
                        )
                    with ui.HStack(spacing=4):
                        tooltip = f"Ignore Embedded Minimum Edge Length.\n\n{tooltip_details}"
                        ui.Spacer(width=10)
                        ui.Label(
                            "Min Edge Length: ",
                            alignment=ui.Alignment.RIGHT,
                            tooltip=tooltip,
                        )
                        ui.FloatField(
                            model=self._override_fallbackTessParamMinEdgeLength,
                            identifier="_override_fallbackTessParamMinEdgeLength",
                            tooltip=tooltip,
                            width=50,
                        )

    def destroy(self) -> None:
        super().destroy()
        self._override_tessellation_geometry_sub = None
        self._override_tessellation_parameters_sub = None
        self._override_fallbackTessParamChordal_sub = None
        self._override_fallbackTessParamAngular_sub = None
        self._override_fallbackTessParamLength_sub = None
        self._override_fallbackTessParamMaxAspect_sub = None
        self._override_fallbackTessParamMinEdgeLength_sub = None


class JtConverterDelegate(ai.AbstractImporterDelegate):
    """
    JT Converter delegate implementation for Asset Importer AbstractImporterDelegate.
    """

    def __init__(self, name, filters, descriptions):
        super().__init__()
        self._name = name
        self._filters = filters
        self._descriptions = descriptions
        self._progress_dialog = None
        self._confirm_dialog_helper = ConfirmDialogHelper()
        self._converter_options = omni.kit.converter.jt_core.JTConverterOptions()
        self._options_builder = JtConverterOptionsBuilder(options_model=self._converter_options)

    def destroy(self):
        if self._progress_dialog:
            self._progress_dialog.destroy()
            self._progress_dialog = None
        if self._confirm_dialog_helper:
            self._confirm_dialog_helper.destroy()
            self._confirm_dialog_helper = None
        if self._options_builder:
            self._options_builder.destroy()
            self._options_builder = None

    @property
    def name(self):
        return self._name

    @property
    def filter_regexes(self):
        return self._filters

    @property
    def filter_descriptions(self):
        return self._descriptions

    def build_options(self, paths):
        self._options_builder.set_instancing_tooltip("Only JtkINSTANCE node types are converted to instanceable prims.")
        self._options_builder.build_pane(paths)

    def supports_usd_stage_cache(self):
        return False

    def show_scene_optimizer_config_frame(self):
        return True

    async def convert_assets(self, paths, **kargs):
        export_folder = kargs["export_folder"] if "export_folder" in kargs else ""
        # import_to_stage = kargs["import_to_stage"] if "import_to_stage" in kargs else True # enable again when UsdStageCahce is supported
        import_as_reference = kargs["import_as_reference"] if "import_as_reference" in kargs else True
        export_file_name = kargs["export_file_name"] if "export_file_name" in kargs else ""
        export_file_format = kargs["export_file_format"] if "export_file_format" in kargs else ""
        scene_optimizer_str = kargs["scene_optimizer_str"] if "scene_optimizer_str" in kargs else ""

        self._progress_dialog = ProgressDialog()
        helper = omni.kit.converter.jt_core.JtConverterHelper()

        converted_assets = {}
        for file_path in paths:
            if not self.is_supported_format(file_path):
                continue

            file_path = validate_file_path(file_path)
            if not file_path:
                carb.log_warn(f"Invalid path: {file_path}")
                continue

            confirm_write, output_path, file_url = await self._confirm_dialog_helper.confirm_write_location(
                file_path, export_folder, import_as_reference, export_file_name, export_file_format
            )
            if not confirm_write:
                continue

            self._progress_dialog.show(step_label=f"Extracting: {file_url.stem}")
            # let the dialog build
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

            self._converter_options.sOptimizeConfig = scene_optimizer_str

            # Sync the file on disk if the source is on Nucleus.
            self._progress_dialog.set_progress_info(f"Sync File: {file_url.stem}", 0)

            get_local_file_response, local_file_url = await file_url.get_local_file_async()

            # Original file name.
            file_path = str(local_file_url).replace("\\", "/")

            # confirm local file exists; else return
            if get_local_file_response != omni.client.Result.OK:
                omni.log.error(f"Could not get local file: {local_file_url}. Reason: {get_local_file_response}")
                self._progress_dialog.hide()
                self._progress_dialog.clear()

                return converted_assets

            # Call a new process to convert files.
            error_code, error_msg = await self.launch_kit_app(file_path, output_path)

            self._progress_dialog.set_step_info(f"Conversion Complete: {file_url.stem}")

            # Check if the process terminated successfully and if the USD file exists before trying to reference
            if error_code != 0 or not Path(output_path).exists:
                post_notification(f"Failed to convert file: {error_msg}", duration=4, status=NotificationStatus.WARNING)
                continue
            elif error_code == 0:
                self._progress_dialog.set_step_info(f"Conversion Complete: {file_url.stem}")

            converted_assets[file_path] = output_path

            self._progress_dialog.clear()

        self._progress_dialog.hide()
        return converted_assets

    def create_temp_json(self, import_path: str) -> str:
        if not import_path:
            raise ValueError("Error! 'import_path' must be defined!")

        default_config_json_path = str(
            carb.tokens.get_tokens_interface().resolve("${temp}") + "/" + str(Path(import_path).stem) + ".json"
        )

        carb.log_info("Temp JSON config path = " + default_config_json_path)
        with open(default_config_json_path, "w") as outfile:
            json.dump(self._converter_options.toArgs(), outfile, indent=4)
            outfile.close()
        return default_config_json_path

    async def launch_kit_app(self, file_path: str, output_path: str) -> tuple[int, str]:
        # Get the full path to the (USD Explorer) Kit executable
        kit_folder_path = str(carb.tokens.get_tokens_interface().resolve("${kit}"))
        kit_ext = str(carb.tokens.get_tokens_interface().resolve("${exe_ext}"))
        kit_exe_path = f"{kit_folder_path}/kit{kit_ext}"

        # Find the extension install path to locate py script
        manager = omni.kit.app.get_app().get_extension_manager()
        ext_id = manager.get_enabled_extension_id(APP_NAME)
        ext_path = manager.get_extension_path(ext_id)

        # utilize Path to handle any escape characters for cross-platform compatibility
        script_path = Path(ext_path + JT_LAUNCH_SCRIPT_PATH)

        config_json_path = Path(self.create_temp_json(file_path))

        file_path = Path(file_path)
        output_path = Path(output_path)

        args = [kit_exe_path]

        for ext_folder in carb.settings.get_settings().get("/app/exts/folders"):
            args.extend(["--ext-folder", ext_folder])
        args.extend(["--enable", "omni.kit.converter.jt_core", "--exec"])
        if platform.system() == "Windows":
            # Need the double quotes in Windows to avoid passing script_path as multiple arguments (e.g., in scenarios w/ spaces and special characters)
            args.extend(
                [
                    f'"{script_path}" --config-path "{config_json_path}" --input-path "{file_path}" --output-path "{output_path}"'
                ]
            )
        else:
            # Need the extra quotes in Linux but this breaks Windows.
            args.extend(
                [
                    f"'{script_path.as_posix()}' --config-path '{config_json_path.as_posix()}' --input-path '{file_path.as_posix()}' --output-path '{output_path.as_posix()}'"
                ]
            )

        # pass --info to kit subprocess to pick up prints
        args += ["--info"]

        # Call the script that invokes kit with JT Converter
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        queue = Queue()
        thread = Thread(target=enqueue_output, args=(process.stdout, queue), daemon=True)
        thread.start()

        def cancel_import() -> None:
            process.kill()
            carb.log_info("File Conversion cancelled by the user.")

        self._progress_dialog.set_cancel_fn(cancel_import)
        log_consumer = ProgressLogConsumer("[omni.converter.jtk_progress]")
        converter_finished = False
        converter_error_code = -1
        converter_error_msg = ""

        while process.poll() is None:
            # read line without blocking
            try:
                stdout_line: bytes = queue.get_nowait()
            except Empty:
                await omni.kit.app.get_app().next_update_async()
            else:
                stdout_line = stdout_line.decode()
                tokens = log_consumer.extract_line(stdout_line)
                if tokens[0] == ProgressStepType.BEGIN:
                    self._progress_dialog.set_step_info(tokens[1])
                elif tokens[0] == ProgressStepType.PROGRESS:
                    self._progress_dialog.set_progress_info(tokens[1], tokens[2])
                elif tokens[0] == ProgressStepType.END:
                    # we don't break out or return once we get the END token
                    # because we still need to wait for the subprocess to terminate cleanly
                    converter_finished = True
                    converter_error_code = int(tokens[1])
                    converter_error_msg = tokens[2]

        self._progress_dialog.set_cancel_fn(None)
        return [converter_error_code, converter_error_msg] if converter_finished else [process.returncode, ""]
