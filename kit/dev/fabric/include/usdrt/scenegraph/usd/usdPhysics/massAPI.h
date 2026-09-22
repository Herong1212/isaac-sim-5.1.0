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

/// @file usdPhysics/massAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdPhysics/tokens.h"


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
// PHYSICSMASSAPI                                                              //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsMassAPI
///
/// Defines explicit mass properties (mass, density, inertia etc.).
/// MassAPI can be applied to any object that has a PhysicsCollisionAPI or
/// a PhysicsRigidBodyAPI.

class UsdPhysicsMassAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdPhysicsMassAPI on UsdPrim @p prim.
    /// Equivalent to UsdPhysicsMassAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsMassAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdPhysicsMassAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdPhysicsMassAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdPhysicsMassAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsMassAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysicsMassAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdPhysicsMassAPI object is returned upon success.
    /// An invalid (or empty) UsdPhysicsMassAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdPhysicsMassAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdPhysicsMassAPI>())
        {
            return UsdPhysicsMassAPI(prim);
        }
        return UsdPhysicsMassAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // MASS
    // --------------------------------------------------------------------- //
    /// If non-zero, directly specifies the mass of the object.
    /// Note that any child prim can also have a mass when they apply massAPI.
    /// In this case, the precedence rule is 'parent mass overrides the
    /// child's'. This may come as counter-intuitive, but mass is a computed
    /// quantity and in general not accumulative. For example, if a parent
    /// has mass of 10, and one of two children has mass of 20, allowing
    /// child's mass to override its parent results in a mass of -10 for the
    /// other child. Note if mass is 0.0 it is ignored. Units: mass.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:mass = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMassAttr() const;

    /// See GetMassAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMassAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DENSITY
    // --------------------------------------------------------------------- //
    /// If non-zero, specifies the density of the object.
    /// In the context of rigid body physics, density indirectly results in
    /// setting mass via (mass = density x volume of the object). How the
    /// volume is computed is up to implementation of the physics system.
    /// It is generally computed from the collision approximation rather than
    /// the graphical mesh. In the case where both density and mass are
    /// specified for the same object, mass has precedence over density.
    /// Unlike mass, child's prim's density overrides parent prim's density
    /// as it is accumulative. Note that density of a collisionAPI can be also
    /// alternatively set through a PhysicsMaterialAPI. The material density
    /// has the weakest precedence in density definition. Note if density is
    /// 0.0 it is ignored. Units: mass/distance/distance/distance.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:density = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDensityAttr() const;

    /// See GetDensityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDensityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CENTEROFMASS
    // --------------------------------------------------------------------- //
    /// Center of mass in the prim's local space. Units: distance.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f physics:centerOfMass = (-inf, -inf, -inf)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3f |

    UsdAttribute GetCenterOfMassAttr() const;

    /// See GetCenterOfMassAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCenterOfMassAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DIAGONALINERTIA
    // --------------------------------------------------------------------- //
    /// If non-zero, specifies diagonalized inertia tensor along the
    /// principal axes. Note if diagonalInertial is (0.0, 0.0, 0.0) it is
    /// ignored. Units: mass*distance*distance.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physics:diagonalInertia = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetDiagonalInertiaAttr() const;

    /// See GetDiagonalInertiaAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDiagonalInertiaAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PRINCIPALAXES
    // --------------------------------------------------------------------- //
    /// Orientation of the inertia tensor's principal axes in the
    /// prim's local space.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `quatf physics:principalAxes = (0, 0, 0, 0)` |
    /// | C++ Type | GfQuatf |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Quatf |

    UsdAttribute GetPrincipalAxesAttr() const;

    /// See GetPrincipalAxesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePrincipalAxesAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsMassAPI::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsMassAPI");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsMassAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsMassAPI");
    return token;
}


inline UsdAttribute UsdPhysicsMassAPI::GetMassAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsMass));
}

inline UsdAttribute UsdPhysicsMassAPI::CreateMassAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsMass), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsMassAPI::GetDensityAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsDensity));
}

inline UsdAttribute UsdPhysicsMassAPI::CreateDensityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsDensity), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsMassAPI::GetCenterOfMassAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsCenterOfMass));
}

inline UsdAttribute UsdPhysicsMassAPI::CreateCenterOfMassAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsCenterOfMass), SdfValueTypeNames->Point3f,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsMassAPI::GetDiagonalInertiaAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsDiagonalInertia));
}

inline UsdAttribute UsdPhysicsMassAPI::CreateDiagonalInertiaAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsDiagonalInertia), SdfValueTypeNames->Float3,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsMassAPI::GetPrincipalAxesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsPrincipalAxes));
}

inline UsdAttribute UsdPhysicsMassAPI::CreatePrincipalAxesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsPrincipalAxes), SdfValueTypeNames->Quatf,
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
