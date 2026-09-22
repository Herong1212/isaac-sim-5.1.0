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

/// @file physxSchema/physxParticleSetAPI.h

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
// PHYSXPARTICLESETAPI                                                         //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxParticleSetAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// Applied to a UsdGeomPointInstancer or a UsdGeomPointBased. Creates a set of particles for granular (i.e.
/// solid-particle) material or fluid simulation with PhysX.

class PhysxSchemaPhysxParticleSetAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxParticleSetAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxParticleSetAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxParticleSetAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxParticleSetAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxParticleSetAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxParticleSetAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxParticleSetAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxParticleSetAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxParticleSetAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxParticleSetAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxParticleSetAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxParticleSetAPI>())
        {
            return PhysxSchemaPhysxParticleSetAPI(prim);
        }
        return PhysxSchemaPhysxParticleSetAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FLUID
    // --------------------------------------------------------------------- //
    /// Flag to toggle simulation as fluid (True) or solid (False).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxParticle:fluid = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetFluidAttr() const;

    /// See GetFluidAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFluidAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SIMULATIONPOINTS
    // --------------------------------------------------------------------- //
    /// This attribute is read-only and is updated from simulation to capture particle-simulation state while smoothed
    /// position data is written to the render position/points attribute of the UsdGeomPointInstancer/UsdGeomPoints.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] physxParticle:simulationPoints` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetSimulationPointsAttr() const;

    /// See GetSimulationPointsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSimulationPointsAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxParticleSetAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxParticleSetAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxParticleSetAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxParticleSetAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxParticleSetAPI::GetFluidAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleFluid));
}

inline UsdAttribute PhysxSchemaPhysxParticleSetAPI::CreateFluidAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleFluid), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSetAPI::GetSimulationPointsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleSimulationPoints));
}

inline UsdAttribute PhysxSchemaPhysxParticleSetAPI::CreateSimulationPointsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleSimulationPoints),
                                     SdfValueTypeNames->Point3fArray,
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
