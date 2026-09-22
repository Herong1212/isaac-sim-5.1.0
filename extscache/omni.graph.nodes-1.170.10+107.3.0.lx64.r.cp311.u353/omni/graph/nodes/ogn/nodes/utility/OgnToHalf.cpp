// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnToHalfDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/graph/core/ogn/UsdTypes.h>

#include "ConversionCommon.h"
#include "CoverageUtils.h"

namespace omni
{
namespace graph
{
namespace nodes
{
namespace
{
template <typename T>
size_t tryComputeAssumingType(OgnToHalfDatabase& db, size_t count)
{
    auto functor = [](auto const& value, auto& converted) { converted = pxr::GfHalf(float(value)); };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, pxr::GfHalf>(
               db.inputs.value(), db.outputs.converted(), functor, count) ?
               count :
               0;
}

template <typename T, size_t tupleSize>
size_t tryComputeAssumingType(OgnToHalfDatabase& db, size_t count)
{
    auto functor = [](auto const& value, auto& converted) { converted = pxr::GfHalf(float(value)); };
    return ogn::compute::tryComputeWithTupleBroadcasting<tupleSize, T, pxr::GfHalf>(
               db.inputs.value(), db.outputs.converted(), functor, count) ?
               count :
               0;
}

} // namespace

class OgnToHalf
{
    static void resolveOutput(const NodeObj& nodeObj)
    {
        auto& state = OgnToHalfDatabase::sSharedState<OgnToHalf>(nodeObj);

        auto valueAttr = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::value.m_token);
        auto outAttr = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::converted.m_token);

        auto valueType = valueAttr.iAttribute->getResolvedType(valueAttr);
        auto outType = outAttr.iAttribute->getResolvedType(outAttr);

        Type resultType = getOutputType(valueType, BaseDataType::eHalf, state.m_role);

        // Output is resolved and either we have an invalid type or the types don't match => unresolve
        if (outType.baseType != BaseDataType::eUnknown &&
            (resultType.baseType == BaseDataType::eUnknown || resultType != outType))
        {
            outAttr.iAttribute->setResolvedType(outAttr, Type(BaseDataType::eUnknown));
        }

        // Output is unresolved and we have a valid type => resolve
        if (outType.baseType == BaseDataType::eUnknown && resultType.baseType != BaseDataType::eUnknown)
        {
            outAttr.iAttribute->setResolvedType(outAttr, resultType);
        }
    }

    static void onValueChanged(AttributeObj const& attrObj, void const* userData)
    {
        NodeObj nodeObj{ attrObj.iAttribute->getNode(attrObj) };
        FIREWALL_RETURN(nodeObj.nodeHandle == kInvalidNodeHandle); // LCOV_EXCL_LINE

        GraphObj graphObj{ nodeObj.iNode->getGraph(nodeObj) };
        FIREWALL_RETURN(graphObj.graphHandle == kInvalidGraphHandle); // LCOV_EXCL_LINE

        GraphContextObj context{ graphObj.iGraph->getDefaultGraphContext(graphObj) };
        FIREWALL_RETURN(context.contextHandle == kInvalidGraphContextHandle); // LCOV_EXCL_LINE

        ConstAttributeDataHandle handle =
            attrObj.iAttribute->getConstAttributeDataHandle(attrObj, kAccordingToContextIndex);

        auto const dataPtr = getDataR<NameToken>(context, handle);
        if (dataPtr)
        {
            auto& state = OgnToHalfDatabase::sSharedState<OgnToHalf>(nodeObj);
            state.m_role = state.m_roles[*dataPtr];
        }

        resolveOutput(nodeObj);
    }

public:
    std::unordered_map<NameToken, AttributeRole> m_roles;

    AttributeRole m_role;

    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        auto& state = OgnToHalfDatabase::sSharedState<OgnToHalf>(nodeObj);

        state.m_roles = { { OgnToHalfDatabase::tokens.eNone, AttributeRole::eNone },
                          { OgnToHalfDatabase::tokens.eColor, AttributeRole::eColor },
                          { OgnToHalfDatabase::tokens.eFrame, AttributeRole::eFrame },
                          { OgnToHalfDatabase::tokens.eNormal, AttributeRole::eNormal },
                          { OgnToHalfDatabase::tokens.ePosition, AttributeRole::ePosition },
                          { OgnToHalfDatabase::tokens.eQuaternion, AttributeRole::eQuaternion },
                          { OgnToHalfDatabase::tokens.eTexCoord, AttributeRole::eTexCoord },
                          { OgnToHalfDatabase::tokens.eVector, AttributeRole::eVector } };

        AttributeObj roleAttrib = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::role.m_token);
        roleAttrib.iAttribute->registerValueChangedCallback(roleAttrib, onValueChanged, true);

        onValueChanged(roleAttrib, nullptr);
    }

    // Node to convert numeric inputs to halfs
    static size_t computeVectorized(OgnToHalfDatabase& db, size_t count)
    {
        auto& inputType = db.inputs.value().type();
        // Compute the components, if the types are all resolved.
        try
        {
            switch (inputType.baseType)
            {
            case BaseDataType::eBool:
                return tryComputeAssumingType<bool>(db, count);
            case BaseDataType::eDouble:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<double>(db, count);
                case 2:
                    return tryComputeAssumingType<double, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<double, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<double, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eFloat:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<float>(db, count);
                case 2:
                    return tryComputeAssumingType<float, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<float, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<float, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eHalf:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<pxr::GfHalf>(db, count);
                case 2:
                    return tryComputeAssumingType<pxr::GfHalf, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<pxr::GfHalf, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<pxr::GfHalf, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<int32_t>(db, count);
                case 2:
                    return tryComputeAssumingType<int32_t, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<int32_t, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<int32_t, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt64:
                return tryComputeAssumingType<int64_t>(db, count);
            case BaseDataType::eUChar:
                return tryComputeAssumingType<uchar>(db, count);
            case BaseDataType::eUInt:
                return tryComputeAssumingType<uint32_t>(db, count);
            case BaseDataType::eUInt64:
                return tryComputeAssumingType<uint64_t>(db, count);
            // LCOV_EXCL_START
            default:
                throw ogn::compute::InputError("Failed to resolve input types");
                // LCOV_EXCL_STOP
            }
        }
        // LCOV_EXCL_START
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return 0;
        // LCOV_EXCL_STOP
    }

    static void onConnectionTypeResolve(const NodeObj& nodeObj)
    {
        resolveOutput(nodeObj);
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
