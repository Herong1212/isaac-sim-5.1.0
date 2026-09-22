// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#pragma message ("OgnWrappers.h is deprecated - include the specific omni/graph/core/ogn/ file you require")

// This file contains simple interface classes which wrap data in the OGN database for easier use
//
// WARNING: These interfaces are subject to change without warning and are only meant to be used by generated code.
//          If you call them directly you may have to modify your code when they change.
//

#include <omni/graph/core/CppWrappers.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/TemplateUtils.h>
#include <omni/graph/core/ogn/Types.h>
#include <omni/graph/core/ogn/StringAttribute.h>
#include <omni/graph/core/ogn/ArrayAttribute.h>
#include <omni/graph/core/ogn/SimpleAttribute.h>
