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

#include <omni/usd/Selection.h>
#include <omni/usd/UsdContext.h>

#include <OgnReadStageSelectionDatabase.h>


namespace omni
{
namespace graph
{
namespace nodes
{

class OgnReadStageSelection
{
public:
    static bool compute(OgnReadStageSelectionDatabase& db)
    {
        omni::usd::UsdContext* usdContext = omni::usd::UsdContext::getContext();
        PXR_NS::SdfPathVector selectedPaths = usdContext->getSelection()->getSelectedPrimPathsV2();
        ogn::array<NameToken>& selectedPrims = db.outputs.selectedPrims();
        selectedPrims.resize(selectedPaths.size());
        std::transform(selectedPaths.begin(), selectedPaths.end(), selectedPrims.begin(),
                       [&db](PXR_NS::SdfPath const& path)
                       {
                           std::string const& s = path.GetString();
                           auto tokenC = db.abi_context().iToken->getHandle(s.c_str());
                           return tokenC;
                       });
        return true;
    }
};

REGISTER_OGN_NODE()

} // nodes
} // graph
} // omni
