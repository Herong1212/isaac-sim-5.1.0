// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include <omni/ui/scene/Object.h>
#include <omni/ui/scene/TransformBasis.h>
#include <usdrt/scenegraph/usd/sdf/path.h>
#include <usdrt/scenegraph/usd/usd/prim.h>

OMNIUI_SCENE_NAMESPACE_OPEN_SCOPE

class XRPrimPathTransformBasisPrivate;

class OMNIUI_SCENE_CLASS_API XRPrimPathTransformBasis : public TransformBasis
{
    OMNIUI_SCENE_OBJECT(XRPrimPathTransformBasis);

public:
    OMNIUI_SCENE_API
    XRPrimPathTransformBasis(const std::string& primPath);

    OMNIUI_SCENE_API
    Matrix44 getMatrix() override;

    [[nodiscard]] usdrt::SdfPath getParentPath() const;

private:
    std::shared_ptr<XRPrimPathTransformBasisPrivate> m_private;

    bool checkPrim();
};

OMNIUI_SCENE_NAMESPACE_CLOSE_SCOPE
