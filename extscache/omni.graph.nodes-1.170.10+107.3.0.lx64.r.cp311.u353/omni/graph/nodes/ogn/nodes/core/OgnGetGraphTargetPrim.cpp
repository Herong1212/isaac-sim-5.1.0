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

#include <OgnGetGraphTargetPrimDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnGetGraphTargetPrim
{
public:
    static size_t computeVectorized(OgnGetGraphTargetPrimDatabase& db, size_t count)
    {
        auto ctx = db.abi_context();
        if (ctx.iContext->getGraphTargetAsPath)
        {
            auto graph = ctx.iContext->getGraph(ctx);
            omni::fabric::FabricId fabricId;
            graph.iGraph->getFabricId(graph, fabricId);
            auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
            auto stageReaderWriterId = iStageReaderWriter->createOrGetFromFabricId(fabricId);

            // recent version, fast path
            auto targets = db.getGraphTargetsAsPath(count);

            AttributeDataHandle hdl = db.outputs.prim.abi_handle();
            auto prims = getDataW<TargetPath*>(ctx, hdl);

            size_t const* sizes =
                iStageReaderWriter->getArrayAttributeSizeRdPtr(stageReaderWriterId, hdl.path(), hdl.name());

            for (size_t idx = 0; idx < count; idx++)
            {
                if (sizes[idx] != 1)
                {
                    // slow setup path
                    auto outPrims = db.outputs.prim(idx);
                    outPrims.resize(1);
                    outPrims[0] = targets[idx];
                }
                else
                    prims[idx][0] = targets[idx];
            }

            return count;
        }

        // old slow path - requires token conversion
        auto targets = db.getGraphTargets(count);
        for (size_t idx = 0; idx < count; idx++)
        {
            auto outPrims = db.outputs.prim(idx);
            outPrims.resize(1);
            outPrims[0] = db.tokenToPath(targets[idx]);
        }
        return count;
    }
};

REGISTER_OGN_NODE()
}
}
}
