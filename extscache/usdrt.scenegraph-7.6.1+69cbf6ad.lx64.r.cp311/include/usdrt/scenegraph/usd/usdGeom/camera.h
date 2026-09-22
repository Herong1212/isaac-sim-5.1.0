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

/// @file usdGeom/camera.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/xformable.h"
#include "usdrt/scenegraph/usd/usdGeom/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/pxr/base/gf/camera.h" */
// clang-format on

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
// CAMERA                                                                      //
// -------------------------------------------------------------------------- //

/// @class UsdGeomCamera
///
/// Transformable camera.
///
/// Describes optical properties of a camera via a common set of attributes
/// that provide control over the camera's frustum as well as its depth of
/// field. For stereo, the left and right camera are individual prims tagged
/// through the \ref UsdGeomCamera::GetStereoRoleAttr() "stereoRole attribute".
///
/// There is a corresponding class GfCamera, which can hold the state of a
/// camera (at a particular time). \ref UsdGeomCamera::GetCamera() and
/// \ref UsdGeomCamera::SetFromCamera() convert between a USD camera prim and
/// a GfCamera.
///
/// To obtain the camera's location in world space, call the following on a
/// UsdGeomCamera 'camera':
/// \code
/// GfMatrix4d camXform = camera.ComputeLocalToWorldTransform(time);
/// \endcode
/// \note
/// <b>Cameras in USD are always "Y up", regardless of the stage's orientation
/// (i.e. UsdGeomGetStageUpAxis()).</b>  This means that the inverse of
/// 'camXform' (the VIEW half of the <A HREF="http://www.glprogramming.com/red/chapter03.html#name2">MODELVIEW transform
/// in OpenGL parlance</A>) will transform the world such that the camera is at the origin, looking down the -Z axis,
/// with +Y as the up axis, and +X pointing to the right. This describes a __right handed coordinate system__.
///
/// \section UsdGeom_CameraUnits Units of Measure for Camera Properties
///
/// Despite the familiarity of millimeters for specifying some physical
/// camera properties, UsdGeomCamera opts for greater consistency with all
/// other UsdGeom schemas, which measure geometric properties in scene units,
/// as determined by UsdGeomGetStageMetersPerUnit().  We do make a
/// concession, however, in that lens and filmback properties are measured in
/// __tenths of a scene unit__ rather than "raw" scene units.  This means
/// that with the fallback value of .01 for _metersPerUnit_ - i.e. scene unit
/// of centimeters - then these "tenth of scene unit" properties are
/// effectively millimeters.
///
/// \note If one adds a Camera prim to a UsdStage whose scene unit is not
/// centimeters, the fallback values for filmback properties will be
/// incorrect (or at the least, unexpected) in an absolute sense; however,
/// proper imaging through a "default camera" with focusing disabled depends
/// only on ratios of the other properties, so the camera is still usable.
/// However, it follows that if even one property is authored in the correct
/// scene units, then they all must be.
///
///
/// \sa \ref UsdGeom_LinAlgBasics
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdGeomTokens.
/// So to set an attribute to the value "rightHanded", use UsdGeomTokens->rightHanded
/// as the value.

class UsdGeomCamera : public UsdGeomXformable
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdGeomCamera on UsdPrim @p prim.
    /// Equivalent to UsdGeomCamera::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomCamera(const UsdPrim& prim = UsdPrim()) : UsdGeomXformable(prim)
    {
    }

    /// Construct a UsdGeomCamera on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomCamera(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomCamera(const UsdSchemaBase& schemaObj) : UsdGeomXformable(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomCamera()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdGeomCamera Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // PROJECTION
    // --------------------------------------------------------------------- //
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token projection = "perspective"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref UsdGeomTokens "Allowed Values" | perspective, orthographic |

    UsdAttribute GetProjectionAttr() const;

    /// See GetProjectionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateProjectionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // HORIZONTALAPERTURE
    // --------------------------------------------------------------------- //
    /// Horizontal aperture in tenths of a scene unit; see
    /// \ref UsdGeom_CameraUnits . Default is the equivalent of
    /// the standard 35mm spherical projector aperture.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float horizontalAperture = 20.955` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetHorizontalApertureAttr() const;

    /// See GetHorizontalApertureAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateHorizontalApertureAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VERTICALAPERTURE
    // --------------------------------------------------------------------- //
    /// Vertical aperture in tenths of a scene unit; see
    /// \ref UsdGeom_CameraUnits . Default is the equivalent of
    /// the standard 35mm spherical projector aperture.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float verticalAperture = 15.2908` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetVerticalApertureAttr() const;

    /// See GetVerticalApertureAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVerticalApertureAttr() const;

public:
    // --------------------------------------------------------------------- //
    // HORIZONTALAPERTUREOFFSET
    // --------------------------------------------------------------------- //
    /// Horizontal aperture offset in the same units as
    /// horizontalAperture. Defaults to 0.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float horizontalApertureOffset = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetHorizontalApertureOffsetAttr() const;

    /// See GetHorizontalApertureOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateHorizontalApertureOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VERTICALAPERTUREOFFSET
    // --------------------------------------------------------------------- //
    /// Vertical aperture offset in the same units as
    /// verticalAperture. Defaults to 0.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float verticalApertureOffset = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetVerticalApertureOffsetAttr() const;

    /// See GetVerticalApertureOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVerticalApertureOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FOCALLENGTH
    // --------------------------------------------------------------------- //
    /// Perspective focal length in tenths of a scene unit; see
    /// \ref UsdGeom_CameraUnits .
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float focalLength = 50` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFocalLengthAttr() const;

    /// See GetFocalLengthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFocalLengthAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CLIPPINGRANGE
    // --------------------------------------------------------------------- //
    /// Near and far clipping distances in scene units; see
    /// \ref UsdGeom_CameraUnits .
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float2 clippingRange = (1, 1000000)` |
    /// | C++ Type | GfVec2f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float2 |

    UsdAttribute GetClippingRangeAttr() const;

    /// See GetClippingRangeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateClippingRangeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CLIPPINGPLANES
    // --------------------------------------------------------------------- //
    /// Additional, arbitrarily oriented clipping planes.
    /// A vector (a,b,c,d) encodes a clipping plane that cuts off
    /// (x,y,z) with a * x + b * y + c * z + d * 1 < 0 where (x,y,z)
    /// are the coordinates in the camera's space.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float4[] clippingPlanes = []` |
    /// | C++ Type | VtArray<GfVec4f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float4Array |

    UsdAttribute GetClippingPlanesAttr() const;

    /// See GetClippingPlanesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateClippingPlanesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FSTOP
    // --------------------------------------------------------------------- //
    /// Lens aperture. Defaults to 0.0, which turns off focusing.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float fStop = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFStopAttr() const;

    /// See GetFStopAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFStopAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FOCUSDISTANCE
    // --------------------------------------------------------------------- //
    /// Distance from the camera to the focus plane in scene units; see
    /// \ref UsdGeom_CameraUnits .
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float focusDistance = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFocusDistanceAttr() const;

    /// See GetFocusDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFocusDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STEREOROLE
    // --------------------------------------------------------------------- //
    /// If different from mono, the camera is intended to be the left
    /// or right camera of a stereo setup.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token stereoRole = "mono"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | mono, left, right |

    UsdAttribute GetStereoRoleAttr() const;

    /// See GetStereoRoleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateStereoRoleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHUTTEROPEN
    // --------------------------------------------------------------------- //
    /// Frame relative shutter open time in UsdTimeCode units (negative
    /// value indicates that the shutter opens before the current
    /// frame time). Used for motion blur.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double shutter:open = 0` |
    /// | C++ Type | double |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double |

    UsdAttribute GetShutterOpenAttr() const;

    /// See GetShutterOpenAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShutterOpenAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHUTTERCLOSE
    // --------------------------------------------------------------------- //
    /// Frame relative shutter close time, analogous comments from
    /// shutter:open apply. A value greater or equal to shutter:open
    /// should be authored, otherwise there is no exposure and a
    /// renderer should produce a black image.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double shutter:close = 0` |
    /// | C++ Type | double |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double |

    UsdAttribute GetShutterCloseAttr() const;

    /// See GetShutterCloseAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShutterCloseAttr() const;

public:
    // --------------------------------------------------------------------- //
    // EXPOSURE
    // --------------------------------------------------------------------- //
    /// Exposure adjustment, as a log base-2 value.  The default
    /// of 0.0 has no effect.  A value of 1.0 will double the
    /// image-plane intensities in a rendered image; a value of
    /// -1.0 will halve them.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float exposure = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetExposureAttr() const;

    /// See GetExposureAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateExposureAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomCamera::_GetStaticTfType()
{
    const static TfToken token("UsdGeomCamera");
    return token;
}

/* virtual */
inline const TfToken UsdGeomCamera::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomCamera");
    return token;
}

/* static */
inline UsdGeomCamera UsdGeomCamera::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdGeomCamera();
    }
    return UsdGeomCamera(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdGeomCamera::GetProjectionAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->projection));
}

inline UsdAttribute UsdGeomCamera::CreateProjectionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->projection), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetHorizontalApertureAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->horizontalAperture));
}

inline UsdAttribute UsdGeomCamera::CreateHorizontalApertureAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->horizontalAperture), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetVerticalApertureAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->verticalAperture));
}

inline UsdAttribute UsdGeomCamera::CreateVerticalApertureAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->verticalAperture), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetHorizontalApertureOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->horizontalApertureOffset));
}

inline UsdAttribute UsdGeomCamera::CreateHorizontalApertureOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->horizontalApertureOffset), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetVerticalApertureOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->verticalApertureOffset));
}

inline UsdAttribute UsdGeomCamera::CreateVerticalApertureOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->verticalApertureOffset), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetFocalLengthAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->focalLength));
}

inline UsdAttribute UsdGeomCamera::CreateFocalLengthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->focalLength), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetClippingRangeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->clippingRange));
}

inline UsdAttribute UsdGeomCamera::CreateClippingRangeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->clippingRange), SdfValueTypeNames->Float2,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetClippingPlanesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->clippingPlanes));
}

inline UsdAttribute UsdGeomCamera::CreateClippingPlanesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->clippingPlanes), SdfValueTypeNames->Float4Array,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetFStopAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->fStop));
}

inline UsdAttribute UsdGeomCamera::CreateFStopAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->fStop), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetFocusDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->focusDistance));
}

inline UsdAttribute UsdGeomCamera::CreateFocusDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->focusDistance), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetStereoRoleAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->stereoRole));
}

inline UsdAttribute UsdGeomCamera::CreateStereoRoleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->stereoRole), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetShutterOpenAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->shutterOpen));
}

inline UsdAttribute UsdGeomCamera::CreateShutterOpenAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->shutterOpen), SdfValueTypeNames->Double,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetShutterCloseAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->shutterClose));
}

inline UsdAttribute UsdGeomCamera::CreateShutterCloseAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->shutterClose), SdfValueTypeNames->Double,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCamera::GetExposureAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->exposure));
}

inline UsdAttribute UsdGeomCamera::CreateExposureAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->exposure), SdfValueTypeNames->Float,
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
