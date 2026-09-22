# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

get_filename_component(OMNI_ISAAC_SIM_SCHEMAS_CMAKE_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)

include("${OMNI_ISAAC_SIM_SCHEMAS_CMAKE_DIR}/isaacSensorSchemaTargets.cmake")
include("${OMNI_ISAAC_SIM_SCHEMAS_CMAKE_DIR}/rangeSensorSchemaTargets.cmake")
