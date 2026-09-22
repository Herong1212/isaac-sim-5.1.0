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

/// @file physxSchema/physxForceAPI.h

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
// PHYSXFORCEAPI                                                               //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxForceAPI
///
/// PhysX schema API that applies a force and torque to a rigid body
/// (UsdGeom.Xformable with UsdPhysicsRigidBodyAPI). The API can be applied to either:
/// - The rigid-body Xformable, in which case the force is applied at the body's center of mass.
/// - To an UsdGeom.Xformable that is a child of the rigid-body Xformable,
/// in which case the force is applied at the location defined by the Xformable.
///
/// The worldFrameEnabled flag defines what coordinate frame the force and torque are expressed in.
/// Note that any scale transform operations will only affect the force and torque values if on "acceleration" mode.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref PhysxSchemaTokens.
/// So to set an attribute to the value "rightHanded", use PhysxSchemaTokens->rightHanded
/// as the value.

class PhysxSchemaPhysxForceAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxForceAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxForceAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxForceAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxForceAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxForceAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxForceAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxForceAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxForceAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxForceAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxForceAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxForceAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxForceAPI>())
        {
            return PhysxSchemaPhysxForceAPI(prim);
        }
        return PhysxSchemaPhysxForceAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FORCEENABLED
    // --------------------------------------------------------------------- //
    /// Boolean defining whether the force and torque are enabled or disabled.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxForce:forceEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetForceEnabledAttr() const;

    /// See GetForceEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateForceEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WORLDFRAMEENABLED
    // --------------------------------------------------------------------- //
    /// Boolean defining whether the force and torque are in world frame or in local frame.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxForce:worldFrameEnabled = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetWorldFrameEnabledAttr() const;

    /// See GetWorldFrameEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWorldFrameEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MODE
    // --------------------------------------------------------------------- //
    /// Force mode, can be either a force or an acceleration.
    /// force - units:  (linear) mass * distance / seconds^2, i.e. a force
    /// (angular) mass * distance * distance / time^2, i.e. a torque
    /// acceleration - units: (linear) distance / seconds^2, i.e. a linear acceleration.
    /// (angular) degrees / seconds^2, i.e. an angular acceleration.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxForce:mode = "acceleration"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | force, acceleration |

    UsdAttribute GetModeAttr() const;

    /// See GetModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateModeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FORCE
    // --------------------------------------------------------------------- //
    /// Force to apply defined in global or local frame depending on worldFrameEnabled. The force is applied at the
    /// position defined by the relative transform to the parent rigid-body Xformable, or at the body's center of mass
    /// if the API is applied directly to a rigid-body Xformable. For units see mode attribute. Range: (-inf, inf)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physxForce:force = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetForceAttr() const;

    /// See GetForceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateForceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TORQUE
    // --------------------------------------------------------------------- //
    /// Torque to apply defined in the global or local frame depending on worldFrameEnabled. For units see mode
    /// attribute. Range: (-inf, inf)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physxForce:torque = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetTorqueAttr() const;

    /// See GetTorqueAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTorqueAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxForceAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxForceAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxForceAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxForceAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxForceAPI::GetForceEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxForceForceEnabled));
}

inline UsdAttribute PhysxSchemaPhysxForceAPI::CreateForceEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxForceForceEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxForceAPI::GetWorldFrameEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxForceWorldFrameEnabled));
}

inline UsdAttribute PhysxSchemaPhysxForceAPI::CreateWorldFrameEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxForceWorldFrameEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxForceAPI::GetModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxForceMode));
}

inline UsdAttribute PhysxSchemaPhysxForceAPI::CreateModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxForceMode), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxForceAPI::GetForceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxForceForce));
}

inline UsdAttribute PhysxSchemaPhysxForceAPI::CreateForceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxForceForce), SdfValueTypeNames->Vector3f,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxForceAPI::GetTorqueAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxForceTorque));
}

inline UsdAttribute PhysxSchemaPhysxForceAPI::CreateTorqueAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxForceTorque), SdfValueTypeNames->Vector3f,
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
