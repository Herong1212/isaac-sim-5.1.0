import asyncio
import unittest
import carb.settings
import omni.kit.app
import omni.kit.test
import omni.kit.stage_templates

# also see kit\source\extensions\omni.kit.menu.file\python\omni\kit\menu\file\tests\test_func_templates.py as simular test
# added here for coverage

class TestNewStageTemplates(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_stage_template_empty(self):
        await omni.kit.stage_templates.new_stage_async(template="empty")

        # verify Empty stage
        stage =  omni.usd.get_context().get_stage()
        prim_list = [prim.GetPath().pathString for prim in stage.TraverseAll()]
        self.assertTrue(prim_list == ['/World'])


    async def test_stage_template_sunlight(self):
        await omni.kit.stage_templates.new_stage_async(template="sunlight")

        # verify Sunlight stage
        stage =  omni.usd.get_context().get_stage()
        prim_list = [prim.GetPath().pathString for prim in stage.TraverseAll()]
        self.assertTrue(prim_list == ['/World', '/Environment', '/Environment/defaultLight'])

    async def test_stage_template_default_stage(self):
        await omni.kit.stage_templates.new_stage_async(template="default stage")

        # verify Default stage
        stage =  omni.usd.get_context().get_stage()
        prim_list = [prim.GetPath().pathString for prim in stage.TraverseAll()]
        self.assertTrue(set(prim_list) == set([
            '/World', '/Environment', '/Environment/Sky',
            '/Environment/DistantLight', '/Environment/Looks',
            '/Environment/Looks/Grid', '/Environment/Looks/Grid/Shader',
            '/Environment/ground', '/Environment/groundCollider']), prim_list)


    async def test_stage_template_noname(self):
        await omni.kit.stage_templates.new_stage_async()

        # verify Empty stage
        stage =  omni.usd.get_context().get_stage()
        prim_list = [prim.GetPath().pathString for prim in stage.TraverseAll()]
        self.assertTrue(prim_list == ['/World'])
