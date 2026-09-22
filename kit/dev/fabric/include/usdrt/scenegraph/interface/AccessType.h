// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <stdint.h>

namespace usdrt
{

//! Type of access requested
enum class AccessType : uint32_t
{
    eUnspecified, //!< Used as a guard against uninitialized or memset(0) data
    eRead, //!< Read only
    eReadWrite, //!< Read/Write
    eOverwrite //!< Initial value won't be read, but may be overwritten and
               //!< then may be read. Knowing that data is about to be
               //!< overwritten allows USDRT to perform optimizations. For
               //!< example, if data is valid on CPU then requested on GPU
               //!< with eOverwrite, USDRT doesn't have to copy the data
               //!< from CPU to GPU because it knows the GPU is about to
               //!< overwrite it.
};

} // namespace usdrt
