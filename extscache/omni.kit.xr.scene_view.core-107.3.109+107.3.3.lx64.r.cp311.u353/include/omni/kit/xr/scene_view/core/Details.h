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

#include <omni/ui/scene/Math.h>
#include <usdrt/scenegraph/usd/sdf/path.h>

#define OMNI_KIT_XR_SCENEVIEW_CORE_NAMESPACE_OPEN                                                                      \
    namespace omni                                                                                                     \
    {                                                                                                                  \
    namespace kit                                                                                                      \
    {                                                                                                                  \
    namespace xr                                                                                                       \
    {                                                                                                                  \
    namespace scene_view                                                                                               \
    {                                                                                                                  \
    namespace core                                                                                                     \
    {

#define OMNI_KIT_XR_SCENEVIEW_CORE_NAMESPACE_CLOSE                                                                     \
    }                                                                                                                  \
    }                                                                                                                  \
    }                                                                                                                  \
    }                                                                                                                  \
    }

namespace omni::ui::scene
{
class DrawBuffer;
}

namespace details
{
usdrt::SdfPath _getBufferPath(const omni::ui::scene::DrawBuffer* buffer, const usdrt::SdfPath& basePath);


template <typename T>
T ConvertUiMatrixTo(const omni::ui::scene::Matrix44& m)
{
    return { m[0][0], m[0][1], m[0][2], m[0][3], m[1][0], m[1][1], m[1][2], m[1][3],
             m[2][0], m[2][1], m[2][2], m[2][3], m[3][0], m[3][1], m[3][2], m[3][3] };
}
}
