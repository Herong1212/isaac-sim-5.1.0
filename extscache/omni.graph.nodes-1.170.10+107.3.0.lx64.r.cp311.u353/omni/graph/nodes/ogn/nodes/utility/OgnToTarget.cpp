// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnToTargetDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include "CoverageUtils.h"

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
size_t tryComputeAssumingString(OgnToTargetDatabase& db, size_t count)
{
    auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
    FIREWALL_RET_ERROR(db, !pathInterface, 0, "Failed to initialize path interface"); // LCOV_EXCL_LINE

    for (size_t idx = 0; idx < count; ++idx)
    {
        auto value = db.inputs.value(idx).template get<const char[]>();
        auto state = db.state.value(idx).template get<char[]>();
        if (value() != state())
        {
            std::string inString(value->data(), value->data() + value->size());
            *state = inString;

            auto& converted = db.outputs.converted(idx);
            if (value->size() > 0)
            {
                converted.resize(1);
                converted[0] = pathInterface->getHandle(inString.c_str());
            }
            else
                converted.resize(0);
        }
    }
    return count;
}

size_t tryComputeAssumingToken(OgnToTargetDatabase& db, size_t count)
{
    auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
    FIREWALL_RET_ERROR(db, !pathInterface, 0, "Failed to initialize path interface"); // LCOV_EXCL_LINE
    auto tokenInterface = carb::getCachedInterface<omni::fabric::IToken>();
    FIREWALL_RET_ERROR(db, !tokenInterface, 0, "Failed to initialize token interface"); // LCOV_EXCL_LINE

    for (size_t idx = 0; idx < count; ++idx)
    {
        const auto value = *db.inputs.value(idx).template get<OgnToken>();
        auto state = db.state.value(idx).template get<OgnToken>();
        if (*state != value)
        {
            *state = value;

            auto& converted = db.outputs.converted(idx);
            if (value != omni::fabric::kUninitializedToken)
            {
                converted.resize(1);
                converted[0] = pathInterface->getHandle(tokenInterface->getText(value));
            }
            else
                converted.resize(0);
        }
    }
    return count;
}

size_t tryComputeAssumingTokenArray(OgnToTargetDatabase& db, size_t count)
{
    auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
    FIREWALL_RET_ERROR(db, !pathInterface, 0, "Failed to initialize path interface"); // LCOV_EXCL_LINE
    auto tokenInterface = carb::getCachedInterface<omni::fabric::IToken>();
    FIREWALL_RET_ERROR(db, !tokenInterface, 0, "Failed to initialize token interface"); // LCOV_EXCL_LINE

    for (size_t idx = 0; idx < count; ++idx)
    {
        const auto value = *db.inputs.value(idx).template get<OgnToken[]>();
        auto state = db.state.value(idx).template get<OgnToken[]>();
        // Take the smaller of the two sizes to compare
        size_t size = value.size() < state.size() ? value.size() : state.size();
        if (memcmp(value.data(), state->data(), sizeof(ogn::Path) * size) != 0 || value.size() != state.size())
        {
            *state = value;

            auto& converted = db.outputs.converted(idx);
            if (!value.empty())
            {
                // Avoid adding empty tokens as they can cause issues for any nodes consuming them
                std::vector<ogn::Path> paths;
                for (size_t i = 0; i < value.size(); i++)
                {
                    if (value[i] != omni::fabric::kUninitializedToken)
                    {
                        paths.push_back(pathInterface->getHandle(tokenInterface->getText(value[i])));
                    }
                }

                converted.resize(paths.size());
                memcpy(converted.data(), paths.data(), sizeof(ogn::Path) * paths.size());
            }
            else
                converted.resize(0);
        }
    }
    return count;
}

} // namespace

class OgnToTarget
{
public:
    static bool computeVectorized(OgnToTargetDatabase& db, size_t count)
    {
        try
        {
            const auto& inputType = db.inputs.value().type();
            switch (inputType.baseType)
            {
            case BaseDataType::eUChar:
                return tryComputeAssumingString(db, count);
            case BaseDataType::eToken:
                switch (inputType.arrayDepth)
                {
                case 0:
                    return tryComputeAssumingToken(db, count);
                case 1:
                    return tryComputeAssumingTokenArray(db, count);
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

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto valueAttr = node.iNode->getAttributeByToken(node, inputs::value.token());
        auto stateAttr = node.iNode->getAttributeByToken(node, state::value.token());
        auto const valueType = valueAttr.iAttribute->getResolvedType(valueAttr);

        if (valueType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 2> attrs{ valueAttr, stateAttr };
            node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
