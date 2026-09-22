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

/// @file physxSchema/physxJointAPI.h

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
// PHYSXJOINTAPI                                                               //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxJointAPI
///
/// PhysX joint extended parameters

class PhysxSchemaPhysxJointAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxJointAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxJointAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxJointAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxJointAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxJointAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxJointAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxJointAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxJointAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxJointAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxJointAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxJointAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxJointAPI>())
        {
            return PhysxSchemaPhysxJointAPI(prim);
        }
        return PhysxSchemaPhysxJointAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ENABLEPROJECTION
    // --------------------------------------------------------------------- //
    /// Whether the actors should get projected for this constraint (the direction will be chosen by PhysX).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxJoint:enableProjection = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableProjectionAttr() const;

    /// See GetEnableProjectionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableProjectionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // JOINTFRICTION
    // --------------------------------------------------------------------- //
    /// Joint friction. Only applies for joints that are parts of an articulation.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxJoint:jointFriction = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetJointFrictionAttr() const;

    /// See GetJointFrictionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateJointFrictionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXJOINTVELOCITY
    // --------------------------------------------------------------------- //
    /// Maximum joint velocity.
    /// Range: [0, inf)
    /// Units: Linear joint - distance / time
    /// Angular joint - degrees / time
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxJoint:maxJointVelocity = 1000000` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxJointVelocityAttr() const;

    /// See GetMaxJointVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxJointVelocityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ARMATURE
    // --------------------------------------------------------------------- //
    /// Armature can help stabilize an articulation by adding to the inertial response of a joint.
    /// Conceptually, armature represents the inertia of an actuator driving the joint.
    /// Note that this parameter is used only when the joint belongs to an articulation.
    /// Range: [0, inf)
    /// Units: Linear joint - mass
    /// Angular joint - mass * (distance)^2
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxJoint:armature = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetArmatureAttr() const;

    /// See GetArmatureAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateArmatureAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxJointAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxJointAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxJointAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxJointAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxJointAPI::GetEnableProjectionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxJointEnableProjection));
}

inline UsdAttribute PhysxSchemaPhysxJointAPI::CreateEnableProjectionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxJointEnableProjection), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxJointAPI::GetJointFrictionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxJointJointFriction));
}

inline UsdAttribute PhysxSchemaPhysxJointAPI::CreateJointFrictionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxJointJointFriction), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxJointAPI::GetMaxJointVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxJointMaxJointVelocity));
}

inline UsdAttribute PhysxSchemaPhysxJointAPI::CreateMaxJointVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxJointMaxJointVelocity), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxJointAPI::GetArmatureAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxJointArmature));
}

inline UsdAttribute PhysxSchemaPhysxJointAPI::CreateArmatureAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxJointArmature), SdfValueTypeNames->Float,
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
