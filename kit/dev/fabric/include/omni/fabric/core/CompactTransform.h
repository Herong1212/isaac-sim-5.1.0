// Copyright (c) 2019-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once


#include <carb/Defines.h>


namespace omni
{
namespace fabric
{

/**
 * @struct CompactTransform
 *
 * @brief Stores a transform for instances in TRS components with mixed precision. This can be used as
 * an alternative for omni:fabric::worldMatrix/localMatrix in instances to save memory.
 */
struct CompactTransform
{
    double position[3];
    float orientation[4];
    float scale[3];

};

static_assert(sizeof(CompactTransform) == 56UL, "Update omni::fabric::Type::baseTypeSize() should you change this size/alignment");


} // namespace fabric
} // namespace omni