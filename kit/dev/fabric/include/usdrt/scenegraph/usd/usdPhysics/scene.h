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

/// @file usdPhysics/scene.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"
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
// PHYSICSSCENE                                                                //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsScene
///
/// General physics simulation properties, required for simulation.

class UsdPhysicsScene : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdPhysicsScene on UsdPrim @p prim.
    /// Equivalent to UsdPhysicsScene::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsScene(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a UsdPhysicsScene on the prim held by @p schemaObj .
    /// Should be preferred over UsdPhysicsScene(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdPhysicsScene(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsScene()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdPhysicsScene Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // GRAVITYDIRECTION
    // --------------------------------------------------------------------- //
    /// Gravity direction vector in simulation world space. Will be
    /// normalized before use. A zero vector is a request to use the negative
    /// upAxis. Unitless.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physics:gravityDirection = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetGravityDirectionAttr() const;

    /// See GetGravityDirectionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGravityDirectionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GRAVITYMAGNITUDE
    // --------------------------------------------------------------------- //
    /// Gravity acceleration magnitude in simulation world space.
    /// A negative value is a request to use a value equivalent to earth
    /// gravity regardless of the metersPerUnit scaling used by this scene.
    /// Units: distance/second/second.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:gravityMagnitude = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetGravityMagnitudeAttr() const;

    /// See GetGravityMagnitudeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGravityMagnitudeAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsScene::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsScene");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsScene::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsScene");
    return token;
}

/* static */
inline UsdPhysicsScene UsdPhysicsScene::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdPhysicsScene();
    }
    return UsdPhysicsScene(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdPhysicsScene::GetGravityDirectionAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsGravityDirection));
}

inline UsdAttribute UsdPhysicsScene::CreateGravityDirectionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsGravityDirection), SdfValueTypeNames->Vector3f,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsScene::GetGravityMagnitudeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsGravityMagnitude));
}

inline UsdAttribute UsdPhysicsScene::CreateGravityMagnitudeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsGravityMagnitude), SdfValueTypeNames->Float,
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
