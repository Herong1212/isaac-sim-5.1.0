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

/// @file physxSchema/physxHairAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/physxSchema/tokens.h"


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
// PHYSXHAIRAPI                                                                //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxHairAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// This is the PhysX Hair API. This API should be applied to a UsdGeomPointBased, for
/// example UsdGeomMesh or UsdGeomBasisCurves to simulate the geometry as a PhysX Hairsystem.

class PhysxSchemaPhysxHairAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxHairAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxHairAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxHairAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxHairAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxHairAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxHairAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxHairAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxHairAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxHairAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxHairAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxHairAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxHairAPI>())
        {
            return PhysxSchemaPhysxHairAPI(prim);
        }
        return PhysxSchemaPhysxHairAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // EXTERNALCOLLISION
    // --------------------------------------------------------------------- //
    /// Enables the hair segments to collide with other physics objects that have a collision API applied to them.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxHair:externalCollision = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetExternalCollisionAttr() const;

    /// See GetExternalCollisionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateExternalCollisionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TWOSIDEDATTACHMENT
    // --------------------------------------------------------------------- //
    /// Whether the hair should have an effect on the body it is attached to.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxHair:twosidedAttachment = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetTwosidedAttachmentAttr() const;

    /// See GetTwosidedAttachmentAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTwosidedAttachmentAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SEGMENTLENGTH
    // --------------------------------------------------------------------- //
    /// Length of one hair segment (i.e., distance between simulation vertices along a strand).
    /// This value is used to automatically place simulation vertices (=control points) along a strand.
    /// The default value of 0 means the length is autocomputed such that the longest strand has 32 vertices.
    /// Range: [0, inf),
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHair:segmentLength = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSegmentLengthAttr() const;

    /// See GetSegmentLengthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSegmentLengthAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GLOBALSHAPECOMPLIANCEATROOT
    // --------------------------------------------------------------------- //
    /// Compliance to the global shape-matching constraint at the root of the strand.
    /// The higher the compliance the softer the constraint.
    /// A negative value disables the shape-matching constraint.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHair:globalShapeComplianceAtRoot = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetGlobalShapeComplianceAtRootAttr() const;

    /// See GetGlobalShapeComplianceAtRootAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGlobalShapeComplianceAtRootAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GLOBALSHAPECOMPLIANCESTRANDATTENUATION
    // --------------------------------------------------------------------- //
    /// The factor by which the compliance to the global shape-matching constraint changes from
    /// a simulation vertex to the next one along the strand. Use it to increase or decrease
    /// the compliance along a strand, starting with globalShapeComplianceAtRoot.
    /// A value > 1.0 means the constraint becomes softer towards the strand tips.
    /// Range: (0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHair:globalShapeComplianceStrandAttenuation = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetGlobalShapeComplianceStrandAttenuationAttr() const;

    /// See GetGlobalShapeComplianceStrandAttenuationAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGlobalShapeComplianceStrandAttenuationAttr() const;

public:
    // --------------------------------------------------------------------- //
    // INTERHAIRREPULSION
    // --------------------------------------------------------------------- //
    /// Strength of the repulsion effect between hair segments.
    /// This effect is based on the volumetric density of hair vertices in space.
    /// Can be used as a substitute or complement to self-collisions.
    /// Range: [0.0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHair:interHairRepulsion = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetInterHairRepulsionAttr() const;

    /// See GetInterHairRepulsionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateInterHairRepulsionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VELSMOOTHING
    // --------------------------------------------------------------------- //
    /// Strength of the velocity smoothing effect.
    /// The higher the value the more the hair moves like a single rigid body.
    /// A value of zero disables the constraint.
    /// Range: [0.0, 1.0]
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHair:velSmoothing = 0.3` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetVelSmoothingAttr() const;

    /// See GetVelSmoothingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVelSmoothingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOCALSHAPEMATCHINGCOMPLIANCE
    // --------------------------------------------------------------------- //
    /// Compliance to the local shape matching constraint, which preserves strand shapes.
    /// The larger the compliance the softer the constraint.
    /// A negative value disables the constraint.
    /// Range [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHair:localShapeMatchingCompliance = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLocalShapeMatchingComplianceAttr() const;

    /// See GetLocalShapeMatchingComplianceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLocalShapeMatchingComplianceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOCALSHAPEMATCHINGLINEARSTRETCHING
    // --------------------------------------------------------------------- //
    /// Proportion of linear stretching vs rigid transformation allowed in the local shape matching constraint.
    /// Only takes effect if local shape matching is enabled.
    /// A value of 0 allows only rigid transforms, a value of 1 permits linear deformations freely.
    /// Range [0.0, 1.0]
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHair:localShapeMatchingLinearStretching = 0.1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLocalShapeMatchingLinearStretchingAttr() const;

    /// See GetLocalShapeMatchingLinearStretchingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLocalShapeMatchingLinearStretchingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOCALSHAPEMATCHINGGROUPSIZE
    // --------------------------------------------------------------------- //
    /// How many vertices of a strand are grouped together into one shape-matching constraint.
    /// The larger this number to more rigid a strand appears. The value is automatically
    /// capped at the strand length. Setting only takes effect if shape matching is enabled.
    /// Range [2, inf).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxHair:localShapeMatchingGroupSize = 32` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetLocalShapeMatchingGroupSizeAttr() const;

    /// See GetLocalShapeMatchingGroupSizeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLocalShapeMatchingGroupSizeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOCALSHAPEMATCHINGGROUPOVERLAP
    // --------------------------------------------------------------------- //
    /// Number of vertices by which consecutive shape-matching groups are overlapping.
    /// Only takes effect if shape matching is enabled.
    /// Default value of -1 means maximum overlap, i.e., shapeMatchingGroupSize/2
    /// Range [0, shapeMatchingGroupSize/2].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxHair:localShapeMatchingGroupOverlap = -1` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetLocalShapeMatchingGroupOverlapAttr() const;

    /// See GetLocalShapeMatchingGroupOverlapAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLocalShapeMatchingGroupOverlapAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxHairAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxHairAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxHairAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxHairAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxHairAPI::GetExternalCollisionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairExternalCollision));
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::CreateExternalCollisionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairExternalCollision), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::GetTwosidedAttachmentAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairTwosidedAttachment));
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::CreateTwosidedAttachmentAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairTwosidedAttachment), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::GetSegmentLengthAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairSegmentLength));
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::CreateSegmentLengthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairSegmentLength), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::GetGlobalShapeComplianceAtRootAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairGlobalShapeComplianceAtRoot));
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::CreateGlobalShapeComplianceAtRootAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairGlobalShapeComplianceAtRoot),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::GetGlobalShapeComplianceStrandAttenuationAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairGlobalShapeComplianceStrandAttenuation));
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::CreateGlobalShapeComplianceStrandAttenuationAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairGlobalShapeComplianceStrandAttenuation),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::GetInterHairRepulsionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairInterHairRepulsion));
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::CreateInterHairRepulsionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairInterHairRepulsion), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::GetVelSmoothingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairVelSmoothing));
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::CreateVelSmoothingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairVelSmoothing), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::GetLocalShapeMatchingComplianceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairLocalShapeMatchingCompliance));
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::CreateLocalShapeMatchingComplianceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairLocalShapeMatchingCompliance),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::GetLocalShapeMatchingLinearStretchingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairLocalShapeMatchingLinearStretching));
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::CreateLocalShapeMatchingLinearStretchingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairLocalShapeMatchingLinearStretching),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::GetLocalShapeMatchingGroupSizeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairLocalShapeMatchingGroupSize));
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::CreateLocalShapeMatchingGroupSizeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairLocalShapeMatchingGroupSize),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::GetLocalShapeMatchingGroupOverlapAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairLocalShapeMatchingGroupOverlap));
}

inline UsdAttribute PhysxSchemaPhysxHairAPI::CreateLocalShapeMatchingGroupOverlapAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairLocalShapeMatchingGroupOverlap),
                                     SdfValueTypeNames->Int,
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
