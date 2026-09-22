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

#include "Details.h"

#include <omni/ui/scene/DrawBuffer.h>
#include <pxr/base/gf/matrix4d.h>
#include <pxr/pxr.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usd/stage.h>
#include <usdrt/scenegraph/base/gf/matrix4d.h>
#include <usdrt/scenegraph/usd/usd/prim.h>

PXR_NS::GfMatrix4d ConvertUiToPxrMatrix4d(const omni::ui::scene::Matrix44& m);

namespace omni::usd
{
class UsdContext;
}

OMNI_KIT_XR_SCENEVIEW_CORE_NAMESPACE_OPEN

class XRUiDrawItemBase
{
public:
    explicit XRUiDrawItemBase(const omni::ui::scene::DrawBuffer* drawBuffer,
                              usd::UsdContext* context,
                              const PXR_NS::UsdStageWeakPtr& stage,
                              XRDrawSystem& drawSystem);
    virtual ~XRUiDrawItemBase();

    [[nodiscard]] bool isValid(const usdrt::SdfPath& path) const;
    virtual void initialize(usd::UsdContext* context, const PXR_NS::UsdStageWeakPtr& stage);
    virtual void update(usd::UsdContext* context, const PXR_NS::UsdStageWeakPtr& stage);

    void refreshTransform();

    void makeVisible() const;

    [[nodiscard]] const PXR_NS::UsdPrim& getPrim() const
    {
        return m_prim;
    }

    [[nodiscard]] const usdrt::UsdPrim& getRtPrim() const
    {
        return m_rtPrim;
    }

    [[nodiscard]] const omni::ui::scene::DrawBuffer* getDrawBuffer() const
    {
        return m_drawBuffer;
    }

    [[nodiscard]] omni::ui::scene::DrawBuffer::DirtyBits currentDirtyBits() const
    {
        return m_dirtyBits;
    }

protected:
    XRDrawSystem& m_drawSystem;

private:
    const omni::ui::scene::DrawBuffer* m_drawBuffer;
    omni::ui::scene::DrawBuffer::DirtyBits m_dirtyBits;
    PXR_NS::UsdPrim m_prim;
    usdrt::UsdPrim m_rtPrim;
    bool m_needsAllDirtyBits;
    usdrt::GfMatrix4d m_prevLocalTransform;

    bool _checkRtPrim();
    void _updateTransform(const usdrt::GfMatrix4d& targetStageTransform);
};

OMNI_KIT_XR_SCENEVIEW_CORE_NAMESPACE_CLOSE
