// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

// Define this macro so that other headers that are supposed to have this header included before them can check against
// it.
#define USD_UTILS_INCLUDES

// Include cstdio here so that vsnprintf is properly declared. This is necessary because pyerrors.h has
// #define vsnprintf _vsnprintf which later causes <cstdio> to declare std::_vsnprintf instead of the correct and proper
// std::vsnprintf. By doing it here before everything else, we avoid this nonsense.
#include <cstdio>

// Python must be included first because it monkeys with macros that cause
// TBB to fail to compile in debug mode if TBB is included before Python
#include <boost/python/object.hpp>
#include <pxr/base/gf/rotation.h>
#include <pxr/base/tf/fileUtils.h>
#include <pxr/usd/kind/registry.h>
#include <pxr/usd/pcp/layerStack.h>
#include <pxr/usd/sdf/attributeSpec.h>
#include <pxr/usd/sdf/copyUtils.h>
#include <pxr/usd/sdf/childrenUtils.h>
#include <pxr/usd/sdf/fileFormat.h>
#include <pxr/usd/sdf/relationshipSpec.h>
#include <pxr/usd/usd/editContext.h>
#include <pxr/usd/usd/modelAPI.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usd/stageCache.h>
#include <pxr/usd/usdGeom/bboxCache.h>
#include <pxr/usd/usdGeom/metrics.h>
#include <pxr/usd/usdGeom/xform.h>
#include <pxr/usd/usdShade/material.h>
#include <pxr/usd/usdUtils/stageCache.h>
#include <pxr/usd/usdUtils/stitch.h>
#include <pxr/usd/usdUtils/dependencies.h>
#include <pxr/usd/usd/primCompositionQuery.h>
