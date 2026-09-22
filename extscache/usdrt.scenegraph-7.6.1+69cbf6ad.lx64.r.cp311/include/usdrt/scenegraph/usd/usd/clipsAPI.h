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

/// @file usd/clipsAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usd/tokens.h"


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
// CLIPSAPI                                                                    //
// -------------------------------------------------------------------------- //

/// @class UsdClipsAPI
///
/// UsdClipsAPI is an API schema that provides an interface to
/// a prim's clip metadata. Clips are a "value resolution" feature that
/// allows one to specify a sequence of usd files (clips) to be consulted,
/// over time, as a source of varying overrides for the prims at and
/// beneath this prim in namespace.
///
/// SetClipAssetPaths() establishes the set of clips that can be consulted.
/// SetClipActive() specifies the ordering of clip application over time
/// (clips can be repeated), while SetClipTimes() specifies time-mapping
/// from stage-time to clip-time for the clip active at a given stage-time,
/// which allows for time-dilation and repetition of clips.
/// Finally, SetClipPrimPath() determines the path within each clip that will
/// map to this prim, i.e. the location within the clip at which we will look
/// for opinions for this prim.
///
/// The clip asset paths, times and active metadata can also be specified
/// through template clip metadata. This can be desirable when your set of
/// assets is very large, as the template metadata is much more concise.
/// SetClipTemplateAssetPath() establishes the asset identifier pattern of the
/// set of clips to be consulted. SetClipTemplateStride(),
/// SetClipTemplateEndTime(), and SetClipTemplateStartTime() specify the range
/// in which USD will search, based on the template. From the set of resolved
/// asset paths, times and active will be derived internally.
///
/// A prim may have multiple "clip sets" -- named sets of clips that each
/// have their own values for the metadata described above. For example,
/// a prim might have a clip set named "Clips_1" that specifies some group
/// of clip asset paths, and another clip set named "Clips_2" that uses
/// an entirely different set of clip asset paths. These clip sets are
/// composed across composition arcs, so clip sets for a prim may be
/// defined in multiple sublayers or references, for example. Individual
/// metadata for a given clip set may be sparsely overridden.
///
/// Important facts about clips:
/// \li Within the layerstack in which clips are established, the
/// opinions within the clips will be \em weaker than any local opinions
/// in the layerstack, but em stronger than varying opinions coming across
/// references and variants.
/// \li We will never look for metadata or default opinions in clips
/// when performing value resolution on the owning stage, since these
/// quantities must be time-invariant.
///
/// This leads to the common structure in which we reference a model asset
/// on a prim, and then author clips at the same site: the asset reference
/// will provide the topology and unvarying data for the model, while the
/// clips will provide the time-sampled animation.
///
/// For further information, see \ref Usd_Page_ValueClips
///

class UsdClipsAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::NonAppliedAPI;


    /// Construct a UsdClipsAPI on UsdPrim @p prim.
    /// Equivalent to UsdClipsAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdClipsAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdClipsAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdClipsAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdClipsAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdClipsAPI()
    {
    }

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

inline const TfToken UsdClipsAPI::_GetStaticTfType()
{
    const static TfToken token("UsdClipsAPI");
    return token;
}

/* virtual */
inline const TfToken UsdClipsAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdClipsAPI");
    return token;
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
