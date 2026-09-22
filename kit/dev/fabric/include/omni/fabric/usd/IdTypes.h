// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <cstdint>
#include <functional>
#include <stddef.h>
#include <type_traits>

namespace omni
{
namespace fabric
{

struct UsdStageId
{
    constexpr UsdStageId() : id(0){};
    constexpr UsdStageId(uint64_t _id) : id(_id){};
    constexpr UsdStageId(long _id) : id((uint64_t)_id){};
    uint64_t id;
    constexpr bool operator<(const UsdStageId& other) const
    {
        return id < other.id;
    }
    constexpr bool operator==(const UsdStageId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const UsdStageId& other) const
    {
        return id != other.id;
    }
};

static_assert(std::is_standard_layout<UsdStageId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr UsdStageId kUninitializedStage{ (uint64_t)0 };

} // namespace fabric
} // namespace omni

// Custom hashes as needed for types.
namespace std
{

template <>
class hash<omni::fabric::UsdStageId>
{
public:
    size_t operator()(const omni::fabric::UsdStageId& key) const
    {
        return key.id;
    }
};
} // namespace std
