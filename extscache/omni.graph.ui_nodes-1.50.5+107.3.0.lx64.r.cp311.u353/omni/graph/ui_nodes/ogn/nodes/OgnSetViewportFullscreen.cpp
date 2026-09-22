// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "OgnSetViewportFullscreenDatabase.h"

#include <omni/kit/IAppWindow.h>
#include <omni/kit/KitUtils.h>

namespace omni
{
namespace graph
{
namespace ui_nodes
{

class OgnSetViewportFullscreen
{
public:
    static bool compute(OgnSetViewportFullscreenDatabase& db)
    {
        NameToken const mode = db.inputs.mode();
        bool fullscreen = false;
        bool hideUI = false;

        if (mode == OgnSetViewportFullscreenDatabase::tokens.Default)
        {
            fullscreen = false;
            hideUI = false;
        }
        else if (mode == OgnSetViewportFullscreenDatabase::tokens.Fullscreen)
        {
            fullscreen = true;
            hideUI = true;
        }
        else if (mode == OgnSetViewportFullscreenDatabase::tokens.HideUI)
        {
            fullscreen = false;
            hideUI = true;
        }
        else
        {
            CARB_ASSERT(false, "Invalid mode");
        }

        carb::settings::ISettings* settings = omni::kit::getSettings();

        // Only toggle fullscreen on/off when displayModeLock is off.
        if (!settings->get<bool>("/app/window/displayModeLock"))
        {
            setFullscreen(fullscreen);
        }

        settings->set("/app/window/hideUi", hideUI);

        db.outputs.exec() = kExecutionAttributeStateEnabled;

        return true;
    }

private:
    static void setFullscreen(bool fullscreen)
    {
        omni::kit::IAppWindow* appWindow = omni::kit::getDefaultAppWindow();
        CARB_ASSERT(appWindow);
        if (appWindow)
        {
            appWindow->setFullscreen(fullscreen);
        }
    }
};

REGISTER_OGN_NODE()

} // ui
} // graph
} // omni
