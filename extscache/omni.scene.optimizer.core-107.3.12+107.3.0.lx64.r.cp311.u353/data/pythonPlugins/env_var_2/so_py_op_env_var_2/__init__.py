__copyright__ = "Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""


from omni.scene.optimizer.core.operation import Operation

RESULT = None


class EnvVar2PythonOperation(Operation):
    def __init__(self):
        super().__init__(
            "envVar2PythonOperation",
            "Env Var 2 Python Operation",
            "This is a valid Python Operation loaded from an environment variable for testing purposes.",
        )
        self.add_argument(
            "resultString",
            "Result String",
            Operation.ArgumentDisplayTypeText,
            "String to set the global RESULT variable to",
            "",
            placeholder="Hello world!",
        )
        self.add_argument(
            "enumArg",
            "Enum Argument",
            Operation.ArgumentDisplayTypeEnum,
            "Testing enum argument",
            1,
            enum_values={1: "A", 2: "B", 3: "C"},
            join_next=("joinNextGroup", "Testing join next"),
        )
        self.add_argument(
            "minMaxArg",
            "Min Max Argument",
            Operation.ArgumentDisplayTypeFloatSlider,
            "Testing min/max",
            1.0,
            min=0.5,
            max=1.5,
            precision=4,
            visible=False,
            enable_if="True",
            visible_if="False",
            metadata={"test": 123},
        )

    @property
    def author(self):
        return "Scene Optimizer Unit Test"

    @property
    def version(self):
        return (1, 2, 3)

    @property
    def visible(self):
        return True

    def execute(self, args):
        global RESULT
        RESULT = args["resultString"]
        return True


#####################################
# Register Scene Optimizer Plugin
#####################################


def sceneOptimizerPluginInit():
    return EnvVar2PythonOperation()
