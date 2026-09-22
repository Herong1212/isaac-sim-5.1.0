// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

/// \file usdMedia/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
//
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
//
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{


/// \class UsdMediaTokensType

/// Provides standard set of public tokens for UsdMedia schema.
/// Access via the RtTokens helper accessor.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// UsdMediaTokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.

/// Use UsdMediaTokens like so:
///
/// \code
///     prim.GetAttribute(RtTokens->worldPosition);
/// \endcode


struct UsdMediaTokensType
{
    UsdMediaTokensType();
    /// @brief "auralMode"
    ///
    /// UsdMediaSpatialAudio
    const TfToken auralMode;
    /// @brief "endTime"
    ///
    /// UsdMediaSpatialAudio
    const TfToken endTime;
    /// @brief "filePath"
    ///
    /// UsdMediaSpatialAudio
    const TfToken filePath;
    /// @brief "gain"
    ///
    /// UsdMediaSpatialAudio
    const TfToken gain;
    /// @brief "loopFromStage"
    ///
    /// Possible value for UsdMediaSpatialAudio::GetPlaybackModeAttr()
    const TfToken loopFromStage;
    /// @brief "loopFromStart"
    ///
    /// Possible value for UsdMediaSpatialAudio::GetPlaybackModeAttr()
    const TfToken loopFromStart;
    /// @brief "loopFromStartToEnd"
    ///
    /// Possible value for UsdMediaSpatialAudio::GetPlaybackModeAttr()
    const TfToken loopFromStartToEnd;
    /// @brief "mediaOffset"
    ///
    /// UsdMediaSpatialAudio
    const TfToken mediaOffset;
    /// @brief "nonSpatial"
    ///
    /// Possible value for UsdMediaSpatialAudio::GetAuralModeAttr()
    const TfToken nonSpatial;
    /// @brief "onceFromStart"
    ///
    /// Possible value for UsdMediaSpatialAudio::GetPlaybackModeAttr(), Default value for
    /// UsdMediaSpatialAudio::GetPlaybackModeAttr()
    const TfToken onceFromStart;
    /// @brief "onceFromStartToEnd"
    ///
    /// Possible value for UsdMediaSpatialAudio::GetPlaybackModeAttr()
    const TfToken onceFromStartToEnd;
    /// @brief "playbackMode"
    ///
    /// UsdMediaSpatialAudio
    const TfToken playbackMode;
    /// @brief "spatial"
    ///
    /// Possible value for UsdMediaSpatialAudio::GetAuralModeAttr(), Default value for
    /// UsdMediaSpatialAudio::GetAuralModeAttr()
    const TfToken spatial;
    /// @brief "startTime"
    ///
    /// UsdMediaSpatialAudio
    const TfToken startTime;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

inline UsdMediaTokensType::UsdMediaTokensType()
    : auralMode("auralMode"),
      endTime("endTime"),
      filePath("filePath"),
      gain("gain"),
      loopFromStage("loopFromStage"),
      loopFromStart("loopFromStart"),
      loopFromStartToEnd("loopFromStartToEnd"),
      mediaOffset("mediaOffset"),
      nonSpatial("nonSpatial"),
      onceFromStart("onceFromStart"),
      onceFromStartToEnd("onceFromStartToEnd"),
      playbackMode("playbackMode"),
      spatial("spatial"),
      startTime("startTime")
{
}

struct UsdMediaTokensTypeAccessor
{
    const UsdMediaTokensType* operator->()
    {
        static const UsdMediaTokensType tokens;
        return &tokens;
    }
};


inline UsdMediaTokensTypeAccessor UsdMediaTokens;


} // namespace usdrt
