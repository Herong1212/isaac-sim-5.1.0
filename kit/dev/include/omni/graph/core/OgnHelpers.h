// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// This file contains helper functions used by the generated .ogn file code.
// You shouldn't normally have to look in here.

#include <omni/core/IObject.h>
#include <omni/graph/core/ogn/AttributeInitializer.h>
#include <omni/graph/core/ogn/Database.h>
#include <omni/graph/core/ogn/Registration.h>
#include <omni/graph/core/ogn/State.h>
#include <omni/graph/core/ogn/Types.h>

// The fabric namespace usage is somewhat more targetted though so it can be explicit
using omni::fabric::IPath;
using omni::fabric::IToken;
