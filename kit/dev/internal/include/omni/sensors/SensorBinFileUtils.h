// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include "SensorBinFileHeaders.h"

#include <omni/String.h>

namespace omni::sensors
{

inline void extendChannelDescWithHeader(const LidarBinFileHeader& header,
                                        carb::dictionary::IDictionary* dict,
                                        carb::dictionary::Item* item,
                                        const omni::string& channelName)
{
    // recorder
    // auto recorderItem = dict->makeDictionaryAtPath(item, "recorder");
    dict->makeAtPath(item, "recorder:channelName", channelName.c_str());
    // Common
    auto commonItem = dict->makeDictionaryAtPath(item, "common");
    dict->makeAtPath(commonItem, "fileMagicNumber", (int64_t)header.common.fileMagicNumber);
    dict->makeIntAtPath(commonItem, "fileVersion", header.common.fileVersion);
    dict->makeIntAtPath(commonItem, "driveworksMajor", header.common.driveworksMajor);
    dict->makeIntAtPath(commonItem, "driveworksMinor", header.common.driveworksMinor);
    dict->makeIntAtPath(commonItem, "driveworksPatch", header.common.driveworksPatch);
    dict->makeStringAtPath(commonItem, "driveworksHash", header.common.driveworksHash);
    // parameter string
    auto lidarItem = dict->makeDictionaryAtPath(item, "lidar");
    dict->makeStringAtPath(lidarItem, "parameterString", reinterpret_cast<const char*>(header.parameterString));
    // beam angles
    auto beamItem = dict->makeDictionaryAtPath(lidarItem, "beamAngles");
    auto elevationItem = dict->createItem(beamItem, "elevation", carb::dictionary::ItemType::eDictionary);
    dict->setFloatArray(elevationItem, header.beamAngles.elevation, 256);
    dict->makeInt64AtPath(beamItem, "numElevations", (int64_t)header.beamAngles.numElevations);
    dict->makeInt64AtPath(beamItem, "sizeHintEle", (int64_t)header.beamAngles.sizeHintEle);
    auto azimuthItem = dict->createItem(beamItem, "azimuth", carb::dictionary::ItemType::eDictionary);
    dict->setFloatArray(azimuthItem, header.beamAngles.azimuth, 256);
    dict->makeInt64AtPath(beamItem, "numAzimuths", (int64_t)header.beamAngles.numAzimuths);
    dict->makeInt64AtPath(beamItem, "sizeHintAzi", (int64_t)header.beamAngles.sizeHintAzi);
    // additional param
    dict->makeStringAtPath(lidarItem, "additionalParam", reinterpret_cast<const char*>(header.additionalParam));
    dict->makeInt64AtPath(lidarItem, "lengthAdditional", header.lengthAdditional);
}

inline void extendChannelDescWithHeader(const RadarBinFileHeader& header,
                                        carb::dictionary::IDictionary* dict,
                                        carb::dictionary::Item* item,
                                        const omni::string& channelName)
{
    // recorder
    dict->makeAtPath(item, "recorder:channelName", channelName.c_str());
    // Common
    auto commonItem = dict->makeDictionaryAtPath(item, "common");
    dict->makeAtPath(commonItem, "fileMagicNumber", (int64_t)header.common.fileMagicNumber);
    dict->makeIntAtPath(commonItem, "fileVersion", header.common.fileVersion);
    dict->makeIntAtPath(commonItem, "driveworksMajor", header.common.driveworksMajor);
    dict->makeIntAtPath(commonItem, "driveworksMinor", header.common.driveworksMinor);
    dict->makeIntAtPath(commonItem, "driveworksPatch", header.common.driveworksPatch);
    dict->makeStringAtPath(commonItem, "driveworksHash", header.common.driveworksHash);
    // parameter string
    auto radarItem = dict->makeDictionaryAtPath(item, "radar");
    dict->makeStringAtPath(radarItem, "parameterString", reinterpret_cast<const char*>(header.parameterString));
}

inline void extendChannelDescWithHeader(const USSBinFileHeader& header,
                                        carb::dictionary::IDictionary* dict,
                                        carb::dictionary::Item* item,
                                        const omni::string& channelName)
{
    // recorder
    // auto recorderItem = dict->makeDictionaryAtPath(item, "recorder");
    dict->makeAtPath(item, "recorder:channelName", channelName.c_str());
    // Common
    auto commonItem = dict->makeDictionaryAtPath(item, "common");
    dict->makeAtPath(commonItem, "fileMagicNumber", (int64_t)header.common.fileMagicNumber);
    dict->makeIntAtPath(commonItem, "fileVersion", header.common.fileVersion);
    dict->makeIntAtPath(commonItem, "driveworksMajor", header.common.driveworksMajor);
    dict->makeIntAtPath(commonItem, "driveworksMinor", header.common.driveworksMinor);
    dict->makeIntAtPath(commonItem, "driveworksPatch", header.common.driveworksPatch);
    dict->makeStringAtPath(commonItem, "driveworksHash", header.common.driveworksHash);
}

inline void extendChannelDescWithHeader(const UbloxBinFileHeader& header,
                                        carb::dictionary::IDictionary* dict,
                                        carb::dictionary::Item* item,
                                        const omni::string& channelName)
{
    // recorder
    dict->makeAtPath(item, "recorder:channelName", channelName.c_str());
    // Common
    auto commonItem = dict->makeDictionaryAtPath(item, "common");
    dict->makeAtPath(commonItem, "fileMagicNumber", (int64_t)header.common.fileMagicNumber);
    dict->makeIntAtPath(commonItem, "fileVersion", header.common.fileVersion);
    dict->makeIntAtPath(commonItem, "driveworksMajor", header.common.driveworksMajor);
    dict->makeIntAtPath(commonItem, "driveworksMinor", header.common.driveworksMinor);
    dict->makeIntAtPath(commonItem, "driveworksPatch", header.common.driveworksPatch);
    dict->makeStringAtPath(commonItem, "driveworksHash", header.common.driveworksHash);
}


inline void fillGenericHeader(carb::dictionary::IDictionary* dict,
                              carb::dictionary::Item* item,
                              const omni::string& channelName,
                              const size_t maxPoints,
                              const omni::string& sensorName,
                              const int gpcAccessType = 2, // -> corresponds to AccessType::RECORD_FULL
                              const bool onlyValid = true)
{
    dict->makeAtPath(item, "recorder:channelName", channelName.c_str());
    auto genericItem = dict->makeDictionaryAtPath(item, "generic");
    dict->makeIntAtPath(genericItem, "maxPoints", static_cast<int>(maxPoints));
    dict->makeStringAtPath(genericItem, "sensorName", sensorName.c_str());
    dict->makeBoolAtPath(genericItem, "onlyValid", onlyValid);
    dict->makeIntAtPath(genericItem, "accessType", gpcAccessType);
}


} // namespace omni::sensors
