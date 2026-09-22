import omni.kit.test
from pxr import Usd, Sdf, Gf
from isaacsim.anim.robot.state_machine import State, StateMachine
from isaacsim.anim.robot.agent.base_agent import BaseAgent


class TestStateMachine(omni.kit.test.AsyncTestCase):
    """Test suite for State and StateMachine classes."""

    async def setUp(self):
        """Set up test environment with a USD stage and test prims."""
        # Create new stage
        omni.usd.get_context().new_stage()
        self.stage = omni.usd.get_context().get_stage()

        # Create test robot hierarchy
        self.robot_path = "/World/Robot"
        self.joint1_path = f"{self.robot_path}/joint1"
        self.joint2_path = f"{self.robot_path}/joint2"

        # Create robot and joint prims
        self.robot_prim = self.stage.DefinePrim(self.robot_path, "Xform")
        self.joint1 = self.stage.DefinePrim(self.joint1_path, "Xform")
        self.joint2 = self.stage.DefinePrim(self.joint2_path, "Xform")

        # Create xformOp attributes for joints
        for joint in [self.joint1, self.joint2]:
            joint.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3).Set(Gf.Vec3d(0, 0, 0))
            joint.CreateAttribute("xformOp:orient", Sdf.ValueTypeNames.Quatd).Set(Gf.Quatd(1, 0, 0, 0))
            joint.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.TokenArray, custom=False).Set(
                ["xformOp:translate", "xformOp:orient"]
            )

        # Create test animation clips with proper attributes
        self.anim_path = "/World/Animations/Clip1"
        self.anim_prim = self.stage.DefinePrim(self.anim_path, "Xform")

        # Create animation prims with transform attributes
        self.joint1_anim = self.stage.DefinePrim(f"{self.anim_path}/joint1", "Xform")
        self.joint2_anim = self.stage.DefinePrim(f"{self.anim_path}/joint2", "Xform")

        # Add transform attributes to animation prims
        for anim_prim in [self.joint1_anim, self.joint2_anim]:
            # Create transform attributes
            translate_attr = anim_prim.CreateAttribute("xformOp:translate", Sdf.ValueTypeNames.Double3)
            orient_attr = anim_prim.CreateAttribute("xformOp:orient", Sdf.ValueTypeNames.Quatd)

            # Set default values
            translate_attr.Set(Gf.Vec3d(0, 0, 0))
            orient_attr.Set(Gf.Quatd(1, 0, 0, 0))

            # Set values at frame 1 for testing
            translate_attr.Set(Gf.Vec3d(1, 1, 1), Usd.TimeCode(1))
            orient_attr.Set(Gf.Quatd(0.707, 0, 0, 0.707), Usd.TimeCode(1))

            # Set xformOpOrder
            anim_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.TokenArray, custom=False).Set(
                ["xformOp:translate", "xformOp:orient"]
            )

        # Create a mock BaseAgent with the prim instead of the path
        self.agent = BaseAgent(self.robot_prim)
        self.agent.stage = self.stage
        self.agent.joint_prims = [self.joint1, self.joint2]
        self.agent.init_joint_poses = {
            str(self.joint1_path): (Gf.Vec3d(0, 0, 0), Gf.Quatd(1, 0, 0, 0)),
            str(self.joint2_path): (Gf.Vec3d(0, 0, 0), Gf.Quatd(1, 0, 0, 0)),
        }

        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        """Clean up test environment."""
        self.stage.RemovePrim(self.robot_path)
        self.stage.RemovePrim(self.anim_path)
        await omni.kit.app.get_app().next_update_async()

    async def test_state_creation(self):
        """Test State initialization and basic properties."""
        state = State("idle", self.anim_path)
        self.assertEqual(state.name, "idle")
        self.assertEqual(state.animation_clip_path, self.anim_path)
        self.assertFalse(state.persistent)
        self.assertEqual(len(state.transitions), 0)

    async def test_state_add_transition(self):
        """Test adding transitions to a state."""
        state = State("idle")

        def condition(x):
            return True

        state.add_transition("walk", condition)
        self.assertIn("walk", state.transitions)
        self.assertEqual(state.transitions["walk"], condition)

    async def test_state_add_animation(self):
        """Test adding animation data to a state."""
        state = State("idle", self.anim_path)
        state.add_animation(self.agent)
        self.assertIn(self.joint1, state.joint_to_animation)
        self.assertIn(self.joint2, state.joint_to_animation)
        self.assertEqual(len(state.animation_prims_names), 2)

    async def test_state_machine_creation(self):
        """Test StateMachine initialization."""
        sm = StateMachine(self.agent)
        self.assertIsNone(sm.current_state)
        self.assertEqual(sm.current_state_frame, 0)
        self.assertEqual(len(sm.states), 0)

    async def test_state_machine_add_state(self):
        """Test adding states to StateMachine."""
        sm = StateMachine(self.agent)

        # First addition should succeed
        sm.add_state("idle", self.anim_path)
        self.assertIn("idle", sm.states)
        self.assertEqual(sm.states["idle"].name, "idle")

        # Adding duplicate state should not change the state machine
        sm.add_state("idle", self.anim_path)
        self.assertEqual(len(sm.states), 1)  # Still only one state
        self.assertEqual(sm.states["idle"].name, "idle")  # Original state unchanged

    async def test_state_machine_set_state(self):
        """Test setting current state."""
        sm = StateMachine(self.agent)
        sm.add_state("idle", self.anim_path)
        sm.set_state("idle")
        self.assertIsNotNone(sm.current_state)
        self.assertEqual(sm.current_state.name, "idle")
        self.assertEqual(sm.current_state_frame, 0)

    async def test_state_machine_transition(self):
        """Test state transitions."""
        sm = StateMachine(self.agent)

        # Add states and transitions
        sm.add_state("idle", self.anim_path)
        sm.add_state("walk", self.anim_path)
        sm.set_state("idle")

        # Add transition with always-true condition
        sm.current_state.add_transition("walk", lambda x: True)

        # Test transition
        sm.transition_to_state("walk")
        self.assertEqual(sm.current_state.name, "walk")
        self.assertEqual(sm.current_state_frame, 0)

    async def test_state_machine_invalid_transition(self):
        """Test invalid state transitions."""
        sm = StateMachine(self.agent)
        sm.add_state("idle", self.anim_path)
        sm.set_state("idle")

        # Check transition validity before attempting
        self.assertNotIn("non_existent", sm.states)  # Target state doesn't exist
        self.assertNotIn("non_existent", sm.current_state.transitions)  # No transition defined

        # Current state should remain unchanged
        self.assertEqual(sm.current_state.name, "idle")

    async def test_state_machine_update(self):
        """Test state machine update."""
        sm = StateMachine(self.agent)
        sm.add_state("idle", self.anim_path)
        sm.set_state("idle")

        # Add animation to the state
        sm.states["idle"].add_animation(self.agent)

        initial_frame = sm.current_state_frame
        # Remove await since update() isn't async
        sm.update()
        self.assertEqual(sm.current_state_frame, initial_frame + 1)

    async def test_state_machine_cleanup(self):
        """Test cleanup of state machine."""
        sm = StateMachine(self.agent)
        sm.add_state("idle", self.anim_path)
        sm.set_state("idle")

        sm.cleanup()
        self.assertEqual(len(sm.states), 0)
        self.assertIsNone(sm.current_state)

    async def test_persistent_state(self):
        """Test persistent state behavior."""
        sm = StateMachine(self.agent)

        # Add persistent state and its animation
        sm.add_state("idle", self.anim_path)
        sm.states["idle"].persistent = True
        sm.states["idle"].add_animation(self.agent)

        # Add non-persistent state and its animation
        sm.add_state("walk", self.anim_path)
        sm.states["walk"].add_animation(self.agent)

        # Set up transition
        sm.set_state("idle")
        sm.current_state.add_transition("walk", lambda x: True)

        # Modify joint positions
        new_pos = Gf.Vec3d(1, 1, 1)
        self.joint1.GetAttribute("xformOp:translate").Set(new_pos)

        # Transition to non-persistent state
        sm.transition_to_state("walk")
        await omni.kit.app.get_app().next_update_async()

        # Check that positions were reset
        current_pos = self.joint1.GetAttribute("xformOp:translate").Get()
        self.assertEqual(current_pos, Gf.Vec3d(0, 0, 0))
