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

/// @file usdVol/volume.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/gprim.h"


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
// VOLUME                                                                      //
// -------------------------------------------------------------------------- //

/// @class UsdVolVolume
///
/// A renderable volume primitive. A volume is made up of any number
/// of FieldBase primitives bound together in this volume. Each
/// FieldBase primitive is specified as a relationship with a
/// namespace prefix of "field".
///
/// The relationship name is used by the renderer to associate
/// individual fields with the named input parameters on the volume
/// shader. Using this indirect approach to connecting fields to
/// shader parameters (rather than using the field prim's name)
/// allows a single field to be reused for different shader inputs, or
/// to be used as different shader parameters when rendering different
/// Volumes. This means that the name of the field prim is not
/// relevant to its contribution to the volume prims which refer to
/// it. Nor does the field prim's location in the scene graph have
/// any relevance, and Volumes may refer to fields anywhere in the
/// scene graph.  **However**, unless Field prims need to be shared
/// by multiple Volumes, a Volume's Field prims should be located
/// under the Volume in namespace, for enhanced organization.

class UsdVolVolume : public UsdGeomGprim
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdVolVolume on UsdPrim @p prim.
    /// Equivalent to UsdVolVolume::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdVolVolume(const UsdPrim& prim = UsdPrim()) : UsdGeomGprim(prim)
    {
    }

    /// Construct a UsdVolVolume on the prim held by @p schemaObj .
    /// Should be preferred over UsdVolVolume(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdVolVolume(const UsdSchemaBase& schemaObj) : UsdGeomGprim(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdVolVolume()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdVolVolume Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdVolVolume::_GetStaticTfType()
{
    const static TfToken token("UsdVolVolume");
    return token;
}

/* virtual */
inline const TfToken UsdVolVolume::_GetTfTypeToken() const
{
    const static TfToken token("UsdVolVolume");
    return token;
}

/* static */
inline UsdVolVolume UsdVolVolume::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdVolVolume();
    }
    return UsdVolVolume(stage->DefinePrim(path, _GetStaticTfType()));
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
