import asyncio
import tempfile
from typing import Generator, TYPE_CHECKING
from contextlib import contextmanager
from pathlib import Path

import carb
import carb.settings
import carb.tokens
import shutil
from omni.metropolis.utils.config_file.util import ConfigFileUtil
from omni.metropolis.utils.unit_test.data import (
    MINIMAL_STAGE_URL,
    CHARACTER_FOLDER_URL,
)


if TYPE_CHECKING:
    from isaacsim.replicator.agent.core.simulation import SimulationManager


@contextmanager
def context_create_example_sim_manager(
    stage_path: str = MINIMAL_STAGE_URL,
) -> Generator["SimulationManager", None, None]:
    # local import because IRA is a runtime test dependency
    try:
        from isaacsim.replicator.agent.core.extension import get_ext_path, get_ext_version
        from isaacsim.replicator.agent.core.simulation import SimulationManager
        from isaacsim.replicator.agent.core.settings import AssetPaths
    except ImportError:
        raise ImportError("Failed to import isaacsim.replicator.agent.core, please add it to your test dependencies")

    settings = carb.settings.get_settings()
    default_scene_path = settings.get(AssetPaths.DEFAULT_SCENE_PATH)
    default_character_path = settings.get(AssetPaths.DEFAULT_CHARACTER_PATH)
    try:
        # temporarily set default paths to point to OMU test data
        settings.set(AssetPaths.DEFAULT_SCENE_PATH, MINIMAL_STAGE_URL)
        settings.set(AssetPaths.DEFAULT_CHARACTER_PATH, CHARACTER_FOLDER_URL)

        with tempfile.TemporaryDirectory() as temp_dir:
            ira_ext_path = Path(get_ext_path())

            # make a copy of files in IRA's test_data/ folder
            temp_dir_path = Path(temp_dir)
            shutil.copytree(ira_ext_path / "test_data", temp_dir_path, dirs_exist_ok=True)

            config_path = str(temp_dir_path / "test_config_file.yaml")
            command_path = str(temp_dir_path / "test_command.txt")
            robot_command_path = str(temp_dir_path / "test_robot_command.txt")

            assert Path(config_path).exists()
            assert Path(command_path).exists()
            assert Path(robot_command_path).exists()

            # Create config file that uses test scene and example command files
            content = {
                "scene": {"asset_path": stage_path},
                "character": {"command_file": command_path},
                "robot": {"command_file": robot_command_path},
            }
            header = "isaacsim.replicator.agent"
            version = get_ext_version()
            if not ConfigFileUtil.create_minimal_config_yaml(config_path, header, version, content):
                raise RuntimeError("Cannot create example config file. Create example SimulationManager fails.")

            sim_manager = SimulationManager()
            sim_manager.load_config_file(config_path)
            yield sim_manager
    finally:
        settings.set(AssetPaths.DEFAULT_SCENE_PATH, default_scene_path)
        settings.set(AssetPaths.DEFAULT_CHARACTER_PATH, default_character_path)


async def wait_for_simulation_set_up_done(sim, sleep=5, timeout=120):
    sub = None
    get_callback = False

    def on_event(e):
        nonlocal get_callback
        nonlocal sub
        get_callback = True
        sub = None

    sub = sim.register_set_up_simulation_done_callback(on_event)
    # Do not use 'asyncio.timeout' due to this issue:
    #   https://mail.python.org/pipermail/async-sig/2016-June/000033.html
    time = 0
    while not get_callback and time < timeout:
        await asyncio.sleep(sleep)
        carb.log_info("Waiting for simulation set up done; Timeout: {0}/{1}".format(time, timeout))
        time = time + sleep
