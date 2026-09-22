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

struct StageReaderWriterId
{
    constexpr StageReaderWriterId() : id(0){};
    constexpr StageReaderWriterId(uint64_t _id) : id(_id){};
    uint64_t id;

    constexpr bool operator<(const StageReaderWriterId& other) const
    {
        return id < other.id;
    }
    constexpr bool operator==(const StageReaderWriterId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const StageReaderWriterId& other) const
    {
        return id != other.id;
    }
};

static_assert(std::is_standard_layout<StageReaderWriterId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr StageReaderWriterId kInvalidStageReaderWriterId { (uint64_t)0 };

struct StageAtTimeIntervalId
{
    constexpr StageAtTimeIntervalId() : id(0){};
    constexpr StageAtTimeIntervalId(uint64_t _id) : id(_id){};
    uint64_t id;

    constexpr bool operator<(const StageAtTimeIntervalId& other) const
    {
        return id < other.id;
    }
    constexpr bool operator==(const StageAtTimeIntervalId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const StageAtTimeIntervalId& other) const
    {
        return id != other.id;
    }
};
static_assert(std::is_standard_layout<StageAtTimeIntervalId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr StageAtTimeIntervalId kInvalidStageAtTimeIntervalId { (uint64_t)0 };

struct SimStageWithHistoryId
{
    constexpr SimStageWithHistoryId() : id(0){};
    constexpr SimStageWithHistoryId(uint64_t _id) : id(_id){};
    uint64_t id;

    constexpr bool operator<(const SimStageWithHistoryId& other) const
    {
        return id < other.id;
    }
    constexpr bool operator==(const SimStageWithHistoryId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const SimStageWithHistoryId& other) const
    {
        return id != other.id;
    }
};
static_assert(std::is_standard_layout<SimStageWithHistoryId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr SimStageWithHistoryId kInvalidSimStageWithHistoryId { (uint64_t)0 };

struct PrimBucketListId
{
    uint64_t id;

    constexpr bool operator<(const PrimBucketListId& other) const
    {
        return id < other.id;
    }
    constexpr bool operator==(const PrimBucketListId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const PrimBucketListId& other) const
    {
        return id != other.id;
    }
};
static_assert(std::is_standard_layout<PrimBucketListId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr PrimBucketListId kInvalidPrimBucketListId { (uint64_t)0 };

enum class PrimBucketListOwnership
{
    eOwned,     // when constructed from id by a thread that owns it, do not increment refcount
    eDetached,  // when constructing from id detached via reset(), do not increment refcount
    eShared,    // when copying a PrimBucketList, increment refcount
};

struct ListenerId
{
    uint64_t id;

    bool operator==(ListenerId other) const
    {
        return id == other.id;
    }
    bool operator!=(ListenerId other) const
    {
        return id != other.id;
    }
};
static_assert(std::is_standard_layout<ListenerId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr ListenerId kInvalidListenerId = { (uint64_t)0 };

// Magic listener for DS Logging workflow... DO NOT USE.. So large no one should track enough things
// to reach this. 
static constexpr ListenerId kUsdValidFalseDSONLY = {std::numeric_limits<uint64_t>::max()};


} // namespace fabric
} // namespace omni

// Custom hashes as needed for types.
namespace std
{

template <>
class hash<omni::fabric::ListenerId>
{
public:
    size_t operator()(const omni::fabric::ListenerId& key) const
    {
        return key.id;
    }
};


} // namespace std
