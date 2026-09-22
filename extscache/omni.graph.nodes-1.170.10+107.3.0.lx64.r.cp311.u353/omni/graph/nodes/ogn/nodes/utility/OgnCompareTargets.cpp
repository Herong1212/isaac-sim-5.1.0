// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnCompareTargetsDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnCompareTargets
{
    static void resolveOutput(const NodeObj& nodeObj)
    {
        auto& state = OgnCompareTargetsDatabase::sSharedState<OgnCompareTargets>(nodeObj);

        auto outAttr = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::result.m_token);
        auto outType = outAttr.iAttribute->getResolvedType(outAttr);

        Type resultType(BaseDataType::eBool, 1, state.m_compareEach ? 1 : 0);

        // Output is resolved and either we have an invalid type or the types don't match => unresolve
        if (outType.baseType != BaseDataType::eUnknown && resultType != outType)
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
        if (nodeObj.nodeHandle == kInvalidNodeHandle)
            return; // LCOV_EXCL_LINE

        GraphObj graphObj{ nodeObj.iNode->getGraph(nodeObj) };
        if (graphObj.graphHandle == kInvalidGraphHandle)
            return; // LCOV_EXCL_LINE

        GraphContextObj context{ graphObj.iGraph->getDefaultGraphContext(graphObj) };
        if (context.contextHandle == kInvalidGraphContextHandle)
            return; // LCOV_EXCL_LINE

        ConstAttributeDataHandle handle =
            attrObj.iAttribute->getConstAttributeDataHandle(attrObj, kAccordingToContextIndex);

        auto const dataPtr = getDataR<bool>(context, handle);
        if (dataPtr)
        {
            auto& state = OgnCompareTargetsDatabase::sSharedState<OgnCompareTargets>(nodeObj);
            state.m_compareEach = *dataPtr;
        }

        resolveOutput(nodeObj);
    }

public:
    bool m_compareEach;

    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        AttributeObj compareAttrib = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::compareEach.m_token);
        compareAttrib.iAttribute->registerValueChangedCallback(compareAttrib, onValueChanged, true);

        onValueChanged(compareAttrib, nullptr);
    }

    static size_t computeVectorized(OgnCompareTargetsDatabase& db, size_t count)
    {
        try
        {
            const auto& outputType = db.outputs.result().type();
            switch (outputType.arrayDepth)
            {
            case 0:
                for (size_t idx = 0; idx < count; ++idx)
                {
                    const auto& a = db.inputs.a(idx);
                    const auto& b = db.inputs.b(idx);
                    const auto& operation = db.inputs.operation(idx);
                    auto& result = *db.outputs.result(idx).template get<bool>();

                    if (operation == db.tokens.eq)
                        result = (a.size() != b.size()) ? false : std::equal(a.begin(), a.end(), b.begin());
                    else if (operation == db.tokens.ne)
                        result = (a.size() != b.size()) ? true : !std::equal(a.begin(), a.end(), b.begin());
                    else
                        throw ogn::compute::InputError("Failed to resolve token " +
                                                       std::string(db.tokenToString(operation)) +
                                                       ", expected one of (==,!=)");
                }
                return count;
            case 1:
                for (size_t idx = 0; idx < count; ++idx)
                {
                    const auto& a = db.inputs.a(idx);
                    const auto& b = db.inputs.b(idx);
                    const auto& operation = db.inputs.operation(idx);
                    auto result = db.outputs.result(idx).template get<bool[]>();

                    if (a.size() != b.size())
                        throw ogn::compute::InputError("Unable to broadcast arrays of differing lengths: " +
                                                       std::to_string(a.size()) + "!=" + std::to_string(b.size()));

                    auto outSize = a.size();
                    result.resize(outSize);
                    memset(result->data(), false, sizeof(bool) * outSize);
                    if (operation == db.tokens.eq)
                    {
                        for (size_t i = 0; i < outSize; i++)
                            (*result)[i] = (a[i] == b[i]);
                    }
                    else if (operation == db.tokens.ne)
                    {
                        for (size_t i = 0; i < outSize; i++)
                            (*result)[i] = (a[i] != b[i]);
                    }
                    else
                        throw ogn::compute::InputError("Failed to resolve token " +
                                                       std::string(db.tokenToString(operation)) +
                                                       ", expected one of (==,!=)");
                }
                return count;
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

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
