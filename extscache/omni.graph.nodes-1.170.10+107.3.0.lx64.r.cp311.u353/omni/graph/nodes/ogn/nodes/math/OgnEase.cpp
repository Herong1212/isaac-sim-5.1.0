// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#define _USE_MATH_DEFINES
#include <OgnEaseDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>
#include <cmath>
#include <functional>

#include "XformUtils.h"

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{

template <typename T>
std::function<T(const T&, const T&, const float&)> getOperation(OgnEaseDatabase& db)
{
    const auto& easeFunc = db.inputs.easeFunc();
    auto exponent = std::max(std::min(db.inputs.blendExponent(), 10), 0);
    // Find the desired comparison
    std::function<T(const T&, const T&, const float&)> fn;
    if (easeFunc == db.tokens.EaseIn)
        fn = [=](const T& start, const T& end, const float& alpha) { return easeIn(start, end, alpha, exponent); };
    else if (easeFunc == db.tokens.EaseOut)
        fn = [=](const T& start, const T& end, const float& alpha) { return easeOut(start, end, alpha, exponent); };
    else if (easeFunc == db.tokens.EaseInOut)
        fn = [=](const T& start, const T& end, const float& alpha) { return easeInOut(start, end, alpha, exponent); };
    else if (easeFunc == db.tokens.Linear)
        fn = [=](const T& start, const T& end, const float& alpha) { return lerp(start, end, alpha); };
    else if (easeFunc == db.tokens.SinIn)
        fn = [=](const T& start, const T& end, const float& alpha) { return easeSinIn(start, end, alpha, exponent); };
    else if (easeFunc == db.tokens.SinOut)
        fn = [=](const T& start, const T& end, const float& alpha) { return easeSinOut(start, end, alpha, exponent); };
    else if (easeFunc == db.tokens.SinInOut)
        fn = [=](const T& start, const T& end, const float& alpha) { return easeSinInOut(start, end, alpha, exponent); };
    else
    {
        throw ogn::compute::InputError("Failed to resolve token " + std::string(db.tokenToString(easeFunc)) +
                                       ", expected one of EaseIn, EaseOut, EaseInOut, Linear, SinIn, SinOut, SinInOut");
    }
    return fn;
}
template <typename T>
bool tryComputeAssumingType(OgnEaseDatabase& db, size_t count)
{
    auto op = getOperation<T>(db);
    auto functor = [&](auto& start, auto& end, auto& alpha, auto& result)
    {
        auto a = std::min(std::max(alpha, (float)0.0), (float)1.0);
        result = op(start, end, a);
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, T, float, T>(
        db.inputs.start(), db.inputs.end(), db.inputs.alpha(), db.outputs.result(), functor, count);
}

template <typename T, size_t N>
bool tryComputeAssumingType(OgnEaseDatabase& db, size_t count)
{
    auto op = getOperation<T>(db);
    auto functor = [&](auto& start, auto& end, auto& alpha, auto& result)
    {
        auto a = std::min(std::max(alpha, (float)0.0), (float)1.0);
        for (size_t i = 0; i < N; i++)
        {
            result[i] = op(start[i], end[i], a);
        }
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N], T[N], float, T[N]>(
        db.inputs.start(), db.inputs.end(), db.inputs.alpha(), db.outputs.result(), functor, count);
}

} // namespace

class OgnEase
{
public:
    static bool computeVectorized(OgnEaseDatabase& db, size_t count)
    {
        auto& inputType = db.inputs.start().type();
        auto& endType = db.inputs.end().type();
        // Compute the components, if the types are all resolved.
        try
        {
            if (inputType.componentCount != endType.componentCount)
                throw ogn::compute::InputError("Mismatched tuple counts: " + std::to_string(inputType.componentCount) +
                                               " and " + std::to_string(endType.componentCount));

            switch (inputType.baseType)
            {
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
                case 9:
                    return tryComputeAssumingType<double, 9>(db, count);
                case 16:
                    return tryComputeAssumingType<double, 16>(db, count);
                default:
                    break;
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
                default:
                    break;
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
                default:
                    break;
                }
            default:
                break;
            }

            throw ogn::compute::InputError("Failed to resolve input types");
        }
        catch (ogn::compute::InputError& error)
        {
            db.logError("OgnEase: %s", error.what());
        }
        return false;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto start = node.iNode->getAttributeByToken(node, inputs::start.token());
        auto end = node.iNode->getAttributeByToken(node, inputs::end.token());
        auto alpha = node.iNode->getAttributeByToken(node, inputs::alpha.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto startType = start.iAttribute->getResolvedType(start);
        auto endType = end.iAttribute->getResolvedType(end);
        auto alphaType = alpha.iAttribute->getResolvedType(alpha);

        // Require start, end, and alpha to be resolved before determining result's type
        if (startType.baseType != BaseDataType::eUnknown && endType.baseType != BaseDataType::eUnknown &&
            alphaType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 3> attrs{ start, end, result };
            std::array<uint8_t, 3> tupleCounts{ startType.componentCount, endType.componentCount,
                                                std::max(startType.componentCount, endType.componentCount) };
            std::array<uint8_t, 3> arrayDepths{ startType.arrayDepth, endType.arrayDepth,
                                                std::max(alphaType.arrayDepth,
                                                         std::max(startType.arrayDepth, endType.arrayDepth)) };
            std::array<AttributeRole, 3> rolesBuf{ startType.role, endType.role, AttributeRole::eUnknown };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
    static bool updateNodeVersion(const GraphContextObj& context, const NodeObj& nodeObj, int oldVersion, int newVersion)
    {
        if (oldVersion < newVersion)
        {
            const INode* const iNode = nodeObj.iNode;
            if (oldVersion < 2)
            {
                auto const instanceIdx = kAccordingToContextIndex;
                auto oldAttrObj = iNode->getAttribute(nodeObj, "inputs:exponent");
                auto oldAttrDataHandle = oldAttrObj.iAttribute->getAttributeDataHandle(oldAttrObj, instanceIdx);
                ConstRawPtr srcDataPtr{ nullptr };
                size_t srcDataSize{ 0 };
                context.iAttributeData->getDataReferenceR(oldAttrDataHandle, context, srcDataPtr, srcDataSize);
                if (srcDataPtr)
                {
                    float exponentFloat = *(const float*)srcDataPtr;

                    auto newAttrObj = iNode->getAttribute(nodeObj, "inputs:blendExponent");
                    auto newAttrDataHandle = newAttrObj.iAttribute->getAttributeDataHandle(newAttrObj, instanceIdx);
                    RawPtr dstDataPtr{ nullptr };
                    size_t srcDataSize{ 0 };
                    context.iAttributeData->getDataReferenceW(newAttrDataHandle, context, dstDataPtr, srcDataSize);
                    if (dstDataPtr)
                    {
                        *dstDataPtr = (int)exponentFloat;
                    }
                }
                iNode->removeAttribute(nodeObj, "inputs:exponent");
            }
            return true;
        }
        return false;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
