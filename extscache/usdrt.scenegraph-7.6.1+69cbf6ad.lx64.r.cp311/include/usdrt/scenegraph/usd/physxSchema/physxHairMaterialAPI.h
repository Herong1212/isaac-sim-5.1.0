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

/// @file physxSchema/physxHairMaterialAPI.h

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
// PHYSXHAIRMATERIALAPI                                                        //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxHairMaterialAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// Applied to USD Material. Defines material properties for hair simulation.

class PhysxSchemaPhysxHairMaterialAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxHairMaterialAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxHairMaterialAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxHairMaterialAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxHairMaterialAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxHairMaterialAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxHairMaterialAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxHairMaterialAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxHairMaterialAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxHairMaterialAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxHairMaterialAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxHairMaterialAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxHairMaterialAPI>())
        {
            return PhysxSchemaPhysxHairMaterialAPI(prim);
        }
        return PhysxSchemaPhysxHairMaterialAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DYNAMICFRICTION
    // --------------------------------------------------------------------- //
    /// Dynamic friction coefficient. Unitless.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHairMaterial:dynamicFriction = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDynamicFrictionAttr() const;

    /// See GetDynamicFrictionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDynamicFrictionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DENSITY
    // --------------------------------------------------------------------- //
    /// If non-zero, defines the density of the material. This can be
    /// used for body mass computation, see PhysicsMassAPI.
    /// Note that if the density is 0.0 it is ignored.
    /// Units: mass/distance/distance/distance.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHairMaterial:density = 0` |
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
    // YOUNGSMODULUS
    // --------------------------------------------------------------------- //
    /// Young's modulus, i.e. the tensile stiffness of the material.
    /// A negative value means the simulation will pick a default.
    /// Range: [0, inf)
    /// Units: mass/(distance*seconds*seconds).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHairMaterial:youngsModulus = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetYoungsModulusAttr() const;

    /// See GetYoungsModulusAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateYoungsModulusAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CURVETHICKNESS
    // --------------------------------------------------------------------- //
    /// Diameter along curve.
    /// A negative value means the simulation will pick a default.
    /// Range: [0, inf)
    /// Units: distance.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHairMaterial:curveThickness = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCurveThicknessAttr() const;

    /// See GetCurveThicknessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCurveThicknessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CURVEBENDSTIFFNESS
    // --------------------------------------------------------------------- //
    /// Optional override for bending stiffness; by default derived from youngsModulus and curveThickness.
    /// Override is active if the value is non-negative.
    /// Range: [0, inf)
    /// Units: mass/(distance*seconds*seconds).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHairMaterial:curveBendStiffness = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCurveBendStiffnessAttr() const;

    /// See GetCurveBendStiffnessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCurveBendStiffnessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CONTACTOFFSETMULTIPLIER
    // --------------------------------------------------------------------- //
    /// Distance at which collisions are generated as a multiple of curveThickness.
    /// This attribute has no effect if contactOffset is non-negative.
    /// Range: [0.0, inf)
    /// Units: dimensionless
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHairMaterial:contactOffsetMultiplier = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetContactOffsetMultiplierAttr() const;

    /// See GetContactOffsetMultiplierAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateContactOffsetMultiplierAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CONTACTOFFSET
    // --------------------------------------------------------------------- //
    /// Distance at which collisions are generated.
    /// Overrides the contactOffsetMultiplier attribute if set to a non-negative value.
    /// Range: [0.0, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxHairMaterial:contactOffset = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetContactOffsetAttr() const;

    /// See GetContactOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateContactOffsetAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxHairMaterialAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxHairMaterialAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxHairMaterialAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxHairMaterialAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::GetDynamicFrictionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialDynamicFriction));
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::CreateDynamicFrictionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialDynamicFriction),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::GetDensityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialDensity));
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::CreateDensityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialDensity), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::GetYoungsModulusAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialYoungsModulus));
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::CreateYoungsModulusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialYoungsModulus), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::GetCurveThicknessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialCurveThickness));
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::CreateCurveThicknessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialCurveThickness),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::GetCurveBendStiffnessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialCurveBendStiffness));
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::CreateCurveBendStiffnessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialCurveBendStiffness),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::GetContactOffsetMultiplierAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialContactOffsetMultiplier));
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::CreateContactOffsetMultiplierAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialContactOffsetMultiplier),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::GetContactOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialContactOffset));
}

inline UsdAttribute PhysxSchemaPhysxHairMaterialAPI::CreateContactOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxHairMaterialContactOffset), SdfValueTypeNames->Float,
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
