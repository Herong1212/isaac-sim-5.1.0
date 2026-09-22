import carb
import omni.kit
import omni.kit.test
from omni.kit.test_suite.helpers import wait_stage_loading
import omni.usd
from pxr import Sdf, Usd, UsdGeom, UsdUtils
from pathlib import Path
import asyncio
import os
import time
from typing import List

from .usda_write import UsdaFile
from .usda_navmesh import usda_navmesh_write_polygons, usda_navmesh_write_lines, usda_navmesh_write_path, UsdaNavMeshConfig
from .usda_read import UsdaReader

import omni.anim.navigation.core as nav


class BaseUnitTest(omni.kit.test.AsyncTestCase):

    async def setUp(self):
        self._ext_path = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
        self._tests_data_path = self._ext_path.joinpath(Path("data/tests/usd"))
        self._tests_golden_data_path = self._ext_path.joinpath(Path("data/tests/golden"))
        self._test_outputs_path = Path(omni.kit.test.get_test_output_path())

        self._inav = nav.acquire_interface()
        self._context = omni.usd.get_context()
        self._selection = self._context.get_selection()
        self._settings = carb.settings.get_settings()
        self._stage = None
        self._stage_loaded_url = None
        self._inav = nav.acquire_interface()
        self._event_stream = self._inav.get_navmesh_event_stream()
        self._navmesh = None

    async def tearDown(self):
        self._tests_data_path = None
        self._tests_golden_data_path = None
        self._test_outputs_path = None
        self._context = None
        self._stage = None
        self._stage_loaded_url = None
        self._events_stream = None
        self._navmesh = None

    @property
    def tests_data_path(self) -> str:
        return self._tests_data_path.as_posix()

    @property
    def tests_golden_data_path(self) -> str:
        return self._tests_golden_data_path.as_posix()

    @property
    def tests_output_path(self) -> str:
        return self._test_outputs_path.as_posix()

    @property
    def settings(self):
        return self._settings

    @property
    def usd_context(self):
        return self._context

    @property
    def stage(self):
        return self._stage

    @property
    def default_prim_path_str(self) -> str:
        if self._stage.HasDefaultPrim():
            return self._stage.GetDefaultPrim().GetPath().pathString
        else:
            return Sdf.Path.absoluteRootPath.pathString

    @property
    def inav(self):
        return self._inav

    @property
    def event_stream(self) -> carb.events.IEventStream:
        return self._event_stream

    async def new_stage(self):
        await self._context.new_stage_async()
        stage_id = self._context.get_stage_id()
        self._stage = UsdUtils.StageCache.Get().Find(Usd.StageCache.Id.FromLongInt(stage_id))
        default_path = "/World"
        UsdGeom.Xform.Define(self._stage, default_path)
        self._stage.SetDefaultPrim(self._stage.GetPrimAtPath(default_path))
        await wait_stage_loading(timeout=10000)
        self._usda_write_config = self.make_usda_write_config()

    async def load_stage(self, base_url, stage_name):
        self._loaded_stage_url = os.path.join(base_url, stage_name)
        print(f"Loading stage:{self._loaded_stage_url}")
        result = None
        (result, err) = await self._context.open_stage_async(self._loaded_stage_url, omni.usd.UsdContextInitialLoadSet.LOAD_ALL)
        await wait_stage_loading(timeout=10000)
        stage_id = self._context.get_stage_id()
        self._stage = UsdUtils.StageCache.Get().Find(Usd.StageCache.Id.FromLongInt(stage_id))
        self.assertTrue(result)
        self._usda_write_config = self.make_usda_write_config()
        return result

    async def next_navmesh_event_async(self, events: list):
        order = omni.kit.app.EVENT_ORDER_DEFAULT
        f = asyncio.Future()

        def on_event(e: carb.events.IEvent):

            if e.type in events:
                events.remove(e.type)
            if not events and not f.done():
                f.set_result((e.type, e.payload.get_dict()))

        sub = self.event_stream.create_subscription_to_pop(on_event, name="navmesh unittest", order=order)

        return await f

    async def bake_navmesh_and_wait(self, events=None) -> nav.INavMesh:
        if not events:
            events = [nav.EVENT_TYPE_NAVMESH_UPDATED]

        self.inav.start_navmesh_baking()
        print("Baking navmesh started...")

        await self.next_navmesh_event_async(events)

        self._navmesh = self.inav.get_navmesh()
        if self._navmesh:
            print("Baking navmesh succeeded.")
        else:
            print("Baking navmesh failed.")
        return self._navmesh

    def clear_navmesh_cache(self):
        self.inav.clear_cache_dir()

    def get_output_usda_and_gold_usda_file_paths(self, ext: str, test_case: str = ""):
        suffix = "" if test_case == "" else f"_{test_case}"
        test_name = f"{self._testMethodName}{suffix}"
        test_file_name = Path(self._loaded_stage_url).stem + f".{test_name}{ext}"
        output_file_path = Path(self.tests_output_path).joinpath(test_file_name)
        golden_file_path = Path(self.tests_golden_data_path).joinpath(test_file_name)
        return output_file_path, golden_file_path

    def compare_output_usda_and_gold_usda_files(self, ext: str, test_case: str = ""):
        output_usda_path, gold_usda_path = self.get_output_usda_and_gold_usda_file_paths(ext, test_case)
        if not output_usda_path.exists():
            self.fail(f"Failed to produce output usda file : {output_usda_path}")
        if not gold_usda_path.exists():
            self.fail(f"Failed golden test data missing: {gold_usda_path}")

        def normalize_newlines(text):
            return text.replace('\r\n', '\n').replace('\r', '\n')

        def compare_files(file1, file2):
            with open(output_usda_path, 'r') as f1, open(gold_usda_path, 'r') as f2:
                content1 = normalize_newlines(f1.read())
                content2 = normalize_newlines(f2.read())
                return content1 == content2

        success = compare_files(output_usda_path, gold_usda_path)

        if not success:
            print(f"Failed gold diff for:\n- {output_usda_path}\n- {gold_usda_path}")
        self.assertTrue(success)

    def compare_navmesh_signature(self, ext: str, test_case: str = ""):
        output_usda_path, gold_usda_path = self.get_output_usda_and_gold_usda_file_paths(ext, test_case)
        success = False
        with UsdaReader(output_usda_path) as out_usda:
            out_signature = out_usda.get_signature()
            print(out_signature)
            with UsdaReader(gold_usda_path) as gold_usda:
                gold_signture = gold_usda.get_signature()
                print(gold_signture)
                success = out_signature == gold_signture
        self.assertTrue(success)

    def compare_navmesh_paths(self, ext: str, test_case: str = ""):
        output_usda_path, gold_usda_path = self.get_output_usda_and_gold_usda_file_paths(ext, test_case)
        with UsdaReader(output_usda_path) as out_usda:
            out_points = out_usda.get_path_points()
            with UsdaReader(gold_usda_path) as gold_usda:
                gold_points = gold_usda.get_path_points()
                self.assertAlmostEqual(out_points[0][0], gold_points[0][0], delta=0.001, msg="NavMeshPath start point x")
                self.assertAlmostEqual(out_points[0][1], gold_points[0][1], delta=0.001, msg="NavMeshPath start point y")
                self.assertAlmostEqual(out_points[0][2], gold_points[0][2], delta=0.001, msg="NavMeshPath start point z")
                self.assertAlmostEqual(out_points[-1][0], gold_points[-1][0], delta=0.001, msg="NavMeshPath end point x")
                self.assertAlmostEqual(out_points[-1][1], gold_points[-1][1], delta=0.001, msg="NavMeshPath end point y")
                self.assertAlmostEqual(out_points[-1][2], gold_points[-1][2], delta=0.001, msg="NavMeshPath end point z")

    def output_current_navmesh(self, usda: UsdaFile):
        with usda.new_xform("NavMesh"):
            usda.write_signature(self._navmesh.get_mesh_signature())
            usda_navmesh_write_polygons(usda, self._navmesh, "", self._inav.get_area_colors(), self._inav.get_area_names())
            # with usda.new_xform("Debug Lines"):
            #    usda_navmesh_write_lines(usda, self._navmesh, "Line")

    async def save_and_compare_navmesh(self, test_case: str = ""):
        self.assertTrue(self._navmesh)
        ext = ".navmesh.usda"
        output_path, gold_path = self.get_output_usda_and_gold_usda_file_paths(ext, test_case)
        with UsdaFile(output_path, self._usda_write_config) as usda:
            self.output_current_navmesh(usda)
        self.compare_navmesh_signature(ext, test_case)

    async def save_and_compare_navmesh_with_paths(self, navmesh_paths: List[nav.INavMeshPath], test_case: str = ""):
        self.assertTrue(self._navmesh)
        ext = ".navmesh_paths.usda"
        output_path, gold_path = self.get_output_usda_and_gold_usda_file_paths(ext, test_case)
        with UsdaFile(output_path, self._usda_write_config) as usda:
            self.output_current_navmesh(usda)
            with usda.new_xform("Paths"):
                for p in navmesh_paths:
                    usda_navmesh_write_path(usda, p, "Path")

        self.compare_navmesh_paths(ext, test_case)

    def make_usda_write_config(self):
        x = (1.0, 0.0, 0.0)
        y = (0.0, 1.0, 0.0)
        z = (0.0, 0.0, 1.0)
        up = UsdGeom.GetStageUpAxis(self._stage)
        up_axis = z
        forward_axis = y
        if up == UsdGeom.Tokens.x:
            up_axis = x
            forward_axis = z
        elif up == UsdGeom.Tokens.y:
            up_axis = y
            forward_axis = z
        else:
            assert up == UsdGeom.Tokens.z
        agent_max_radius = self.settings.get(nav.NavMeshSettings.AGENT_MAX_RADIUS_SETTING_PATH)
        agent_min_height = self.settings.get(nav.NavMeshSettings.AGENT_MIN_HEIGHT_SETTING_PATH)
        cfg = UsdaNavMeshConfig.default_config(agent_max_radius, agent_min_height)
        cfg['up_axis'] = up_axis
        cfg['forward_axis'] = forward_axis
        return cfg
