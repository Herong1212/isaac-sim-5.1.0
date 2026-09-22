from .robot_randomizer import RobotRandomizer

"""
Class for the Robot Randomizer
    Initialize special attributes for the robots
"""


class IwHubRandomizer(RobotRandomizer):
    def __init__(self, global_seed):
        super().__init__(global_seed)
        # iw.hub's radius
        self.radius = 0.8
