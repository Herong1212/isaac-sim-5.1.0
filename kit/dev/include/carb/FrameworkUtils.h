// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include "Framework.h"
#include "extras/Path.h"

#include <string>
#include <unordered_set>
#include <vector>

namespace carb
{
/**
 * Get all registered plugins and collect folders they are located in.
 */
inline std::unordered_set<std::string> getPluginFolders()
{
    Framework* framework = carb::getFramework();
    std::vector<PluginDesc> plugins(framework->getPluginCount());
    framework->getPlugins(plugins.data());
    std::unordered_set<std::string> folders;
    for (const auto& desc : plugins)
    {
        extras::Path p(desc.libPath);
        const std::string& folder = p.getParent();
        if (!folder.empty())
        {
            folders.insert(folder);
        }
    }
    return folders;
}
} // namespace carb
