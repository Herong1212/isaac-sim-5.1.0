import omni.anim.graph.core as ag
from pxr import Usd, UsdUtils, Sdf, Tf


ERROR_CODE_MESSAGE = [
    "No Error",
    "Missing Input",
    "Invalid Input",
    "Missing Default State",
    "Missing Transition Input",
    "Duplicate Joint",
    "Missing Joint",
    "Missing Parent Joint",
    "Duplicate Blend Shape",
    "Retarget Solver Missing Tag",
    "Retarget Solver Invalid Chain",
    "Dependency Error",
    "Missing Set Effector Nodes",
    "Error Unknown"
]

ERROR_CODE_DEPS_ERROR_INDEX = 11

ERROR_INPUT_ARGUMENT_NAMES = {
    "AnimationGraph": ["Pose (Final)"],
    "StateMachine": ["Pose"],
    "State": ["Pose (Final)"],
    "Transition": ["Condition (Final)"],
    "ConditionAND": ["Condition 0", "Condition 1"],
    "ConditionOR": ["Condition 0", "Condition 1"],
    "Blend": ["Pose 0", "Pose 1", "Blend Weight", "Joint Position Blend Mode", "Joint Rotation Blend Mode", "Blendshape Blend Mode", "Pass Through Mode"],
    "LookAtIK": ["Pose", "Target Position", "Blend Weight", "Start Joint", "End Joint"],
    "MotionMatching": ["Path Points", "Movement Direction", "Forward Direction"],
    "Filter": ["Pose"],
    "FullBodyIK": ["Pose"],
    "SetEffector": ["Pose", "Position", "Rotation", "Weight", "Effector"],
    "TwoBoneIK": ["Pose", "Target Position", "Blend Weight", "Start Joint", "Hinge Joint", "End Joint"],
}


def asset_error_to_message(stage, asset_path, error_code, argument) -> str:
    asset_prim = stage.GetPrimAtPath(asset_path)
    asset_type = asset_prim.GetTypeName()
    message_details = ""
    # handle gathering the missing or invalid inputs
    if error_code < 2 and asset_type in ERROR_INPUT_ARGUMENT_NAMES:
        argument_names = ERROR_INPUT_ARGUMENT_NAMES[asset_type]
        if argument < len(argument_names):
            message_details = f": {argument_names[argument]}"
    elif error_code > 2 and error_code < 6:
        message_details = f": {argument}"

    return f"{ERROR_CODE_MESSAGE[error_code]} {message_details}"
