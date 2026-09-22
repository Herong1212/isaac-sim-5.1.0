from .robot_randomizer import RobotRandomizer

"""
Class for the Robot Randomizer
    Initialize special attributes for the robots
"""


class CarterRandomizer(RobotRandomizer):
    def __init__(self, global_seed):
        super().__init__(global_seed)
        # Carter's radius
        self.radius = 0.6