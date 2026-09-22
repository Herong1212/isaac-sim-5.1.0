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

/// @file physxSchema/physxPhysicsAttachment.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"
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
// PHYSXPHYSICSATTACHMENT                                                      //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxPhysicsAttachment
///
/// Represents attachments between physics actors, for example, between a rigid body and a deformable body, or a
/// deformable body and a particle cloth. For any described attribute @em Fallback @em Value or @em Allowed @em Values
/// below that are text/tokens, the actual token is published and defined in @ref PhysxSchemaTokens. So to set an
/// attribute to the value "rightHanded", use PhysxSchemaTokens->rightHanded as the value.

class PhysxSchemaPhysxPhysicsAttachment : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a PhysxSchemaPhysxPhysicsAttachment on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxPhysicsAttachment::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxPhysicsAttachment(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxPhysicsAttachment on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxPhysicsAttachment(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxPhysicsAttachment(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxPhysicsAttachment()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static PhysxSchemaPhysxPhysicsAttachment Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ATTACHMENTENABLED
    // --------------------------------------------------------------------- //
    /// Enable or disable the attachment.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool attachmentEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetAttachmentEnabledAttr() const;

    /// See GetAttachmentEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAttachmentEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // POINTS0
    // --------------------------------------------------------------------- //
    /// Attachment points in Actor 0 local space, defined in the actor's rest state, if it is deformable. Elements
    /// correspond one-to-one to elements in points1 attribute.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] points0` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetPoints0Attr() const;

    /// See GetPoints0Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePoints0Attr() const;

public:
    // --------------------------------------------------------------------- //
    // POINTS1
    // --------------------------------------------------------------------- //
    /// Attachment points in Actor 1 local space, defined in the actor's rest state, if it is deformable. Elements
    /// correspond one-to-one to elements in points0 attribute.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] points1` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetPoints1Attr() const;

    /// See GetPoints1Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePoints1Attr() const;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONFILTERINDICES0
    // --------------------------------------------------------------------- //
    /// Indices to geometry of Actor 0 that should not generate collisions with Actor 1 as specified by filterType0.
    /// Ignored for rigid bodies.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint[] collisionFilterIndices0` |
    /// | C++ Type | VtArray<unsigned int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UIntArray |

    UsdAttribute GetCollisionFilterIndices0Attr() const;

    /// See GetCollisionFilterIndices0Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollisionFilterIndices0Attr() const;

public:
    // --------------------------------------------------------------------- //
    // FILTERTYPE0
    // --------------------------------------------------------------------- //
    /// Specify if indices in collisionFilterIndices0 correspond to vertices; or mesh cell-geometry, i.e. triangles,
    /// tetrahedrons, etc.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token filterType0` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | Vertices, Geometry |

    UsdAttribute GetFilterType0Attr() const;

    /// See GetFilterType0Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFilterType0Attr() const;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONFILTERINDICES1
    // --------------------------------------------------------------------- //
    /// Indices to mesh triangle/tet/hex/etc. of Actor 1 that should not generate collisions with Actor 0. Ignored for
    /// rigid bodies.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint[] collisionFilterIndices1` |
    /// | C++ Type | VtArray<unsigned int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UIntArray |

    UsdAttribute GetCollisionFilterIndices1Attr() const;

    /// See GetCollisionFilterIndices1Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollisionFilterIndices1Attr() const;

public:
    // --------------------------------------------------------------------- //
    // FILTERTYPE1
    // --------------------------------------------------------------------- //
    /// Specify if indices in collisionFilterIndices1 correspond to vertices; or mesh cell-geometry, i.e. triangles,
    /// tetrahedrons, etc.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token filterType1` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | Vertices, Geometry |

    UsdAttribute GetFilterType1Attr() const;

    /// See GetFilterType1Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFilterType1Attr() const;

public:
    // --------------------------------------------------------------------- //
    // ACTOR0
    // --------------------------------------------------------------------- //
    /// Reference to the first actor.
    ///
    UsdRelationship GetActor0Rel() const;

    /// See GetActor0Rel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateActor0Rel() const;

public:
    // --------------------------------------------------------------------- //
    // ACTOR1
    // --------------------------------------------------------------------- //
    /// Reference to the second actor.
    ///
    UsdRelationship GetActor1Rel() const;

    /// See GetActor1Rel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateActor1Rel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxPhysicsAttachment::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxPhysicsAttachment");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxPhysicsAttachment::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxPhysicsAttachment");
    return token;
}

/* static */
inline PhysxSchemaPhysxPhysicsAttachment PhysxSchemaPhysxPhysicsAttachment::Define(const UsdStageRefPtr& stage,
                                                                                   const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return PhysxSchemaPhysxPhysicsAttachment();
    }
    return PhysxSchemaPhysxPhysicsAttachment(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::GetAttachmentEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->attachmentEnabled));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::CreateAttachmentEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->attachmentEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::GetPoints0Attr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->points0));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::CreatePoints0Attr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->points0), SdfValueTypeNames->Point3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::GetPoints1Attr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->points1));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::CreatePoints1Attr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->points1), SdfValueTypeNames->Point3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::GetCollisionFilterIndices0Attr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->collisionFilterIndices0));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::CreateCollisionFilterIndices0Attr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->collisionFilterIndices0), SdfValueTypeNames->UIntArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::GetFilterType0Attr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->filterType0));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::CreateFilterType0Attr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->filterType0), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::GetCollisionFilterIndices1Attr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->collisionFilterIndices1));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::CreateCollisionFilterIndices1Attr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->collisionFilterIndices1), SdfValueTypeNames->UIntArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::GetFilterType1Attr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->filterType1));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsAttachment::CreateFilterType1Attr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->filterType1), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxPhysicsAttachment::GetActor0Rel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->actor0);
}

inline UsdRelationship PhysxSchemaPhysxPhysicsAttachment::CreateActor0Rel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->actor0,
                                        /* custom = */ false);
}
inline UsdRelationship PhysxSchemaPhysxPhysicsAttachment::GetActor1Rel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->actor1);
}

inline UsdRelationship PhysxSchemaPhysxPhysicsAttachment::CreateActor1Rel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->actor1,
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
