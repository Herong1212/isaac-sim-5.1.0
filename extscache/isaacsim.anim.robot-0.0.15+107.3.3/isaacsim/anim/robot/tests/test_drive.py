import omni.kit.test
from pxr import Gf
from omni.metropolis.utils.math_util import MathUtil

from isaacsim.anim.robot.drive import OmniDirectionalDrive, DifferentialDrive


class TestAttribute:
    def __init__(self, initial_value):
        self._value = initial_value

    def Get(self):
        return self._value

    def Set(self, value):
        self._value = value


class TestPrim:
    def __init__(self, translate_value, orient_value):
        self._translate = TestAttribute(translate_value)
        self._orient = TestAttribute(orient_value)

    def GetAttribute(self, attr_name):
        if attr_name == "xformOp:translate":
            return self._translate
        if attr_name == "xformOp:orient":
            return self._orient
        return None


class TestAgent:
    def __init__(self, translate_value, orient_value):
        self.prim = TestPrim(translate_value, orient_value)
        self.linear_velocity = 1.0
        self.angular_velocity = 45.0
        self.forward_vec = Gf.Vec3d(1, 0, 0)


class TestStateMachine:
    def __init__(self):
        self.current_state = "idle"
        self.state_history = []

    def is_in_state(self, state):
        return self.current_state == state

    def transition_to_state(self, state):
        self.state_history.append(state)
        self.current_state = state


class TestDrive(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.initial_pos = Gf.Vec3d(0, 0, 0)
        self.initial_rot = Gf.Quatd(1, 0, 0, 0)

    async def test_omni_drive(self):
        """Test OmniDirectionalDrive behaviors."""
        agent = TestAgent(self.initial_pos, self.initial_rot)
        state_machine = TestStateMachine()
        drive = OmniDirectionalDrive(agent, state_machine)

        # Test idle to forward transition
        path = [Gf.Vec3d(1, 1, 0)]
        drive.update(path, 0.1)
        self.assertEqual(state_machine.current_state, "forward")

        # Test target snapping
        agent.prim._translate._value = Gf.Vec3d(0.9, 0.9, 0)
        target = Gf.Vec3d(1, 1, 0)
        path = [target]
        drive.update(path, 0.2)
        self.assertEqual(agent.prim._translate._value, target)
        self.assertEqual(state_machine.current_state, "idle")
        self.assertEqual(len(path), 0)

    async def test_differential_drive(self):
        """Test DifferentialDrive behaviors."""
        agent = TestAgent(self.initial_pos, self.initial_rot)
        state_machine = TestStateMachine()
        drive = DifferentialDrive(agent, state_machine)

        # Test idle to turn transition
        path = [Gf.Vec3d(1, 1, 0)]
        drive.update(path, 0.1)
        self.assertTrue(state_machine.current_state in ["turn_left", "turn_right"])

        # # Test turning
        state_machine.current_state = "turn_right"
        path = [Gf.Vec3d(0, 1, 0)]
        drive.update(path, 2)
        self.assertAlmostEqual(
            MathUtil.get_quaternion_distance(agent.prim._orient._value, Gf.Quatd(0.707, 0, 0, 0.707)), 0, delta=0.01
        )

        # Test forward movement
        state_machine.current_state = "forward"
        drive.update(path, 1)
        self.assertEqual(agent.prim._translate._value, Gf.Vec3d(0, 1, 0))
