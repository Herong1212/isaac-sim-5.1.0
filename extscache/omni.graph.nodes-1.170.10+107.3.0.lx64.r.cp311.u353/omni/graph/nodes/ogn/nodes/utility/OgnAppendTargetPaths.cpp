// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnAppendTargetPathsDatabase.h>
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
static void tryCompute(omni::fabric::IPath* pathInterface,
                       omni::fabric::IToken* tokenInterface,
                       ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu> const& suffix,
                       std::vector<TargetPath>& targetPaths)
{
    const auto& suffixType = suffix.type();
    if (suffixType.baseType == BaseDataType::eToken && suffixType.arrayDepth == 0)
    {
        auto suffixToken = *suffix.template get<OgnToken>();
        if (suffixToken != omni::fabric::kUninitializedToken)
        {
            for (size_t i = 0; i < targetPaths.size(); i++)
            {
                targetPaths[i] = pathInterface->appendPath(
                    targetPaths[i], pathInterface->getHandle(tokenInterface->getText(suffixToken)));
            }
        }
    }
    else if (suffixType.baseType == BaseDataType::eToken && suffixType.arrayDepth == 1)
    {
        const auto suffixTokens = *suffix.template get<OgnToken[]>();
        if (!suffixTokens.empty())
        {
            if (targetPaths.size() == 1 && suffixTokens.size() > 1)
                targetPaths = std::vector<TargetPath>(suffixTokens.size(), targetPaths[0]);
            else if (targetPaths.size() != suffixTokens.size())
                throw ogn::compute::InputError(
                    "Unable to broadcast arrays of differing lengths: " + std::to_string(targetPaths.size()) +
                    "!=" + std::to_string(suffixTokens.size()));

            for (size_t i = 0; i < suffixTokens.size(); i++)
            {
                if (suffixTokens[i] != omni::fabric::kUninitializedToken)
                {
                    targetPaths[i] = pathInterface->appendPath(
                        targetPaths[i], pathInterface->getHandle(tokenInterface->getText(suffixTokens[i])));
                }
            }
        }
    }
    else if (suffixType.baseType == BaseDataType::eUChar && suffixType.arrayDepth == 1)
    {
        auto const suffixData = suffix.template get<uchar[]>();
        std::string suffixString(suffixData->data(), suffixData->data() + suffixData->size());
        if (!suffixString.empty())
        {
            for (size_t i = 0; i < targetPaths.size(); i++)
            {
                targetPaths[i] =
                    pathInterface->appendPath(targetPaths[i], pathInterface->getHandle(suffixString.c_str()));
            }
        }
    }
}

} // namespace

class OgnAppendTargetPaths
{
public:
    static size_t computeVectorized(OgnAppendTargetPathsDatabase& db, size_t count)
    {
        auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
        FIREWALL_RET_ERROR(db, !pathInterface, 0, "Failed to initialize path interface"); // LCOV_EXCL_LINE
        auto tokenInterface = carb::getCachedInterface<omni::fabric::IToken>();
        FIREWALL_RET_ERROR(db, !tokenInterface, 0, "Failed to initialize token interface"); // LCOV_EXCL_LINE

        try
        {
            auto const& dynamicInputs = db.getDynamicInputs();
            std::vector<ogn::DynamicInput> allInputs{ db.inputs.input0 };
            allInputs.reserve(dynamicInputs.size() + 1);
            allInputs.insert(allInputs.end(), dynamicInputs.begin(), dynamicInputs.end());

            std::vector<TargetPath> targetPaths;

            for (size_t idx = 0; idx < count; ++idx)
            {
                auto const& rootTargets = db.inputs.rootTargets(idx);
                targetPaths.clear();
                if (!rootTargets.empty())
                    targetPaths.insert(targetPaths.end(), rootTargets.begin(), rootTargets.end());
                else
                    targetPaths.push_back(pathInterface->getHandle("/"));

                for (auto const& input : allInputs)
                    tryCompute(pathInterface, tokenInterface, input(idx), targetPaths);

                auto& output = db.outputs.targets(idx);
                output.resize(targetPaths.size());
                memcpy(output.data(), targetPaths.data(), sizeof(ogn::Path) * targetPaths.size());
            }
            return count;
        }
        // LCOV_EXCL_START
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return 0;
        // LCOV_EXCL_STOP
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
