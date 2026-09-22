// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>

#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/Enums.h>
#include <omni/fabric/FabricTypes.h>
#include <omni/fabric/IdTypes.h>
#include <omni/fabric/Ordered_Set.h>
#include <omni/fabric/FabricTime.h>

// Shim in new headers as we transition to a proper hourglass model
#include <omni/fabric/core/interface/IFabric.h>
#include <omni/fabric/core/interface/IFabricRingBuffer.h>
#include <omni/fabric/core/interface/IPlatform.h>
#include <omni/fabric/core/interface/IPath.h>

#include <omni/fabric/stage/interface/IStageAtTimeInterval.h>
#include <omni/fabric/stage/interface/IStageReaderWriter.h>
#include <omni/fabric/stage/interface/ISimStageWithHistory.h>
#include <omni/fabric/stage/interface/IPrimBucketList.h>
#include <omni/fabric/stage/interface/ISerializer.h>
#include <omni/fabric/stage/interface/IChangeTracking.h>
#include <omni/fabric/stage/interface/IChangeTrackingConfig.h>
