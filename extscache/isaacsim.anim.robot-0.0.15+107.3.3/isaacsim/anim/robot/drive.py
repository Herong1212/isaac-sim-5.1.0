from abc import ABC, abstractmethod
from pxr import Gf
import carb

from isaacsim.anim.robot.state_machine import StateMachine
from isaacsim.anim.robot.agent.base_agent import BaseAgent
from omni.metropolis.utils.math_util import MathUtil


class DriveBase(ABC):
    """Base class for all drive types."""

    def __init__(self, agent: BaseAgent, state_machine: StateMachine) -> None:
        self._agent = agent
        self._state_machine = state_machine

    @abstractmethod
    def update(self, path: list[Gf.Vec3d], dt: float) -> None:
        """
        Update drive state.
        This method will be called at each frame during a GoTo command.

        Args:
            path: List of target positions to navigate to.
            dt: Time since the last frame.
        """
        pass


class OmniDirectionalDrive(DriveBase):
    """
    Drive class for omni-directional agents.

    Omni-directional agents can move in all directions without turning and have a constant linear velocity.
    """

    def update(self, path: list[Gf.Vec3d], dt: float) -> None:
        current_position_gf = self._agent.prim.GetAttribute("xformOp:translate").Get()
        target_pos = Gf.Vec3d(*path[0])
        target_vec = (target_pos - current_position_gf).GetNormalized()
        target_vec[2] = 0.0  # zero-out the z component

        if self._state_machine.is_in_state("idle"):
            self._state_machine.transition_to_state("forward")
        elif self._state_machine.is_in_state("forward"):
            # Snap the agent to the target position if close enough
            distance = MathUtil.get_euclidean_distance(current_position_gf, target_pos)
            if distance < dt * self._agent.linear_velocity:
                self._agent.prim.GetAttribute("xformOp:translate").Set(target_pos)
                path.pop(0)
                self._state_machine.transition_to_state("idle")
                return

            new_pos = current_position_gf + target_vec * self._agent.linear_velocity * dt
            self._agent.prim.GetAttribute("xformOp:translate").Set(new_pos)


class DifferentialDrive(DriveBase):
    """
    Drive class for differential drive agents.

    Differential drive agents can turn in place and have a constant linear velocity.
    They move in a straight line by turning towards the target direction and driving forward.
    """

    def update(self, path: list[Gf.Vec3d], dt: float) -> None:
        current_position_gf = self._agent.prim.GetAttribute("xformOp:translate").Get()
        current_rotation_gf_quat = self._agent.prim.GetAttribute("xformOp:orient").Get()
        target_pos = Gf.Vec3d(*path[0])
        target_vec = (target_pos - current_position_gf).GetNormalized()
        target_vec[2] = 0.0  # zero-out the z component
        rot_to_target = Gf.Rotation(self._agent.forward_vec, target_vec).GetQuat()

        if self._state_machine.is_in_state("idle"):
            # Decide rotation direction
            rot_dist = MathUtil.get_quaternion_distance(current_rotation_gf_quat, rot_to_target)
            self._state_machine.transition_to_state("turn_left" if rot_dist > 0 else "turn_right")

        elif self._state_machine.is_in_state("turn_right") or self._state_machine.is_in_state("turn_left"):
            rot_dist = MathUtil.get_quaternion_distance(current_rotation_gf_quat, rot_to_target)
            rot_sign = 1 if rot_dist > 0 else -1
            rot_quat = Gf.Rotation(Gf.Vec3d.ZAxis(), rot_sign * self._agent.angular_velocity * dt).GetQuat()

            self._agent.prim.GetAttribute("xformOp:orient").Set(rot_quat * current_rotation_gf_quat)

            # Snap to target direction if close enough
            distance = abs(MathUtil.get_quaternion_distance(current_rotation_gf_quat, rot_to_target))
            if distance < dt * self._agent.angular_velocity:
                self._agent.prim.GetAttribute("xformOp:orient").Set(rot_to_target)
                self._state_machine.transition_to_state("forward")
                return

        elif self._state_machine.is_in_state("forward"):
            # Snap to target position if close enough
            distance = MathUtil.get_euclidean_distance(current_position_gf, target_pos)
            if distance < dt * self._agent.linear_velocity:
                self._agent.prim.GetAttribute("xformOp:translate").Set(target_pos)
                path.pop(0)
                self._state_machine.transition_to_state("idle")
                return

            new_pos = current_position_gf + target_vec * self._agent.linear_velocity * dt
            self._agent.prim.GetAttribute("xformOp:translate").Set(new_pos)

        else:
            carb.log_error("Agent is not in any valid state")


class AckermannDrive(DriveBase):
    """Drive class for Ackermann steering agents (like cars)."""

    def update(self, path: list[Gf.Vec3d], dt: float) -> None:
        # TODO: Implement Ackermann steering
        pass
