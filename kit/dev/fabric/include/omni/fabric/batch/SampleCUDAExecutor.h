// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "SampleExecutor.h"

namespace omni
{
namespace fabric
{
namespace batch
{

// SampleCUDAExecutor implements an example way of driving execution over Batch API in deferred mode.
// This example executes on the calling thread.
//
// CUDA Lambda's use the same top-level executor mechanisms as a single-threaded SampleExecutor because most of the
// multiprocessing magic happens in CUDA / on GPU after the kernel launch. This type alias exists just for ease of
// discovery.
//
using SampleCUDAExecutor = SampleExecutor;

} // namespace batch
} // namespace fabric
} // namespace omni
