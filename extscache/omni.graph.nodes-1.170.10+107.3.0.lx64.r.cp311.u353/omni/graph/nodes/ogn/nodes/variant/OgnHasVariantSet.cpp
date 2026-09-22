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

#include "PrimCommon.h"

#include <carb/logging/Log.h>

#include <omni/usd/UsdContext.h>

#include <OgnHasVariantSetDatabase.h>

namespace omni::graph::nodes
{
class OgnHasVariantSet
{
public:
    static bool compute(OgnHasVariantSetDatabase& db)
    {
        try
        {
            pxr::UsdPrim prim = tryGetTargetPrim(db, db.inputs.prim(), "prim");

            pxr::UsdVariantSets variantSets = prim.GetVariantSets();
            db.outputs.exists() = variantSets.HasVariantSet(db.tokenToString(db.inputs.variantSetName()));
            return true;
        }
        catch (const warning& e)
        {
            db.logWarning(e.what());
        }
        // LCOV_EXCL_START
        catch (const std::exception& e)
        {
            db.logError(e.what());
        }
        // LCOV_EXCL_STOP

        db.outputs.exists() = false;
        return false;
    }
};

REGISTER_OGN_NODE()

} // namespace omni::graph::nodes
