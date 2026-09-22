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

/// @file physxSchema/physxVehicleTireFrictionTable.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"
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
// PHYSXVEHICLETIREFRICTIONTABLE                                               //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleTireFrictionTable
///
/// Table defining the friction values of a tire against a given set of ground materials.

class PhysxSchemaPhysxVehicleTireFrictionTable : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a PhysxSchemaPhysxVehicleTireFrictionTable on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleTireFrictionTable::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleTireFrictionTable(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleTireFrictionTable on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleTireFrictionTable(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleTireFrictionTable(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleTireFrictionTable()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static PhysxSchemaPhysxVehicleTireFrictionTable Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FRICTIONVALUES
    // --------------------------------------------------------------------- //
    /// The friction values to use for the tire against the ground materials listed under groundMaterials. The array
    /// needs to have the same size as the list of materials specified in groundMaterials.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] frictionValues` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetFrictionValuesAttr() const;

    /// See GetFrictionValuesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFrictionValuesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DEFAULTFRICTIONVALUE
    // --------------------------------------------------------------------- //
    /// The friction value to use for the tire against the ground if the material of the ground surface is not among the
    /// materials listed in groundMaterials. The value has to be greater or equal 0.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float defaultFrictionValue = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDefaultFrictionValueAttr() const;

    /// See GetDefaultFrictionValueAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDefaultFrictionValueAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GROUNDMATERIALS
    // --------------------------------------------------------------------- //
    /// Relationships to Material instances that have PhysicsMaterialAPI applied. For each material, a friction value
    /// has to be specified in the frictionValues attribute. If a material is encountered that has not been listed, the
    /// value declared in defaultFrictionValue will be used.
    ///
    UsdRelationship GetGroundMaterialsRel() const;

    /// See GetGroundMaterialsRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateGroundMaterialsRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleTireFrictionTable::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleTireFrictionTable");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleTireFrictionTable::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleTireFrictionTable");
    return token;
}

/* static */
inline PhysxSchemaPhysxVehicleTireFrictionTable PhysxSchemaPhysxVehicleTireFrictionTable::Define(const UsdStageRefPtr& stage,
                                                                                                 const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return PhysxSchemaPhysxVehicleTireFrictionTable();
    }
    return PhysxSchemaPhysxVehicleTireFrictionTable(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute PhysxSchemaPhysxVehicleTireFrictionTable::GetFrictionValuesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->frictionValues));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireFrictionTable::CreateFrictionValuesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->frictionValues), SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireFrictionTable::GetDefaultFrictionValueAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->defaultFrictionValue));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireFrictionTable::CreateDefaultFrictionValueAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->defaultFrictionValue), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxVehicleTireFrictionTable::GetGroundMaterialsRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->groundMaterials);
}

inline UsdRelationship PhysxSchemaPhysxVehicleTireFrictionTable::CreateGroundMaterialsRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->groundMaterials,
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
