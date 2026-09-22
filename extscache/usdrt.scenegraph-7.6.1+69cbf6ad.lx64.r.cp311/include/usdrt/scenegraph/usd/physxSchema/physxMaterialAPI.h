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

/// @file physxSchema/physxMaterialAPI.h

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
// PHYSXMATERIALAPI                                                            //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxMaterialAPI
///
/// PhysX material extended parameters
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref PhysxSchemaTokens.
/// So to set an attribute to the value "rightHanded", use PhysxSchemaTokens->rightHanded
/// as the value.

class PhysxSchemaPhysxMaterialAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxMaterialAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxMaterialAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxMaterialAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxMaterialAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxMaterialAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxMaterialAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxMaterialAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxMaterialAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxMaterialAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxMaterialAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxMaterialAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxMaterialAPI>())
        {
            return PhysxSchemaPhysxMaterialAPI(prim);
        }
        return PhysxSchemaPhysxMaterialAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FRICTIONCOMBINEMODE
    // --------------------------------------------------------------------- //
    /// Determines the way in which two material properties will be combined to yield a friction or restitution
    /// coefficient for a collision.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxMaterial:frictionCombineMode = "average"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | average, min, multiply, max |

    UsdAttribute GetFrictionCombineModeAttr() const;

    /// See GetFrictionCombineModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFrictionCombineModeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RESTITUTIONCOMBINEMODE
    // --------------------------------------------------------------------- //
    /// Determines the way in which two material properties will be combined to yield a friction or restitution
    /// coefficient for a collision.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxMaterial:restitutionCombineMode = "average"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | average, min, multiply, max |

    UsdAttribute GetRestitutionCombineModeAttr() const;

    /// See GetRestitutionCombineModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRestitutionCombineModeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // IMPROVEPATCHFRICTION
    // --------------------------------------------------------------------- //
    /// Flag only has an effect if physxScene:frictionType "patch" friction model is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxMaterial:improvePatchFriction = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetImprovePatchFrictionAttr() const;

    /// See GetImprovePatchFrictionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateImprovePatchFrictionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COMPLIANTCONTACTSTIFFNESS
    // --------------------------------------------------------------------- //
    /// Spring stiffness for a compliant contact model using implicit springs. A higher stiffness results in behavior
    /// closer to a rigid contact. The compliant contact model is only enabled if the stiffness is larger than 0.
    /// Range: [0, inf)
    /// Units: force/distance = mass / seconds / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxMaterial:compliantContactStiffness = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCompliantContactStiffnessAttr() const;

    /// See GetCompliantContactStiffnessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCompliantContactStiffnessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COMPLIANTCONTACTDAMPING
    // --------------------------------------------------------------------- //
    /// Damping coefficient for a compliant contact model using implicit springs. Irrelevant if compliant contacts
    /// are disabled when compliantContactStiffness is set to zero and rigid contacts are active.
    /// Range: [0, inf)
    /// Units: force / (distance / seconds) = mass / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxMaterial:compliantContactDamping = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCompliantContactDampingAttr() const;

    /// See GetCompliantContactDampingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCompliantContactDampingAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxMaterialAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxMaterialAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxMaterialAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxMaterialAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxMaterialAPI::GetFrictionCombineModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxMaterialFrictionCombineMode));
}

inline UsdAttribute PhysxSchemaPhysxMaterialAPI::CreateFrictionCombineModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxMaterialFrictionCombineMode),
                                     SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxMaterialAPI::GetRestitutionCombineModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxMaterialRestitutionCombineMode));
}

inline UsdAttribute PhysxSchemaPhysxMaterialAPI::CreateRestitutionCombineModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxMaterialRestitutionCombineMode),
                                     SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxMaterialAPI::GetImprovePatchFrictionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxMaterialImprovePatchFriction));
}

inline UsdAttribute PhysxSchemaPhysxMaterialAPI::CreateImprovePatchFrictionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxMaterialImprovePatchFriction),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxMaterialAPI::GetCompliantContactStiffnessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxMaterialCompliantContactStiffness));
}

inline UsdAttribute PhysxSchemaPhysxMaterialAPI::CreateCompliantContactStiffnessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxMaterialCompliantContactStiffness),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxMaterialAPI::GetCompliantContactDampingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxMaterialCompliantContactDamping));
}

inline UsdAttribute PhysxSchemaPhysxMaterialAPI::CreateCompliantContactDampingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxMaterialCompliantContactDamping),
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
