import omni.kit.undo
import omni.kit.commands
import omni.timeline
import omni.usd
import omni.anim.graph.core
from pxr import Sdf
import AnimGraphSchema
from .base_unit_test import BaseUnitTest
from pathlib import Path


class TestCommands(BaseUnitTest):
    async def test_create_animation_graph_command(self):
        await self.load_stage(self.usd_data_dir, "TestCommands.usda")
        self._stage = self._context.get_stage()
        omni.kit.commands.execute("CreateAnimationGraphCommand", path=Sdf.Path("/World/TestAnimationGraph"), skeleton_path=Sdf.Path("/World/TestSkeleton"))
        prim = self._stage.GetPrimAtPath("/World/TestAnimationGraph")
        self.assertTrue(prim.IsValid())
        omni.kit.undo.undo()
        self.assertFalse(prim.IsValid())

    async def test_applyanimation_graph_api_command(self):
        await self.load_stage(self.usd_data_dir, "TestApplyGraph.usda")
        self._stage = self._context.get_stage()
        omni.kit.commands.execute(
            "ApplyAnimationGraphAPICommand",
            paths=[Sdf.Path("/World/TestSkeleton")],
            animation_graph_path=Sdf.Path("/World/TestAnimationGraph")
        )
        prim = self._stage.GetPrimAtPath("/World/TestSkeleton")
        self.assertTrue(prim.HasAPI(AnimGraphSchema.AnimationGraphAPI))
        omni.kit.undo.undo()
        self.assertFalse(prim.HasAPI(AnimGraphSchema.AnimationGraphAPI))

    async def test_remove_animation_graph_api_command(self):
        await self.load_stage(self.usd_data_dir, "TestApplyGraph.usda")
        self._stage = self._context.get_stage()
        omni.kit.commands.execute(
            "ApplyAnimationGraphAPICommand",
            paths=[Sdf.Path("/World/TestSkeleton")],
            animation_graph_path=Sdf.Path("/World/TestAnimationGraph")
        )
        prim = self._stage.GetPrimAtPath("/World/TestSkeleton")
        self.assertTrue(prim.HasAPI(AnimGraphSchema.AnimationGraphAPI))
        omni.kit.commands.execute(
            "RemoveAnimationGraphAPICommand",
            paths=[Sdf.Path("/World/TestSkeleton")]
        )
        self.assertFalse(prim.HasAPI(AnimGraphSchema.AnimationGraphAPI))
        omni.kit.undo.undo()
        self.assertTrue(prim.HasAPI(AnimGraphSchema.AnimationGraphAPI))

    async def test_rename_variable_attribute_command(self):
        await self.load_stage(self.usd_data_dir, "TestApplyGraph.usda")
        self._stage = self._context.get_stage()
        prim = self._stage.GetPrimAtPath("/World/TestAnimationGraph")
        old_attr_name = "anim:graph:variable:TestVariable"
        new_attr_name = "anim:graph:variable:RenamedVariable"
        omni.kit.commands.execute(
            "RenameAnimationGraphVariableAttributeCommand",
            prim=prim,
            old_attr_name=old_attr_name,
            new_attr_name=new_attr_name
        )
        # TODO: can we test references within the graph too?
        self.assertFalse(prim.HasAttribute(old_attr_name))
        self.assertTrue(prim.HasAttribute(new_attr_name))
        omni.kit.undo.undo()
        self.assertTrue(prim.HasAttribute(old_attr_name))
        self.assertFalse(prim.HasAttribute(new_attr_name))

    async def test_rename_variable_attribute_command2(self):
        await self.load_stage(self.usd_data_dir, "TestApplyGraph.usda")
        self._stage = self._context.get_stage()
        prim = self._stage.GetPrimAtPath("/World/TestAnimationGraph")
        attr_name = "anim:graph:variable:TestVariable"
        omni.kit.commands.execute(
            "SetAnimationGraphVariableAttributeTypeCommand",
            prim=prim,
            attr_name=attr_name,
            new_type=Sdf.ValueTypeNames.String,
            new_value="Test"
        )
        # TODO: can we test references within the graph too?
        attr = prim.GetAttribute(attr_name)
        self.assertEqual(attr.GetTypeName(), Sdf.ValueTypeNames.String)
        self.assertEqual(attr.Get(), "Test")
        omni.kit.undo.undo()
        attr = prim.GetAttribute(attr_name)
        self.assertEqual(attr.GetTypeName(), Sdf.ValueTypeNames.Float)
        self.assertEqual(attr.Get(), 0.0)

    async def test_set_variable_description_command(self):
        await self.load_stage(self.usd_data_dir, "TestApplyGraph.usda")
        self._stage = self._context.get_stage()
        prim = self._stage.GetPrimAtPath("/World/TestAnimationGraph")
        attr_name = "anim:graph:variable:TestVariable"
        omni.kit.commands.execute(
            "SetAnimationGraphVariableDescriptionCommand",
            prim=prim,
            attr_name=attr_name,
            description="Test Description",
        )
        attr = prim.GetAttribute(attr_name)
        self.assertEqual(attr.GetDocumentation(), "Test Description")
        omni.kit.undo.undo()
        attr = prim.GetAttribute(attr_name)
        self.assertEqual(attr.GetDocumentation(), "")
