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

/// @file physxSchema/tetrahedralMesh.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/pointBased.h"
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
// TETRAHEDRALMESH                                                             //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaTetrahedralMesh
///
/// Describes a tetrahedral mesh in 3D space.

class PhysxSchemaTetrahedralMesh : public UsdGeomPointBased
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a PhysxSchemaTetrahedralMesh on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaTetrahedralMesh::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaTetrahedralMesh(const UsdPrim& prim = UsdPrim()) : UsdGeomPointBased(prim)
    {
    }

    /// Construct a PhysxSchemaTetrahedralMesh on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaTetrahedralMesh(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaTetrahedralMesh(const UsdSchemaBase& schemaObj) : UsdGeomPointBased(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaTetrahedralMesh()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static PhysxSchemaTetrahedralMesh Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // INDICES
    // --------------------------------------------------------------------- //
    /// Flat list of the index (into the 'points' attribute) of each vertex of each tetrahedron in the mesh.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] indices` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetIndicesAttr() const;

    /// See GetIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateIndicesAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaTetrahedralMesh::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaTetrahedralMesh");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaTetrahedralMesh::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaTetrahedralMesh");
    return token;
}

/* static */
inline PhysxSchemaTetrahedralMesh PhysxSchemaTetrahedralMesh::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return PhysxSchemaTetrahedralMesh();
    }
    return PhysxSchemaTetrahedralMesh(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute PhysxSchemaTetrahedralMesh::GetIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->indices));
}

inline UsdAttribute PhysxSchemaTetrahedralMesh::CreateIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->indices), SdfValueTypeNames->IntArray,
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
