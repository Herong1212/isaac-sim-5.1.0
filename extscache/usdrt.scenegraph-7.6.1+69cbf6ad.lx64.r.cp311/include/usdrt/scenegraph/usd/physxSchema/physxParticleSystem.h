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

/// @file physxSchema/physxParticleSystem.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/gprim.h"
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
// PHYSXPARTICLESYSTEM                                                         //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxParticleSystem
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// PhysX particle system, used to simulate fluids, cloth and inflatables. This prim allows the user to configure the
/// solver parameters that are common to the particle objects associated with this system via their particleSystem
/// relationship.

class PhysxSchemaPhysxParticleSystem : public UsdGeomGprim
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a PhysxSchemaPhysxParticleSystem on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxParticleSystem::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxParticleSystem(const UsdPrim& prim = UsdPrim()) : UsdGeomGprim(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxParticleSystem on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxParticleSystem(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxParticleSystem(const UsdSchemaBase& schemaObj) : UsdGeomGprim(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxParticleSystem()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static PhysxSchemaPhysxParticleSystem Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // PARTICLESYSTEMENABLED
    // --------------------------------------------------------------------- //
    /// Enable or disable the particle system.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool particleSystemEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetParticleSystemEnabledAttr() const;

    /// See GetParticleSystemEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateParticleSystemEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CONTACTOFFSET
    // --------------------------------------------------------------------- //
    /// Contact offset used for collisions with non-particle objects such as rigid or deformable bodies.
    /// Must be larger than restOffset. Default value -inf results in a simulation-determined value.
    /// Range: (restOffset, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float contactOffset = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetContactOffsetAttr() const;

    /// See GetContactOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateContactOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RESTOFFSET
    // --------------------------------------------------------------------- //
    /// Rest offset used for collisions with non-particle objects such as rigid or deformable bodies.
    /// Must be smaller than contact offset. Default value -inf results in a simulation-determined value.
    /// Range: [0, contactOffset)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float restOffset = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRestOffsetAttr() const;

    /// See GetRestOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRestOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PARTICLECONTACTOFFSET
    // --------------------------------------------------------------------- //
    /// Contact offset used for interactions between particles. Must be larger than solid and fluid rest offsets.
    /// Range: (max(solidRestOffset, fluidRestOffset), inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float particleContactOffset = 0.05` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetParticleContactOffsetAttr() const;

    /// See GetParticleContactOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateParticleContactOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SOLIDRESTOFFSET
    // --------------------------------------------------------------------- //
    /// Rest offset used for solid-solid or solid-fluid particle interactions. Must be smaller than
    /// particleContactOffset. Default value -inf results in a simulation-determined value. Range: [0,
    /// particleContactOffset) Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float solidRestOffset = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSolidRestOffsetAttr() const;

    /// See GetSolidRestOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSolidRestOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FLUIDRESTOFFSET
    // --------------------------------------------------------------------- //
    /// Rest offset used for fluid-fluid particle interactions. Must be smaller than particleContactOffset.
    /// Default value -inf results in a simulation-determined value.
    /// Range: [0, particleContactOffset)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float fluidRestOffset = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFluidRestOffsetAttr() const;

    /// See GetFluidRestOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFluidRestOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLECCD
    // --------------------------------------------------------------------- //
    /// Enable continuous collision detection for particles to help avoid tunneling effects.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool enableCCD = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableCCDAttr() const;

    /// See GetEnableCCDAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableCCDAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SOLVERPOSITIONITERATIONCOUNT
    // --------------------------------------------------------------------- //
    /// Number of solver iterations for position.
    /// Range: [1, 255]
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int solverPositionIterationCount = 16` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetSolverPositionIterationCountAttr() const;

    /// See GetSolverPositionIterationCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSolverPositionIterationCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXDEPENETRATIONVELOCITY
    // --------------------------------------------------------------------- //
    /// The maximum velocity permitted to be introduced by the solver to depenetrate intersecting particles.
    /// Range: [0, inf)
    /// Units: distance / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float maxDepenetrationVelocity = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxDepenetrationVelocityAttr() const;

    /// See GetMaxDepenetrationVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxDepenetrationVelocityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WIND
    // --------------------------------------------------------------------- //
    /// The wind applied to the current particle system.
    /// Range: (-inf, inf)
    /// Units: distance / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 wind = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetWindAttr() const;

    /// See GetWindAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWindAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXNEIGHBORHOOD
    // --------------------------------------------------------------------- //
    /// Defines how many particle neighbors per particle may be considered for interaction computations.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int maxNeighborhood = 96` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetMaxNeighborhoodAttr() const;

    /// See GetMaxNeighborhoodAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxNeighborhoodAttr() const;

public:
    // --------------------------------------------------------------------- //
    // NEIGHBORHOODSCALE
    // --------------------------------------------------------------------- //
    /// Defines by how much the default neighborhood volume is inflated to ensure that all relevant neighboring
    /// particles are found while particles interact. Simulations with high relative velocities might require larger
    /// volumes. Range: [1, inf)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float neighborhoodScale = 1.01` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetNeighborhoodScaleAttr() const;

    /// See GetNeighborhoodScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateNeighborhoodScaleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXVELOCITY
    // --------------------------------------------------------------------- //
    /// Maximum particle velocity. See also cflCoefficient in PhysxPBDMaterialAPI for limiting particle-particle
    /// relative velocity. Range: [0, inf) Units: distance / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float maxVelocity = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxVelocityAttr() const;

    /// See GetMaxVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxVelocityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GLOBALSELFCOLLISIONENABLED
    // --------------------------------------------------------------------- //
    /// If True, self collisions follow particle-object-specific settings. If False, all particle self collisions are
    /// disabled, regardless of any other settings. Improves performance if self collisions are not needed.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool globalSelfCollisionEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetGlobalSelfCollisionEnabledAttr() const;

    /// See GetGlobalSelfCollisionEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGlobalSelfCollisionEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // NONPARTICLECOLLISIONENABLED
    // --------------------------------------------------------------------- //
    /// Enable or disable particle collision with nonparticle objects for all particles in the system.
    /// Improves performance if nonparticle collisions are not needed.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool nonParticleCollisionEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetNonParticleCollisionEnabledAttr() const;

    /// See GetNonParticleCollisionEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateNonParticleCollisionEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SIMULATIONOWNER
    // --------------------------------------------------------------------- //
    /// Single PhysicsScene that simulates this particle system. By default,
    /// this is the first PhysicsScene found in the stage using UsdStage::Traverse().
    ///
    UsdRelationship GetSimulationOwnerRel() const;

    /// See GetSimulationOwnerRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateSimulationOwnerRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxParticleSystem::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxParticleSystem");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxParticleSystem::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxParticleSystem");
    return token;
}

/* static */
inline PhysxSchemaPhysxParticleSystem PhysxSchemaPhysxParticleSystem::Define(const UsdStageRefPtr& stage,
                                                                             const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return PhysxSchemaPhysxParticleSystem();
    }
    return PhysxSchemaPhysxParticleSystem(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetParticleSystemEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->particleSystemEnabled));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateParticleSystemEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->particleSystemEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetContactOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->contactOffset));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateContactOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->contactOffset), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetRestOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->restOffset));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateRestOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->restOffset), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetParticleContactOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->particleContactOffset));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateParticleContactOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->particleContactOffset), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetSolidRestOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->solidRestOffset));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateSolidRestOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->solidRestOffset), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetFluidRestOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->fluidRestOffset));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateFluidRestOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->fluidRestOffset), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetEnableCCDAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->enableCCD));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateEnableCCDAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->enableCCD), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetSolverPositionIterationCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->solverPositionIterationCount));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateSolverPositionIterationCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->solverPositionIterationCount), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetMaxDepenetrationVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->maxDepenetrationVelocity));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateMaxDepenetrationVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->maxDepenetrationVelocity), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetWindAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->wind));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateWindAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->wind), SdfValueTypeNames->Float3,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetMaxNeighborhoodAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->maxNeighborhood));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateMaxNeighborhoodAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->maxNeighborhood), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetNeighborhoodScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->neighborhoodScale));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateNeighborhoodScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->neighborhoodScale), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetMaxVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->maxVelocity));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateMaxVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->maxVelocity), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetGlobalSelfCollisionEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->globalSelfCollisionEnabled));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateGlobalSelfCollisionEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->globalSelfCollisionEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::GetNonParticleCollisionEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->nonParticleCollisionEnabled));
}

inline UsdAttribute PhysxSchemaPhysxParticleSystem::CreateNonParticleCollisionEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->nonParticleCollisionEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxParticleSystem::GetSimulationOwnerRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->simulationOwner);
}

inline UsdRelationship PhysxSchemaPhysxParticleSystem::CreateSimulationOwnerRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->simulationOwner,
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
