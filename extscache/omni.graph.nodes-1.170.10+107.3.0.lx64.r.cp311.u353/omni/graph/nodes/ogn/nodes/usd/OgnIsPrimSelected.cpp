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
#include <omni/fabric/FabricUSD.h>

#include <OgnIsPrimSelectedDatabase.h>


namespace omni
{
namespace graph
{
namespace nodes
{

class OgnIsPrimSelected
{
public:
    static bool compute(OgnIsPrimSelectedDatabase& db)
    {
        omni::usd::UsdContext* usdContext = omni::usd::UsdContext::getContext();
        NameToken primPathToken =
            db.inputs.prim().size() == 0 ? db.inputs.primPath() : db.pathToToken(db.inputs.prim()[0]);
        bool isSelected{ false };
        if (primPathToken != omni::fabric::kUninitializedToken)
        {
            char const* primPath = db.abi_context().iToken->getText(primPathToken);
            if (primPath)
                isSelected = usdContext->getSelection()->isPrimPathSelected(primPath);
        }
        db.outputs.isSelected() = isSelected;
        return true;
    }
};

REGISTER_OGN_NODE()

} // nodes
} // graph
} // omni
