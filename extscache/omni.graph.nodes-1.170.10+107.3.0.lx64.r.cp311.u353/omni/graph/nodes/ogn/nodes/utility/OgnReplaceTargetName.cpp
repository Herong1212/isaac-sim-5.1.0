// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnReplaceTargetNameDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <usdrt/scenegraph/usd/sdf/path.h>
#include "CoverageUtils.h"

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{

size_t tryComputeAssumingString(OgnReplaceTargetNameDatabase& db, size_t count)
{
    auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
    FIREWALL_RET_ERROR(db, !pathInterface, 0, "Failed to initialize path interface"); // LCOV_EXCL_LINE

    for (size_t idx = 0; idx < count; ++idx)
    {
        const auto& targets = db.inputs.targets(idx);
        const auto newName = db.inputs.newName(idx).template get<char[]>();
        auto& outTargets = db.outputs.targets(idx);
        if (!targets.empty())
        {
            outTargets.resize(targets.size());
            if (newName && !newName->empty())
            {
                for (size_t i = 0; i < targets.size(); i++)
                {
                    const auto& replacedPath = usdrt::SdfPath(targets[i]).ReplaceName(usdrt::TfToken(*newName));
                    pathInterface->addRef((omni::fabric::PathC)replacedPath); // refcount needs to be manually updated
                    outTargets[i] = (omni::fabric::PathC)replacedPath;
                }
            }
            else
                std::copy(targets.begin(), targets.end(), outTargets.begin());
        }
        else
            outTargets.resize(0);
    }
    return count;
}

size_t tryComputeAssumingToken(OgnReplaceTargetNameDatabase& db, size_t count)
{
    auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
    FIREWALL_RET_ERROR(db, !pathInterface, 0, "Failed to initialize path interface"); // LCOV_EXCL_LINE

    for (size_t idx = 0; idx < count; ++idx)
    {
        const auto& targets = db.inputs.targets(idx);
        const auto newName = db.inputs.newName(idx).template get<ogn::Token>();
        auto& outTargets = db.outputs.targets(idx);

        if (!targets.empty())
        {
            outTargets.resize(targets.size());
            if (newName && *newName != omni::fabric::kUninitializedToken)
            {
                for (size_t i = 0; i < targets.size(); i++)
                {
                    const auto& replacedPath = usdrt::SdfPath(targets[i]).ReplaceName(usdrt::TfToken(*newName));
                    pathInterface->addRef((omni::fabric::PathC)replacedPath); // refcount needs to be manually updated
                    outTargets[i] = (omni::fabric::PathC)replacedPath;
                }
            }
            else
                memcpy(outTargets.data(), targets.data(), sizeof(ogn::Path) * targets.size());
        }
        else
            outTargets.resize(0);
    }
    return count;
}

size_t tryComputeAssumingTokenArray(OgnReplaceTargetNameDatabase& db, size_t count)
{
    auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
    FIREWALL_RET_ERROR(db, !pathInterface, 0, "Failed to initialize path interface"); // LCOV_EXCL_LINE

    for (size_t idx = 0; idx < count; ++idx)
    {
        const auto& targets = db.inputs.targets(idx);
        const auto newNames = db.inputs.newName(idx).template get<ogn::Token[]>();
        auto& outTargets = db.outputs.targets(idx);

        if (targets.size() != newNames.size())
            throw ogn::compute::InputError("Unable to broadcast arrays of differing lengths: " +
                                           std::to_string(targets.size()) + "!=" + std::to_string(newNames.size()));

        if (!targets.empty())
        {
            outTargets.resize(targets.size());
            for (size_t i = 0; i < targets.size(); i++)
            {
                if ((*newNames)[i] != omni::fabric::kUninitializedToken)
                {
                    const auto& replacedPath = usdrt::SdfPath(targets[i]).ReplaceName(usdrt::TfToken((*newNames)[i]));
                    pathInterface->addRef((omni::fabric::PathC)replacedPath); // refcount needs to be manually updated
                    outTargets[i] = (omni::fabric::PathC)replacedPath;
                }
                else
                    memcpy(&outTargets[i], &targets[i], sizeof(ogn::Path));
            }
        }
        else
            outTargets.resize(0);
    }
    return count;
}

} // namespace

class OgnReplaceTargetName
{
public:
    static size_t computeVectorized(OgnReplaceTargetNameDatabase& db, size_t count)
    {
        try
        {
            auto& inputType = db.inputs.newName().type();
            switch (inputType.baseType)
            {
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

            case BaseDataType::eUChar:
                return tryComputeAssumingString(db, count);
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
};


REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
