import asyncio
import unittest
import carb.settings
import omni.kit.app
import omni.kit.test
import omni.kit.stage_template.core

# also see kit\source\extensions\omni.kit.menu.file\python\omni\kit\menu\file\tests\test_func_templates.py as similar test
# added here for coverage

class TestNewStageTemplates(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        omni.kit.stage_template.core.register_template("empty", self.__new_stage_empty, 0)

    async def tearDown(self):
        omni.kit.stage_template.core.unregister_template("empty")

    def __new_stage_empty(self, rootname):
        pass


    async def test_stage_template_empty(self):
        await omni.kit.stage_template.core.new_stage_async(template="empty")

        # verify Empty stage
        stage =  omni.usd.get_context().get_stage()
        prim_list = [prim.GetPath().pathString for prim in stage.TraverseAll()]
        self.assertTrue(prim_list == ['/World'])


    async def test_stage_template_noname(self):
        await omni.kit.stage_template.core.new_stage_async()

        # verify Empty stage
        stage =  omni.usd.get_context().get_stage()
        prim_list = [prim.GetPath().pathString for prim in stage.TraverseAll()]
        self.assertTrue(prim_list == ['/World'])
