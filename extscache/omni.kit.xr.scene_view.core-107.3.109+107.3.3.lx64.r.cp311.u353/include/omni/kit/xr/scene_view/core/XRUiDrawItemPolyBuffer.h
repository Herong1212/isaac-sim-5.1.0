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

#include "XRUiDrawItemBase.h"

#include <pxr/usd/usdGeom/mesh.h>
#include <pxr/usd/usdShade/material.h>
#include <pxr/usd/usdShade/shader.h>

OMNI_KIT_XR_SCENEVIEW_CORE_NAMESPACE_OPEN

class XRDrawSystem;

class XRUiDrawItemPolyBuffer : public XRUiDrawItemBase
{
public:
    explicit XRUiDrawItemPolyBuffer(const omni::ui::scene::DrawBuffer* drawBuffer,
                                    usd::UsdContext* context,
                                    const PXR_NS::UsdStageWeakPtr& stage,
                                    XRDrawSystem& drawSystem);
    ~XRUiDrawItemPolyBuffer() override;

    void initialize(usd::UsdContext* context, const PXR_NS::UsdStageWeakPtr& stage) override;
    void update(usd::UsdContext* context, const PXR_NS::UsdStageWeakPtr& stage) override;

private:
    PXR_NS::UsdGeomMesh m_mesh;
    PXR_NS::UsdShadeMaterial m_material;
    PXR_NS::UsdShadeShader m_shader;
    std::string m_textureUri;
    rtx::resourcemanager::RpResource* m_managedResource = nullptr;
    rtx::resourcemanager::Context* m_resourceManagerContext;
    rtx::resourcemanager::ResourceManager* m_resourceManager;

    std::string _generateTextureUri() const;
    void _updateResourceNames(const scene::DrawBuffer::Polys* polys);
};

OMNI_KIT_XR_SCENEVIEW_CORE_NAMESPACE_CLOSE
