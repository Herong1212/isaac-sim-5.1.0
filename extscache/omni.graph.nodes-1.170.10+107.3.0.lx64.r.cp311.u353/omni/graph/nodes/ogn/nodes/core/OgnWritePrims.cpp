// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

/*
  _____   ______  _____   _____   ______  _____         _______  ______  _____
 |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
 | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
 | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
 | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
 |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/

 OgnWritePrims is deprecated. Use WritePrimsV2 instead.

 OgnWritePrims always writes back to the original sourcePrimPath from input bundle.
 The successor OgnWritePrimsV2 removed this feedback loop. Target(s) is always required to write prims to.
 This old OgnWritePrims version is kept for backward compatibility.
*/

#include "OgnWritePrimsDatabase.h"
#include "WritePrimCommon.h"
#include "SpanUtils.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnWritePrims
{
    static size_t getConnectedPrimCount(OgnWritePrimsDatabase& db)
    {
        GraphContextObj const& contextObj = db.abi_context();
        NodeObj const& nodeObj = db.abi_node();

        NodeContextHandle const nodeHandle = nodeObj.nodeContextHandle;
        NameToken const primsToken = inputs::primsBundle.token();
        return contextObj.iContext->getInputTargetCount(contextObj, nodeHandle, primsToken, db.getInstanceIndex());
    }

public:
    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        ogn::OmniGraphDatabase::logWarning(nodeObj, "WritePrim node is deprecated, use WritePrimV2 instead");
    }

    static bool compute(OgnWritePrimsDatabase& db)
    {
        auto result = WritePrimResult::None;

        // Since the bundle input allows multiple connections, we need to collect all of them
        size_t const connectedPrimCount = getConnectedPrimCount(db);

        // Even when we have no connected prims, we still return true, because the node *did* compute, and execOut
        // attribute will be set.
        if (connectedPrimCount > 0)
        {
            auto handler = [&db, &result](gsl::span<ConstBundleHandle> connectedBundleHandles)
            {
                GraphContextObj const& contextObj = db.abi_context();
                NodeObj const& nodeObj = db.abi_node();

                NodeContextHandle const nodeHandle = nodeObj.nodeContextHandle;
                NameToken const primsToken = inputs::primsBundle.token();

                bool const usdWriteBack = db.inputs.usdWriteBack();
                ogn::const_string const attrPattern = db.inputs.attrNamesToExport();
                ogn::const_string const pathPattern = db.inputs.pathPattern();
                ogn::const_string const typePattern = db.inputs.typePattern();

                WritePrimMatchers const matchers{ attrPattern, pathPattern, typePattern };

                contextObj.iContext->getInputTargets(contextObj, nodeHandle, primsToken,
                                                     (omni::fabric::PathC*)(connectedBundleHandles.data()),
                                                     db.getInstanceIndex());

                // Write back all bundles
                WritePrimDiagnostics diagnostics;

                for (ConstBundleHandle const& bundleHandle : connectedBundleHandles)
                {
                    WritePrimResult const subResult = writeBundleHierarchyToPrims(
                        contextObj, nodeObj, diagnostics, bundleHandle, matchers, usdWriteBack);

                    mergeWritePrimResult(result, subResult);
                }

                // Report skipped invalid bundles
                mergeWritePrimResult(result, diagnostics.report(contextObj, nodeObj));
            };

            withStackScopeBuffer<ConstBundleHandle>(connectedPrimCount, handler);
        }

        auto const ok = result != WritePrimResult::Fail;

        if (ok)
        {
            db.outputs.execOut() = kExecutionAttributeStateEnabled;
        }

        return ok;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
