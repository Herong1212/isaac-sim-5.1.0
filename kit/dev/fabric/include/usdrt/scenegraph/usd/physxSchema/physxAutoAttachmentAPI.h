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

/// @file physxSchema/physxAutoAttachmentAPI.h

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
// PHYSXAUTOATTACHMENTAPI                                                      //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxAutoAttachmentAPI
///
/// Auto generates the attachment points and filtering ids based on the attributes defined in the API.

class PhysxSchemaPhysxAutoAttachmentAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxAutoAttachmentAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxAutoAttachmentAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxAutoAttachmentAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxAutoAttachmentAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxAutoAttachmentAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxAutoAttachmentAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxAutoAttachmentAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxAutoAttachmentAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxAutoAttachmentAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxAutoAttachmentAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxAutoAttachmentAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxAutoAttachmentAPI>())
        {
            return PhysxSchemaPhysxAutoAttachmentAPI(prim);
        }
        return PhysxSchemaPhysxAutoAttachmentAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ENABLEDEFORMABLEVERTEXATTACHMENTS
    // --------------------------------------------------------------------- //
    /// Enables attaching deformable mesh vertices which overlap with the other actor's volume.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxAutoAttachment:enableDeformableVertexAttachments = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableDeformableVertexAttachmentsAttr() const;

    /// See GetEnableDeformableVertexAttachmentsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableDeformableVertexAttachmentsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DEFORMABLEVERTEXOVERLAPOFFSET
    // --------------------------------------------------------------------- //
    /// Deformable mesh vertices are attached if their distance to the other actor's volume is smaller than the offset.
    /// Range: [0, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxAutoAttachment:deformableVertexOverlapOffset = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDeformableVertexOverlapOffsetAttr() const;

    /// See GetDeformableVertexOverlapOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDeformableVertexOverlapOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLERIGIDSURFACEATTACHMENTS
    // --------------------------------------------------------------------- //
    /// Enables sampling attachment points on the rigid actor's surface.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxAutoAttachment:enableRigidSurfaceAttachments = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableRigidSurfaceAttachmentsAttr() const;

    /// See GetEnableRigidSurfaceAttachmentsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableRigidSurfaceAttachmentsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RIGIDSURFACESAMPLINGDISTANCE
    // --------------------------------------------------------------------- //
    /// Attachment points on the rigid surface are positioned such that their typical neighbor distance matches the
    /// sampling distance. Use heuristic by default. Range: [0, inf) Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxAutoAttachment:rigidSurfaceSamplingDistance = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRigidSurfaceSamplingDistanceAttr() const;

    /// See GetRigidSurfaceSamplingDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRigidSurfaceSamplingDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLECOLLISIONFILTERING
    // --------------------------------------------------------------------- //
    /// Enables adding collision filtering in the vicinity of the attachment points.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxAutoAttachment:enableCollisionFiltering = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableCollisionFilteringAttr() const;

    /// See GetEnableCollisionFilteringAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableCollisionFilteringAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONFILTERINGOFFSET
    // --------------------------------------------------------------------- //
    /// Filtering ids are generated for deformable mesh vertices if their distance to the other actor's volume is
    /// smaller than the offset. Use heuristic by default. Range: [0, inf) Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxAutoAttachment:collisionFilteringOffset = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCollisionFilteringOffsetAttr() const;

    /// See GetCollisionFilteringOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollisionFilteringOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLEDEFORMABLEFILTERINGPAIRS
    // --------------------------------------------------------------------- //
    /// Enables geometry pair based collision filtering for deformable-deformable attachments.
    /// By default a filtered geometry of one actor is filtered against all geometries of the other actor.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxAutoAttachment:enableDeformableFilteringPairs = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableDeformableFilteringPairsAttr() const;

    /// See GetEnableDeformableFilteringPairsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableDeformableFilteringPairsAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxAutoAttachmentAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxAutoAttachmentAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxAutoAttachmentAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxAutoAttachmentAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::GetEnableDeformableVertexAttachmentsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentEnableDeformableVertexAttachments));
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::CreateEnableDeformableVertexAttachmentsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentEnableDeformableVertexAttachments),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::GetDeformableVertexOverlapOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentDeformableVertexOverlapOffset));
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::CreateDeformableVertexOverlapOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentDeformableVertexOverlapOffset),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::GetEnableRigidSurfaceAttachmentsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentEnableRigidSurfaceAttachments));
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::CreateEnableRigidSurfaceAttachmentsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentEnableRigidSurfaceAttachments),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::GetRigidSurfaceSamplingDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentRigidSurfaceSamplingDistance));
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::CreateRigidSurfaceSamplingDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentRigidSurfaceSamplingDistance),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::GetEnableCollisionFilteringAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentEnableCollisionFiltering));
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::CreateEnableCollisionFilteringAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentEnableCollisionFiltering),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::GetCollisionFilteringOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentCollisionFilteringOffset));
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::CreateCollisionFilteringOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentCollisionFilteringOffset),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::GetEnableDeformableFilteringPairsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentEnableDeformableFilteringPairs));
}

inline UsdAttribute PhysxSchemaPhysxAutoAttachmentAPI::CreateEnableDeformableFilteringPairsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxAutoAttachmentEnableDeformableFilteringPairs),
                                     SdfValueTypeNames->Bool,
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
