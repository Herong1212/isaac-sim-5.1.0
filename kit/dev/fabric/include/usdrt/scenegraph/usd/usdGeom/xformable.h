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

/// @file usdGeom/xformable.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/imageable.h"
#include "usdrt/scenegraph/usd/usdGeom/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usdGeom/xformOp.h" 
#include <vector> */
// clang-format on

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
// XFORMABLE                                                                   //
// -------------------------------------------------------------------------- //

/// @class UsdGeomXformable
///
/// Base class for all transformable prims, which allows arbitrary
/// sequences of component affine transformations to be encoded.
///
/// \note
/// You may find it useful to review \ref UsdGeom_LinAlgBasics while reading
/// this class description.
///
/// <b>Supported Component Transformation Operations</b>
///
/// UsdGeomXformable currently supports arbitrary sequences of the following
/// operations, each of which can be encoded in an attribute of the proper
/// shape in any supported precision:
/// \li translate - 3D
/// \li scale     - 3D
/// \li rotateX   - 1D angle in degrees
/// \li rotateY   - 1D angle in degrees
/// \li rotateZ   - 1D angle in degrees
/// \li rotateABC - 3D where ABC can be any combination of the six principle
/// Euler Angle sets: XYZ, XZY, YXZ, YZX, ZXY, ZYX.  See
/// \ref usdGeom_rotationPackingOrder "note on rotation packing order"
/// \li orient    - 4D (quaternion)
/// \li transform - 4x4D
///
/// <b>Creating a Component Transformation</b>
///
/// To add components to a UsdGeomXformable prim, simply call AddXformOp()
/// with the desired op type, as enumerated in \ref UsdGeomXformOp::Type,
/// and the desired precision, which is one of \ref UsdGeomXformOp::Precision.
/// Optionally, you can also provide an "op suffix" for the operator that
/// disambiguates it from other components of the same type on the same prim.
/// Application-specific transform schemas can use the suffixes to fill a role
/// similar to that played by AbcGeom::XformOp's "Hint" enums for their own
/// round-tripping logic.
///
/// We also provide specific "Add" API for each type, for clarity and
/// conciseness, e.g. AddTranslateOp(), AddRotateXYZOp() etc.
///
/// AddXformOp() will return a UsdGeomXformOp object, which is a schema on a
/// newly created UsdAttribute that provides convenience API for authoring
/// and computing the component transformations.  The UsdGeomXformOp can then
/// be used to author any number of timesamples and default for the op.
///
/// Each successive call to AddXformOp() adds an operator that will be applied
/// "more locally" than the preceding operator, just as if we were pushing
/// transforms onto a transformation stack - which is precisely what should
/// happen when the operators are consumed by a reader.
///
/// \note
/// If you can, please try to use the UsdGeomXformCommonAPI, which wraps
/// the UsdGeomXformable with an interface in which Op creation is taken
/// care of for you, and there is a much higher chance that the data you
/// author will be importable without flattening into other DCC's, as it
/// conforms to a fixed set of Scale-Rotate-Translate Ops.
///
/// \sa \ref usdGeom_xformableExamples "Using the Authoring API"
///
/// <b>Data Encoding and Op Ordering</b>
///
/// Because there is no "fixed schema" of operations, all of the attributes
/// that encode transform operations are dynamic, and are scoped in
/// the namespace "xformOp". The second component of an attribute's name provides
/// the \em type of operation, as listed above.  An "xformOp" attribute can
/// have additional namespace components derived from the \em opSuffix argument
/// to the AddXformOp() suite of methods, which provides a preferred way of
/// naming the ops such that we can have multiple "translate" ops with unique
/// attribute names. For example, in the attribute named
/// "xformOp:translate:maya:pivot", "translate" is the type of operation and
/// "maya:pivot" is the suffix.
///
/// The following ordered list of attribute declarations in usda
/// define a basic Scale-Rotate-Translate with XYZ Euler angles, wherein the
/// translation is double-precision, and the remainder of the ops are single,
/// in which we will:
///
/// <ol>
/// <li> Scale by 2.0 in each dimension
/// <li> Rotate about the X, Y, and Z axes by 30, 60, and 90 degrees, respectively
/// <li> Translate by 100 units in the Y direction
/// </ol>
///
/// \code
/// float3 xformOp:rotateXYZ = (30, 60, 90)
/// float3 xformOp:scale = (2, 2, 2)
/// double3 xformOp:translate = (0, 100, 0)
/// uniform token[] xformOpOrder = [ "xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale" ]
/// \endcode
///
/// The attributes appear in the dictionary order in which USD, by default,
/// sorts them.  To ensure the ops are recovered and evaluated in the correct
/// order, the schema introduces the **xformOpOrder** attribute, which
/// contains the names of the op attributes, in the precise sequence in which
/// they should be pushed onto a transform stack. **Note** that the order is
/// opposite to what you might expect, given the matrix algebra described in
/// \ref UsdGeom_LinAlgBasics.  This also dictates order of op creation,
/// since each call to AddXformOp() adds a new op to the end of the
/// \b xformOpOrder array, as a new "most-local" operation.  See
/// \ref usdGeom_xformableExamples "Example 2 below" for C++ code that could
/// have produced this USD.
///
/// If it were important for the prim's rotations to be independently
/// overridable, we could equivalently (at some performance cost) encode
/// the transformation also like so:
/// \code
/// float xformOp:rotateX = 30
/// float xformOp:rotateY = 60
/// float xformOp:rotateZ = 90
/// float3 xformOp:scale = (2, 2, 2)
/// double3 xformOp:translate = (0, 100, 0)
/// uniform token[] xformOpOrder = [ "xformOp:translate", "xformOp:rotateZ", "xformOp:rotateY", "xformOp:rotateX",
/// "xformOp:scale" ] \endcode
///
/// Again, note that although we are encoding an XYZ rotation, the three
/// rotations appear in the **xformOpOrder** in the opposite order, with Z,
/// followed, by Y, followed by X.
///
/// Were we to add a Maya-style scalePivot to the above example, it might
/// look like the following:
/// \code
/// float3 xformOp:rotateXYZ = (30, 60, 90)
/// float3 xformOp:scale = (2, 2, 2)
/// double3 xformOp:translate = (0, 100, 0)
/// double3 xformOp:translate:scalePivot
/// uniform token[] xformOpOrder = [ "xformOp:translate", "xformOp:rotateXYZ", "xformOp:translate:scalePivot",
/// "xformOp:scale" ] \endcode
///
/// <b>Paired "Inverted" Ops</b>
///
/// We have been claiming that the ordered list of ops serves as a set
/// of instructions to a transform stack, but you may have noticed in the last
/// example that there is a missing operation - the pivot for the scale op
/// needs to be applied in its inverse-form as a final (most local) op!  In the
/// AbcGeom::Xform schema, we would have encoded an actual "final" translation
/// op whose value was authored by the exporter as the negation of the pivot's
/// value.  However, doing so would be brittle in USD, given that each op can
/// be independently overridden, and the constraint that one attribute must be
/// maintained as the negation of the other in order for successful
/// re-importation of the schema cannot be expressed in USD.
///
/// Our solution leverages the **xformOpOrder** member of the schema, which,
/// in addition to ordering the ops, may also contain one of two special
/// tokens that address the paired op and "stack resetting" behavior.
///
/// The "paired op" behavior is encoded as an "!invert!" prefix in
/// \b xformOpOrder, as the result of an AddXformOp(isInverseOp=True) call.
/// The \b xformOpOrder for the last example would look like:
/// \code
/// uniform token[] xformOpOrder = [ "xformOp:translate", "xformOp:rotateXYZ", "xformOp:translate:scalePivot",
/// "xformOp:scale", "!invert!xformOp:translate:scalePivot" ] \endcode
///
/// When asked for its value via UsdGeomXformOp::GetOpTransform(), an
/// "inverted" Op (i.e. the "inverted" half of a set of paired Ops) will fetch
/// the value of its paired attribute and return its negation.  This works for
/// all op types - an error will be issued if a "transform" type op is singular
/// and cannot be inverted. When getting the authored value of an inverted op
/// via UsdGeomXformOp::Get(), the raw, uninverted value of the associated
/// attribute is returned.
///
/// For the sake of robustness, <b>setting a value on an inverted op is disallowed.</b>
/// Attempting to set a value on an inverted op will result in a coding error
/// and no value being set.
///
/// <b>Resetting the Transform Stack</b>
///
/// The other special op/token that can appear in \em xformOpOrder is
/// \em "!resetXformStack!", which, appearing as the first element of
/// \em xformOpOrder, indicates this prim should not inherit the transformation
/// of its namespace parent.  See SetResetXformStack()
///
/// <b>Expected Behavior for "Missing" Ops</b>
///
/// If an importer expects Scale-Rotate-Translate operations, but a prim
/// has only translate and rotate ops authored, the importer should assume
/// an identity scale.  This allows us to optimize the data a bit, if only
/// a few components of a very rich schema (like Maya's) are authored in the
/// app.
///
/// \anchor usdGeom_xformableExamples
/// <b>Using the C++ API</b>
///
/// #1. Creating a simple transform matrix encoding
/// \snippet examples.cpp CreateMatrixWithDefault
///
/// #2. Creating the simple SRT from the example above
/// \snippet examples.cpp CreateExampleSRT
///
/// #3. Creating a parameterized SRT with pivot using UsdGeomXformCommonAPI
/// \snippet examples.cpp CreateSRTWithDefaults
///
/// #4. Creating a rotate-only pivot transform with animated
/// rotation and translation
/// \snippet examples.cpp CreateAnimatedTransform
///
///

class UsdGeomXformable : public UsdGeomImageable
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractTyped;


    /// Construct a UsdGeomXformable on UsdPrim @p prim.
    /// Equivalent to UsdGeomXformable::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomXformable(const UsdPrim& prim = UsdPrim()) : UsdGeomImageable(prim)
    {
    }

    /// Construct a UsdGeomXformable on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomXformable(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomXformable(const UsdSchemaBase& schemaObj) : UsdGeomImageable(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomXformable()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // XFORMOPORDER
    // --------------------------------------------------------------------- //
    /// Encodes the sequence of transformation operations in the
    /// order in which they should be pushed onto a transform stack while
    /// visiting a UsdStage's prims in a graph traversal that will effect
    /// the desired positioning for this prim and its descendant prims.
    ///
    /// You should rarely, if ever, need to manipulate this attribute directly.
    /// It is managed by the AddXformOp(), SetResetXformStack(), and
    /// SetXformOpOrder(), and consulted by GetOrderedXformOps() and
    /// GetLocalTransformation().
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token[] xformOpOrder` |
    /// | C++ Type | VtArray<TfToken> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TokenArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetXformOpOrderAttr() const;

    /// See GetXformOpOrderAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateXformOpOrderAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomXformable::_GetStaticTfType()
{
    const static TfToken token("UsdGeomXformable");
    return token;
}

/* virtual */
inline const TfToken UsdGeomXformable::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomXformable");
    return token;
}


inline UsdAttribute UsdGeomXformable::GetXformOpOrderAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->xformOpOrder));
}

inline UsdAttribute UsdGeomXformable::CreateXformOpOrderAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->xformOpOrder), SdfValueTypeNames->TokenArray,
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
