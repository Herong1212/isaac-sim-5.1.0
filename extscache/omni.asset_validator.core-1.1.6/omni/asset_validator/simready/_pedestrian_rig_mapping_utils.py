# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
__all__ = ["JointsPreset", "RigMapping", "find_best_rig_mapping"]

from dataclasses import dataclass
from enum import Enum

from pxr import Sdf, UsdSkel


@dataclass(frozen=True)
class RigMapping:
    name: str
    version: str
    mappings: dict[str, str]


class JointsPreset(str, Enum):
    HEAD = "Head"
    NECK = "Neck"
    CHEST = "Chest"
    PELVIS = "Pelvis"
    LEFT_SHOULDER = "Left_Shoulder"
    LEFT_ELBOW = "Left_Elbow"
    LEFT_HAND = "Left_Hand"
    LEFT_THUMB = "Left_Thumb"
    LEFT_INDEX = "Left_Index"
    LEFT_MIDDLE = "Left_Middle"
    LEFT_RING = "Left_Ring"
    LEFT_PINKY = "Left_Pinky"
    LEFT_THIGH = "Left_Thigh"
    LEFT_KNEE = "Left_Knee"
    LEFT_FOOT = "Left_Foot"
    LEFT_TOE = "Left_Toe"
    RIGHT_SHOULDER = "Right_Shoulder"
    RIGHT_ELBOW = "Right_Elbow"
    RIGHT_HAND = "Right_Hand"
    RIGHT_THUMB = "Right_Thumb"
    RIGHT_INDEX = "Right_Index"
    RIGHT_MIDDLE = "Right_Middle"
    RIGHT_RING = "Right_Ring"
    RIGHT_PINKY = "Right_Pinky"
    RIGHT_THIGH = "Right_Thigh"
    RIGHT_KNEE = "Right_Knee"
    RIGHT_FOOT = "Right_Foot"
    RIGHT_TOE = "Right_Toe"


_RIG_MAPPING_PRESETS: list[RigMapping] = [
    RigMapping(
        name="Omniverse Default",
        version="105.0.0",
        mappings=dict(
            [
                (JointsPreset.HEAD, "Head"),
                (JointsPreset.NECK, "Neck1"),
                (JointsPreset.CHEST, "Chest"),
                (JointsPreset.PELVIS, "Pelvis"),
                (JointsPreset.LEFT_SHOULDER, "L_UpArm"),
                (JointsPreset.LEFT_ELBOW, "L_LoArm"),
                (JointsPreset.LEFT_HAND, "L_Wrist"),
                (JointsPreset.LEFT_THUMB, "L_ThumbFingerEnd"),
                (JointsPreset.LEFT_INDEX, "L_IndexFingerEnd"),
                (JointsPreset.LEFT_MIDDLE, "L_MiddleFingerEnd"),
                (JointsPreset.LEFT_RING, "L_RingFingerEnd"),
                (JointsPreset.LEFT_PINKY, "L_PinkyFingerEnd"),
                (JointsPreset.LEFT_THIGH, "L_UpLeg"),
                (JointsPreset.LEFT_KNEE, "L_LoLeg"),
                (JointsPreset.LEFT_FOOT, "L_Ankle"),
                (JointsPreset.LEFT_TOE, "L_Ball"),
                (JointsPreset.RIGHT_SHOULDER, "R_UpArm"),
                (JointsPreset.RIGHT_ELBOW, "R_LoArm"),
                (JointsPreset.RIGHT_HAND, "R_Wrist"),
                (JointsPreset.RIGHT_THUMB, "R_ThumbFingerEnd"),
                (JointsPreset.RIGHT_INDEX, "R_IndexFingerEnd"),
                (JointsPreset.RIGHT_MIDDLE, "R_MiddleFingerEnd"),
                (JointsPreset.RIGHT_RING, "R_RingFingerEnd"),
                (JointsPreset.RIGHT_PINKY, "R_PinkyFingerEnd"),
                (JointsPreset.RIGHT_THIGH, "R_UpLeg"),
                (JointsPreset.RIGHT_KNEE, "R_LoLeg"),
                (JointsPreset.RIGHT_FOOT, "R_Ankle"),
                (JointsPreset.RIGHT_TOE, "R_Ball"),
            ]
        ),
    ),
    RigMapping(
        name="Omniverse Digital Human",
        version="107.0.0",
        mappings=dict(
            [
                (JointsPreset.HEAD, "Head"),
                (JointsPreset.NECK, "Neck1"),
                (JointsPreset.CHEST, "Chest"),
                (JointsPreset.PELVIS, "Hips"),
                (JointsPreset.LEFT_SHOULDER, "LeftArm"),
                (JointsPreset.LEFT_ELBOW, "LeftForeArm"),
                (JointsPreset.LEFT_HAND, "LeftHand"),
                (JointsPreset.LEFT_THUMB, "LeftHandThumb3"),
                (JointsPreset.LEFT_INDEX, "LeftHandIndex4"),
                (JointsPreset.LEFT_MIDDLE, "LeftHandMiddle4"),
                (JointsPreset.LEFT_RING, "LeftHandRing4"),
                (JointsPreset.LEFT_PINKY, "LeftHandPinky4"),
                (JointsPreset.LEFT_THIGH, "LeftLeg"),
                (JointsPreset.LEFT_KNEE, "LeftShin"),
                (JointsPreset.LEFT_FOOT, "LeftFoot"),
                (JointsPreset.LEFT_TOE, "LeftToeBase"),
                (JointsPreset.RIGHT_SHOULDER, "RightArm"),
                (JointsPreset.RIGHT_ELBOW, "RightForeArm"),
                (JointsPreset.RIGHT_HAND, "RightHand"),
                (JointsPreset.RIGHT_THUMB, "RightHandThumb3"),
                (JointsPreset.RIGHT_INDEX, "RightHandIndex4"),
                (JointsPreset.RIGHT_MIDDLE, "RightHandMiddle4"),
                (JointsPreset.RIGHT_RING, "RightHandRing4"),
                (JointsPreset.RIGHT_PINKY, "RightHandPinky4"),
                (JointsPreset.RIGHT_THIGH, "RightLeg"),
                (JointsPreset.RIGHT_KNEE, "RightShin"),
                (JointsPreset.RIGHT_FOOT, "RightFoot"),
                (JointsPreset.RIGHT_TOE, "RightToeBase"),
            ]
        ),
    ),
    RigMapping(
        name="Reallusion",
        version="107.0.0",
        mappings=dict(
            [
                (JointsPreset.HEAD, "Head"),
                (JointsPreset.NECK, "NeckTwist01"),
                (JointsPreset.PELVIS, "Hip"),
                (JointsPreset.CHEST, "Spine02"),
                (JointsPreset.LEFT_SHOULDER, "L_Upperarm"),
                (JointsPreset.LEFT_ELBOW, "L_Forearm"),
                (JointsPreset.LEFT_HAND, "L_Hand"),
                (JointsPreset.LEFT_THUMB, "L_Thumb3"),
                (JointsPreset.LEFT_INDEX, "L_Index3"),
                (JointsPreset.LEFT_MIDDLE, "L_Mid3"),
                (JointsPreset.LEFT_RING, "L_Ring3"),
                (JointsPreset.LEFT_PINKY, "L_Pinky3"),
                (JointsPreset.LEFT_THIGH, "L_Thigh"),
                (JointsPreset.LEFT_KNEE, "L_Calf"),
                (JointsPreset.LEFT_FOOT, "L_Foot"),
                (JointsPreset.LEFT_TOE, "L_ToeBase"),
                (JointsPreset.RIGHT_SHOULDER, "R_Upperarm"),
                (JointsPreset.RIGHT_ELBOW, "R_Forearm"),
                (JointsPreset.RIGHT_HAND, "R_Hand"),
                (JointsPreset.RIGHT_THUMB, "R_Thumb3"),
                (JointsPreset.RIGHT_INDEX, "R_Index3"),
                (JointsPreset.RIGHT_MIDDLE, "R_Mid3"),
                (JointsPreset.RIGHT_RING, "R_Ring3"),
                (JointsPreset.RIGHT_PINKY, "R_Pinky3"),
                (JointsPreset.RIGHT_THIGH, "R_Thigh"),
                (JointsPreset.RIGHT_KNEE, "R_Calf"),
                (JointsPreset.RIGHT_FOOT, "R_Foot"),
                (JointsPreset.RIGHT_TOE, "R_ToeBase"),
            ]
        ),
    ),
    RigMapping(
        name="Unreal Mannequin",
        version="107.0.0",
        mappings=dict(
            [
                (JointsPreset.HEAD, "head"),
                (JointsPreset.NECK, "neck_01"),
                (JointsPreset.PELVIS, "pelvis"),
                (JointsPreset.CHEST, "spine_03"),
                (JointsPreset.LEFT_SHOULDER, "upperarm_l"),
                (JointsPreset.LEFT_ELBOW, "lowerarm_l"),
                (JointsPreset.LEFT_HAND, "hand_l"),
                (JointsPreset.LEFT_THUMB, "thumb_03_l"),
                (JointsPreset.LEFT_INDEX, "index_03_l"),
                (JointsPreset.LEFT_MIDDLE, "middle_03_l"),
                (JointsPreset.LEFT_RING, "ring_03_l"),
                (JointsPreset.LEFT_PINKY, "pinky_03_l"),
                (JointsPreset.LEFT_THIGH, "thigh_l"),
                (JointsPreset.LEFT_KNEE, "calf_l"),
                (JointsPreset.LEFT_FOOT, "foot_l"),
                (JointsPreset.LEFT_TOE, "ball_l"),
                (JointsPreset.RIGHT_SHOULDER, "upperarm_r"),
                (JointsPreset.RIGHT_ELBOW, "lowerarm_r"),
                (JointsPreset.RIGHT_HAND, "hand_r"),
                (JointsPreset.RIGHT_THUMB, "thumb_03_r"),
                (JointsPreset.RIGHT_INDEX, "index_03_r"),
                (JointsPreset.RIGHT_MIDDLE, "middle_03_r"),
                (JointsPreset.RIGHT_RING, "ring_03_r"),
                (JointsPreset.RIGHT_PINKY, "pinky_03_r"),
                (JointsPreset.RIGHT_THIGH, "thigh_r"),
                (JointsPreset.RIGHT_KNEE, "calf_r"),
                (JointsPreset.RIGHT_FOOT, "foot_r"),
                (JointsPreset.RIGHT_TOE, "ball_r"),
            ]
        ),
    ),
]


def _get_joint_names(skeleton: UsdSkel.Skeleton) -> list[str]:
    joint_attr = skeleton.GetJointsAttr()
    if not joint_attr:
        return []

    joint_names = []
    for joint in joint_attr.Get():
        joint_names.append(Sdf.Path(joint).name)

    return joint_names


def find_best_rig_mapping(skeleton: UsdSkel.Skeleton):
    joints = _get_joint_names(skeleton)

    best_rig_match_score = 0
    best_rig_mapping = None
    rig_missing_joints = None
    for rig_mapping in _RIG_MAPPING_PRESETS:
        missing_joints = []
        score = 0
        for expected_joint in rig_mapping.mappings.values():
            if expected_joint in joints:
                score += 1
            else:
                missing_joints.append(expected_joint)

        if score > best_rig_match_score:
            best_rig_mapping = rig_mapping
            best_rig_match_score = score
            rig_missing_joints = missing_joints

    return best_rig_mapping, rig_missing_joints
