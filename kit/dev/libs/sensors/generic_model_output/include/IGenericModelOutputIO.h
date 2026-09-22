// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include "GenericModelOutputTypes.h"
#include "GMOAuxiliaryDataTypes.h"

#include <memory>


namespace omni::sensors
{


enum AccessType
{
    READ = 0,
    RECORD_BASIC = 1,
    RECORD_FULL = 2
};

enum GenericModelOutputFlags : uint8_t
{
    BUFFER_COMPLETE = 1 << 0,
    RECORD_COMPLETE = 1 << 1,
};

struct GMOIOConfig
{
    AccessType accessType{ AccessType::RECORD_FULL };
    bool onlyValid{ false };
    bool loop{ false };
    uint32_t maxPoints{ 0 };
    char* fileName{ nullptr };
    char* groupName{ nullptr };
    char* clientName{ nullptr };
};


class IGenericModelOutputIO
{
public:
    virtual ~IGenericModelOutputIO(){};

    virtual void init(const GMOIOConfig& cfg) = 0;
    // Could add frame id or timestamp as argument(s)
    virtual void writeModelOutput(const GenericModelOutput& modelOutput) = 0;

    // frameId == -1 -> read frames in order; frameId > -1 -> read specific frame
    virtual GenericModelOutput readModelOutput(const char* clientName = nullptr, const int frameId = -1) = 0;

    // Native recording is done over udp packets -- accumulate binary udp packets until one point cloud buffer is
    // complete
    virtual void addPacket(void* packet, const size_t packetSize) = 0;
};

using IGenericModelOutputIOPtr = std::unique_ptr<IGenericModelOutputIO>;

#ifdef _WIN32
#   ifdef GENERIC_MODEL_OUTPUT_IO_EXPORTS
#       define GENERIC_MODEL_OUTPUT_IO_API __declspec(dllexport)
#   else
#       define GENERIC_MODEL_OUTPUT_IO_API __declspec(dllimport)
#   endif
#else
#   ifdef GENERIC_MODEL_OUTPUT_IO_EXPORTS
#      define GENERIC_MODEL_OUTPUT_IO_API __attribute__((visibility("default")))
#   else
#      define GENERIC_MODEL_OUTPUT_IO_API
#   endif
#endif

class GENERIC_MODEL_OUTPUT_IO_API GenericModelOutputIOFactory
{
public:
    static IGenericModelOutputIOPtr createInstance();
};


} // namespace omni::sensors
