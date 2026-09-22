// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnBreakMatrix4Database.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/vec.h>
#include "CoverageUtils.h"

using omni::math::linalg::matrix4;
using omni::math::linalg::vec3;
using omni::math::linalg::vec4;

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
template <typename T>
size_t tryComputeAssumingType4(OgnBreakMatrix4Database& db, size_t count)
{
    auto functor = [](auto const& input, auto& xOut, auto& yOut, auto& zOut, auto& wOut)
    {
        const auto& matrix = *reinterpret_cast<const matrix4<T>*>(input);
        auto& x = *reinterpret_cast<vec4<T>*>(xOut);
        auto& y = *reinterpret_cast<vec4<T>*>(yOut);
        auto& z = *reinterpret_cast<vec4<T>*>(zOut);
        auto& w = *reinterpret_cast<vec4<T>*>(wOut);
        x = matrix.GetRow(0);
        y = matrix.GetRow(1);
        z = matrix.GetRow(2);
        w = matrix.GetRow(3);
    };

    switch (db.inputs.matrix().type().arrayDepth)
    {
    case 0:
    {
        const auto input = db.inputs.matrix().template get<T[16]>();
        auto xOut = db.outputs.x().template get<T[4]>();
        auto yOut = db.outputs.y().template get<T[4]>();
        auto zOut = db.outputs.z().template get<T[4]>();
        auto wOut = db.outputs.w().template get<T[4]>();
        if (input && xOut && yOut && zOut && wOut)
        {
            const auto inputVec = input.vectorized(count);
            const auto xOutVec = xOut.vectorized(count);
            const auto yOutVec = yOut.vectorized(count);
            const auto zOutVec = zOut.vectorized(count);
            const auto wOutVec = wOut.vectorized(count);
            if (!inputVec.empty() && !xOutVec.empty() && !yOutVec.empty() && !zOutVec.empty() && !wOutVec.empty())
            {
                for (size_t idx = 0; idx < count; idx++)
                    functor(inputVec[idx], xOutVec[idx], yOutVec[idx], zOutVec[idx], wOutVec[idx]);
            }
        }
        return count;
    }
    case 1:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto input = db.inputs.matrix(idx).template get<T[][16]>();
            auto xOut = db.outputs.x(idx).template get<T[][4]>();
            auto yOut = db.outputs.y(idx).template get<T[][4]>();
            auto zOut = db.outputs.z(idx).template get<T[][4]>();
            auto wOut = db.outputs.w(idx).template get<T[][4]>();
            if (input && xOut && yOut && zOut && wOut)
            {
                xOut->resize(input->size());
                yOut->resize(input->size());
                zOut->resize(input->size());
                wOut->resize(input->size());
                for (size_t i = 0; i < input->size(); i++)
                    functor((*input)[i], (*xOut)[i], (*yOut)[i], (*zOut)[i], (*wOut)[i]);
            }
        }
        return count;
    // LCOV_EXCL_START
    default:
        throw ogn::compute::InputError("Failed to resolve input types");
        // LCOV_EXCL_STOP
    }
}

template <typename T>
bool tryComputeAssumingType3(OgnBreakMatrix4Database& db, size_t count)
{
    auto functor = [](auto const& input, auto& xOut, auto& yOut, auto& zOut, auto& wOut)
    {
        auto matrix = *reinterpret_cast<const matrix4<T>*>(input);
        auto& x = *reinterpret_cast<vec3<T>*>(xOut);
        auto& y = *reinterpret_cast<vec3<T>*>(yOut);
        auto& z = *reinterpret_cast<vec3<T>*>(zOut);
        auto& w = *reinterpret_cast<vec3<T>*>(wOut);
        x = matrix.GetRow3(0);
        y = matrix.GetRow3(1);
        z = matrix.GetRow3(2);
        w = matrix.GetRow3(3);
    };

    switch (db.inputs.matrix().type().arrayDepth)
    {
    case 0:
    {
        const auto input = db.inputs.matrix().template get<T[16]>();
        auto xOut = db.outputs.x().template get<T[3]>();
        auto yOut = db.outputs.y().template get<T[3]>();
        auto zOut = db.outputs.z().template get<T[3]>();
        auto wOut = db.outputs.w().template get<T[3]>();
        if (input && xOut && yOut && zOut && wOut)
        {
            const auto inputVec = input.vectorized(count);
            const auto xOutVec = xOut.vectorized(count);
            const auto yOutVec = yOut.vectorized(count);
            const auto zOutVec = zOut.vectorized(count);
            const auto wOutVec = wOut.vectorized(count);
            if (!inputVec.empty() && !xOutVec.empty() && !yOutVec.empty() && !zOutVec.empty() && !wOutVec.empty())
            {
                for (size_t idx = 0; idx < count; idx++)
                    functor(inputVec[idx], xOutVec[idx], yOutVec[idx], zOutVec[idx], wOutVec[idx]);
            }
        }
        return count;
    }
    case 1:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto input = db.inputs.matrix(idx).template get<T[][16]>();
            auto xOut = db.outputs.x(idx).template get<T[][3]>();
            auto yOut = db.outputs.y(idx).template get<T[][3]>();
            auto zOut = db.outputs.z(idx).template get<T[][3]>();
            auto wOut = db.outputs.w(idx).template get<T[][3]>();
            if (input && xOut && yOut && zOut && wOut)
            {
                xOut->resize(input->size());
                yOut->resize(input->size());
                zOut->resize(input->size());
                wOut->resize(input->size());
                for (size_t i = 0; i < input->size(); i++)
                    functor((*input)[i], (*xOut)[i], (*yOut)[i], (*zOut)[i], (*wOut)[i]);
            }
        }
        return count;
    // LCOV_EXCL_START
    default:
        throw ogn::compute::InputError("Failed to resolve input types");
        // LCOV_EXCL_STOP
    }
}
} // namespace

class OgnBreakMatrix4
{
    static void resolveOutput(const NodeObj& nodeObj)
    {
        auto& state = OgnBreakMatrix4Database::sSharedState<OgnBreakMatrix4>(nodeObj);

        auto matrix = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::matrix.token());
        auto x = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::x.token());
        auto y = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::y.token());
        auto z = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::z.token());
        auto w = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::w.token());

        auto matrixType = matrix.iAttribute->getResolvedType(matrix);
        Type resultType;
        if (matrixType.baseType != BaseDataType::eUnknown)
            resultType = Type(matrixType.baseType, state.m_componentCount, matrixType.arrayDepth, AttributeRole::eNone);
        else
            resultType = Type(BaseDataType::eUnknown);

        std::array<AttributeObj, 4> attrs{ x, y, z, w };
        for (AttributeObj& attr : attrs)
        {
            auto attrType = attr.iAttribute->getResolvedType(attr);

            // Output is resolved and either we have an invalid type or the types don't match => unresolve
            if (attrType.baseType != BaseDataType::eUnknown &&
                (resultType.baseType == BaseDataType::eUnknown || resultType != attrType))
            {
                attr.iAttribute->setResolvedType(attr, Type(BaseDataType::eUnknown));
            }

            // Output is unresolved and we have a valid type => resolve
            if (attrType.baseType == BaseDataType::eUnknown && resultType.baseType != BaseDataType::eUnknown)
            {
                attr.iAttribute->setResolvedType(attr, resultType);
            }
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
            auto& state = OgnBreakMatrix4Database::sSharedState<OgnBreakMatrix4>(nodeObj);
            if (*dataPtr == OgnBreakMatrix4Database::tokens.Double_3)
                state.m_componentCount = 3;
            else
                state.m_componentCount = 4;
        }

        resolveOutput(nodeObj);
    }

public:
    uint8_t m_componentCount;

    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        AttributeObj outputTypeAttrib = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::outputType.m_token);
        outputTypeAttrib.iAttribute->registerValueChangedCallback(outputTypeAttrib, onValueChanged, true);

        onValueChanged(outputTypeAttrib, nullptr);
    }

    static size_t computeVectorized(OgnBreakMatrix4Database& db, size_t count)
    {
        try
        {
            const auto& outputType = db.outputs.x().type();
            switch (outputType.baseType)
            {
            case BaseDataType::eDouble:
                switch (outputType.componentCount)
                {
                case 3:
                    return tryComputeAssumingType3<double>(db, count);
                case 4:
                    return tryComputeAssumingType4<double>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
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

}
}
}
