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

/// @file physxSchema/physxPBDMaterialAPI.h

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
// PHYSXPBDMATERIALAPI                                                         //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxPBDMaterialAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// Applied to a USD Material. PhysX position-based-dynamics (PBD) material for particles used to simulate fluids, cloth
/// and inflatables. Currently, only a single material per particle system is supported which applies to all objects
/// that are associated with the system.

class PhysxSchemaPhysxPBDMaterialAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxPBDMaterialAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxPBDMaterialAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxPBDMaterialAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxPBDMaterialAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxPBDMaterialAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxPBDMaterialAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxPBDMaterialAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxPBDMaterialAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxPBDMaterialAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxPBDMaterialAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxPBDMaterialAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxPBDMaterialAPI>())
        {
            return PhysxSchemaPhysxPBDMaterialAPI(prim);
        }
        return PhysxSchemaPhysxPBDMaterialAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FRICTION
    // --------------------------------------------------------------------- //
    /// Friction coefficient. The maximal friction force tangential to the surface is equal to the normal force times
    /// the friction. The friction takes effect in all interactions between particles and rigids or deformables.
    /// For solid particle-particle interactions it is multiplied by the particle friction scale.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:friction = 0.2` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFrictionAttr() const;

    /// See GetFrictionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFrictionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PARTICLEFRICTIONSCALE
    // --------------------------------------------------------------------- //
    /// Coefficient that scales friction for solid particle-particle interations.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:particleFrictionScale = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetParticleFrictionScaleAttr() const;

    /// See GetParticleFrictionScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateParticleFrictionScaleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DAMPING
    // --------------------------------------------------------------------- //
    /// Global velocity damping coefficient.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:damping = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDampingAttr() const;

    /// See GetDampingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDampingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VISCOSITY
    // --------------------------------------------------------------------- //
    /// Viscosity for fluid particles.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:viscosity = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetViscosityAttr() const;

    /// See GetViscosityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateViscosityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VORTICITYCONFINEMENT
    // --------------------------------------------------------------------- //
    /// Vorticity confinement for fluid particles. Helps prevent energy loss due to numerical solver by adding
    /// vortex-like accelerations to the particles. Range: [0, inf) Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:vorticityConfinement = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetVorticityConfinementAttr() const;

    /// See GetVorticityConfinementAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVorticityConfinementAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SURFACETENSION
    // --------------------------------------------------------------------- //
    /// Surface tension for fluid particles.
    /// Range: [0, inf)
    /// Units: 1 / (distance * distance * distance)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:surfaceTension = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSurfaceTensionAttr() const;

    /// See GetSurfaceTensionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSurfaceTensionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COHESION
    // --------------------------------------------------------------------- //
    /// Cohesion for interaction between fluid particles.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:cohesion = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCohesionAttr() const;

    /// See GetCohesionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCohesionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ADHESION
    // --------------------------------------------------------------------- //
    /// Adhesion for interactions between particles (solid or fluid), and rigids or deformables.
    /// Adhesion also applies to solid-solid particle interactions, but is multiplied with the particle adhesion scale.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:adhesion = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetAdhesionAttr() const;

    /// See GetAdhesionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAdhesionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PARTICLEADHESIONSCALE
    // --------------------------------------------------------------------- //
    /// Coefficient that scales adhesion for solid particle-particle interations.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:particleAdhesionScale = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetParticleAdhesionScaleAttr() const;

    /// See GetParticleAdhesionScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateParticleAdhesionScaleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ADHESIONOFFSETSCALE
    // --------------------------------------------------------------------- //
    /// Offset scale defining the offset at which adhesion ceases to take effect. For interactions between particles
    /// (fluid or solid), and rigids or deformables, the adhesion offset is defined relative to the rest offset. For
    /// solid particle-particle interactions, the adhesion offset is defined relative to the solid rest offset. Range:
    /// [0, inf) Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:adhesionOffsetScale = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetAdhesionOffsetScaleAttr() const;

    /// See GetAdhesionOffsetScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAdhesionOffsetScaleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GRAVITYSCALE
    // --------------------------------------------------------------------- //
    /// Gravitational acceleration scaling factor. Can be used to approximate lighter-than-air inflatables, for example
    /// (-1.0 would invert gravity). Range: (-inf, inf) Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:gravityScale = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetGravityScaleAttr() const;

    /// See GetGravityScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGravityScaleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LIFT
    // --------------------------------------------------------------------- //
    /// Lift coefficient for cloth and inflatable particle objects. Basic aerodynamic lift model coefficient.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:lift = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLiftAttr() const;

    /// See GetLiftAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLiftAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DRAG
    // --------------------------------------------------------------------- //
    /// Drag coefficient for cloth and inflatable particle objects. Basic aerodynamic drag model coefficient.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:drag = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDragAttr() const;

    /// See GetDragAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDragAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DENSITY
    // --------------------------------------------------------------------- //
    /// Density used to compute particle object mass. If set to 0.0, the simulation determines a default density.
    /// A density or mass set with a PhysicsMassAPI on a particle object overrides the material density.
    /// Range: [0, inf)
    /// Units: mass / distance / distance / distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:density = 0` |
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
    // CFLCOEFFICIENT
    // --------------------------------------------------------------------- //
    /// This coefficient scales the CFL term used to limit relative motion between approaching fluid particles. A very
    /// large value disables the limit. Range: [0, inf) Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxPBDMaterial:cflCoefficient = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCflCoefficientAttr() const;

    /// See GetCflCoefficientAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCflCoefficientAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxPBDMaterialAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxPBDMaterialAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxPBDMaterialAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxPBDMaterialAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetFrictionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialFriction));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateFrictionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialFriction), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetParticleFrictionScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialParticleFrictionScale));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateParticleFrictionScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialParticleFrictionScale),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetDampingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialDamping));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateDampingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialDamping), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetViscosityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialViscosity));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateViscosityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialViscosity), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetVorticityConfinementAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialVorticityConfinement));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateVorticityConfinementAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialVorticityConfinement),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetSurfaceTensionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialSurfaceTension));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateSurfaceTensionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialSurfaceTension), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetCohesionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialCohesion));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateCohesionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialCohesion), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetAdhesionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialAdhesion));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateAdhesionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialAdhesion), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetParticleAdhesionScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialParticleAdhesionScale));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateParticleAdhesionScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialParticleAdhesionScale),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetAdhesionOffsetScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialAdhesionOffsetScale));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateAdhesionOffsetScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialAdhesionOffsetScale),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetGravityScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialGravityScale));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateGravityScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialGravityScale), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetLiftAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialLift));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateLiftAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialLift), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetDragAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialDrag));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateDragAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialDrag), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetDensityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialDensity));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateDensityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialDensity), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::GetCflCoefficientAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialCflCoefficient));
}

inline UsdAttribute PhysxSchemaPhysxPBDMaterialAPI::CreateCflCoefficientAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxPBDMaterialCflCoefficient), SdfValueTypeNames->Float,
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
