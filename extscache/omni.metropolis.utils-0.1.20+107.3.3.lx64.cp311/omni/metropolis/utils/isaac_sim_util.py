import isaacsim.storage.native
from omni.metropolis.utils.carb_util import CarbSettingUtil
from typing import Optional


def get_isaac_sim_asset_root_path() -> Optional[str]:
    """
    Get the Isaac Sim asset root path from carb settings.

    Returns:
        Optional[str]: The asset root path if found and valid, None otherwise.
    """
    return CarbSettingUtil.get_value_by_key("/persistent/isaac/asset_root/default")
