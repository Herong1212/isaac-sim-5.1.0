from omni.physics.stageupdate import get_physics_stage_update_node_interface
import omni.kit.test
import carb
import omni.timeline


class PhysicsStageUpdateNodeStage(omni.kit.test.AsyncTestCase):

    async def test_stage_update_attached_node(self):

        self.assertTrue(get_physics_stage_update_node_interface().is_node_attached())


    async def test_stage_update_detached_node(self):


        get_physics_stage_update_node_interface().detach_node()

        self.assertTrue(not get_physics_stage_update_node_interface().is_node_attached())

        get_physics_stage_update_node_interface().attach_node()

        self.assertTrue(get_physics_stage_update_node_interface().is_node_attached())