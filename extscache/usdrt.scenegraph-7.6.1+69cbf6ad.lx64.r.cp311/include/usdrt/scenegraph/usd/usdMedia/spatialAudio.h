// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
// TODO USD COPYRIGHT AS WELL?
#pragma once

/// @file usdMedia/spatialAudio.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/xformable.h"
#include "usdrt/scenegraph/usd/usdMedia/tokens.h"


// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
// --(END CUSTOM INCLUDES)--

#include <omni/core/IObject.h>
#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/base/vt/array.h>
#include <usdrt/scenegraph/interface/IRtAttribute.h>
#include <usdrt/scenegraph/interface/IRtPrim.h>
#include <usdrt/scenegraph/interface/IRtPrimRange.h>
#include <usdrt/scenegraph/interface/IRtRelationship.h>
#include <usdrt/scenegraph/interface/IRtStage.h>
#include <usdrt/scenegraph/usd/sdf/path.h>
#include <usdrt/scenegraph/usd/sdf/types.h>
#include <usdrt/scenegraph/usd/sdf/valueTypeName.h>
#include <usdrt/scenegraph/usd/usd/attribute.h>
#include <usdrt/scenegraph/usd/usd/common.h>
#include <usdrt/scenegraph/usd/usd/prim.h>
#include <usdrt/scenegraph/usd/usd/timeCode.h>

namespace usdrt
{

// -------------------------------------------------------------------------- //
// SPATIALAUDIO                                                                //
// -------------------------------------------------------------------------- //

/// @class UsdMediaSpatialAudio
///
/// The SpatialAudio primitive defines basic properties for encoding
/// playback of an audio file or stream within a USD Stage. The SpatialAudio
/// schema derives from UsdGeomXformable since it can support full spatial
/// audio while also supporting non-spatial mono and stereo sounds. One or
/// more SpatialAudio prims can be placed anywhere in the namespace, though it
/// is advantageous to place truly spatial audio prims under/inside the models
/// from which the sound emanates, so that the audio prim need only be
/// transformed relative to the model, rather than copying its animation.
///
/// \section Usd_SpatialAudio_TimeScaling Timecode Attributes and Time Scaling
/// \a startTime and \a endTime are \ref SdfTimeCode "timecode" valued
/// attributes which gives them the special behavior that
/// \ref SdfLayerOffset "layer offsets" affecting the layer in
/// which one of these values is authored are applied to the attribute's value
/// itself during value resolution. This allows audio playback to be kept in
/// sync with time sampled animation as the animation is affected by
/// \ref SdfLayerOffset "layer offsets" in the composition. But this behavior
/// brings with it some interesting edge cases and caveats when it comes to
/// \ref SdfLayerOffset "layer offsets" that include scale.
///
/// ####  Layer Offsets do not affect Media Dilation
/// Although authored layer offsets may have a time scale which can scale the
/// duration between an authored \a startTime and \a endTime, we make no
/// attempt to infer any playback dilation of the actual audio media itself.
/// Given that \a startTime and \a endTime can be independently authored in
/// different layers with differing time scales, it is not possible, in general,
/// to define an "original timeframe" from which we can compute a dilation to
/// composed stage-time. Even if we could compute a composed dilation this way,
/// it would still be impossible to flatten a stage or layer stack into a single
/// layer and still retain the composed audio dilation using this schema.
///
/// #### Inverting startTime and endTime
/// Although we do not expect it to be common, it is possible to apply a
/// negative time scale to USD layers, which mostly has the effect of reversing
/// animation in the affected composition. If a negative scale is applied to a
/// composition that contains authored \a startTime and \a endTime, it will
/// reverse their relative ordering in time. Therefore, we stipulate when
/// \a playbackMode is "onceFromStartToEnd" or "loopFromStartToEnd", if
/// \a endTime is less than \a startTime, then begin playback at \a endTime,
/// and continue until \a startTime. When \a startTime and \a endTime are
/// inverted, we do not, however, stipulate that playback of the audio media
/// itself be inverted, since doing so "successfully" would require perfect
/// knowledge of when, within the audio clip, relevant audio ends (so that we
/// know how to offset the reversed audio to align it so that we reach the
/// "beginning" at \a startTime), and sounds played in reverse are not likely
/// to produce desirable results.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdMediaTokens.
/// So to set an attribute to the value "rightHanded", use UsdMediaTokens->rightHanded
/// as the value.

class UsdMediaSpatialAudio : public UsdGeomXformable
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdMediaSpatialAudio on UsdPrim @p prim.
    /// Equivalent to UsdMediaSpatialAudio::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdMediaSpatialAudio(const UsdPrim& prim = UsdPrim()) : UsdGeomXformable(prim)
    {
    }

    /// Construct a UsdMediaSpatialAudio on the prim held by @p schemaObj .
    /// Should be preferred over UsdMediaSpatialAudio(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdMediaSpatialAudio(const UsdSchemaBase& schemaObj) : UsdGeomXformable(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdMediaSpatialAudio()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdMediaSpatialAudio Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FILEPATH
    // --------------------------------------------------------------------- //
    /// Path to the audio file.
    /// In general, the formats allowed for audio files is no more constrained
    /// by USD than is image-type. As with images, however, usdz has stricter
    /// requirements based on DMA and format support in browsers and consumer
    /// devices. The allowed audio filetypes for usdz are M4A, MP3, WAV
    /// (in order of preference).
    /// \sa <a
    /// href="http://graphics.pixar.com/usd/docs/Usdz-File-Format-Specification.html#UsdzFileFormatSpecification-UsdzSpecification">Usdz
    /// Specification</a>
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform asset filePath = @@` |
    /// | C++ Type | SdfAssetPath |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Asset |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetFilePathAttr() const;

    /// See GetFilePathAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFilePathAttr() const;

public:
    // --------------------------------------------------------------------- //
    // AURALMODE
    // --------------------------------------------------------------------- //
    /// Determines how audio should be played.
    /// Valid values are:
    /// - spatial: Play the audio in 3D space if the device can support spatial
    /// audio. if not, fall back to mono.
    /// - nonSpatial: Play the audio without regard to the SpatialAudio prim's
    /// position. If the audio media contains any form of stereo or other
    /// multi-channel sound, it is left to the application to determine
    /// whether the listener's position should be taken into account. We
    /// expect nonSpatial to be the choice for ambient sounds and music
    /// sound-tracks.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token auralMode = "spatial"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdMediaTokens "Allowed Values" | spatial, nonSpatial |

    UsdAttribute GetAuralModeAttr() const;

    /// See GetAuralModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAuralModeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PLAYBACKMODE
    // --------------------------------------------------------------------- //
    /// Along with \a startTime and \a endTime, determines when the
    /// audio playback should start and stop during the stage's animation
    /// playback and whether the audio should loop during its duration.
    /// Valid values are:
    /// - onceFromStart: Play the audio once, starting at \a startTime,
    /// continuing until the audio completes.
    /// - onceFromStartToEnd: Play the audio once beginning at \a startTime,
    /// continuing until \a endTime or until the audio completes, whichever
    /// comes first.
    /// - loopFromStart: Start playing the audio at \a startTime and continue
    /// looping through to the stage's authored \a endTimeCode.
    /// - loopFromStartToEnd: Start playing the audio at \a startTime and
    /// continue looping through, stopping the audio at \a endTime.
    /// - loopFromStage: Start playing the audio at the stage's authored
    /// \a startTimeCode and continue looping through to the stage's authored
    /// \a endTimeCode. This can be useful for ambient sounds that should always
    /// be active.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token playbackMode = "onceFromStart"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdMediaTokens "Allowed Values" | onceFromStart, onceFromStartToEnd, loopFromStart, loopFromStartToEnd,
    /// loopFromStage |

    UsdAttribute GetPlaybackModeAttr() const;

    /// See GetPlaybackModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePlaybackModeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STARTTIME
    // --------------------------------------------------------------------- //
    /// Expressed in the timeCodesPerSecond of the containing stage,
    /// \a startTime specifies when the audio stream will start playing during
    /// animation playback. This value is ignored when \a playbackMode is set
    /// to loopFromStage as, in this mode, the audio will always start at the
    /// stage's authored \a startTimeCode.
    /// Note that \a startTime is expressed as a timecode so that the stage can
    /// properly apply layer offsets when resolving its value. See
    /// \ref Usd_SpatialAudio_TimeScaling for more details and caveats.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform timecode startTime = 0` |
    /// | C++ Type | SdfTimeCode |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TimeCode |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetStartTimeAttr() const;

    /// See GetStartTimeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateStartTimeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENDTIME
    // --------------------------------------------------------------------- //
    /// Expressed in the timeCodesPerSecond of the containing stage,
    /// \a endTime specifies when the audio stream will cease playing during
    /// animation playback if the length of the referenced audio clip is
    /// longer than desired. This only applies if \a playbackMode is set to
    /// onceFromStartToEnd or loopFromStartToEnd, otherwise the \a endTimeCode
    /// of the stage is used instead of \a endTime.
    /// If \a endTime is less than \a startTime, it is expected that the audio
    /// will instead be played from \a endTime to \a startTime.
    /// Note that \a endTime is expressed as a timecode so that the stage can
    /// properly apply layer offsets when resolving its value.
    /// See \ref Usd_SpatialAudio_TimeScaling for more details and caveats.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform timecode endTime = 0` |
    /// | C++ Type | SdfTimeCode |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TimeCode |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetEndTimeAttr() const;

    /// See GetEndTimeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEndTimeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MEDIAOFFSET
    // --------------------------------------------------------------------- //
    /// Expressed in seconds, \a mediaOffset specifies the offset from
    /// the referenced audio file's beginning at which we should begin playback
    /// when stage playback reaches the time that prim's audio should start.
    /// If the prim's \a playbackMode is a looping mode, \a mediaOffset is
    /// applied only to the first run-through of the audio clip; the second and
    /// all other loops begin from the start of the audio clip.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform double mediaOffset = 0` |
    /// | C++ Type | double |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetMediaOffsetAttr() const;

    /// See GetMediaOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMediaOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GAIN
    // --------------------------------------------------------------------- //
    /// Multiplier on the incoming audio signal. A value of 0 "mutes"
    /// the signal. Negative values will be clamped to 0.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double gain = 1` |
    /// | C++ Type | double |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double |

    UsdAttribute GetGainAttr() const;

    /// See GetGainAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGainAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdMediaSpatialAudio::_GetStaticTfType()
{
    const static TfToken token("UsdMediaSpatialAudio");
    return token;
}

/* virtual */
inline const TfToken UsdMediaSpatialAudio::_GetTfTypeToken() const
{
    const static TfToken token("UsdMediaSpatialAudio");
    return token;
}

/* static */
inline UsdMediaSpatialAudio UsdMediaSpatialAudio::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdMediaSpatialAudio();
    }
    return UsdMediaSpatialAudio(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdMediaSpatialAudio::GetFilePathAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdMediaTokens->filePath));
}

inline UsdAttribute UsdMediaSpatialAudio::CreateFilePathAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdMediaTokens->filePath), SdfValueTypeNames->Asset,
                                     /* custom = */ false);
}

inline UsdAttribute UsdMediaSpatialAudio::GetAuralModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdMediaTokens->auralMode));
}

inline UsdAttribute UsdMediaSpatialAudio::CreateAuralModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdMediaTokens->auralMode), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdMediaSpatialAudio::GetPlaybackModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdMediaTokens->playbackMode));
}

inline UsdAttribute UsdMediaSpatialAudio::CreatePlaybackModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdMediaTokens->playbackMode), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdMediaSpatialAudio::GetStartTimeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdMediaTokens->startTime));
}

inline UsdAttribute UsdMediaSpatialAudio::CreateStartTimeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdMediaTokens->startTime), SdfValueTypeNames->TimeCode,
                                     /* custom = */ false);
}

inline UsdAttribute UsdMediaSpatialAudio::GetEndTimeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdMediaTokens->endTime));
}

inline UsdAttribute UsdMediaSpatialAudio::CreateEndTimeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdMediaTokens->endTime), SdfValueTypeNames->TimeCode,
                                     /* custom = */ false);
}

inline UsdAttribute UsdMediaSpatialAudio::GetMediaOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdMediaTokens->mediaOffset));
}

inline UsdAttribute UsdMediaSpatialAudio::CreateMediaOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdMediaTokens->mediaOffset), SdfValueTypeNames->Double,
                                     /* custom = */ false);
}

inline UsdAttribute UsdMediaSpatialAudio::GetGainAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdMediaTokens->gain));
}

inline UsdAttribute UsdMediaSpatialAudio::CreateGainAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdMediaTokens->gain), SdfValueTypeNames->Double,
                                     /* custom = */ false);
}


} // namespace usdrt
// ===================================================================== //
// Feel free to add custom code below this line. It will be preserved by
// the code generator.
//
// Just remember to wrap code in the appropriate delimiters:
// 'namespace usdrt {', '}'.
// ===================================================================== //
// --(BEGIN CUSTOM CODE)--
