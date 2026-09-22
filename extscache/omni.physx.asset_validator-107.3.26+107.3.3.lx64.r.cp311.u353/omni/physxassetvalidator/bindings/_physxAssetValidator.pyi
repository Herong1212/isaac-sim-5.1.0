"""pybind11 omni.physx.asset_validator bindings"""
from __future__ import annotations
import omni.physxassetvalidator.bindings._physxAssetValidator
import typing

__all__ = [
    "IPhysxAssetValidator",
    "acquire_physx_asset_validator_interface",
    "release_physx_asset_validator_interface",
    "release_physx_asset_validator_interface_scripting"
]


class IPhysxAssetValidator():
    def backward_compatibility_check(self, stage_id: int) -> bool: 
        """
        Check if the stage is backward compatible with the current version of the asset validator.
        """
    def convex_gpu_compatibility_is_valid(self, stage_id: int, prim_id: int) -> bool: 
        """
        Check if resulting convex mesh is GPU compatible for given prim.
        Stage must be already parsed and PhysX objects already created prior to calling this function (use IPhysX::forceLoadPhysicsFromUsd or equivalent)
        """
    def get_backward_compatibility_log(self) -> str: 
        """
        Get the log of the backward compatibility check.
        """
    def joint_state_apply_fix(self, stage_id: int, prim_id: int) -> None: 
        """
        Modifies bodies of the articulations to make them match what's specified by applied Joint States APIs. 
        Stage must be already parsed and PhysX objects already created prior to calling this function (use IPhysX::forceLoadPhysicsFromUsd or equivalent)

        Args:
            stage_id: Stage Id containing the USD Path to check
            prim_id: USD Path of prim with an applied ArticulationRootAPI
        """
    def joint_state_is_valid(self, stage_id: int, prim_id: int) -> bool: 
        """
        Check if Joint States for given articulation root api are coherent with body transforms for the articulation.
        Stage must be already parsed and PhysX objects already created prior to calling this function (use IPhysX::forceLoadPhysicsFromUsd or equivalent)

        Args:
            stage_id: Stage Id containing the USD Path to check
            prim_id: USD Path of prim with an applied ArticulationRootAPI

        Returns:
            bool: True if the joint states are coherent with body transformations of the given ArticulationRootAPI
        """
    def run_backward_compatibility_check(self, stage_id: int) -> None: 
        """
        Run backward compatibility check on the stage.
        """
    pass
def acquire_physx_asset_validator_interface(plugin_name: str = None, library_path: str = None) -> IPhysxAssetValidator:
    pass
def release_physx_asset_validator_interface(arg0: IPhysxAssetValidator) -> None:
    pass
def release_physx_asset_validator_interface_scripting(arg0: IPhysxAssetValidator) -> None:
    pass
