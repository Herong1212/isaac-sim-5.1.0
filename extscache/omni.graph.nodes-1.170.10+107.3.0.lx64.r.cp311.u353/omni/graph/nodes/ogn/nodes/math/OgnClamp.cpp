// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnClampDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/graph/core/ogn/UsdTypes.h>
//clang-format on

namespace omni
{
namespace graph
{
namespace nodes
{
namespace
{
template <typename T>
void clamp(T const& input, T const& lower, T const& upper, T& result)
{
    if (lower > upper)
    {
        throw ogn::compute::InputError("Lower is greater than upper!");
    }

    if (input <= lower)
    {
        result = lower;
    }
    else if (input < upper)
    {
        result = input;
    }
    else
    {
        result = upper;
    }
}


template <typename T>
bool tryComputeAssumingType(OgnClampDatabase& db, size_t count)
{
    return ogn::compute::tryComputeWithArrayBroadcasting<T>(
        db.inputs.input(), db.inputs.lower(), db.inputs.upper(), db.outputs.result(), &clamp<T>, count);
}

template <typename T, size_t tupleSize>
bool tryComputeAssumingType(OgnClampDatabase& db, size_t count)
{
    return ogn::compute::tryComputeWithTupleBroadcasting<tupleSize, T>(
        db.inputs.input(), db.inputs.lower(), db.inputs.upper(), db.outputs.result(), &clamp<T>, count);
}

} // namespace

// Node to clamp an input value or array of values to some range [lower, upper],
class OgnClamp
{
public:
    // Clamp a number or array of numbers to a specified range
    // If an array of numbers is provided as the input and lower/upper are scalers
    // Then each input numeric will be clamped to the range [lower, upper]
    // If all inputs are arrays, clamping will be done element-wise. lower & upper are broadcast against input
    static bool computeVectorized(OgnClampDatabase& db, size_t count)
    {
        auto& inputType = db.inputs.input().type();
        // Compute the components, if the types are all resolved.
        try
        {
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
                default:
                    break;
                };
            case BaseDataType::eInt64:
                return tryComputeAssumingType<int64_t>(db, count);
            case BaseDataType::eUChar:
                return tryComputeAssumingType<unsigned char>(db, count);
            case BaseDataType::eUInt:
                return tryComputeAssumingType<uint32_t>(db, count);
            case BaseDataType::eUInt64:
                return tryComputeAssumingType<uint64_t>(db, count);
            default:
                break;
            }

            db.logWarning("Failed to resolve input types");
        }
        catch (const std::exception& e)
        {
            db.logError("Clamping could not be performed: %s", e.what());
            return false;
        }

        return true;
    }

    static void onConnectionTypeResolve(const NodeObj& nodeObj)
    {
        auto inputAttr = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::input.token());
        auto lowerAttr = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::lower.token());
        auto upperAttr = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::upper.token());
        auto resultAttr = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::result.token());

        auto inputType = inputAttr.iAttribute->getResolvedType(inputAttr);
        auto lowerType = lowerAttr.iAttribute->getResolvedType(lowerAttr);
        auto upperType = upperAttr.iAttribute->getResolvedType(upperAttr);

        // If one of the upper or lower is resolved we can resolve the other because they should match
        if ((lowerType == BaseDataType::eUnknown) != (upperType == BaseDataType::eUnknown))
        {
            std::array<AttributeObj, 2> attrs{ lowerAttr, upperAttr };
            nodeObj.iNode->resolveCoupledAttributes(nodeObj, attrs.data(), attrs.size());
            lowerType = lowerAttr.iAttribute->getResolvedType(lowerAttr);
            upperType = upperAttr.iAttribute->getResolvedType(upperAttr);
        }

        // The output shape must match the input shape and visa-versa, however we can't say anything
        // about the input base type until it's connected
        if (inputType.baseType != BaseDataType::eUnknown && lowerType != BaseDataType::eUnknown &&
            upperType != BaseDataType::eUnknown)
        {
            if (inputType.baseType != lowerType.baseType || inputType.baseType != upperType.baseType)
            {
                nodeObj.iNode->logComputeMessageOnInstance(nodeObj, kAuthoringGraphIndex, ogn::Severity::eError,
                                                           "Unable to connect inputs to clamp with different base types");
                return;
            }
            std::array<AttributeObj, 2> attrs{ inputAttr, resultAttr };
            nodeObj.iNode->resolveCoupledAttributes(nodeObj, attrs.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE();

}
}
}
