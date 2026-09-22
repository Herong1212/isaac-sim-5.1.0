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

/// @file physxSchema/physxPhysicsDistanceJointAPI.h

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
// PHYSXPHYSICSDISTANCEJOINTAPI                                                //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxPhysicsDistanceJointAPI
///
/// PhysX distance joint extended parameters

class PhysxSchemaPhysxPhysicsDistanceJointAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxPhysicsDistanceJointAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxPhysicsDistanceJointAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxPhysicsDistanceJointAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxPhysicsDistanceJointAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxPhysicsDistanceJointAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxPhysicsDistanceJointAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxPhysicsDistanceJointAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxPhysicsDistanceJointAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxPhysicsDistanceJointAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxPhysicsDistanceJointAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxPhysicsDistanceJointAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxPhysicsDistanceJointAPI>())
        {
            return PhysxSchemaPhysxPhysicsDistanceJointAPI(prim);
        }
        return PhysxSchemaPhysxPhysicsDistanceJointAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SPRINGENABLED
    // --------------------------------------------------------------------- //
    /// Whether spring should be enabled. (default off)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxPhysicsDistanceJoint:springEnabled = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetSpringEnabledAttr() const;

    /// See GetSpringEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPRINGSTIFFNESS
    // --------------------------------------------------------------------- //
    /// Spring stiffness.
    /// Range: [0, inf)
    /// Units: force / distance = mass / seconds^2
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPhysicsDistanceJoint:springStiffness = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpringStiffnessAttr() const;

    /// See GetSpringStiffnessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringStiffnessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPRINGDAMPING
    // --------------------------------------------------------------------- //
    /// Spring damping.
    /// Range: [0, inf)
    /// Units: force * seconds / distance = mass / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPhysicsDistanceJoint:springDamping = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpringDampingAttr() const;

    /// See GetSpringDampingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringDampingAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxPhysicsDistanceJointAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxPhysicsDistanceJointAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxPhysicsDistanceJointAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxPhysicsDistanceJointAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxPhysicsDistanceJointAPI::GetSpringEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPhysicsDistanceJointSpringEnabled));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsDistanceJointAPI::CreateSpringEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPhysicsDistanceJointSpringEnabled),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsDistanceJointAPI::GetSpringStiffnessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPhysicsDistanceJointSpringStiffness));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsDistanceJointAPI::CreateSpringStiffnessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPhysicsDistanceJointSpringStiffness),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsDistanceJointAPI::GetSpringDampingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPhysicsDistanceJointSpringDamping));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsDistanceJointAPI::CreateSpringDampingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPhysicsDistanceJointSpringDamping),
                                     SdfValueTypeNames->Float,
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
