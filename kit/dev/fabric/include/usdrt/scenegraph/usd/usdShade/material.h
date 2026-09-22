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

/// @file usdShade/material.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdShade/nodeGraph.h"
#include "usdrt/scenegraph/usd/usdShade/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usd/variantSets.h"
#include "usdrt/scenegraph/usd/usdGeom/subset.h"
#include "usdrt/scenegraph/usd/usdShade/connectableAPI.h"*/
// clang-format on

// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
#include <usdrt/scenegraph/usd/usdShade/connectableAPI.h>
#include <usdrt/scenegraph/usd/usdShade/shader.h>
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
// MATERIAL                                                                    //
// -------------------------------------------------------------------------- //

/// @class UsdShadeMaterial
///
/// A Material provides a container into which multiple "render targets"
/// can add data that defines a "shading material" for a renderer.  Typically
/// this consists of one or more UsdRelationship properties that target
/// other prims of type \em Shader - though a target/client is free to add
/// any data that is suitable.  We <b>strongly advise</b> that all targets
/// adopt the convention that all properties be prefixed with a namespace
/// that identifies the target, e.g. "rel ri:surface = </Shaders/mySurf>".
///
/// ## Binding Materials
///
/// In the UsdShading model, geometry expresses a binding to a single Material or
/// to a set of Materials partitioned by UsdGeomSubsets defined beneath the
/// geometry; it is legal to bind a Material at the root (or other sub-prim) of
/// a model, and then bind a different Material to individual gprims, but the
/// meaning of inheritance and "ancestral overriding" of Material bindings is
/// left to each render-target to determine.  Since UsdGeom has no concept of
/// shading, we provide the API for binding and unbinding geometry on the API
/// schema UsdShadeMaterialBindingAPI.
///
/// ## Material Variation
///
/// The entire power of USD VariantSets and all the other composition
/// operators can leveraged when encoding shading variation.
/// UsdShadeMaterial provides facilities for a particular way of building
/// "Material variants" in which neither the identity of the Materials themselves
/// nor the geometry Material-bindings need to change - instead we vary the
/// targeted networks, interface values, and even parameter values within
/// a single variantSet.
/// See \ref UsdShadeMaterial_Variations "Authoring Material Variations"
/// for more details.
///
/// ## Materials Encapsulate their Networks in Namespace
///
/// UsdShade requires that all of the shaders that "belong" to the Material
/// live under the Material in namespace. This supports powerful, easy reuse
/// of Materials, because it allows us to *reference* a Material from one
/// asset (the asset might be a library of Materials) into another asset: USD
/// references compose all descendant prims of the reference target into the
/// referencer's namespace, which means that all of the referenced Material's
/// shader networks will come along with the Material. When referenced in this
/// way, Materials can also be [instanced](http://openusd.org/docs/USD-Glossary.html#USDGlossary-Instancing), for ease
/// of deduplication and compactness. Finally, Material encapsulation also allows us to \ref
/// UsdShadeMaterial_BaseMaterial "specialize" child materials from parent materials.
///
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdShadeTokens.
/// So to set an attribute to the value "rightHanded", use UsdShadeTokens->rightHanded
/// as the value.

class UsdShadeMaterial : public UsdShadeNodeGraph
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdShadeMaterial on UsdPrim @p prim.
    /// Equivalent to UsdShadeMaterial::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdShadeMaterial(const UsdPrim& prim = UsdPrim()) : UsdShadeNodeGraph(prim)
    {
    }

    /// Construct a UsdShadeMaterial on the prim held by @p schemaObj .
    /// Should be preferred over UsdShadeMaterial(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdShadeMaterial(const UsdSchemaBase& schemaObj) : UsdShadeNodeGraph(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdShadeMaterial()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdShadeMaterial Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SURFACE
    // --------------------------------------------------------------------- //
    /// Represents the universal "surface" output terminal of a
    /// material.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token outputs:surface` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |

    UsdAttribute GetSurfaceAttr() const;

    /// See GetSurfaceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSurfaceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DISPLACEMENT
    // --------------------------------------------------------------------- //
    /// Represents the universal "displacement" output terminal of a
    /// material.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token outputs:displacement` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |

    UsdAttribute GetDisplacementAttr() const;

    /// See GetDisplacementAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDisplacementAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VOLUME
    // --------------------------------------------------------------------- //
    /// Represents the universal "volume" output terminal of a
    /// material.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token outputs:volume` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |

    UsdAttribute GetVolumeAttr() const;

    /// See GetVolumeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVolumeAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--

    // --------------------------------------------------------------------- //
    /// \anchor UsdShadeMaterial_Outputs
    /// \name Standard Material Terminal Outputs
    /// A UsdShadeMaterial can have any number of "terminal" outputs. These
    /// outputs are generally used to point to outputs of shader prims or
    /// NodeGraphs that describe certain properties of the material that a
    /// renderer might wish to consume. There are three standard output
    /// terminals that are supported by the core API: <b>surface</b>,
    /// <b>displacement</b> and <b>volume</b>.
    ///
    /// Each terminal output can further be qualified by a token-valued
    /// <b>renderContext</b>. When a non-empty renderContext value is specified
    /// to the API, the output is considered to have a specific or restricted
    /// renderContext. If the renderContext value is empty (i.e. equal to
    /// UsdShadeTokens->universalRenderContext), then the output is considered
    /// to be a "universal", meaning it could apply to any render contexts.
    /// Render context token values is typically driven by the rendering backend
    /// consuming the terminal output (eg, RI or glslfx).
    /// @{

    /// Creates and returns the "surface" output on this material for the
    /// specified \p renderContext.
    ///
    /// If the output already exists on the material, it is returned and no
    /// authoring is performed. The returned output will always have the
    /// requested renderContext.
    UsdShadeOutput CreateSurfaceOutput(const TfToken& renderContext = UsdShadeTokens->universalRenderContext) const;

    /// Returns the "surface" output of this material for the specified
    /// \p renderContext. The returned output will always have the requested
    /// renderContext.
    ///
    /// An invalid output is returned if an output corresponding to the
    /// requested specific-renderContext does not exist.
    ///
    /// \sa UsdShadeMaterial::ComputeSurfaceSource()
    UsdShadeOutput GetSurfaceOutput(const TfToken& renderContext = UsdShadeTokens->universalRenderContext) const;

    /// Returns the "surface" outputs of this material for all available
    /// renderContexts.
    ///
    /// The returned vector will include all authored "surface" outputs with
    /// the <i>universal</i> renderContext output first, if present. Outputs
    /// are returned regardless of whether they are connected to a valid
    /// source.
    std::vector<UsdShadeOutput> GetSurfaceOutputs() const;

    // Computes the resolved "surface" output source for the given
    /// \p contextVector. Using the earliest renderContext in the contextVector
    /// that produces a valid Shader object.
    ///
    /// If a "surface" output corresponding to each of the renderContexts
    /// does not exist <b>or</b> is not connected to a valid source, then this
    /// checks the <i>universal</i> surface output.
    ///
    /// Returns an empty Shader object if there is no valid <i>surface</i>
    /// output source for any of the renderContexts in the \p contextVector.
    /// The python version of this method returns a tuple containing three
    /// elements (the source surface shader, sourceName, sourceType).
    // UsdShadeShader ComputeSurfaceSource(const TfTokenVector& contextVector = { UsdShadeTokens->universalRenderContext
    // },
    //                                     TfToken* sourceName = nullptr,
    //                                     UsdShadeAttributeType* sourceType = nullptr) const;

    /// Creates and returns the "displacement" output on this material for the
    /// specified \p renderContext.
    ///
    /// If the output already exists on the material, it is returned and no
    /// authoring is performed. The returned output will always have the
    /// requested renderContext.
    UsdShadeOutput CreateDisplacementOutput(const TfToken& renderContext = UsdShadeTokens->universalRenderContext) const;

    /// Returns the "displacement" output of this material for the specified
    /// renderContext. The returned output will always have the requested
    /// renderContext.
    ///
    /// An invalid output is returned if an output corresponding to the
    /// requested specific-renderContext does not exist.
    ///
    /// \sa UsdShadeMaterial::ComputeDisplacementSource()
    UsdShadeOutput GetDisplacementOutput(const TfToken& renderContext = UsdShadeTokens->universalRenderContext) const;

    /// Returns the "displacement" outputs of this material for all available
    /// renderContexts.
    ///
    /// The returned vector will include all authored "displacement" outputs
    /// with the <i>universal</i> renderContext output first, if present.
    /// Outputs are returned regardless of whether they are connected to a
    /// valid source.
    std::vector<UsdShadeOutput> GetDisplacementOutputs() const;

    /// Computes the resolved "displacement" output source for the given
    /// \p contextVector. Using the earliest renderContext in the contextVector
    /// that produces a valid Shader object.
    ///
    /// If a "displacement" output corresponding to each of the renderContexts
    /// does not exist <b>or</b> is not connected to a valid source, then this
    /// checks the <i>universal</i> displacement output.
    ///
    /// Returns an empty Shader object if there is no valid <i>displacement</i>
    /// output source for any of the renderContexts in the \p contextVector.
    /// The python version of this method returns a tuple containing three
    /// elements (the source displacement shader, sourceName, sourceType).
    // UsdShadeShader ComputeDisplacementSource(const TfTokenVector& contextVector = {
    // UsdShadeTokens->universalRenderContext },
    //                                          TfToken* sourceName = nullptr,
    //                                          UsdShadeAttributeType* sourceType = nullptr) const;

    /// Creates and returns the "volume" output on this material for the
    /// specified \p renderContext.
    ///
    /// If the output already exists on the material, it is returned and no
    /// authoring is performed. The returned output will always have the
    /// requested renderContext.
    UsdShadeOutput CreateVolumeOutput(const TfToken& renderContext = UsdShadeTokens->universalRenderContext) const;

    /// Returns the "volume" output of this material for the specified
    /// renderContext. The returned output will always have the requested
    /// renderContext.
    ///
    /// An invalid output is returned if an output corresponding to the
    /// requested specific-renderContext does not exist.
    ///
    /// \sa UsdShadeMaterial::ComputeVolumeSource()
    UsdShadeOutput GetVolumeOutput(const TfToken& renderContext = UsdShadeTokens->universalRenderContext) const;

    /// Returns the "volume" outputs of this material for all available
    /// renderContexts.
    ///
    /// The returned vector will include all authored "volume" outputs with the
    /// <i>universal</i> renderContext output first, if present. Outputs are
    /// returned regardless of whether they are connected to a valid source.
    std::vector<UsdShadeOutput> GetVolumeOutputs() const;

    /// Computes the resolved "volume" output source for the given
    /// \p contextVector. Using the earliest renderContext in the contextVector
    /// that produces a valid Shader object.
    ///
    /// If a "volume" output corresponding to each of the renderContexts
    /// does not exist <b>or</b> is not connected to a valid source, then this
    /// checks the <i>universal</i> volume output.
    ///
    /// Returns an empty Shader object if there is no valid <i>volume</i> output
    /// output source for any of the renderContexts in the \p contextVector.
    /// The python version of this method returns a tuple containing three
    /// elements (the source volume shader, sourceName, sourceType).
    // UsdShadeShader ComputeVolumeSource(const TfTokenVector& contextVector = { UsdShadeTokens->universalRenderContext
    // },
    //                                    TfToken* sourceName = nullptr,
    //                                    UsdShadeAttributeType* sourceType = nullptr) const;

private:
    // Helper method to retrieve outputs in all renderContexts that match the
    // given terminalName.
    std::vector<UsdShadeOutput> _GetOutputsForTerminalName(const TfToken& terminalName) const;

    // Helper method to compute the source shader of a given output, identified
    // by its baseName, for the renderContexts in the specified contextVector.
    // UsdShadeShader _ComputeNamedOutputShader(const TfToken& baseName,
    //                                          const TfTokenVector& contextVector,
    //                                          TfToken* sourceName,
    //                                          UsdShadeAttributeType* sourceType) const;

    static TfToken _GetOutputName(const TfToken& baseName, const TfToken& renderContext);

    /// @}
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdShadeMaterial::_GetStaticTfType()
{
    const static TfToken token("UsdShadeMaterial");
    return token;
}

/* virtual */
inline const TfToken UsdShadeMaterial::_GetTfTypeToken() const
{
    const static TfToken token("UsdShadeMaterial");
    return token;
}

/* static */
inline UsdShadeMaterial UsdShadeMaterial::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdShadeMaterial();
    }
    return UsdShadeMaterial(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdShadeMaterial::GetSurfaceAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdShadeTokens->outputsSurface));
}

inline UsdAttribute UsdShadeMaterial::CreateSurfaceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdShadeTokens->outputsSurface), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdShadeMaterial::GetDisplacementAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdShadeTokens->outputsDisplacement));
}

inline UsdAttribute UsdShadeMaterial::CreateDisplacementAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdShadeTokens->outputsDisplacement), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdShadeMaterial::GetVolumeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdShadeTokens->outputsVolume));
}

inline UsdAttribute UsdShadeMaterial::CreateVolumeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdShadeTokens->outputsVolume), SdfValueTypeNames->Token,
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

namespace usdrt
{

inline UsdShadeOutput UsdShadeMaterial::CreateSurfaceOutput(const TfToken& renderContext) const
{
    return CreateOutput(_GetOutputName(UsdShadeTokens->surface, renderContext), SdfValueTypeNames->Token);
}

inline UsdShadeOutput UsdShadeMaterial::GetSurfaceOutput(const TfToken& renderContext) const
{
    return GetOutput(_GetOutputName(UsdShadeTokens->surface, renderContext));
}

inline std::vector<UsdShadeOutput> UsdShadeMaterial::GetSurfaceOutputs() const
{
    return _GetOutputsForTerminalName(UsdShadeTokens->surface);
}

// inline UsdShadeShader UsdShadeMaterial::ComputeSurfaceSource(const TfTokenVector& contextVector,
//                                                              TfToken* sourceName,
//                                                              UsdShadeAttributeType* sourceType) const
// {
//     return _ComputeNamedOutputShader(UsdShadeTokens->surface, contextVector, sourceName, sourceType);
// }

inline UsdShadeOutput UsdShadeMaterial::CreateDisplacementOutput(const TfToken& renderContext) const
{
    return CreateOutput(_GetOutputName(UsdShadeTokens->displacement, renderContext), SdfValueTypeNames->Token);
}

inline UsdShadeOutput UsdShadeMaterial::GetDisplacementOutput(const TfToken& renderContext) const
{
    return GetOutput(_GetOutputName(UsdShadeTokens->displacement, renderContext));
}

inline std::vector<UsdShadeOutput> UsdShadeMaterial::GetDisplacementOutputs() const
{
    return _GetOutputsForTerminalName(UsdShadeTokens->displacement);
}

// inline UsdShadeShader UsdShadeMaterial::ComputeDisplacementSource(const TfTokenVector& contextVector,
//                                                                   TfToken* sourceName,
//                                                                   UsdShadeAttributeType* sourceType) const
// {
//     return _ComputeNamedOutputShader(UsdShadeTokens->displacement, contextVector, sourceName, sourceType);
// }

inline UsdShadeOutput UsdShadeMaterial::CreateVolumeOutput(const TfToken& renderContext) const
{
    return CreateOutput(_GetOutputName(UsdShadeTokens->volume, renderContext), SdfValueTypeNames->Token);
}

inline UsdShadeOutput UsdShadeMaterial::GetVolumeOutput(const TfToken& renderContext) const
{
    return GetOutput(_GetOutputName(UsdShadeTokens->volume, renderContext));
}

inline std::vector<UsdShadeOutput> UsdShadeMaterial::GetVolumeOutputs() const
{
    return _GetOutputsForTerminalName(UsdShadeTokens->volume);
}

// inline UsdShadeShader UsdShadeMaterial::ComputeVolumeSource(const TfTokenVector& contextVector,
//                                                             TfToken* sourceName,
//                                                             UsdShadeAttributeType* sourceType) const
// {
//     return _ComputeNamedOutputShader(UsdShadeTokens->volume, contextVector, sourceName, sourceType);
// }

inline std::vector<UsdShadeOutput> UsdShadeMaterial::_GetOutputsForTerminalName(const TfToken& terminalName) const
{
    std::vector<UsdShadeOutput> outputs;

    for (const UsdShadeOutput& output : GetOutputs())
    {
        const auto baseNameComponents = SdfPath::TokenizeIdentifier(output.GetBaseName().GetString());

        if (!baseNameComponents.empty() && baseNameComponents.back() == terminalName.GetString())
        {
            outputs.push_back(output);
        }
    }

    return outputs;
}

// inline UsdShadeShader UsdShadeMaterial::_ComputeNamedOutputShader(const TfToken& baseName,
//                                                                   const TfTokenVector& contextVector,
//                                                                   TfToken* sourceName,
//                                                                   UsdShadeAttributeType* sourceType) const
// {
//     for (const auto& context : contextVector)
//     {
//     }
// }

inline TfToken UsdShadeMaterial::_GetOutputName(const TfToken& baseName, const TfToken& renderContext)
{
    return TfToken(SdfPath::JoinIdentifier({ renderContext, baseName }));
}

} // namespace usdrt
