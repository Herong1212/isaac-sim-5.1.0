import logging, carb
from .utility.interface import *
from .utility.metadata import *

from .description import parse
from .description.parse import *
from .mutables.scene_dev import *
from .utility.scene import iro_environment_setup

# for global debug, before publishing turn off
DBG_MODE = False


async def on_simulate_dev(
    extension,
    description_path,
    progress_bar=None,
    windowless=False,
    data_in=None,
    data_out=None,
    images_root=None,
    assets_root=None,
    binary_obj_det=None,
):
    with PROFILE("oro simulate"):
        function_name = "on_simulate"
        logging.info(f"{EXTENSION_NAME} [{function_name}]: entry")
        return_code = 0
        try:
            description_paths = get_config_path_or_folder(
                description_path
            )  # a folder, or a path, or a name in config folder
            if isinstance(description_paths, str):
                description_paths = [description_paths]
            with CHECK("simulate"):
                CLEAR()
                for path in description_paths:
                    with CHECK(f"simulate {path}"):
                        global_message(f"simulate {path}")
                        scene = Scene_DEV(binary_obj_det, progress_bar)
                        await parse.simulate(path, scene)

        except Exception as e:
            logging.error(f"simulation terminated, error at: {e}")
            if DBG_MODE:
                raise e
            return_code = 1

        if windowless:
            logging.info(f"{EXTENSION_NAME} [{function_name}]: shutting down extension.")
            carb.settings.get_settings().set("/app/fastShutdown", True)
            await omni.usd.get_context().close_stage_async()
            omni.kit.app.get_app().post_quit(return_code=return_code)


async def on_init_scene_randomization(extension, description_path, tweak=None):
    try:
        clean_up_embedded(extension)
        iro_environment_setup(extension)
        if not get_prim("/World"):
            create_xform_prim("/World")
        if not get_prim("/World/Shapes"):
            create_xform_prim("/World/Shapes")
        await wait_frames()

        description_path = get_config_path_or_folder(description_path)
        if not isinstance(description_path, str):
            error(f"In embedded mode, {description_path} should point to a file")

        scene = Scene_DEV()
        config = read_yaml_recursive(description_path)
        if tweak is not None:
            config.update(tweak)
        description = Description(config, scene)
        description.initialize(9999999)

        metadata = resolve_scene(description, True)
        await scene.initialize_embedded(metadata)
        extension.embedded_scene = scene
        extension.embedded_description = description
        extension.embedded_index = 0
        extension.seed = 0
        # clear IRO created assets in the last run
    except Exception as e:
        logging.error(f"simulation terminated, error at: {e}")
        if DBG_MODE:
            raise e
        return_code = 1


async def on_randomize_scene(extension, seed=None):
    seed = extension.embedded_description.seed if seed is None else seed
    extension.embedded_description.initialize(extension.embedded_index, seed)
    metadata = resolve_scene(extension.embedded_description)
    await extension.embedded_scene.step_embedded(metadata, extension.embedded_index, seed)
    extension.embedded_index += 1
    extension.embedded_description.seed += 1


def clean_up_embedded(extension):
    if extension.embedded_scene is not None:
        for mutable in extension.embedded_scene.mutables.values():
            if mutable.prim:
                get_stage().RemovePrim(mutable.prim.GetPath())

            # DEV
            if hasattr(mutable, "animation") and mutable.animation is not None:
                get_stage().RemovePrim(mutable.animation.GetPath())
