import omni.kit.test
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from pxr import Gf, Usd, Sdf, UsdGeom
import carb
from dataclasses import dataclass, field

from isaacsim.anim.robot.agent.base_agent import BaseAgent
from isaacsim.anim.robot.agent.iw_hub import IwHub, LiftUp, LiftDown, IwHubController
from isaacsim.anim.robot.agent.nova_carter import NovaCarter, NovaCarterController
from isaacsim.anim.robot.agent.agent_controller import AgentController
from isaacsim.anim.robot.path_planner import PathPlanner, NavMeshPathPlanner
from typing import List


class MockUSDAttribute:
    def __init__(self, value):
        self._value = value
    
    def Get(self):
        return self._value
    
    def Set(self, value):
        self._value = value


class MockUSDPrim:
    def __init__(self, path="/World/Robot", is_valid=True, is_active=True):
        self.path = path
        self._is_valid = is_valid
        self._is_active = is_active
        self._attributes = {}
        self._metadata = {}
        self._references = Mock()
        self._children = []
        self._stage = Mock()
        
    def IsValid(self):
        return self._is_valid
    
    def IsActive(self):
        return self._is_active
    
    def GetPath(self):
        return Sdf.Path(self.path)
    
    def GetPrimPath(self):
        """Added method that was missing from mock"""
        return Sdf.Path(self.path)
    
    def GetStage(self):
        return self._stage
    
    def GetAttribute(self, attr_name):
        if attr_name not in self._attributes:
            # Create default attributes for common xform operations
            if attr_name == "xformOp:translate":
                self._attributes[attr_name] = MockUSDAttribute(Gf.Vec3d(0, 0, 0))
            elif attr_name == "xformOp:orient":
                self._attributes[attr_name] = MockUSDAttribute(Gf.Quatd(1, 0, 0, 0))
            else:
                self._attributes[attr_name] = MockUSDAttribute(None)
        return self._attributes[attr_name]
    
    def GetMetadata(self, key):
        return self._metadata.get(key)
    
    def GetReferences(self):
        return self._references
    
    def GetChildren(self):
        return self._children
    
    def GetName(self):
        return self.path.split('/')[-1]


class TestBaseAgent(omni.kit.test.AsyncTestCase):
    """Test suite for BaseAgent class."""

    async def setUp(self):
        """Set up test environment."""
        # Create mock stage and prim
        self.mock_stage = Mock()
        self.mock_prim = MockUSDPrim("/World/TestRobot")
        self.mock_prim._stage = self.mock_stage
        
        # Mock UsdGeom.BBoxCache for bbox computation
        self.mock_bbox = Mock()
        self.mock_bbox_cache = Mock()
        self.mock_bbox_cache.ComputeLocalBound.return_value = self.mock_bbox

    async def test_base_agent_initialization_valid_prim(self):
        """Test BaseAgent initialization with valid prim."""
        with patch('pxr.UsdGeom.BBoxCache', return_value=self.mock_bbox_cache):
            agent = BaseAgent(prim=self.mock_prim)
            
            self.assertEqual(agent.prim, self.mock_prim)
            self.assertEqual(agent.agent_name, "Base Agent")
            self.assertEqual(agent.linear_velocity, 1.0)
            self.assertEqual(agent.angular_velocity, 45.0)
            self.assertEqual(agent.forward_vec, Gf.Vec3d(1, 0, 0))
            self.assertEqual(agent.drive_base, "omni_directional")
            self.assertIsInstance(agent.path_planner, PathPlanner)

    async def test_base_agent_initialization_invalid_prim(self):
        """Test BaseAgent initialization with invalid prim."""
        invalid_prim = MockUSDPrim(is_valid=False)
        
        with patch('pxr.UsdGeom.BBoxCache', return_value=self.mock_bbox_cache):
            with patch('carb.log_error') as mock_log_error:
                agent = BaseAgent(prim=invalid_prim)
                mock_log_error.assert_called_with("Non-valid prim for agent Base Agent")

    async def test_base_agent_initialization_inactive_prim(self):
        """Test BaseAgent initialization with inactive prim."""
        inactive_prim = MockUSDPrim(is_active=False)
        
        with patch('pxr.UsdGeom.BBoxCache', return_value=self.mock_bbox_cache):
            with patch('carb.log_error') as mock_log_error:
                agent = BaseAgent(prim=inactive_prim)
                mock_log_error.assert_called_with("Non-active prim for agent Base Agent")

    async def test_base_agent_joint_setup(self):
        """Test BaseAgent joint prim setup."""
        # Set up mock joints
        joint_paths = ["/joint1", "/joint2"]
        
        def mock_get_prim_at_path(path):
            # Create full paths by combining with robot path
            full_path = str(self.mock_prim.path) + str(path)
            return MockUSDPrim(full_path)
        
        self.mock_prim.GetStage().GetPrimAtPath.side_effect = mock_get_prim_at_path
        
        with patch('pxr.UsdGeom.BBoxCache', return_value=self.mock_bbox_cache):
            agent = BaseAgent(prim=self.mock_prim, joints=joint_paths)
            
            self.assertEqual(len(agent.joint_prims), 2)
            self.assertEqual(len(agent.init_joint_poses), 2)
            
            # Verify initial poses are recorded
            for joint_prim in agent.joint_prims:
                joint_path = str(joint_prim.GetPrimPath())
                self.assertIn(joint_path, agent.init_joint_poses)
                translate, orient = agent.init_joint_poses[joint_path]
                self.assertEqual(translate, Gf.Vec3d(0, 0, 0))
                self.assertEqual(orient, Gf.Quatd(1, 0, 0, 0))

    async def test_base_agent_asset_reference_addition(self):
        """Test BaseAgent asset reference addition."""
        asset_path = "/path/to/asset.usd"
        
        with patch('pxr.UsdGeom.BBoxCache', return_value=self.mock_bbox_cache):
            with patch('omni.client.is_local_url', return_value=False):
                agent = BaseAgent(prim=self.mock_prim)
                # asset_path is a field with init=False, so set it after initialization
                agent.asset_path = asset_path
                # Manually trigger the asset loading logic that would happen in __post_init__
                agent.__post_init__()
                
                # Should add reference
                agent.prim.GetReferences().AddReference.assert_called_with(asset_path)

    async def test_base_agent_default_values(self):
        """Test BaseAgent default values."""
        with patch('pxr.UsdGeom.BBoxCache', return_value=self.mock_bbox_cache):
            agent = BaseAgent(prim=self.mock_prim)
            
            self.assertEqual(agent.states, ["idle", "turn_left", "turn_right", "forward"])
            self.assertIn("idle", agent.transitions)
            self.assertIn("turn_left", agent.transitions)
            self.assertIn("turn_right", agent.transitions)
            self.assertIn("forward", agent.transitions)


class TestIwHub(omni.kit.test.AsyncTestCase):
    """Test suite for IwHub agent class."""

    async def setUp(self):
        """Set up test environment."""
        self.mock_stage = Mock()
        self.mock_prim = MockUSDPrim("/World/IwHub")
        self.mock_prim._stage = self.mock_stage
        self.mock_bbox_cache = Mock()
        self.mock_bbox_cache.ComputeLocalBound.return_value = Mock()

    async def test_iw_hub_initialization(self):
        """Test IwHub initialization."""
        with patch('pxr.UsdGeom.BBoxCache', return_value=self.mock_bbox_cache):
            with patch('isaacsim.anim.robot.agent.iw_hub._get_iw_hub_asset_path', return_value="/path/to/iw_hub.usd"):
                with patch('omni.client.is_local_url', return_value=False):
                    hub = IwHub(prim=self.mock_prim)
                    
                    self.assertEqual(hub.agent_name, "iw_hub")
                    self.assertEqual(hub.linear_velocity, 0.5)
                    self.assertEqual(hub.angular_velocity, 30.0)
                    self.assertEqual(hub.drive_base, "differential")
                    self.assertIsInstance(hub.path_planner, NavMeshPathPlanner)
                    
                    # Check extended states and transitions
                    self.assertIn("lift_up", hub.states)
                    self.assertIn("lift_down", hub.states)
                    self.assertIn("lift_up", hub.transitions["idle"])
                    self.assertIn("lift_down", hub.transitions["idle"])

    async def test_iw_hub_joints_configuration(self):
        """Test IwHub joint configuration."""
        with patch('pxr.UsdGeom.BBoxCache', return_value=self.mock_bbox_cache):
            with patch('isaacsim.anim.robot.agent.iw_hub._get_iw_hub_asset_path', return_value="/path/to/iw_hub.usd"):
                with patch('omni.client.is_local_url', return_value=False):
                    hub = IwHub(prim=self.mock_prim)
                    
                    expected_joints = [
                        "/chassis/lift",
                        "/chassis/left_wheel",
                        "/chassis/right_wheel",
                        "/chassis/left_swivel/left_caster",
                        "/chassis/right_swivel/right_caster",
                        "/chassis/left_swivel",
                        "/chassis/right_swivel",
                    ]
                    self.assertEqual(hub.joints, expected_joints)

    async def test_iw_hub_animation_paths(self):
        """Test IwHub animation paths configuration."""
        with patch('pxr.UsdGeom.BBoxCache', return_value=self.mock_bbox_cache):
            with patch('isaacsim.anim.robot.agent.iw_hub._get_iw_hub_asset_path', return_value="/path/to/iw_hub.usd"):
                with patch('omni.client.is_local_url', return_value=False):
                    hub = IwHub(prim=self.mock_prim)
                    
                    expected_animations = ["turn_left", "turn_right", "forward", "lift_up", "lift_down"]
                    for anim_name in expected_animations:
                        self.assertIn(anim_name, hub.animation_paths)
                        self.assertTrue(hub.animation_paths[anim_name])  # Path should not be empty


class TestNovaCarter(omni.kit.test.AsyncTestCase):
    """Test suite for NovaCarter agent class."""

    async def setUp(self):
        """Set up test environment."""
        self.mock_stage = Mock()
        self.mock_prim = MockUSDPrim("/World/NovaCarter")
        self.mock_prim._stage = self.mock_stage
        self.mock_bbox_cache = Mock()
        self.mock_bbox_cache.ComputeLocalBound.return_value = Mock()

    async def test_nova_carter_initialization(self):
        """Test NovaCarter initialization."""
        with patch('pxr.UsdGeom.BBoxCache', return_value=self.mock_bbox_cache):
            with patch('isaacsim.anim.robot.agent.nova_carter._get_nova_carter_asset_path', return_value="/path/to/nova_carter.usd"):
                with patch('omni.client.is_local_url', return_value=False):
                    carter = NovaCarter(prim=self.mock_prim)
                    
                    self.assertEqual(carter.agent_name, "Nova Carter")
                    self.assertEqual(carter.linear_velocity, 0.5)
                    self.assertEqual(carter.angular_velocity, 30.0)
                    self.assertEqual(carter.drive_base, "differential")
                    self.assertIsInstance(carter.path_planner, NavMeshPathPlanner)

    async def test_nova_carter_joints_configuration(self):
        """Test NovaCarter joint configuration."""
        with patch('pxr.UsdGeom.BBoxCache', return_value=self.mock_bbox_cache):
            with patch('isaacsim.anim.robot.agent.nova_carter._get_nova_carter_asset_path', return_value="/path/to/nova_carter.usd"):
                with patch('omni.client.is_local_url', return_value=False):
                    carter = NovaCarter(prim=self.mock_prim)
                    
                    expected_joints = [
                        "/chassis_link/wheel_right",
                        "/chassis_link/wheel_left",
                        "/chassis_link/caster_swivel_left",
                        "/chassis_link/caster_swivel_right",
                        "/chassis_link/caster_swivel_left/caster_wheel_left",
                        "/chassis_link/caster_swivel_right/caster_wheel_right",
                    ]
                    self.assertEqual(carter.joints, expected_joints)


class TestLiftCommands(omni.kit.test.AsyncTestCase):
    """Test suite for IwHub-specific command classes."""

    async def setUp(self):
        """Set up test environment."""
        self.mock_agent = Mock()
        self.mock_state_machine = Mock()

    async def test_lift_up_command_initialization(self):
        """Test LiftUp command initialization."""
        with patch('omni.metropolis.utils.simulation_util.SimulationUtil.get_current_timecode', return_value=10.0):
            command = LiftUp("", self.mock_agent, self.mock_state_machine)
            
            self.assertEqual(command.command, "")
            self.assertEqual(command._agent, self.mock_agent)
            self.assertEqual(command._state_machine, self.mock_state_machine)
            self.mock_state_machine.set_state.assert_called_with("lift_up")

    async def test_lift_up_command_update_not_finished(self):
        """Test LiftUp command update when not finished."""
        with patch('omni.metropolis.utils.simulation_util.SimulationUtil.get_current_timecode', return_value=10.0):
            command = LiftUp("", self.mock_agent, self.mock_state_machine)
            
            command.update(0.5)
            
            self.assertFalse(command.is_done)
            self.assertEqual(command.time_passed, 0.5)
            self.mock_state_machine.update.assert_called_once()

    async def test_lift_up_command_update_finished(self):
        """Test LiftUp command update when finished."""
        with patch('omni.metropolis.utils.simulation_util.SimulationUtil.get_current_timecode', return_value=10.0):
            command = LiftUp("", self.mock_agent, self.mock_state_machine)
            
            command.update(1.5)
            
            self.assertTrue(command.is_done)
            self.assertEqual(command.time_passed, 1.5)
            self.mock_state_machine.transition_to_state.assert_called_with("idle")

    async def test_lift_down_command_initialization(self):
        """Test LiftDown command initialization."""
        with patch('omni.metropolis.utils.simulation_util.SimulationUtil.get_current_timecode', return_value=10.0):
            command = LiftDown("", self.mock_agent, self.mock_state_machine)
            
            self.assertEqual(command.command, "")
            self.assertEqual(command._agent, self.mock_agent)
            self.assertEqual(command._state_machine, self.mock_state_machine)
            self.mock_state_machine.set_state.assert_called_with("lift_down")

    async def test_lift_down_command_update_not_finished(self):
        """Test LiftDown command update when not finished."""
        with patch('omni.metropolis.utils.simulation_util.SimulationUtil.get_current_timecode', return_value=10.0):
            command = LiftDown("", self.mock_agent, self.mock_state_machine)
            
            command.update(0.5)
            
            self.assertFalse(command.is_done)
            self.assertEqual(command.time_passed, 0.5)
            self.mock_state_machine.update.assert_called_once()

    async def test_lift_down_command_update_finished(self):
        """Test LiftDown command update when finished."""
        with patch('omni.metropolis.utils.simulation_util.SimulationUtil.get_current_timecode', return_value=10.0):
            command = LiftDown("", self.mock_agent, self.mock_state_machine)
            
            command.update(1.5)
            
            self.assertTrue(command.is_done)
            self.assertEqual(command.time_passed, 1.5)
            self.mock_state_machine.transition_to_state.assert_called_with("idle")


class TestAgentController(omni.kit.test.AsyncTestCase):
    """Test suite for AgentController class."""

    async def setUp(self):
        """Set up test environment."""
        # Create mock for BehaviorScript base class
        self.mock_prim_path = "/World/TestRobot"
        self.mock_prim = MockUSDPrim(self.mock_prim_path)
        self.mock_stage = Mock()

    async def test_agent_controller_initialization(self):
        """Test AgentController initialization."""
        with patch.multiple(
            'isaacsim.anim.robot.agent.agent_controller',
            carb=Mock(),
            omni=Mock()
        ):
            # Mock the settings
            mock_settings = Mock()
            mock_settings.get.side_effect = lambda key: {
                "/exts/isaacsim.anim.robot/command_settings/command_file_path": "/path/to/commands.txt",
                "/exts/isaacsim.anim.robot/simulation_settings/dynamic_avoidance": False
            }.get(key)
            
            with patch('carb.settings.get_settings', return_value=mock_settings):
                with patch('pxr.UsdGeom.BBoxCache'):
                    # Mock BehaviorScript base class to avoid prim_path requirement
                    with patch('omni.kit.scripting.BehaviorScript.__init__', return_value=None):
                        controller = AgentController()
                        
                        # Mock the read-only properties
                        with patch.object(type(controller), 'prim_path', new_callable=PropertyMock) as mock_prim_path:
                            with patch.object(type(controller), 'prim', new_callable=PropertyMock) as mock_prim:
                                with patch.object(type(controller), 'stage', new_callable=PropertyMock) as mock_stage:
                                    mock_prim_path.return_value = self.mock_prim_path
                                    mock_prim.return_value = self.mock_prim
                                    mock_stage.return_value = self.mock_stage
                                    
                                    controller.on_init()
                                    
                                    # Verify basic initialization
                                    self.assertIsInstance(controller.agent, BaseAgent)
                                    self.assertIsNone(controller.current_command)
                                    self.assertEqual(controller.commands, [])
                                    self.assertIsNotNone(controller.state_machine)

    async def test_read_commands_from_file(self):
        """Test reading commands from file."""
        mock_file_content = [
            "TestRobot GoTo 1.0 2.0 0.0",
            "OtherRobot Idle 5.0",
            "TestRobot Idle 3.0"
        ]
        
        with patch('isaacsim.anim.robot.agent.agent_controller.TextFileUtil.read_text_file', return_value="\n".join(mock_file_content)):
            with patch.multiple(
                'isaacsim.anim.robot.agent.agent_controller',
                carb=Mock(),
                omni=Mock()
            ):
                mock_settings = Mock()
                mock_settings.get.return_value = "/path/to/commands.txt"
                
                with patch('carb.settings.get_settings', return_value=mock_settings):
                    with patch('pxr.UsdGeom.BBoxCache'):
                        with patch('omni.kit.scripting.BehaviorScript.__init__', return_value=None):
                            controller = AgentController()
                            
                            # Mock the read-only properties
                            with patch.object(type(controller), 'prim_path', new_callable=PropertyMock) as mock_prim_path:
                                with patch.object(type(controller), 'prim', new_callable=PropertyMock) as mock_prim:
                                    with patch.object(type(controller), 'stage', new_callable=PropertyMock) as mock_stage:
                                        mock_prim_path.return_value = self.mock_prim_path
                                        mock_prim.return_value = self.mock_prim
                                        mock_stage.return_value = self.mock_stage
                                        
                                        controller.on_init()
                                        commands = controller.read_commands_from_file("/path/to/commands.txt")
                                        
                                        # Should only get commands for TestRobot
                                        expected_commands = ["GoTo 1.0 2.0 0.0", "Idle 3.0"]
                                        self.assertEqual(commands, expected_commands)

    async def test_inject_command(self):
        """Test command injection functionality."""
        with patch.multiple(
            'isaacsim.anim.robot.agent.agent_controller',
            carb=Mock(),
            omni=Mock()
        ):
            mock_settings = Mock()
            mock_settings.get.return_value = "/path/to/commands.txt"
            
            with patch('carb.settings.get_settings', return_value=mock_settings):
                with patch('pxr.UsdGeom.BBoxCache'):
                    with patch('omni.kit.scripting.BehaviorScript.__init__', return_value=None):
                        controller = AgentController()
                        
                        # Mock the read-only properties
                        with patch.object(type(controller), 'prim_path', new_callable=PropertyMock) as mock_prim_path:
                            with patch.object(type(controller), 'prim', new_callable=PropertyMock) as mock_prim:
                                with patch.object(type(controller), 'stage', new_callable=PropertyMock) as mock_stage:
                                    mock_prim_path.return_value = self.mock_prim_path
                                    mock_prim.return_value = self.mock_prim
                                    mock_stage.return_value = self.mock_stage
                                    
                                    controller.on_init()
                                    controller.commands = ["Original Command"]
                                    
                                    # Inject new commands
                                    new_commands = ["TestRobot GoTo 5.0 5.0 0.0", "TestRobot Idle 2.0"]
                                    controller.inject_command(new_commands)
                                    
                                    # Commands should be prepended
                                    expected_commands = ["GoTo 5.0 5.0 0.0", "Idle 2.0", "Original Command"]
                                    self.assertEqual(controller.commands, expected_commands)

    async def test_end_current_command(self):
        """Test ending current command."""
        with patch.multiple(
            'isaacsim.anim.robot.agent.agent_controller',
            carb=Mock(),
            omni=Mock()
        ):
            mock_settings = Mock()
            mock_settings.get.return_value = "/path/to/commands.txt"
            
            with patch('carb.settings.get_settings', return_value=mock_settings):
                with patch('pxr.UsdGeom.BBoxCache'):
                    with patch('omni.kit.scripting.BehaviorScript.__init__', return_value=None):
                        controller = AgentController()
                        
                        # Mock the read-only properties
                        with patch.object(type(controller), 'prim_path', new_callable=PropertyMock) as mock_prim_path:
                            with patch.object(type(controller), 'prim', new_callable=PropertyMock) as mock_prim:
                                with patch.object(type(controller), 'stage', new_callable=PropertyMock) as mock_stage:
                                    mock_prim_path.return_value = self.mock_prim_path
                                    mock_prim.return_value = self.mock_prim
                                    mock_stage.return_value = self.mock_stage
                                    
                                    controller.on_init()
                                    
                                    # Create mock current command
                                    mock_command = Mock()
                                    controller.current_command = mock_command
                                    
                                    controller.end_current_command()
                                    
                                    mock_command.force_quit_command.assert_called_once()


class TestAssetPathFunctions(omni.kit.test.AsyncTestCase):
    """Test suite for asset path utility functions."""

    async def test_get_iw_hub_asset_path_success(self):
        """Test successful iw_hub asset path retrieval."""
        with patch('isaacsim.anim.robot.agent.iw_hub.get_isaac_sim_asset_root_path', return_value="/isaac/sim/root"):
            with patch('os.path.join', return_value="/isaac/sim/root/Isaac/Samples/AnimRobot/iw_hub.usd"):
                from isaacsim.anim.robot.agent.iw_hub import _get_iw_hub_asset_path
                result = _get_iw_hub_asset_path()
                self.assertEqual(result, "/isaac/sim/root/Isaac/Samples/AnimRobot/iw_hub.usd")

    async def test_get_iw_hub_asset_path_fallback(self):
        """Test fallback iw_hub asset path retrieval."""
        with patch('isaacsim.anim.robot.agent.iw_hub.get_isaac_sim_asset_root_path', return_value=None):
            with patch('isaacsim.anim.robot.agent.iw_hub.get_assets_root_path', return_value="/fallback/root"):
                with patch('os.path.join', return_value="/fallback/root/Isaac/Samples/AnimRobot/iw_hub.usd"):
                    with patch('carb.log_warn') as mock_warn:
                        from isaacsim.anim.robot.agent.iw_hub import _get_iw_hub_asset_path
                        result = _get_iw_hub_asset_path()
                        self.assertEqual(result, "/fallback/root/Isaac/Samples/AnimRobot/iw_hub.usd")
                        mock_warn.assert_called_once()

    async def test_get_nova_carter_asset_path_success(self):
        """Test successful Nova Carter asset path retrieval."""
        with patch('isaacsim.anim.robot.agent.nova_carter.get_isaac_sim_asset_root_path', return_value="/isaac/sim/root"):
            with patch('os.path.join', return_value="/isaac/sim/root/Isaac/Samples/AnimRobot/nova_carter.usd"):
                from isaacsim.anim.robot.agent.nova_carter import _get_nova_carter_asset_path
                result = _get_nova_carter_asset_path()
                self.assertEqual(result, "/isaac/sim/root/Isaac/Samples/AnimRobot/nova_carter.usd")

    async def test_get_nova_carter_asset_path_fallback(self):
        """Test fallback Nova Carter asset path retrieval."""
        with patch('isaacsim.anim.robot.agent.nova_carter.get_isaac_sim_asset_root_path', return_value=None):
            with patch('isaacsim.anim.robot.agent.nova_carter.get_assets_root_path', return_value="/fallback/root"):
                with patch('os.path.join', return_value="/fallback/root/Isaac/Samples/AnimRobot/nova_carter.usd"):
                    with patch('carb.log_warn') as mock_warn:
                        from isaacsim.anim.robot.agent.nova_carter import _get_nova_carter_asset_path
                        result = _get_nova_carter_asset_path()
                        self.assertEqual(result, "/fallback/root/Isaac/Samples/AnimRobot/nova_carter.usd")
                        mock_warn.assert_called_once()
