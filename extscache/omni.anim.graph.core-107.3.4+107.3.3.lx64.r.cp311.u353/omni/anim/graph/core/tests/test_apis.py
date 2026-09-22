import carb
import omni.anim.graph.core as ag
import omni.kit.commands

from .base_unit_test import BaseUnitTest

SAMPLES_PATH = "https://omniverse-content-staging.s3.us-west-2.amazonaws.com/Assets/AnimGraph/106.2/Test/Graph/"


class TestApis(BaseUnitTest):
    async def test_get_character(self):
        await self.load_stage(self._usd_data_dir, "VisualTest/blend.usda")
        await self.play()

        c = ag.get_character("/World/CharacterDoNotExist")
        self.assertTrue(c is None)

        c = ag.get_character("/World/Character")
        self.assertTrue(c is not None)

    async def test_get_characters(self):
        await self.load_stage(self._usd_data_dir, "VisualTest/blend_instancing.usda")
        await self.play()

        character_count = ag.get_character_count()
        self.assertTrue(character_count == 3)

        characters = ag.get_characters()
        self.assertTrue(character_count == len(characters))
        for c in characters:
            self.assertTrue(c is not None)

    async def test_get_set_variable(self):
        await self.load_stage(self._usd_data_dir, "VisualTest/look_at_ik.usda")
        await self.play()

        c = ag.get_character("/World/Character")

        c.set_variable("BlendWeight", 0.75)
        blend_weight = c.get_variable("BlendWeight")
        self.assertTrue(len(blend_weight) == 1)
        self.assertTrue(blend_weight[0] == 0.75)

        test_target_pos = carb.Float3(0, 200, 150)
        c.set_variable("TargetPosition", test_target_pos)
        target_pos = c.get_variable("TargetPosition")
        self.assertTrue(len(target_pos) == 1)
        self.assertFloat3Equals(target_pos[0], test_target_pos)

    # async def test_get_set_variable_array(self):
    #    """# todo: mbuttner fix me.""""
    #     await self.load_stage(SAMPLES_PATH, "path-points.usda")
    #     await self.play()

    #     c = ag.get_character("/World/Character")

    #     path_points = c.get_variable("PathPoints")
    #     self.assertTrue(len(path_points) == 5)

    #     self.assertFloat3Equals(path_points[0], carb.Float3(0, 0, 0))
    #     self.assertFloat3Equals(path_points[1], carb.Float3(0, 0, 200))
    #     self.assertFloat3Equals(path_points[2], carb.Float3(600, 0, 0))
    #     self.assertFloat3Equals(path_points[3], carb.Float3(300, 0, -300))
    #     self.assertFloat3Equals(path_points[4], carb.Float3(0, 0, 0))

    #     test_path_points = [
    #         carb.Float3(1, 1, 1),
    #         carb.Float3(1, 1, 201),
    #         carb.Float3(601, 1, 1),
    #         carb.Float3(301, 1, -301),
    #         carb.Float3(1, 1, 1)
    #     ]
    #     c.set_variable("PathPoints", test_path_points)

    #     path_points = c.get_variable("PathPoints")
    #     self.assertFloat3Equals(path_points[0], test_path_points[0])
    #     self.assertFloat3Equals(path_points[1], test_path_points[1])
    #     self.assertFloat3Equals(path_points[2], test_path_points[2])
    #     self.assertFloat3Equals(path_points[3], test_path_points[3])
    #     self.assertFloat3Equals(path_points[4], test_path_points[4])

    async def test_set_get_world_transform(self):
        await self.load_stage(self._usd_data_dir, "VisualTest/blend.usda")
        await self.play()

        c = ag.get_character("/World/Character")
        test_pos = carb.Float3(100, 5, 100)
        test_rot = carb.Float4(0.0, 0.7071, 0.0, 0.0)
        c.set_world_transform(test_pos, test_rot)

        pos = carb.Float3(0.0, 0.0, 0.0)
        rot = carb.Float4(0.0, 0.0, 0.0, 0.0)
        c.get_world_transform(pos, rot)
        self.assertFloat3Equals(pos, test_pos)
        self.assertFloat4Equals(rot, test_rot)

    async def test_get_joint_transform(self):
        await self.load_stage(self._usd_data_dir, "VisualTest/blend.usda")
        await self.play()
        await self.step_frames(24)

        c = ag.get_character("/World/Character")

        pos = carb.Float3(0.0, 0.0, 0.0)
        rot = carb.Float4(0.0, 0.0, 0.0, 0.0)
        c.get_joint_transform("R_Ankle", pos, rot)
        #print(f"R_Ankle:pos({pos.x},{pos.y},{pos.z}),rot({rot.x},{rot.y},{rot.z},{rot.w})")
        # NOTE: the VisualTest version of this file runs at 24 fps, the old S3 test at 60, so the numbers changed.
        self.assertFloat3Equals(pos, carb.Float3(-9.121687889099121,12.85535717010498,13.868141174316406))
        self.assertFloat4Equals(rot, carb.Float4(-0.04510693997144699,-0.6970890164375305,-0.218546062707901,-0.6814037561416626))

    async def test_get_joint_local_transforms(self):
        await self.load_stage(self._usd_data_dir, "VisualTest/blend.usda")
        await self.play()
        await self.step_frames(24)

        c = ag.get_character("/World/Character")

        pos = ag.vector_float3()
        rot = ag.vector_float4()
        c.get_joint_local_transforms(pos, rot)

        self.assertFloat3Equals(pos[4], carb.Float3(-44.377662658691406, 0.00022197564248926938, -2.2761529180570506e-05))
        self.assertFloat4Equals(rot[4], carb.Float4(0.05643419176340103, -0.060178060084581375, 0.7699133157730103, -0.6328003406524658))

        pos2, rot2 = c.get_joint_local_transforms()
        for i in range(len(pos)):
            self.assertFloat3Equals(pos[i], pos2[i])
            self.assertFloat4Equals(rot[i], rot2[i])

    async def test_get_blend_shape_weights(self):
        # TODO: prepare blendshape example usd file
        await self.load_stage(self._usd_data_dir, "VisualTest/blend.usda")
        await self.play()
        await self.step_frames(24)

        c = ag.get_character("/World/Character")

        self.assertTrue(0.0 == c.get_blend_shape_weight('Key_1'))

        weights = ag.vector_float()
        c.get_blend_shape_weights(weights)
        self.assertTrue(0 == len(weights))

        weights = c.get_blend_shape_weights()
        self.assertTrue(0 == len(weights))
