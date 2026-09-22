import unittest
import carb.settings
import omni.kit.test
import omni.kit.stage_template.core
from pxr import UsdGeom


class TestCommands(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._staged_called = 0
        self._stage_name = "$$_test_stage_$$"

    async def tearDown(self):
        pass

    def new_stage_test(self, rootname):
        self._staged_called += 1

    async def test_command_new_stage(self):
        # check template already exists
        item = omni.kit.stage_template.core.get_stage_template(self._stage_name)
        self.assertTrue(item == None)

        # add new template
        omni.kit.stage_template.core.register_template(self._stage_name, self.new_stage_test, 0)

        # check new template exists
        item = omni.kit.stage_template.core.get_stage_template(self._stage_name)
        self.assertTrue(item != None)
        self.assertTrue(item[0] == self._stage_name)
        self.assertTrue(item[1] == self.new_stage_test)

        # run template & check was called once
        await omni.kit.stage_template.core.new_stage_async(self._stage_name)
        self.assertTrue(self._staged_called == 1)

        stage = omni.usd.get_context().get_stage()
        settings = carb.settings.get_settings()
        default_prim_name = settings.get("/persistent/app/stage/defaultPrimName")
        rootname = f"/{default_prim_name}"

        # create cube
        cube_path = omni.usd.get_stage_next_free_path(stage, "{}/Cube".format(rootname), False)
        omni.kit.commands.execute(
            "CreatePrim",
            prim_path=cube_path,
            prim_type="Cube",
            select_new_prim=False,
            attributes={UsdGeom.Tokens.size: 100, UsdGeom.Tokens.extent: [(-50, -50, -50), (50, 50, 50)]},
        )
        prim = stage.GetPrimAtPath(cube_path)
        self.assertTrue(prim, "Cube Prim exists")

        # create sphere
        sphere_path = omni.usd.get_stage_next_free_path(stage, "{}/Sphere".format(rootname), False)
        omni.kit.commands.execute("CreatePrim", prim_path=sphere_path, prim_type="Sphere", select_new_prim=False)
        prim = stage.GetPrimAtPath(sphere_path)
        self.assertTrue(prim, "Sphere Prim exists")

        # delete template
        omni.kit.stage_template.core.unregister_template(self._stage_name)
        item = omni.kit.stage_template.core.get_stage_template(self._stage_name)
        self.assertTrue(item == None)
