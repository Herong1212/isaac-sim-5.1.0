from enum import IntFlag, auto
import carb
import carb.tokens
import omni.kit.app
import omni.usd
from pathlib import Path
from .data import MINIMAL_STAGE_URL, NAVMESH_AREA_TEST_STAGE_URL


class StageSetupOptions(IntFlag):
    NONE = auto()
    BAKE_NAV_MESH = auto()


class TestStage:
    def __init__(self, stage_path: str | None = None, stage_setup_opts: StageSetupOptions = StageSetupOptions.NONE):
        self.stage_path = stage_path
        self.stage_setup_opts = stage_setup_opts

    async def __aenter__(self):
        ctx = omni.usd.get_context()
        while not ctx.can_open_stage():
            await omni.kit.app.get_app().next_update_async()

        if self.stage_path is not None:
            self.res, msg = await ctx.open_stage_async(self.stage_path)
        else:
            self.res, msg = await ctx.new_stage_async()
        if not self.res:
            carb.log_error(f"Failed to create a new stage: {msg}")
        else:
            await omni.kit.app.get_app().next_update_async()

        if StageSetupOptions.BAKE_NAV_MESH in self.stage_setup_opts:
            import omni.anim.navigation.core as nav  # noqa

            inav = nav.acquire_interface()
            inav.start_navmesh_baking_and_wait()
            if inav.get_navmesh() is None:
                carb.log_error(
                    "NavMesh building failed. Please check whether the stage has a valid NavmeshVolume. "
                    "Will not load assets to scene."
                )
                return

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self.res:
            return
        ctx = omni.usd.get_context()

        # ---- ugly fix for https://jirasw.nvidia.com/browse/METROPERF-300 ----
        try:
            import gc  # noqa

            from omni.anim.graph.core import VariablesService  # noqa

            for obj in gc.get_objects():
                if isinstance(obj, VariablesService) and hasattr(obj, "_pending_dirty_handler"):
                    await obj._pending_dirty_handler()
        except:
            pass
        # ---------------------------------------------------------------------

        while not ctx.can_close_stage():
            await omni.kit.app.get_app().next_update_async()
        await ctx.close_stage_async()
        await omni.kit.app.get_app().next_update_async()
