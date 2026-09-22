// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnGetPrimRelationshipDatabase.h"

#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/usd/sdf/path.h>
#include <pxr/usd/usd/common.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usd/relationship.h>
#include <pxr/usd/usdUtils/stageCache.h>
#include <omni/graph/core/PostUsdInclude.h>

#include <algorithm>

#include "PrimCommon.h"
// clang-format on

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnGetPrimRelationship
{
public:
    // Queries relationship data on a prim
    static bool compute(OgnGetPrimRelationshipDatabase& db)
    {
        auto& nodeObj = db.abi_node();
        const auto& contextObj = db.abi_context();
        auto iContext = contextObj.iContext;

        try
        {
            auto primPath = getPrimOrPath(contextObj, nodeObj, inputs::prim.token(), inputs::path.token(),
                                          inputs::usePath.token(), db.getInstanceIndex());

            const char* relName = db.tokenToString(db.inputs.name());
            if (!relName)
                return false;

            long int stageId = iContext->getStageId(contextObj);
            pxr::UsdStageRefPtr stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));

            pxr::UsdPrim prim = stage->GetPrimAtPath(primPath);
            if (!prim)
                return false;

            pxr::UsdRelationship relationship = prim.GetRelationship(pxr::TfToken(relName));
            pxr::SdfPathVector targets;
            if (relationship.GetTargets(&targets))
            {
                auto& outputPaths = db.outputs.paths();
                outputPaths.resize(targets.size());
                std::transform(targets.begin(), targets.end(), outputPaths.begin(),
                               [&db](const pxr::SdfPath& path) { return db.stringToToken(path.GetText()); });
            }

            return true;
        }
        catch (const std::exception& e)
        {
            db.logError(e.what());
            return false;
        }
    }

    static bool updateNodeVersion(const GraphContextObj& context, const NodeObj& nodeObj, int oldVersion, int newVersion)
    {
        if (oldVersion < newVersion)
        {
            if (oldVersion < 2)
            {
                // for older nodes, inputs:usePath must equal true so the prim path method is on by default
                const bool val{ true };
                nodeObj.iNode->createAttribute(nodeObj, "inputs:usePath", Type(BaseDataType::eBool), &val, nullptr,
                                               kAttributePortType_Input, kExtendedAttributeType_Regular, nullptr);
            }
            return true;
        }
        return false;
    }
};

REGISTER_OGN_NODE()

}
}
}
