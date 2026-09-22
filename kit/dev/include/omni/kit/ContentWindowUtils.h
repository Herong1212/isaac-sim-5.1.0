// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/InterfaceUtils.h>

#include <omni/kit/IContentUi.h>

namespace omni
{
namespace kit
{

/**
 * Gets the default (first) IContentWindow
 *
 * @return Default IContentWindow
 */
inline IContentWindow* getDefaultContentWindow()
{
    auto contentWindow = carb::getCachedInterface<omni::kit::IContentUi>();
    if (contentWindow)
    {
        return contentWindow->getContentWindow(nullptr);
    }
    return nullptr;
}
}
}
