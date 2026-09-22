# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

PERSISTENT_SETTINGS_PREFIX = "/persistent"


class NavMeshSettings:
    DEFAULT_EXCLUDE_RIGID_BODIES_PATH = (
        f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/excludeRigidBodies"
    )

    # ======= Defaults Setting Paths ===========

    # bake settings
    DEFAULT_AGENT_MIN_HEIGHT_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/agentMinHeight"
    DEFAULT_AGENT_MIN_RADIUS_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/agentMinRadius"
    DEFAULT_AGENT_MAX_RADIUS_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/agentMaxRadius"
    DEFAULT_AGENT_MAX_STEP_HEIGHT_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/agentMaxStepHeight"
    DEFAULT_AGENT_MAX_FLOOR_SLOPE_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/agentMaxFloorSlope"
    DEFAULT_AGENT_MIN_ISLAND_RADIUS_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/agentMinIslandRadius"

    DEFAULT_AUTO_REBAKE_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/autoRebakeOnChanges"
    DEFAULT_AUTO_REBAKE_DELAY_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/autoRebakeDelaySeconds"

    # visualization
    DEFAULT_VIZ_GEOM_ENABLE_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/vizGeomEnable"
    DEFAULT_VIZ_SURFACE_ENABLE_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/vizSurfaceEnable"
    DEFAULT_VIZ_OUTLINE_ENABLE_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/vizOutlineEnable"
    DEFAULT_VIZ_OUTLINE_BORDER_ONLY_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/config/vizOutlineBorderOnly"

    # ======= Setting Paths ===========
    VIEW_NAVMESH_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/viewNavMesh"
    USE_GPU_NAVMESH_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/useGpu"
    MAX_VERTICES_PER_TILE_SETTING_PATH = f"{PERSISTENT_SETTINGS_PREFIX}/exts/omni.anim.navigation.core/navMesh/maxVerticesPerTile"

    CACHE_ENABLED_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/cache/enabled"
    EXCLUDE_RIGID_BODIES_PATH = "/exts/omni.anim.navigation.core/navMesh/config/excludeRigidBodies"
    AUTO_REBAKE_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/config/autoRebakeOnChanges"
    AUTO_REBAKE_DELAY_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/config/autoRebakeDelaySeconds"
    AGENT_MIN_HEIGHT_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/config/agentMinHeight"
    AGENT_MIN_RADIUS_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/config/agentMinRadius"
    AGENT_MAX_RADIUS_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/config/agentMaxRadius"
    AGENT_MAX_STEP_HEIGHT_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/config/agentMaxStepHeight"
    AGENT_MAX_FLOOR_SLOPE_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/config/agentMaxFloorSlope"
    AGENT_MIN_ISLAND_RADIUS_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/config/agentMinIslandRadius"

    # visualization
    VIZ_GEOM_ENABLE_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/config/vizGeomEnable"
    VIZ_SURFACE_ENABLE_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/config/vizSurfaceEnable"
    VIZ_OUTLINE_ENABLE_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/config/vizOutlineEnable"
    VIZ_OUTLINE_BORDER_ONLY_SETTING_PATH = "/exts/omni.anim.navigation.core/navMesh/config/vizOutlineBorderOnly"
