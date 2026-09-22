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

/// @file usdLux/lightListAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdLux/tokens.h"


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
// LIGHTLISTAPI                                                                //
// -------------------------------------------------------------------------- //

/// @class UsdLuxLightListAPI
///
/// API schema to support discovery and publishing of lights in a scene.
///
/// \section UsdLuxLightListAPI_Discovery Discovering Lights via Traversal
///
/// To motivate this API, consider what is required to discover all
/// lights in a scene.  We must load all payloads and traverse all prims:
///
/// \code
/// 01  // Load everything on the stage so we can find all lights,
/// 02  // including those inside payloads
/// 03  stage->Load();
/// 04
/// 05  // Traverse all prims, checking if they have an applied UsdLuxLightAPI
/// 06  // (Note: ignoring instancing and a few other things for simplicity)
/// 07  SdfPathVector lights;
/// 08  for (UsdPrim prim: stage->Traverse()) {
/// 09      if (prim.HasAPI<UsdLuxLightAPI>()) {
/// 10          lights.push_back(i->GetPath());
/// 11      }
/// 12  }
/// \endcode
///
/// This traversal -- suitably elaborated to handle certain details --
/// is the first and simplest thing UsdLuxLightListAPI provides.
/// UsdLuxLightListAPI::ComputeLightList() performs this traversal and returns
/// all lights in the scene:
///
/// \code
/// 01  UsdLuxLightListAPI listAPI(stage->GetPseudoRoot());
/// 02  SdfPathVector lights = listAPI.ComputeLightList();
/// \endcode
///
/// \section UsdLuxLightListAPI_LightList Publishing a Cached Light List
///
/// Consider a USD client that needs to quickly discover lights but
/// wants to defer loading payloads and traversing the entire scene
/// where possible, and is willing to do up-front computation and
/// caching to achieve that.
///
/// UsdLuxLightListAPI provides a way to cache the computed light list,
/// by publishing the list of lights onto prims in the model
/// hierarchy.  Consider a big set that contains lights:
///
/// \code
/// 01  def Xform "BigSetWithLights" (
/// 02      kind = "assembly"
/// 03      payload = @BigSetWithLights.usd@   // Heavy payload
/// 04  ) {
/// 05      // Pre-computed, cached list of lights inside payload
/// 06      rel lightList = [
/// 07          <./Lights/light_1>,
/// 08          <./Lights/light_2>,
/// 09          ...
/// 10      ]
/// 11      token lightList:cacheBehavior = "consumeAndContinue";
/// 12  }
/// \endcode
///
/// The lightList relationship encodes a set of lights, and the
/// lightList:cacheBehavior property provides fine-grained
/// control over how to use that cache.  (See details below.)
///
/// The cache can be created by first invoking
/// ComputeLightList(ComputeModeIgnoreCache) to pre-compute the list
/// and then storing the result with UsdLuxLightListAPI::StoreLightList().
///
/// To enable efficient retrieval of the cache, it should be stored
/// on a model hierarchy prim.  Furthermore, note that while you can
/// use a UsdLuxLightListAPI bound to the pseudo-root prim to query the
/// lights (as in the example above) because it will perform a
/// traversal over descendants, you cannot store the cache back to the
/// pseduo-root prim.
///
/// To consult the cached list, we invoke
/// ComputeLightList(ComputeModeConsultModelHierarchyCache):
///
/// \code
/// 01  // Find and load all lights, using lightList cache where available
/// 02  UsdLuxLightListAPI list(stage->GetPseudoRoot());
/// 03  SdfPathSet lights = list.ComputeLightList(
/// 04      UsdLuxLightListAPI::ComputeModeConsultModelHierarchyCache);
/// 05  stage.LoadAndUnload(lights, SdfPathSet());
/// \endcode
///
/// In this mode, ComputeLightList() will traverse the model
/// hierarchy, accumulating cached light lists.
///
/// \section UsdLuxLightListAPI_CacheBehavior Controlling Cache Behavior
///
/// The lightList:cacheBehavior property gives additional fine-grained
/// control over cache behavior:
///
/// \li The fallback value, "ignore", indicates that the lightList should
/// be disregarded.  This provides a way to invalidate cache entries.
/// Note that unless "ignore" is specified, a lightList with an empty
/// list of targets is considered a cache indicating that no lights
/// are present.
///
/// \li The value "consumeAndContinue" indicates that the cache should
/// be consulted to contribute lights to the scene, and that recursion
/// should continue down the model hierarchy in case additional lights
/// are added as descedants. This is the default value established when
/// StoreLightList() is invoked. This behavior allows the lights within
/// a large model, such as the BigSetWithLights example above, to be
/// published outside the payload, while also allowing referencing and
/// layering to add additional lights over that set.
///
/// \li The value "consumeAndHalt" provides a way to terminate recursive
/// traversal of the scene for light discovery. The cache will be
/// consulted but no descendant prims will be examined.
///
/// \section UsdLuxLightListAPI_Instancing Instancing
///
/// Where instances are present, UsdLuxLightListAPI::ComputeLightList() will
/// return the instance-unique paths to any lights discovered within
/// those instances.  Lights within a UsdGeomPointInstancer will
/// not be returned, however, since they cannot be referred to
/// solely via paths.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdLuxTokens.
/// So to set an attribute to the value "rightHanded", use UsdLuxTokens->rightHanded
/// as the value.

class UsdLuxLightListAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdLuxLightListAPI on UsdPrim @p prim.
    /// Equivalent to UsdLuxLightListAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxLightListAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdLuxLightListAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxLightListAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxLightListAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxLightListAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "LightListAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdLuxLightListAPI object is returned upon success.
    /// An invalid (or empty) UsdLuxLightListAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdLuxLightListAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdLuxLightListAPI>())
        {
            return UsdLuxLightListAPI(prim);
        }
        return UsdLuxLightListAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // LIGHTLISTCACHEBEHAVIOR
    // --------------------------------------------------------------------- //
    /// Controls how the lightList should be interpreted.
    /// Valid values are:
    /// - consumeAndHalt: The lightList should be consulted,
    /// and if it exists, treated as a final authoritative statement
    /// of any lights that exist at or below this prim, halting
    /// recursive discovery of lights.
    /// - consumeAndContinue: The lightList should be consulted,
    /// but recursive traversal over nameChildren should continue
    /// in case additional lights are added by descendants.
    /// - ignore: The lightList should be entirely ignored.  This
    /// provides a simple way to temporarily invalidate an existing
    /// cache.  This is the fallback behavior.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token lightList:cacheBehavior` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref UsdLuxTokens "Allowed Values" | consumeAndHalt, consumeAndContinue, ignore |

    UsdAttribute GetLightListCacheBehaviorAttr() const;

    /// See GetLightListCacheBehaviorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLightListCacheBehaviorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LIGHTLIST
    // --------------------------------------------------------------------- //
    /// Relationship to lights in the scene.
    ///
    UsdRelationship GetLightListRel() const;

    /// See GetLightListRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateLightListRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdLuxLightListAPI::_GetStaticTfType()
{
    const static TfToken token("UsdLuxLightListAPI");
    return token;
}

/* virtual */
inline const TfToken UsdLuxLightListAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxLightListAPI");
    return token;
}


inline UsdAttribute UsdLuxLightListAPI::GetLightListCacheBehaviorAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->lightListCacheBehavior));
}

inline UsdAttribute UsdLuxLightListAPI::CreateLightListCacheBehaviorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->lightListCacheBehavior), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}


inline UsdRelationship UsdLuxLightListAPI::GetLightListRel() const
{
    return GetPrim().GetRelationship(UsdLuxTokens->lightList);
}

inline UsdRelationship UsdLuxLightListAPI::CreateLightListRel() const
{
    return GetPrim().CreateRelationship(UsdLuxTokens->lightList,
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
