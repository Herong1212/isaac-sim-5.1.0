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
#include <limits>
#include <stddef.h>
#include <type_traits>

namespace omni
{
namespace fabric
{

struct BucketId
{
    constexpr BucketId() : id(0){};
    constexpr BucketId(uint64_t _id) : id(_id){};
    uint64_t id;
    constexpr bool operator<(const BucketId& other) const
    {
        return id < other.id;
    }
    constexpr bool operator<=(const BucketId& other) const
    {
        return id <= other.id;
    }
    constexpr bool operator==(const BucketId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const BucketId& other) const
    {
        return id != other.id;
    }
    constexpr BucketId& operator++()
    {
        ++id;
        return *this;
    }
    constexpr BucketId& operator--()
    {
        --id;
        return *this;
    }
    constexpr explicit operator size_t() const
    {
        return id;
    }
};

static_assert(std::is_standard_layout<BucketId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr BucketId kInvalidBucketId{ 0xffff'ffff'ffff'ffff };

struct FabricId
{
    constexpr FabricId() : id(0){};
    constexpr FabricId(uint64_t _id) : id(_id){};
    uint64_t id;
    constexpr bool operator<(const FabricId& other) const
    {
        return id < other.id;
    }
    constexpr bool operator==(const FabricId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const FabricId& other) const
    {
        return id != other.id;
    }
};

static_assert(std::is_standard_layout<FabricId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr FabricId kInvalidFabricId{ uint64_t(0) };

struct RingBufferId
{
    constexpr RingBufferId() : id(0){};
    constexpr RingBufferId(uint64_t _id) : id(_id){};
    uint64_t id;

    constexpr bool operator<(const RingBufferId& other) const
    {
        return id < other.id;
    }
    constexpr bool operator==(const RingBufferId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const RingBufferId& other) const
    {
        return id != other.id;
    }
};
static_assert(std::is_standard_layout<RingBufferId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr RingBufferId kInvalidRingBufferId{ uint64_t(0) };

struct LockedRingBufferWindowId
{
    constexpr LockedRingBufferWindowId() : id(0){};
    constexpr LockedRingBufferWindowId(uint64_t _id) : id(_id){};
    uint64_t id;

    constexpr bool operator<(const LockedRingBufferWindowId& other) const
    {
        return id < other.id;
    }
    constexpr bool operator==(const LockedRingBufferWindowId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const LockedRingBufferWindowId& other) const
    {
        return id != other.id;
    }
};
static_assert(std::is_standard_layout<LockedRingBufferWindowId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr LockedRingBufferWindowId kInvalidLockedRingBufferWindowId{ std::numeric_limits<uint64_t>::max() };


struct FabricSampleStorageId
{
    constexpr FabricSampleStorageId() : id(0){};
    constexpr FabricSampleStorageId(uint64_t _id) : id(_id){};
    uint64_t id;

    constexpr bool operator<(const FabricSampleStorageId& other) const
    {
        return id < other.id;
    }
    constexpr bool operator==(const FabricSampleStorageId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const FabricSampleStorageId& other) const
    {
        return id != other.id;
    }
};
static_assert(std::is_standard_layout<FabricSampleStorageId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr FabricSampleStorageId kInvalidFabricSampleStorageId{ uint64_t(0) };

struct LockedReadSamplesId
{
    constexpr LockedReadSamplesId() : id(0){};
    constexpr LockedReadSamplesId(uint64_t _id) : id(_id){};
    uint64_t id;

    constexpr bool operator<(const LockedReadSamplesId& other) const
    {
        return id < other.id;
    }
    constexpr bool operator==(const LockedReadSamplesId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const LockedReadSamplesId& other) const
    {
        return id != other.id;
    }
};
static_assert(std::is_standard_layout<LockedReadSamplesId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr LockedReadSamplesId kInvalidLockedReadSamplesId{ std::numeric_limits<uint64_t>::max() };


struct LockedWriteSampleId
{
    constexpr LockedWriteSampleId() : id(0){};
    constexpr LockedWriteSampleId(uint64_t _id) : id(_id){};
    uint64_t id;

    constexpr bool operator<(const LockedWriteSampleId& other) const
    {
        return id < other.id;
    }
    constexpr bool operator==(const LockedWriteSampleId& other) const
    {
        return id == other.id;
    }
    constexpr bool operator!=(const LockedWriteSampleId& other) const
    {
        return id != other.id;
    }
};
static_assert(std::is_standard_layout<LockedWriteSampleId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr LockedWriteSampleId kInvalidLockedWriteSampleId{ std::numeric_limits<uint64_t>::max() };


} // namespace fabric
} // namespace omni

// Custom hashes as needed for types.
namespace std
{

template <>
class hash<omni::fabric::BucketId>
{
public:
    size_t operator()(const omni::fabric::BucketId& key) const
    {
        return key.id;
    }
};

template <>
class hash<omni::fabric::FabricId>
{
public:
    size_t operator()(const omni::fabric::FabricId& key) const
    {
        return key.id;
    }
};
} // namespace std
