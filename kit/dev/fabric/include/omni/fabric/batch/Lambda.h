// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Types.h"

namespace omni
{
namespace fabric
{
namespace batch
{

// The core definition of a Lambda.
// - options:      Determines various aspects of View generation. See ViewGenerationOptions definition for more details.
//
// - filter:       Use by the Batch to filter Fabric data prior to executing the Lambda
//
// - hook:         Callback where control is passed back to this once the Lambda is ready to be executed.
//                 CPU hooks should expect to be called concurrently.
//
// - userData:     User-provided data. Batch hands this back to each invocation of the hook function. If concurrent
//                 writes are required into userData, the user must implement their own multi-processing mechanisms.
//
struct Lambda
{
    ViewGenerationOptions options;
    const struct BatchFilter* filter;
    KernelHookFunction hook;
    void* userData;
    size_t userDataSize; // DEPRECATED. Left for backwards compatibility.
};

} // namespace batch
} // namespace fabric
} // namespace omni
