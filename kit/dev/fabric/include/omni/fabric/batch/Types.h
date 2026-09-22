// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <limits>
#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/core/Enums.h>
#include <omni/fabric/core/Defines.h>
#include <omni/fabric/core/span.h>

#include "BitArray.h"

namespace omni
{
namespace fabric
{
namespace batch
{

enum class FilterMode : uint8_t
{
    Unspecified, // Used as a guard against uninitialized or memset(0) data
    Create,
    Exclude,
    Include,
    Count,
};

enum class DataAccessMode : uint8_t
{
    Unspecified, // Used as a guard against uninitialized or memset(0) data
    Read,
    Write,
    ReadWrite,
    NoAccess,
    Count,
};

// Convenience structs defined to assist with explicit full template specialization for applications that want
// compile-time feature flag switches between different device implementations.
struct CpuDevice
{
};
struct CudaDevice
{
};

using AttributeRef = uint8_t;
using ViewElementRef = uint32_t;
using PageIndex = uint8_t;
using BucketIndex = uint16_t;
using BatchId = uintptr_t;
using BatchRunContextId = uint64_t;
constexpr BatchRunContextId BATCH_RUN_CONTEXT_ID_INVALID = 0;
constexpr BatchRunContextId BATCH_RUN_CONTEXT_ID_INITIAL = 1;

constexpr AttributeRef ATTRIBUTE_REF_MAX = std::numeric_limits<AttributeRef>::max();
using WriteMask = BitArray<ATTRIBUTE_REF_MAX>;

using KernelHookFunction = void (*)(const struct View&, const struct BatchFilter&, void*);

struct BatchPreferences
{
    // Prints Batch internal information to carb::logging
    bool verbose = false;

    // Enable to gathers statistics about the Batch instance
    bool enableStats = false;

    // Desired CPU concurrency width. Determines View partitioning and number of queues used for CPU compute.
    //
    // Default Behavior: 0 means carb::thread::hardware_concurrency()
    //
    // Recommendations is to leave default unless...
    //   - Wider partitioning is desired for thread mapping flexibility over per-thread work cohesion
    //   - Narrower concurrency is needed to mitigage NUMA effects
    size_t cpuConcurrencyWidth = 0;

    // Only applies to Batch instances with multiple Lambdas added.
    //
    // Enable to allow threads participating in run() to proceed to execute Lambda N + 1 after completing some work in
    // Lambda N, even if other threads/work are active and not yet completed.
    //
    // This is useful if Batch has multiple lambdas that don't need read consistency and can execute in any order.
    // Default behavior is disabled, requiring all writes from Lambda N to complete, and threads to be synchronized such that those
    // write are visiible to others, before allowing any participating thread to proceed executing Lambda N + 1.
    bool runUnordered = false;
};

struct ViewGenerationOptions
{
    // Determines the target device that Fabric data will be hosted on at the time the Lambda is executed or the View is
    // generated. GPU devices will use async memcpy to do this, so technically the data copy request will guarantee to
    // be submitted, but the stream may not have been flushed yet.
    omni::fabric::DeviceType device = omni::fabric::DeviceType::eCpu;

    // Determines if View's will provide path information to the user.
    // This is well supported, but it should be noted that requesting paths to be provided will cost significantly more
    // memory, and in the case of GPU kernels, significantly larger memory transfer performance costs for kernel
    // launches.
    bool shouldProvidePaths = false;
};

// == DEVELOPER SETTINGS ==
//
// Use with caution, typically only for testing purposes.
// These are necer cleared automatically by Batch API, they must be manually changed via setDeveloperSettings().
//
struct BatchDeveloperSettings
{
    // Suppresses error logging from printing
    // Primarily used when testing edge cases in unit tests.
    bool suppressErrorLogging = false;

    // Suppresses asserts due to mismatches on BatchRunContextId.
    // Batch should never crash in release from this class of error, which is behaviorally equivalent to setting this to
    // true. Explicitly tested in unit tests.
    bool suppressBatchRunContextIdMismatchAsserts = false;
};

struct AttributeSpecification
{
    FilterMode filter;
    DataAccessMode access;
    AttributeRef ref;
    omni::fabric::AttrNameAndType nameAndType;
};

} // namespace batch
} // namespace fabric
} // namespace omni
