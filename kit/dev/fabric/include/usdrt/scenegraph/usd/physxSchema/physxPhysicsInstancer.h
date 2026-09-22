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

/// @file physxSchema/physxPhysicsInstancer.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/imageable.h"
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
// PHYSXPHYSICSINSTANCER                                                       //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxPhysicsInstancer
///
/// Core class for instancing physics prims

class PhysxSchemaPhysxPhysicsInstancer : public UsdGeomImageable
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a PhysxSchemaPhysxPhysicsInstancer on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxPhysicsInstancer::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxPhysicsInstancer(const UsdPrim& prim = UsdPrim()) : UsdGeomImageable(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxPhysicsInstancer on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxPhysicsInstancer(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxPhysicsInstancer(const UsdSchemaBase& schemaObj) : UsdGeomImageable(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxPhysicsInstancer()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static PhysxSchemaPhysxPhysicsInstancer Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // PHYSICSPROTOINDICES
    // --------------------------------------------------------------------- //
    /// <b>Required property</b>. Per-instance index into
    /// \em prototypes relationship that identifies what physics prims are instanced.  <b>Topology attribute</b> - can
    /// be animated, but at a potential performance impact for streaming.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] physics:protoIndices` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetPhysicsProtoIndicesAttr() const;

    /// See GetPhysicsProtoIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePhysicsProtoIndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PHYSICSPROTOTYPES
    // --------------------------------------------------------------------- //
    /// <b>Required property</b>. Orders and targets the prototype root
    /// prims, which can be located anywhere in the scenegraph that is convenient,
    /// although we promote organizing prototypes as children of the
    /// PhysxPhysicsInstancer.  The position of a prototype in this relationship defines
    /// the value an instance would specify in the \em protoIndices attribute to
    /// instance that prototype. Since relationships are uniform, this property
    /// cannot be animated.
    ///
    UsdRelationship GetPhysicsPrototypesRel() const;

    /// See GetPhysicsPrototypesRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreatePhysicsPrototypesRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxPhysicsInstancer::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxPhysicsInstancer");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxPhysicsInstancer::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxPhysicsInstancer");
    return token;
}

/* static */
inline PhysxSchemaPhysxPhysicsInstancer PhysxSchemaPhysxPhysicsInstancer::Define(const UsdStageRefPtr& stage,
                                                                                 const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return PhysxSchemaPhysxPhysicsInstancer();
    }
    return PhysxSchemaPhysxPhysicsInstancer(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute PhysxSchemaPhysxPhysicsInstancer::GetPhysicsProtoIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physicsProtoIndices));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsInstancer::CreatePhysicsProtoIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physicsProtoIndices), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxPhysicsInstancer::GetPhysicsPrototypesRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physicsPrototypes);
}

inline UsdRelationship PhysxSchemaPhysxPhysicsInstancer::CreatePhysicsPrototypesRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physicsPrototypes,
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
