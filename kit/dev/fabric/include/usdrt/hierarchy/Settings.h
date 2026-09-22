// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// The simplest way of sharing Carbonite Settings Keys without any linking between libraries

#define USDRT_HIERARCHY_RECOMPUTEALLABOVETHRESHOLD "/app/usdrt/hierarchy/recomputeAllAboveThreshold" // deprecated, no longer in use
#define USDRT_HIERARCHY_PROGRESSIVEEXTENTSUPDATE "/app/usdrt/hierarchy/progressiveExtentsUpdate"  // Set this to 0 to update all extents on each change
#define USDRT_HIERARCHY_FASTLEAFUPDATES "/app/usdrt/hierarchy/fastLeafUpdates"
#define USDRT_HIERARCHY_CUBRICUPDATEHOST "/app/usdrt/hierarchy/cubricUpdateHost"
#define USDRT_HIERARCHY_CUBRICUPDATEDEVICE "/app/usdrt/hierarchy/cubricUpdateDevice"
#define USDRT_HIERARCHY_PARTIAL_GPU_UPDATE "/app/usdrt/hierarchy/partialGpuUpdate"
