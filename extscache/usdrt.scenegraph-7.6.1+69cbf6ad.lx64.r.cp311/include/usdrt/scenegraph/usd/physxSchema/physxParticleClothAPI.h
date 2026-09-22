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

/// @file physxSchema/physxParticleClothAPI.h

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
// PHYSXPARTICLECLOTHAPI                                                       //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxParticleClothAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// Applied to a UsdGeomMesh. The mesh is simulated as a particle-based cloth or inflatable, depending on the mesh
/// geometry and the pressure attribute. See PhysxAutoParticleClothAPI for an auto-compute helper for cloth springs and
/// dampings.

class PhysxSchemaPhysxParticleClothAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxParticleClothAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxParticleClothAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxParticleClothAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxParticleClothAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxParticleClothAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxParticleClothAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxParticleClothAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxParticleClothAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxParticleClothAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxParticleClothAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxParticleClothAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxParticleClothAPI>())
        {
            return PhysxSchemaPhysxParticleClothAPI(prim);
        }
        return PhysxSchemaPhysxParticleClothAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SELFCOLLISIONFILTER
    // --------------------------------------------------------------------- //
    /// Whether the simulation should filter particle-particle collisions based on their rest position distances.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxParticle:selfCollisionFilter = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetSelfCollisionFilterAttr() const;

    /// See GetSelfCollisionFilterAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSelfCollisionFilterAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RESTPOINTS
    // --------------------------------------------------------------------- //
    /// Particle positions in cloth rest configuration.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] physxParticle:restPoints` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetRestPointsAttr() const;

    /// See GetRestPointsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRestPointsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPRINGINDICES
    // --------------------------------------------------------------------- //
    /// List of index pairs describing which points are connected by spring constraints.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform int2[] physxParticle:springIndices` |
    /// | C++ Type | VtArray<GfVec2i> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int2Array |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetSpringIndicesAttr() const;

    /// See GetSpringIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringIndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPRINGSTIFFNESSES
    // --------------------------------------------------------------------- //
    /// Stiffness values for linear-distance springs between a pair of particles as defined by index pairs in
    /// springIndices. Range: [0, inf) Units: force / distance = mass / second / second
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] physxParticle:springStiffnesses` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetSpringStiffnessesAttr() const;

    /// See GetSpringStiffnessesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringStiffnessesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPRINGDAMPINGS
    // --------------------------------------------------------------------- //
    /// Coefficients for linear-distance dampers between a pair of particles as defined by index pairs in springIndices.
    /// Range: [0, inf)
    /// Units: force * second / distance = mass / second
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] physxParticle:springDampings` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetSpringDampingsAttr() const;

    /// See GetSpringDampingsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringDampingsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPRINGRESTLENGTHS
    // --------------------------------------------------------------------- //
    /// Spring rest lengths corresponding to spring index pairs.
    /// Range: (-inf, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] physxParticle:springRestLengths` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetSpringRestLengthsAttr() const;

    /// See GetSpringRestLengthsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringRestLengthsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PRESSURE
    // --------------------------------------------------------------------- //
    /// Pressure: If > 0, a particle cloth has an additional pressure constraint
    /// that provides inflatable (i.e. balloon-like) dynamics. The pressure times the rest volume defines
    /// the volume the inflatable tries to match. Pressure only works well for closed or approximately closed meshes.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxParticle:pressure = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetPressureAttr() const;

    /// See GetPressureAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePressureAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxParticleClothAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxParticleClothAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxParticleClothAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxParticleClothAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::GetSelfCollisionFilterAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleSelfCollisionFilter));
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::CreateSelfCollisionFilterAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleSelfCollisionFilter),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::GetRestPointsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleRestPoints));
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::CreateRestPointsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleRestPoints), SdfValueTypeNames->Point3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::GetSpringIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleSpringIndices));
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::CreateSpringIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleSpringIndices), SdfValueTypeNames->Int2Array,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::GetSpringStiffnessesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleSpringStiffnesses));
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::CreateSpringStiffnessesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleSpringStiffnesses),
                                     SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::GetSpringDampingsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleSpringDampings));
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::CreateSpringDampingsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleSpringDampings),
                                     SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::GetSpringRestLengthsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleSpringRestLengths));
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::CreateSpringRestLengthsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleSpringRestLengths),
                                     SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::GetPressureAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticlePressure));
}

inline UsdAttribute PhysxSchemaPhysxParticleClothAPI::CreatePressureAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticlePressure), SdfValueTypeNames->Float,
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
