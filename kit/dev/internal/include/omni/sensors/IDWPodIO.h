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

#include <carb/IObject.h>
#include <carb/Interface.h>

#include "InternalTypes.h"
#include <omni/String.h>
#include <omni/Vector.h>

#include <cstdint>

namespace omni::sensors
{

enum class DWPodAccessType : uint8_t
{
    READ = 0,
    WRITE = 1
};


struct DWPodIOConfig
{
    DWPodAccessType accessType{ DWPodAccessType::WRITE };
    TimedDataBuffer trackHeaderDataBuffer;
    omni::string fileName{ "" };
    int desiredTrackId{ 1 }; // TODO:  -1 could mean all data of all tracks; only recommended for files with one data
                             // track/stream
};


class IDWPodIO : public carb::IObject
{
public:
    virtual ~IDWPodIO(){};

    // Returns track header data
    virtual void init(const DWPodIOConfig& cfg) = 0;
    // Maybe add optinonal seek frame boolean?
    virtual void dumpPacket(void* packet,
                            const uint64_t packetSize,
                            void* packetHeader,
                            const uint64_t packetHeaderSize,
                            const uint64_t packetTimestampNs) = 0;
    virtual TimedDataBuffer readNextPacket() = 0;
    virtual const DWPodIOConfig& getCfg() const = 0;
};

using IDWPodIOPtr = carb::ObjectPtr<IDWPodIO>;

class IDWPodIOFactory
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::common::IDWPodIOFactory", 0, 1)

    virtual IDWPodIOPtr createInstance() = 0;
};


} // namespace omni::sensors
