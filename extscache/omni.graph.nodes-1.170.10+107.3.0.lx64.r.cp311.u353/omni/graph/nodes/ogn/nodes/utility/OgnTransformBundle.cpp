// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnTransformBundleDatabase.h>

#include "Transform.h"

class OgnTransformBundle
{
public:
    static bool compute(OgnTransformBundleDatabase& db)
    {
        auto& context = db.abi_context();
        const auto* const iContext = context.iContext;

        ConstBundleHandle inputBundleHandle = db.inputs.input().abi_bundleHandle();
        BundleHandle outputBundleHandle = db.outputs.output().abi_bundleHandle();

        iContext->clearBundleContents(context, outputBundleHandle);
        iContext->copyBundleContentsInto(context, outputBundleHandle, inputBundleHandle);

        const matrix4d transform = db.inputs.transform();
        transformPrim(context, outputBundleHandle, transform);

        return true;
    }
};

REGISTER_OGN_NODE()
