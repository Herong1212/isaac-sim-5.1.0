import re
import asyncio
from dataclasses import dataclass, field
import hashlib
from typing import Dict, List, Tuple, Optional
from abc import ABC, abstractmethod
import numpy as np
import carb
import omni.usd
import omni.kit.app
import omni.anim.navigation.core as nav
from omni.anim.people.scripts.interactable_object_helper import InteractableObjectHelper
from omni.kit.notification_manager import post_notification, NotificationStatus
from omni.metropolis.utils.carb_util import CarbUtil
from omni.metropolis.utils.simulation_util import SimulationUtil
from omni.metropolis.utils.semantics_util import SemanticsUtils
from isaacsim.replicator.agent.core.settings import CommandSetting
from .randomizer_util import RandomizerUtil


@dataclass
class RandomizerConfig:
    """Configuration class for randomizer parameters"""
    max_random_attempts: int = 1000
    command_timeout: float = 5.0
    agent_radius: float = 0.5
    agent_distance: float = 2.0
    num_precision: int = 2


# Legacy constants for backward compatibility
MAX_RANDOM_CNT = 1000
ONE_AGENT_RANDOM_COMMAND_TIMEOUT = 5
AGENT_RADIUS = 0.5
AGENT_DIST = 2


class Command(ABC):
    """
    Command:
        Base class for randomization of one type of command.
        Each subclass is to implement randomiztion rules in randomize().
    """

    def __init__(self, name="", num_precision: Optional[int] = None):
        self.name = name if name else self.__class__.__name__
        # How many digits to keep in the command parameter's text form
        self.num_precision = num_precision if num_precision is not None else 2


    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Command):
            return self.name == other.name
        return False

    # Generate one random command.
    # Return the command text form and estimated duration.
    @abstractmethod
    def randomize(
        self,
        agent,
        agent_speed,
        agent_pos_dict,
        navmesh,
        interactable_objects,
        rng,
        navigation_area,
        config: Optional[RandomizerConfig] = None,
    ) -> Tuple[str, float]:
        raise NotImplementedError()


class TimingCommand(Command):
    """
    TimingCommand:
        Base class to randoimze duration parameter.
    """

    def __init__(self, name, min_time, max_time):
        super().__init__()
        self.name = name
        self.min_time = min_time  # Time range to be randomized
        self.max_time = max_time

    def randomize(
        self,
        agent,
        agent_speed,
        agent_pos_dict,
        navmesh,
        interactable_objects,
        rng,
        navigation_area,
        config: Optional[RandomizerConfig] = None,
    ) -> Tuple[str, float]:
        duration = self._randomize_duration(rng)
        text = f"{agent} {self.name} {round(duration, self.num_precision)}"
        return (text, duration)

    def _randomize_duration(self, rng):
        """Get a randomize duration"""
        if self.min_time < 0 or self.max_time < 0 or self.min_time > self.max_time:
            carb.log_warn(f"Command class {self.name} has invalid time range. 1.0 will be used for duration.")
            return 1.0
        return float(rng.uniform(self.min_time, self.max_time))


class TimingToObjectCommand(TimingCommand):
    """
    TimingToObjectCommand:
        Base class to randomly pick object to interact as parameter.
        Inherient TimingCommand for randomizaing duration.
    """

    def __init__(self, name, min_time, max_time, object_filter_str):
        super().__init__(name, min_time, max_time)
        self.object_filter_str = object_filter_str  # Filter for interactable objects

    def randomize(
        self,
        agent,
        agent_speed,
        agent_pos_dict,
        navmesh,
        interactable_objects,
        rng,
        navigation_area,
        config: Optional[RandomizerConfig] = None,
    ) -> Tuple[str, float]:
        # Pick object to interact
        agent_pos = carb.Float3(agent_pos_dict[agent])
        object_prim = self._random_pick_object(interactable_objects, rng)
        if not object_prim:
            carb.log_info(f"No object to interact with. Creating {self.name} command fails.")
            return None, 0
        object_path = object_prim.GetPrimPath()
        stage = omni.usd.get_context().get_stage()
        target_point, _, _, _ = InteractableObjectHelper.get_interact_prim_offsets(stage, object_prim)
        closest_point = navmesh.query_closest_point(
            target_point, area_indices=navigation_area, agent_radius=config.agent_radius
        )[0]
        if not navmesh.query_shortest_path(
            start_pos=agent_pos, end_pos=closest_point, agent_radius=config.agent_radius
        ):
            carb.log_info(f"{object_path} is not reachable.")
            return None, 0
        walk_to_duration = CarbUtil.dist3(closest_point, agent_pos) / agent_speed
        # Randomize interact duration
        interact_duration = self._randomize_duration(rng)
        text = f"{agent} {self.name} {object_path} {round(interact_duration, self.num_precision)}"
        duration = walk_to_duration + interact_duration
        return (text, duration)

    def _random_pick_object(self, interactable_objects, rng):
        """Pick a randomize object to interact with"""
        p = re.compile(self.object_filter_str)
        filter_objects = []
        for obj in interactable_objects:
            sem_list = SemanticsUtils.get_prim_semantics(obj)
            for t, d in sem_list:
                if t == "class" and p.match(d):
                    filter_objects.append(obj)
        if filter_objects:
            idx = int(rng.integers(0, len(filter_objects)))
            return filter_objects[idx]
        else:
            return None


class GoToCommand(Command):
    """
    GoToCommand:
        Base class to randomly pick a goto location.
    """

    def __init__(self, name, min_distance, max_distance, random_rotation):
        super().__init__(name)
        self.min_distance = min_distance
        self.max_distance = max_distance
        self.random_rotation = random_rotation

    def randomize(
        self,
        agent,
        agent_speed,
        agent_pos_dict,
        navmesh,
        interactable_objects,
        rng,
        navigation_area,
        config: Optional[RandomizerConfig] = None,
    ) -> Tuple[str, float]:
        # Create a dedicated RNG stream for navmesh random queries per agent and call
        # to ensure deterministic yet isolated sampling for GoTo without affecting global nav RNG.
        goto_random_id = f"{self.name}_{agent}"
        inav = nav.acquire_interface()
        nav_seed = int(rng.integers(0, 2**31 - 1))
        inav.set_random_seed(goto_random_id, RandomizerUtil.handle_overflow(nav_seed))
        # Find a valid and reachable point on the navmesh
        agent_pos = carb.Float3(list(agent_pos_dict[agent]))
        valid_point = carb.Float3(0, 0, 0)
        valid = False  # Whether the target point is a point on the navmesh
        reachable = None  # Whether there exists a path from the starting point to the target point
        num_attempts = 0  # Number of attempts to find a valid path

        navigation_area_idx = RandomizerUtil.area_name_to_index(navmesh, navigation_area)
        closest_navmesh_point = navmesh.query_closest_point(
            agent_pos,
            area_indices=navigation_area_idx,
            agent_radius=config.agent_radius,
        )[0]
        agent_in_area = SimulationUtil.is_the_same_point(agent_pos, closest_navmesh_point)
        area_probabilities = RandomizerUtil.area_idx_to_probability(navmesh, navigation_area_idx)

        while not valid or reachable is None:
            if num_attempts > config.max_random_attempts:
                # If failed to find a valid destination after max attempts, terminate and reset to the default command
                carb.log_info(f"Can't find a valid random point for {agent}.")
                return None, 0
            if agent_in_area:  # agent is in the area, query some random point
                valid_point = navmesh.query_random_point(
                    goto_random_id, area_probabilities=area_probabilities, agent_radius=config.agent_radius
                )
                if not valid_point:
                    carb.log_error("NavMesh returned no random point. Command randomization aborted.")
                    return None, 0
                distance = CarbUtil.dist3(agent_pos, valid_point)
                valid = self.min_distance < distance < self.max_distance
                reachable = navmesh.query_shortest_path(
                    start_pos=agent_pos, end_pos=valid_point, agent_radius=config.agent_radius
                )
            else:  # agent is not in the area, move agent to the area first
                valid_point = navmesh.query_random_point(
                    goto_random_id, area_probabilities=area_probabilities, agent_radius=config.agent_radius
                )
                if not valid_point:
                    carb.log_error("NavMesh returned no random point. Command randomization aborted.")
                    return None, 0
                valid = True
                reachable = navmesh.query_shortest_path(
                    start_pos=agent_pos, end_pos=valid_point, agent_radius=config.agent_radius
                )
            num_attempts += 1

        x = str(round(valid_point.x, self.num_precision))
        y = str(round(valid_point.y, self.num_precision))
        z = str(round(valid_point.z, self.num_precision))
        parameter = f"{x} {y} {z}"
        # Update the starting position of this agent for the next GoTo command to work
        agent_pos_dict[agent] = [valid_point.x, valid_point.y, valid_point.z]
        text = f"{agent} {self.name} {parameter}"
        if self.random_rotation:
            text += " _"
        duration = CarbUtil.dist3(valid_point, agent_pos) / agent_speed  # Duration = Dist / Speed
        return (text, duration)


class CommandTransitionMap:
    """
    CommandTransitionMap
        Define command transition to be used in Randomizer.
    """

    @dataclass
    class Command:
        name: str
        weight: float
        transitions: Dict[str, float] = field(default=lambda: {})

    def __init__(self, json_data):
        self._commands: List[CommandTransitionMap.Command] = []
        for name, cmd in json_data.items():
            self._commands.append(
                CommandTransitionMap.Command(name=name, weight=cmd["weight"], transitions=cmd["transitions"])
            )

    def get_all_commands(self):
        return self._commands

    def get_command_by_name(self, command_name):
        for cmd in self._commands:
            if cmd.name == command_name:
                return cmd
        return None

    def add_command(self, command_name: str, weight: float, transitions: Dict[str, float]) -> bool:
        if any(cmd.name == command_name for cmd in self._commands):
            carb.log_warn(f"Command [{command_name}] exists. Adding command to transition map fails.")
            return False
        self._commands.append(CommandTransitionMap.Command(command_name, weight, transitions))
        return True

    def remove_command(self, command_name) -> bool:
        cmd = self.get_command_by_name(command_name)
        if cmd is None:
            carb.log_warn(f"Command [{command_name}] does not exist. Removing command from transition map fails.")
            return False
        self._commands.remove(cmd)
        return True

    def add_command_transition(self, command_name: str, to_command_name: str, weight: float) -> bool:
        if not any(cmd.name == command_name for cmd in self._commands):
            carb.log_warn(f"Command [{command_name}] does not exist. Adding command transiton fails.")
            return False
        transitions = self._commands[command_name].transitions
        if any(cmd.name == to_command_name for cmd in transitions.keys()):
            carb.log_warn(
                f"Command [{command_name}] has transition for {to_command_name} already. Adding transition fails."
            )
            return False
        transitions[to_command_name] = weight
        return True

    def remove_command_transition(self, command_name: str, to_command_name: str) -> bool:
        if not any(cmd.name == command_name for cmd in self._commands):
            carb.log_warn(f"Command [{command_name}] does not exist. Removing transition fails.")
            return False
        transitions = self._commands[command_name].transitions
        if any(cmd.name == to_command_name for cmd in transitions.keys()):
            carb.log_warn(
                f"Command [{command_name}] has transition for {to_command_name} already. Removing transition fails."
            )
            return False
        transitions.pop(to_command_name)
        return True

    def to_dict(self) -> dict:
        result = {}
        for cmd in self._commands:
            result[cmd.name] = {"weight": cmd.weight, "transitions": cmd.transitions}
        return result


class Randomizer:
    """
    Base Randomizer Class
        It supports generating random position and get the random commands for agents.
    """

    ID_counter = -1

    def __init__(self, global_seed, config:Optional[RandomizerConfig] = None):
        self._global_seed = global_seed
        self.config = config if config is not None else RandomizerConfig()
        self.name = self.__class__.__name__.replace("Randomizer", "")  # child class name
        self.agent_positions = set()  # Positions for all agents in the scene (avoid overlaps among different agents)
        self.agent_id = Randomizer.ID_counter  # an offset for differentiating spawn locations for different agents.
        Randomizer.ID_counter += 1
        # Command settings. To be initialized in the children randomizers.
        self.commands_dict: Dict[str, Command] = {}  # All avaliable commands to be randomized.
        self.fallback_command: Command = None  # Fallback command when one command randomization fails.
        # Agent speed for command randomization
        self.agent_speed = -1
        # Default radius - use config value
        self.radius = self.config.agent_radius

        # Get the navmesh in the stage
        self.inav = nav.acquire_interface()
        spawn_seed = RandomizerUtil.handle_overflow(self._global_seed + self.agent_id)
        self.inav.set_random_seed(self.name, spawn_seed)

        self.transition_map: CommandTransitionMap = None

    # Every time global seed is changed, the randomized state needs to be reset
    def update_seed(self, new_seed):
        self._global_seed = new_seed
        self.reset()

    # Need to be called after another agent called spawn()
    def update_agent_positions(self, pos):
        if isinstance(pos, (list, tuple)):
            self.agent_positions.update(tuple(carb.Float3(list(p))) for p in pos)
        elif isinstance(pos, set):
            self.agent_positions.update(tuple(carb.Float3(list(p))) for p in pos)
        else:
            self.agent_positions.update([tuple(carb.Float3(list(pos)))])

    # Reset the randomization state
    # Should be called when a new environment is loaded
    def reset(self):
        spawn_seed = RandomizerUtil.handle_overflow(self._global_seed + self.agent_id)
        self.inav.set_random_seed(self.name, spawn_seed)
        # Clear agent positions to allow fresh position generation
        self.agent_positions.clear()

    # Generate random commands for the given agent list
    async def generate_commands(self, global_seed, duration, agent_pos_dict, navigation_area):
        # Clean up last result
        self.commands = []
        # Get the navmesh in the stage
        navmesh = self.inav.get_navmesh()
        # Get all interactable objects in the stage
        interactable_objects = InteractableObjectHelper.get_all_interactable_objects_in_stage(
            CommandSetting.get_character_interact_object_root_path()
        )

        for area in navigation_area:
            if area.strip() == "":
                continue  # empty string is used for default navigation area
            if self.inav.find_area(area) == -1:
                post_notification(
                    f"Unknown navigation area: '{area}', please check your configuration.",
                    status=NotificationStatus.WARNING,
                )
                return None

        async def one_agent_generate_commands(agent, one_agent_commands, one_agent_duration, navigation_area):
            # This helps each agent generate unique seed
            # Note: Hash collision may still happen, although
            agent_name_hash = int(hashlib.sha256(agent.encode()).hexdigest(), 16) % 10000
            command_seed = RandomizerUtil.handle_overflow(global_seed + agent_name_hash)
            rng = np.random.default_rng(command_seed)

            command_name = ""
            cnt = 0
            while one_agent_duration < duration:
                if not command_name:
                    # Pick first command
                    t_commands = self.transition_map.get_all_commands()
                    name_list = [cmd.name for cmd in t_commands]
                    weight_list = [cmd.weight for cmd in t_commands]
                    if not name_list:
                        carb.log_warn("No commands available in transition map. Aborting.")
                        return None
                    total_weight = float(sum(weight_list)) if weight_list else 0.0
                    if total_weight <= 0.0:
                        # fallback to uniform if weights invalid
                        probs = None
                    else:
                        probs = [w / total_weight for w in weight_list]
                    command_name = rng.choice(name_list, p=probs)
                else:
                    # Pick next command
                    t_command = self.transition_map.get_command_by_name(command_name)
                    if not t_command:
                        carb.log_info(
                            f"{command_name} command is not in transition map. Default command will be used instead."
                        )
                        command_name = self.fallback_command.name
                    else:
                        name_list = list(t_command.transitions.keys())
                        weight_list = list(t_command.transitions.values())
                        if not name_list:
                            carb.log_warn("No transitions available. Falling back to default command.")
                            command_name = self.fallback_command.name
                        else:
                            total_weight = float(sum(weight_list)) if weight_list else 0.0
                            if total_weight <= 0.0:
                                probs = None
                            else:
                                probs = [w / total_weight for w in weight_list]
                            command_name = rng.choice(name_list, p=probs)

                # Check if command exists
                command = None
                if command_name not in self.commands_dict:
                    carb.log_info(f"{command_name} command is not registered. Default command will be used instead.")
                    command = self.fallback_command
                else:
                    command = self.commands_dict[command_name]
                # Run randomization on command
                text, cmd_duration = command.randomize(
                    agent,
                    self.agent_speed,
                    agent_pos_dict,
                    navmesh,
                    interactable_objects,
                    rng,
                    navigation_area,
                    self.config,
                )
                if not text or not cmd_duration:
                    carb.log_info(
                        f"{command_name} can not be propery randomized. Default command will be used instead."
                    )
                    text, cmd_duration = self.fallback_command.randomize(
                        agent,
                        self.agent_speed,
                        agent_pos_dict,
                        navmesh,
                        interactable_objects,
                        rng,
                        navigation_area,
                        self.config,
                    )
                one_agent_commands.append(text)
                one_agent_duration += cmd_duration

                cnt += 1
                if cnt >= self.config.max_random_attempts:
                    carb.log_warn(
                        f"Reach random command generation maxinum attempts "
                        f"({self.config.max_random_attempts}) for {agent}. "
                        f"Generated commands duration: {one_agent_duration}."
                    )
                    break

        # Generate commands for the agents one by one
        # agent is a the name of the agent in stage
        for agent in agent_pos_dict:
            one_agent_commands = []
            one_agent_duration = 0
            try:
                await asyncio.wait_for(
                    one_agent_generate_commands(
                        agent=agent,
                        one_agent_commands=one_agent_commands,
                        one_agent_duration=one_agent_duration,
                        navigation_area=navigation_area,
                    ),
                    timeout=self.config.command_timeout,
                )
            except TimeoutError:
                carb.log_warn(
                    f"Reach random command generation timeout ({self.config.command_timeout}) for {agent}. "
                    f"Generated commands duration: {one_agent_duration}."
                )
            finally:
                for cmd in one_agent_commands:
                    self.commands.append(cmd)
                carb.log_info(f"Generate commands for {agent} done.")
                await omni.kit.app.get_app().next_update_async()

        return self.commands

    # Randomly generate a valid agent position
    # Along with the global seed, each idx gives a deterministic result
    def get_random_position(self, spawn_area=None) -> Optional[carb.Float3]:
        if spawn_area is None:
            spawn_area = []
        spawn_location = carb.Float3(0, 0, 0)

        navmesh = self.inav.get_navmesh()
        if navmesh is None:
            carb.log_error("Navmesh not found when trying to get random positions")
            return None

        valid = False
        num_attempts = 0
        has_overlap = False

        if spawn_area is not None:
            # Make sure the spawn areas are valid
            for area in spawn_area:
                if area.strip() == "":
                    continue  # empty string is used for default spawn area
                if self.inav.find_area(area) == -1:
                    post_notification(
                        f"Unknown spawn area: '{area}', please check your configuration.",
                        status=NotificationStatus.WARNING,
                    )
                    return None

        # determine area probabilities based on spawn_area_idx
        spawn_area_indices = RandomizerUtil.area_name_to_index(navmesh, spawn_area)
        area_probabilities = RandomizerUtil.area_idx_to_probability(navmesh, spawn_area_indices)

        while not valid:
            if num_attempts > self.config.max_random_attempts:
                has_overlap = True
                break


            spawn_location = navmesh.query_random_point(
                self.name, area_probabilities=area_probabilities, agent_radius=self.config.agent_radius
            )
            if not spawn_location:
                carb.log_error("NavMesh returned no random point. Please check your NavMesh configuration.")
                return carb.Float3(0, 0, 0)

            valid = True
            # Avoid overlapping with existing positions of other agents
            if self.agent_positions:
                for pos in self.agent_positions:
                    distance_threshold = self.config.agent_distance + 2 * self.config.agent_radius
                    if CarbUtil.dist3(carb.Float3(pos), spawn_location) < distance_threshold:
                        valid = False
                        break

            num_attempts += 1

        if has_overlap:
            carb.log_warn(
                "With the current number of agents and the scene asset, "
                "agent overlapping may not be avoided"
            )

        # Update agent_positions set with the new spawn location
        self.agent_positions.add(tuple(spawn_location))
        return spawn_location

    # Command transition map operations

    def get_command_transition_map(self):
        return self.transition_map
