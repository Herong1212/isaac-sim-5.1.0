// Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

namespace omni
{
namespace skel
{

/**
 * Defines the type that tells whether an omni.anim.skelJoint instance uses Fabric.
 */

enum class FabricUseType
{
    From_settings, ///! Use the value from the global settings
    Off, ///! Don't use Fabric, no matter what is set in the settings
    On ///! Use Fabric, no matter what is set in the settings
};

}
}
