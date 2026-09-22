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

/// @file physxSchema/physxAutoParticleClothAPI.h

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
// PHYSXAUTOPARTICLECLOTHAPI                                                   //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxAutoParticleClothAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// Applied to a UsdGeomMesh with PhysxParticleClothAPI. Defines parameters to automatically compute spring constraints.

class PhysxSchemaPhysxAutoParticleClothAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxAutoParticleClothAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxAutoParticleClothAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxAutoParticleClothAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxAutoParticleClothAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxAutoParticleClothAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxAutoParticleClothAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxAutoParticleClothAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxAutoParticleClothAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxAutoParticleClothAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxAutoParticleClothAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxAutoParticleClothAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxAutoParticleClothAPI>())
        {
            return PhysxSchemaPhysxAutoParticleClothAPI(prim);
        }
        return PhysxSchemaPhysxAutoParticleClothAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SPRINGSTRETCHSTIFFNESS
    // --------------------------------------------------------------------- //
    /// Stretch stiffness. Represents a stiffness for linear springs placed between particles to counteract stretching.
    /// Range: [0, inf)
    /// Units: force / distance = mass / second / second
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxAutoParticleCloth:springStretchStiffness = 1.5` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpringStretchStiffnessAttr() const;

    /// See GetSpringStretchStiffnessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringStretchStiffnessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPRINGBENDSTIFFNESS
    // --------------------------------------------------------------------- //
    /// Bend stiffness. Represents a stiffness for linear springs placed in a way to counteract bending.
    /// Range: [0, inf)
    /// Units:  force / distance = mass / second / second
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxAutoParticleCloth:springBendStiffness = 1.5` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpringBendStiffnessAttr() const;

    /// See GetSpringBendStiffnessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringBendStiffnessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPRINGSHEARSTIFFNESS
    // --------------------------------------------------------------------- //
    /// Shear stiffness. Represents a stiffness for linear springs placed in a way to counteract shear.
    /// Range: [0, inf)
    /// Units:  force / distance = mass / second / second
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxAutoParticleCloth:springShearStiffness = 1.5` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpringShearStiffnessAttr() const;

    /// See GetSpringShearStiffnessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringShearStiffnessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPRINGDAMPING
    // --------------------------------------------------------------------- //
    /// Damping on cloth spring constraints. Applies to all constraints parametrized by stiffness attributes.
    /// Range: [0, inf)
    /// Units: force * second / distance = mass / second
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxAutoParticleCloth:springDamping = 10` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpringDampingAttr() const;

    /// See GetSpringDampingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringDampingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DISABLEMESHWELDING
    // --------------------------------------------------------------------- //
    /// Disable welding of the UsdGeomMesh vertices for cloth simulation.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxAutoParticleCloth:disableMeshWelding = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetDisableMeshWeldingAttr() const;

    /// See GetDisableMeshWeldingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDisableMeshWeldingAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxAutoParticleClothAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxAutoParticleClothAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxAutoParticleClothAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxAutoParticleClothAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxAutoParticleClothAPI::GetSpringStretchStiffnessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxAutoParticleClothSpringStretchStiffness));
}

inline UsdAttribute PhysxSchemaPhysxAutoParticleClothAPI::CreateSpringStretchStiffnessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxAutoParticleClothSpringStretchStiffness),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxAutoParticleClothAPI::GetSpringBendStiffnessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxAutoParticleClothSpringBendStiffness));
}

inline UsdAttribute PhysxSchemaPhysxAutoParticleClothAPI::CreateSpringBendStiffnessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxAutoParticleClothSpringBendStiffness),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxAutoParticleClothAPI::GetSpringShearStiffnessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxAutoParticleClothSpringShearStiffness));
}

inline UsdAttribute PhysxSchemaPhysxAutoParticleClothAPI::CreateSpringShearStiffnessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxAutoParticleClothSpringShearStiffness),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxAutoParticleClothAPI::GetSpringDampingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxAutoParticleClothSpringDamping));
}

inline UsdAttribute PhysxSchemaPhysxAutoParticleClothAPI::CreateSpringDampingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxAutoParticleClothSpringDamping),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxAutoParticleClothAPI::GetDisableMeshWeldingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxAutoParticleClothDisableMeshWelding));
}

inline UsdAttribute PhysxSchemaPhysxAutoParticleClothAPI::CreateDisableMeshWeldingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxAutoParticleClothDisableMeshWelding),
                                     SdfValueTypeNames->Bool,
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
