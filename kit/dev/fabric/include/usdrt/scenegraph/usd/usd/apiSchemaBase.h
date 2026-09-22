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

/// @file usd/apiSchemaBase.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"


// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
#include <usdrt/scenegraph/usd/usd/schemaRegistry.h>
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
// APISCHEMABASE                                                               //
// -------------------------------------------------------------------------- //

/// @class UsdAPISchemaBase
///
/// The base class for all \em API schemas.
///
/// An API schema provides an interface to a prim's qualities, but does not
/// specify a typeName for the underlying prim. The prim's qualities include
/// its inheritance structure, attributes, relationships etc. Since it cannot
/// provide a typeName, an API schema is considered to be non-concrete.
///
/// To auto-generate an API schema using usdGenSchema, simply leave the
/// typeName empty and make it inherit from "/APISchemaBase" or from another
/// API schema. See UsdModelAPI, UsdClipsAPI and UsdCollectionAPI for examples.
///
/// API schemas are classified into applied and non-applied API schemas.
/// The author of an API schema has to decide on the type of API schema
/// at the time of its creation by setting customData['apiSchemaType'] in the
/// schema definition (i.e. in  the associated primSpec inside the schema.usda
/// file).  UsdAPISchemaBase implements methods that are used to record the
/// application of an API schema on a USD prim.
///
/// If an API schema only provides an interface to set certain core bits of
/// metadata (like UsdModelAPI, which sets model kind and UsdClipsAPI, which
/// sets clips-related metadata) OR if the API schema can apply to any type of
/// prim or only to a known fixed set of prim types OR if there is no use of
/// recording the application of the API schema, in such cases, it would be
/// better to make it a non-applied API schema. Examples of non-applied API
/// schemas include UsdModelAPI, UsdClipsAPI, UsdShadeConnectableAPI and
/// UsdGeomPrimvarsAPI.
///
/// If there is a need to discover (or record) whether a prim contains or
/// subscribes to a given API schema, it would be advantageous to make the API
/// schema be "applied". In general, API schemas that add one or more properties
/// to a prim should be tagged as applied API schemas. A public Apply() method
/// is generated for applied API schemas by usdGenSchema. An applied API schema
/// must be applied to a prim via a call to the generated Apply() method, for
/// the schema object to evaluate to true when converted to a bool using the
/// explicit bool conversion operator. Examples of applied API schemas include
/// UsdCollectionAPI, UsdGeomModelAPI and UsdGeomMotionAPI
///
/// \anchor UsdAPISchemaBase_SingleVsMultipleApply
/// \name Single vs. Multiple Apply API Schemas
///
/// Applied API schemas can further be classified into single-apply and
/// multiple-apply API schemas. As the name suggests, a single-apply API schema
/// can only be applied once to a prim. A multiple-apply API schema can be
/// applied multiple times with different 'instanceName' values. An example of
/// a multiple-apply API schema is UsdCollectionAPI, where the API schema is
/// applied to a prim once for every collection owned by the prim.
///
/// \note An applied API schema can only inherit from another applied API
/// schema or directly from APISchemaBase. Similarly, a non-applied API schema
/// can only inherit from a non-applied API Schema or directly from
/// APISchemaBase. 'usdGenSchema' attempts to issue a warning if it detects
/// an incompatibility.
///
/// \note A multiple-apply API schema may not inherit from a single-apply API
/// schema and vice versa.
///
/// \note When the bool-conversion operator is invoked on an applied API
/// schema, it evaluates to true only if the application of the API schema has
/// been recorded on the prim via a call to the auto-generated Apply() method.
///
///

class UsdAPISchemaBase : public UsdSchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractBase;


    /// Construct a UsdAPISchemaBase on UsdPrim @p prim.
    /// Equivalent to UsdAPISchemaBase::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdAPISchemaBase(const UsdPrim& prim = UsdPrim()) : UsdSchemaBase(prim)
    {
    }

    /// Construct a UsdAPISchemaBase on the prim held by @p schemaObj .
    /// Should be preferred over UsdAPISchemaBase(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdAPISchemaBase(const UsdSchemaBase& schemaObj) : UsdSchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdAPISchemaBase() /* = 0 //PYBIND11 doesn't like this ...*/
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
protected:
    /// Construct a multiple-apply UsdAPISchemaBase on UsdPrim \p prim with
    /// the specified \p instanceName.
    explicit UsdAPISchemaBase(const UsdPrim& prim, const TfToken& instanceName)
        : UsdSchemaBase(prim), _instanceName(instanceName)
    {
    }

    /// Construct a multiple-apply UsdAPISchemaBase on the prim held by
    /// \p schemaObj with the given \p instanceName.
    explicit UsdAPISchemaBase(const UsdSchemaBase& schemaObj, const TfToken& instanceName)
        : UsdSchemaBase(schemaObj), _instanceName(instanceName)
    {
    }

    /// Returns the instance name of the API schema object belonging to a
    /// multiple-apply API schema.
    ///
    /// The returned instance name will be empty for non-applied and
    /// single-apply API schemas.
    const TfToken& _GetInstanceName() const
    {
        return _instanceName;
    }

    /// Check whether this APISchema object is valid for the currently held
    /// prim.
    ///
    /// If this is an applied API schema, this returns true if the held prim
    /// is valid and already has the API schema applied to it, along with the
    /// instanceName (in the case of multiple-apply). The instanceName should
    /// not be empty in the case of a multiple-apply API schema.
    ///
    /// This check is performed when clients invoke the explicit bool conversion
    /// operator, implemented in UsdSchemaBase.
    ///
    /// \sa UsdPrim::HasAPI()
    /* virtual */
    bool _IsCompatible() const;

private:
    // The instance name associated with this schema object, if it is a
    // multiple-apply API schema. For example, in the case of UsdCollectionAPI,
    // this will hold the name of the collection.
    TfToken _instanceName;
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdAPISchemaBase::_GetStaticTfType()
{
    const static TfToken token("UsdAPISchemaBase");
    return token;
}

/* virtual */
inline const TfToken UsdAPISchemaBase::_GetTfTypeToken() const
{
    const static TfToken token("UsdAPISchemaBase");
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

namespace usdrt
{
/* virtual */
inline bool UsdAPISchemaBase::_IsCompatible() const
{
    if (!UsdSchemaBase::_IsCompatible())
        return false;
    // Verify this is an applied API schema, and check if it's been properly applied to the prim.
    if (UsdSchemaRegistry::GetInstance().IsAppliedAPISchema(_GetType()))
    {
        if (UsdSchemaRegistry::GetInstance().IsMultipleApplyAPISchema(_GetType()))
        {
            if (_instanceName.IsEmpty() || !GetPrim().HasAPI(_GetType(), _instanceName))
            {
                return false;
            }
        }
        else
        {
            if (!GetPrim().HasAPI(_GetType()))
            {
                return false;
            }
        }
        return true;
    }

    return false;
}
} // namespace usdrt
