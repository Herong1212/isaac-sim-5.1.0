// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include "PrimCommon.h"
#include "VariantCommon.h"
#include "LayerIdentifierResolver.h"

#include <omni/math/linalg/SafeCast.h>
#include <omni/usd/UsdContext.h>
#include <pxr/usd/sdf/variantSetSpec.h>
#include <pxr/usd/sdf/variantSpec.h>

#include <OgnBlendVariantsDatabase.h>

using omni::graph::core::ogn::eAttributeType::kOgnOutput;
using omni::graph::core::ogn::eMemoryType::kCpu;
using omni::math::linalg::vec3f;

using DB = OgnBlendVariantsDatabase;

namespace omni::graph::nodes
{
namespace
{
using LerpFunction = void (*)(const double alpha,
                              const pxr::SdfAttributeSpecHandle& attributeA,
                              const pxr::SdfAttributeSpecHandle& attributeB,
                              pxr::UsdAttribute attribute);
template <typename T>
void continuousLerp(const double alpha,
                    const pxr::SdfAttributeSpecHandle& attributeA,
                    const pxr::SdfAttributeSpecHandle& attributeB,
                    pxr::UsdAttribute attribute)
{
    const T& a = attributeA->GetDefaultValue().Get<T>();
    const T& b = attributeB->GetDefaultValue().Get<T>();

    T c = pxr::GfLerp(alpha, a, b);
    if (attribute.IsValid())
        attribute.Set<T>(c);
}

template <typename T>
void discreteLerp(const double alpha,
                  const pxr::SdfAttributeSpecHandle& attributeA,
                  const pxr::SdfAttributeSpecHandle& attributeB,
                  pxr::UsdAttribute attribute)
{
    const T& a = attributeA->GetDefaultValue().Get<T>();
    const T& b = attributeB->GetDefaultValue().Get<T>();
    if (attribute.IsValid())
    {
        if (alpha < 0.5)
            attribute.Set<T>(a);
        else
            attribute.Set<T>(b);
    }
}

void lerpAttribute(const double alpha,
                   const pxr::SdfAttributeSpecHandle& attributeA,
                   const pxr::SdfAttributeSpecHandle& attributeB,
                   const pxr::UsdAttribute& attribute)
{
    if (attributeA->GetSpecType() != attributeB->GetSpecType())
        throw warning("Attribute spec types do not match (attribute " + attribute.GetPath().GetString() + ")");

    if (attributeA->GetTypeName() != attribute.GetTypeName())
        throw warning("Attribute types do not match (attribute " + attribute.GetPath().GetString() + ")");

    if (attributeA->GetValueType() != attributeB->GetValueType())
        throw warning("Attribute value types do not match");

    auto typeName = attributeA->GetValueType().GetTypeName();

    auto handleType = [alpha, &attributeA, &attributeB, &attribute, &typeName](
                          const char* type, LerpFunction lerpFunction) -> bool
    {
        if (typeName == type)
        {
            lerpFunction(alpha, attributeA, attributeB, attribute);
            return true;
        }
        return false;
    };


    if (!handleType("bool", discreteLerp<bool>) && !handleType("double", continuousLerp<double>) &&
        !handleType("float", continuousLerp<float>) && !handleType("pxr_half::half", continuousLerp<pxr::GfHalf>) &&
        !handleType("int", discreteLerp<int>) && !handleType("__int64", discreteLerp<int64_t>) // Windows
        && !handleType("long", discreteLerp<int64_t>) // Linux
        && !handleType("unsigned char", discreteLerp<uint8_t>) && !handleType("unsigned int", discreteLerp<uint32_t>) &&
        !handleType("unsigned __int64", discreteLerp<uint64_t>) // Windows
        && !handleType("unsigned long", discreteLerp<uint64_t>) // Linux
        && !handleType("TfToken", discreteLerp<pxr::TfToken>) &&
        !handleType("SdfTimeCode", continuousLerp<pxr::SdfTimeCode>) &&
        !handleType("GfVec2d", continuousLerp<pxr::GfVec2d>) && !handleType("GfVec2f", continuousLerp<pxr::GfVec2f>) &&
        !handleType("GfVec2h", continuousLerp<pxr::GfVec2h>) && !handleType("GfVec2i", discreteLerp<pxr::GfVec2i>) &&
        !handleType("GfVec3d", continuousLerp<pxr::GfVec3d>) && !handleType("GfVec3f", continuousLerp<pxr::GfVec3f>) &&
        !handleType("GfVec3h", continuousLerp<pxr::GfVec3h>) && !handleType("GfVec3i", discreteLerp<pxr::GfVec3i>) &&
        !handleType("GfVec4d", continuousLerp<pxr::GfVec4d>) && !handleType("GfVec4f", continuousLerp<pxr::GfVec4f>) &&
        !handleType("GfVec4h", continuousLerp<pxr::GfVec4h>) && !handleType("GfVec4i", discreteLerp<pxr::GfVec4i>) &&
        !handleType("GfQuatd", continuousLerp<pxr::GfQuatd>) && !handleType("GfQuatf", continuousLerp<pxr::GfQuatf>) &&
        !handleType("GfQuath", continuousLerp<pxr::GfQuath>) &&
        !handleType("GfMatrix2d", continuousLerp<pxr::GfMatrix2d>) &&
        !handleType("GfMatrix3d", continuousLerp<pxr::GfMatrix3d>) &&
        !handleType("GfMatrix4d", continuousLerp<pxr::GfMatrix4d>))
        throw warning("Unsupported attribute type " + typeName); // LCOV_EXCL_LINE  Should never fail
}
}

class OgnBlendVariants
{
    PXR_NS::UsdEditTarget m_editTarget;

public:
    static bool compute(OgnBlendVariantsDatabase& db)
    {
        auto ok = [&db]()
        {
            db.outputs.execOut() = kExecutionAttributeStateEnabled;
            return true;
        };

        try
        {
            pxr::UsdPrim prim = tryGetTargetPrim(db, db.inputs.prim(), "prim");

            std::string variantSetName = db.tokenToString(db.inputs.variantSetName());
            std::string variantNameA = db.tokenToString(db.inputs.variantNameA());
            std::string variantNameB = db.tokenToString(db.inputs.variantNameB());
            double blend = std::max(std::min(db.inputs.blend(), 1.0), 0.0);

            pxr::UsdVariantSets variantSets = prim.GetVariantSets();
            pxr::UsdVariantSet variantSet = variantSets.GetVariantSet(variantSetName);
            if (!variantSet.IsValid())
                throw warning("Invalid variant set " + variantSetName);

            NodeObj nodeObj = db.abi_node();
            GraphContextObj context = db.abi_context();

            auto& state = db.perInstanceState<OgnBlendVariants>();

            long stageId = context.iContext->getStageId(context);
            auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));

            auto layerIdentifier = db.inputs.layerIdentifier();
            if (db.state.layerIdentifier() != layerIdentifier)
            {
                state.m_editTarget =
                    resolveLayerEditTarget(nodeObj, stage, inputs::layerIdentifier.m_token, layerIdentifier);
                db.state.layerIdentifier() = layerIdentifier;
            }

            PXR_NS::UsdEditTarget editTarget = stage->GetEditTarget();
            if (layerIdentifier != fabric::kUninitializedToken)
                editTarget = state.m_editTarget;

            pxr::UsdEditContext editContext(stage, editTarget);

            bool finishing = (1.0 - blend) < 1e-6;

            if (finishing && db.inputs.setVariant())
                variantSet.SetVariantSelection(variantNameB);

            VariantData variantDataA = getVariantData(prim, variantSetName, variantNameA);
            VariantData variantDataB = getVariantData(prim, variantSetName, variantNameB);

            auto& aAttributes = variantDataA.attributeSpecs;
            auto& bAttributes = variantDataB.attributeSpecs;

            for (const auto& [path, attributeA] : aAttributes)
            {
                if (bAttributes.find(path) == bAttributes.end())
                {
                    continue;
                }

                auto attributeB = bAttributes[path];

                auto attribute = prim.GetStage()->GetAttributeAtPath(path);
                if (!attribute.IsValid())
                {
                    throw warning("Invalid attribute " + path.GetString());
                }

                if (finishing && db.inputs.setVariant())
                {
                    attribute.Clear();
                }
                else
                {
                    lerpAttribute(blend, attributeA, attributeB, attribute);
                }
            }

            if (blend < 0.5)
            {
                setMaterialBindingsRT(variantDataA);
            }
            else
            {
                setMaterialBindingsRT(variantDataB);
            }

            return ok();
        }
        catch (const warning& e)
        {
            db.logWarning(e.what());
        }
        // LCOV_EXCL_START
        catch (const std::exception& e)
        {
            db.logError(e.what());
        }
        // LCOV_EXCL_STOP

        return false;
    }
};

REGISTER_OGN_NODE()

} // namespace omni::graph::nodes
