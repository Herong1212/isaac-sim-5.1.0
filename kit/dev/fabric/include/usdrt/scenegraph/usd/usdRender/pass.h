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

/// @file usdRender/pass.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"
#include "usdrt/scenegraph/usd/usdRender/tokens.h"


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
// RENDERPASS                                                                  //
// -------------------------------------------------------------------------- //

/// @class UsdRenderPass
///
/// A RenderPass prim encapsulates the necessary information
/// to generate multipass renders.  It houses properties for generating
/// dependencies and the necessary commands to run to generate renders, as
/// well as visibility controls for the scene.  While RenderSettings
/// describes the information needed to generate images from a single
/// invocation of a renderer, RenderPass describes the additional information
/// needed to generate a time varying set of images.
///
/// There are two consumers of RenderPass prims - a runtime executable that
/// generates images from usdRender prims, and pipeline specific code that
/// translates between usdRender prims and the pipeline's resource scheduling
/// software.  We'll refer to the latter as 'job submission code'.
///
/// The name of the prim is used as the pass's name.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdRenderTokens.
/// So to set an attribute to the value "rightHanded", use UsdRenderTokens->rightHanded
/// as the value.

class UsdRenderPass : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdRenderPass on UsdPrim @p prim.
    /// Equivalent to UsdRenderPass::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdRenderPass(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a UsdRenderPass on the prim held by @p schemaObj .
    /// Should be preferred over UsdRenderPass(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdRenderPass(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdRenderPass()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdRenderPass Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // PASSTYPE
    // --------------------------------------------------------------------- //
    /// A string used to categorize differently structured
    /// or executed types of passes within a customized pipeline.
    ///
    /// For example, when multiple DCC's (e.g. Houdini, Katana, Nuke)
    /// each compute and contribute different Products to a final result,
    /// it may be clearest and most flexible to create a separate
    /// RenderPass for each.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token passType` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetPassTypeAttr() const;

    /// See GetPassTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePassTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COMMAND
    // --------------------------------------------------------------------- //
    /// The command to run in order to generate
    /// renders for this pass.  The job submission code can use
    /// this to properly send tasks to the job scheduling software
    /// that will generate products.
    ///
    /// The command can contain variables that will be substituted
    /// appropriately during submission, as seen in the example below
    /// with {fileName}.
    ///
    /// For example:
    /// command[0] = "prman"
    /// command[1] = "-progress"
    /// command[2] = "-pixelvariance"
    /// command[3] = "-0.15"
    /// command[4] = "{fileName}" # the fileName property will be substituted
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform string[] command` |
    /// | C++ Type | VtArray<std::string> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->StringArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetCommandAttr() const;

    /// See GetCommandAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCommandAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FILENAME
    // --------------------------------------------------------------------- //
    /// The asset that contains the rendering prims or other
    /// information needed to render this pass.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform asset fileName` |
    /// | C++ Type | SdfAssetPath |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Asset |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetFileNameAttr() const;

    /// See GetFileNameAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFileNameAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DENOISEENABLE
    // --------------------------------------------------------------------- //
    /// When True, this Pass pass should be denoised.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool denoise:enable = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetDenoiseEnableAttr() const;

    /// See GetDenoiseEnableAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDenoiseEnableAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RENDERSOURCE
    // --------------------------------------------------------------------- //
    /// The source prim to render from.  If _fileName_ is not present,
    /// the source is assumed to be a RenderSettings prim present in the current
    /// Usd stage. If fileName is present, the source should be found in the
    /// file there. This relationship might target a string attribute on this
    /// or another prim that identifies the appropriate object in the external
    /// container.
    ///
    /// For example, for a Usd-backed pass, this would point to a RenderSettings
    /// prim.  Houdini passes would point to a Rop.  Nuke passes would point to
    /// a write node.
    ///
    ///
    UsdRelationship GetRenderSourceRel() const;

    /// See GetRenderSourceRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateRenderSourceRel() const;

public:
    // --------------------------------------------------------------------- //
    // INPUTPASSES
    // --------------------------------------------------------------------- //
    /// The set of other Passes that this Pass depends on
    /// in order to be constructed properly.  For example, a Pass A
    /// may generate a texture, which is then used as an input to
    /// Pass B.
    ///
    /// By default, usdRender makes some assumptions about the
    /// relationship between this prim and the prims listed in inputPasses.
    /// Namely, when per-frame tasks are generated from these pass prims,
    /// usdRender will assume a one-to-one relationship between tasks
    /// that share their frame number.  Consider a pass named 'composite'
    /// whose _inputPasses_ targets a Pass prim named 'beauty`.
    /// By default, each frame for 'composite' will depend on the
    /// same frame from 'beauty':
    /// beauty.1 -> composite.1
    /// beauty.2 -> composite.2
    /// etc
    ///
    /// The consumer of this RenderPass graph of inputs will need to resolve
    /// the transitive dependencies.
    ///
    ///
    UsdRelationship GetInputPassesRel() const;

    /// See GetInputPassesRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateInputPassesRel() const;

public:
    // --------------------------------------------------------------------- //
    // DENOISEPASS
    // --------------------------------------------------------------------- //
    /// The The UsdRenderDenoisePass prim from which to
    /// source denoise settings.
    ///
    ///
    UsdRelationship GetDenoisePassRel() const;

    /// See GetDenoisePassRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateDenoisePassRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdRenderPass::_GetStaticTfType()
{
    const static TfToken token("UsdRenderPass");
    return token;
}

/* virtual */
inline const TfToken UsdRenderPass::_GetTfTypeToken() const
{
    const static TfToken token("UsdRenderPass");
    return token;
}

/* static */
inline UsdRenderPass UsdRenderPass::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdRenderPass();
    }
    return UsdRenderPass(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdRenderPass::GetPassTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->passType));
}

inline UsdAttribute UsdRenderPass::CreatePassTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->passType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderPass::GetCommandAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->command));
}

inline UsdAttribute UsdRenderPass::CreateCommandAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->command), SdfValueTypeNames->StringArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderPass::GetFileNameAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->fileName));
}

inline UsdAttribute UsdRenderPass::CreateFileNameAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->fileName), SdfValueTypeNames->Asset,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderPass::GetDenoiseEnableAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->denoiseEnable));
}

inline UsdAttribute UsdRenderPass::CreateDenoiseEnableAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->denoiseEnable), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}


inline UsdRelationship UsdRenderPass::GetRenderSourceRel() const
{
    return GetPrim().GetRelationship(UsdRenderTokens->renderSource);
}

inline UsdRelationship UsdRenderPass::CreateRenderSourceRel() const
{
    return GetPrim().CreateRelationship(UsdRenderTokens->renderSource,
                                        /* custom = */ false);
}
inline UsdRelationship UsdRenderPass::GetInputPassesRel() const
{
    return GetPrim().GetRelationship(UsdRenderTokens->inputPasses);
}

inline UsdRelationship UsdRenderPass::CreateInputPassesRel() const
{
    return GetPrim().CreateRelationship(UsdRenderTokens->inputPasses,
                                        /* custom = */ false);
}
inline UsdRelationship UsdRenderPass::GetDenoisePassRel() const
{
    return GetPrim().GetRelationship(UsdRenderTokens->denoisePass);
}

inline UsdRelationship UsdRenderPass::CreateDenoisePassRel() const
{
    return GetPrim().CreateRelationship(UsdRenderTokens->denoisePass,
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
