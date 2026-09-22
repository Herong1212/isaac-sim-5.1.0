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

#include <carb/logging/Log.h>

#include <GenericModelOutputTypes.h>
#include <cstdint>
#include <vector>
// DOXYGEN needs a namespace in order to handle the LidarProfile structs // still needed?
#ifdef DOXYGEN_BUILD
namespace
{
#endif


static inline std::string ToLower(std::string str)
{
    std::transform(str.begin(), str.end(), str.begin(), ::tolower);
    return str;
}


// === Radar ===

struct DmatApproxRadarScanParams
{
    float maxRangeM;
    std::vector<float> maxVelMpsSequence;
    float maxAzAngRad;
    float maxElevAngRad;

    float rangeSepM;
    float velSepMps;
    float boreAzSepRad;
    float boreElevSepRad;

    uint8_t elevMode;
};

struct DmatApproxRadarProfile
{
    DmatApproxRadarScanParams nearScan;

    DmatApproxRadarScanParams farScan;

    float numRaysPerDeg;
    uint8_t numExtraThreads;
    uint64_t frameDurationNs;
};


// === WPM Radar ===

enum class ElevMode : uint8_t
{
    NO_EL = 0,
    POS_EL,
    FULL_EL
};

static inline ElevMode getElevModeFromString(const std::string& elevModeStr)
{
    std::string ems = ToLower(elevModeStr);
    if (ems == "no_el" || ems == "noel")
    {
        return ElevMode::NO_EL;
    }
    if (ems == "pos_el" || ems == "posel")
    {
        return ElevMode::POS_EL;
    }
    if (ems == "full_el" || ems == "fullel")
    {
        return ElevMode::FULL_EL;
    }
    CARB_LOG_ERROR("Invalid elevation mode: %s. Defaulting to FULL_EL.", elevModeStr.c_str());
    return ElevMode::FULL_EL;
}

static inline std::string getElevModeString(ElevMode elevMode)
{
    switch (elevMode)
    {
    case ElevMode::NO_EL:
        return "NO_EL";
    case ElevMode::POS_EL:
        return "POS_EL";
    case ElevMode::FULL_EL:
        return "FULL_EL";
    default:
        return "invalid";
    }
}


enum class CfarMode : uint8_t
{
    D2 = 0,
    D4
};

// function that returns cfar mode from string
static inline CfarMode getCfarModeFromString(const std::string& cfarModeStr)
{
    std::string cfms = ToLower(cfarModeStr);
    if (cfms == "d4" || cfms == "4d")
    {
        return CfarMode::D4;
    }
    if (cfms == "d2" || cfms == "2d")
    {
        return CfarMode::D2;
    }

    CARB_LOG_ERROR("Invalid CFAR mode: %s. Defaulting to D2.", cfarModeStr.c_str());
    return CfarMode::D2;
}

static inline std::string getCfarModeString(CfarMode cfarMode)
{
    switch (cfarMode)
    {
    case CfarMode::D2:
        return "D2";
    case CfarMode::D4:
        return "D4";
    default:
        return "invalid";
    }
}


enum class AntennaGainMode : uint8_t
{
    CONSTANT = 0,
    COSINE_FALLOFF
};

static inline AntennaGainMode getAntennaGainModeFromString(const std::string& antennaGainModeStr)
{
    std::string agms = ToLower(antennaGainModeStr);
    if (agms == "constant")
    {
        return AntennaGainMode::CONSTANT;
    }
    if (agms == "cosine_falloff" || agms == "cosinefalloff")
    {
        return AntennaGainMode::COSINE_FALLOFF;
    }

    CARB_LOG_ERROR("Invalid antenna gain mode: %s. Defaulting to COSINE_FALLOFF.", antennaGainModeStr.c_str());
    return AntennaGainMode::COSINE_FALLOFF;
}

static inline std::string getAntennaGainModeString(AntennaGainMode antennaGainMode)
{
    switch (antennaGainMode)
    {
    case AntennaGainMode::CONSTANT:
        return "CONSTANT";
    case AntennaGainMode::COSINE_FALLOFF:
        return "COSINE_FALLOFF";
    default:
        return "invalid";
    }
}


enum class InstanceTimeOffsetType : uint8_t
{
    // Sensor timestamp has no additional offset
    INSTANCE_TIME_OFFSET_NONE = 0,
    // A constant offset is given, e.g. by sensor idx (used to be the default in DRIVE Sim)
    INSTANCE_TIME_OFFSET_CONSTANT = 1,
    // Offset is given by a list of time offsets, e.g. taken from inspecting a real recording
    INSTANCE_TIME_OFFSET_LIST = 2,
    // Offset is given by a distribution of time offsets, e.g. taken from inspecting a real recording
    INSTANCE_TIME_OFFSET_DISTRIBUTION = 3,
};

static inline InstanceTimeOffsetType getInstanceTimeOffsetTypeFromString(const std::string& timeOffsetTypeStr)
{
    std::string itots = ToLower(timeOffsetTypeStr);
    if (itots == "none")
    {
        return InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_NONE;
    }
    if (itots == "sensor_idx" || itots == "sensoridx" || itots == "constant" || itots == "const")
    {
        return InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_CONSTANT;
    }
    if (itots == "list")
    {
        return InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_LIST;
    }
    if (itots == "distribution" || itots == "dist")
    {
        return InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_DISTRIBUTION;
    }

    CARB_LOG_ERROR("Invalid instance time offset type: %s. Defaulting to NONE.", timeOffsetTypeStr.c_str());
    return InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_NONE;
}

static inline std::string getInstanceTimeOffsetTypeString(InstanceTimeOffsetType timeOffsetType)
{
    switch (timeOffsetType)
    {
    case InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_NONE:
        return "NONE";
    case InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_CONSTANT:
        return "CONSTANT";
    case InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_LIST:
        return "LIST";
    case InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_DISTRIBUTION:
        return "DISTRIBUTION";
    default:
        return "invalid";
    }
}


struct InstanceTimeOffsetConfig
{
    InstanceTimeOffsetType timeOffsetType = InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_NONE;
    uint32_t timeOffsetUsec = 0;
    std::vector<uint32_t> timeOffsetsListUsec = {};
    float timeOffsetDistributionUsecMean = 0.0;
    float timeOffsetDistributionUsecStdDev = 0.0;

    // Constructor
    InstanceTimeOffsetConfig() = default;

    // Constructor for sensor idx
    InstanceTimeOffsetConfig(uint32_t timeOffsetUsec)
        : timeOffsetType(InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_CONSTANT), timeOffsetUsec(timeOffsetUsec)
    {
    }

    // Constructor for list
    InstanceTimeOffsetConfig(const std::vector<uint32_t>& timeOffsetsListUsec)
        : timeOffsetType(InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_LIST), timeOffsetsListUsec(timeOffsetsListUsec)
    {
    }

    // Constructor for distribution
    InstanceTimeOffsetConfig(float timeOffsetDistributionUsecMean, float timeOffsetDistributionUsecStdDev)
        : timeOffsetType(InstanceTimeOffsetType::INSTANCE_TIME_OFFSET_DISTRIBUTION),
          timeOffsetDistributionUsecMean(timeOffsetDistributionUsecMean),
          timeOffsetDistributionUsecStdDev(timeOffsetDistributionUsecStdDev)
    {
    }
};


struct WpmDmatApproxRadarCfarVizSettings
{
    float3 scale{ 0.0F, 0.0F, 0.0F };
    float offset = 20.0F;
    float3 P_user{ 0.0F, 0.0F, 0.0F };
    float4 Q_user{ 1.0F, 0.0F, 0.0F, 0.0F };
};

struct WpmDmatApproxRadarScanParams
{
    float raysPerDeg;
    uint32_t timeOffsetUsec;
    float powerFactor;

    float maxRangeM;
    float maxAzAngDeg;
    float maxElAngDeg;

    float rangeResM;
    float velResMps;
    float boreAzResDeg;
    float boreElResDeg;

    uint16_t rBins;
    uint16_t vBins;
    uint16_t azBins;
    uint16_t elBins;

    bool binsFromSpec;
    bool enAngAliasing;
    ElevMode elevMode;
    bool detValFromBinIdx;

    uint8_t cfarRnT;
    uint8_t cfarRnG;
    uint8_t cfarVnT;
    uint8_t cfarVnG;
    uint8_t cfarAznT;
    uint8_t cfarAznG;
    uint8_t cfarElnT;
    uint8_t cfarElnG;
    float cfarMinVal;
    float cfarOffset;
    float cfarNoiseMean;
    float cfarNoiseSDev;

    float azRadNoiseMean;
    float azRadNoiseSDev;
    float rangeNoiseMean;
    float rangeNoiseSDev;
    float velNoiseMean;
    float velNoiseSDev;
    float elRadNoiseMean;
    float elRadNoiseSDev;

    std::vector<float> maxVelMpsSequence;

    // Coefficients for RCS tuning.
    std::vector<float> rcsTuningCoefficients;

    float exponentialDecayFactor;
};


struct InstanceTimeOffsetParams
{
    InstanceTimeOffsetType timeOffsetType;
    uint32_t timeOffsetUsec;
    std::vector<uint32_t> timeOffsetsListUsec;
    float timeOffsetDistributionUsecMean;
    float timeOffsetDistributionUsecStdDev;
};


struct WpmDmatApproxRadarProfile
{
    float waveLengthMm;
    uint8_t traceTreeDepth;
    omni::sensors::AuxType auxOutputType{ omni::sensors::AuxType::NONE };
    omni::sensors::FrameOfReference outFrameOfReference{ omni::sensors::FrameOfReference::SENSOR };
    omni::sensors::CoordsType elementsCoordsType{ omni::sensors::CoordsType::SPHERICAL };
    float3 customOutPos{ 0.0f, 0.0f, 0.0f };
    float4 customOutOrientation{ 0.0f, 0.0f, 0.0f, 1.0f };
    uint64_t frameDurationNs;
    uint32_t traceConfigReloadInterval;
    CfarMode cfarMode{};
    AntennaGainMode antennaGainMode{};
    InstanceTimeOffsetParams instanceTimeOffsetParams;
    std::vector<WpmDmatApproxRadarScanParams> scanCfgs;
    WpmDmatApproxRadarCfarVizSettings cfarSettings;
};


#ifdef DOXYGEN_BUILD
}
#endif
