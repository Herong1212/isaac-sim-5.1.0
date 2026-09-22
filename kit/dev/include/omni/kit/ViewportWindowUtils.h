// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/dictionary/IDictionary.h>
#include <carb/dictionary/DictionaryUtils.h>
#include <carb/events/EventsUtils.h>

#include <omni/kit/IViewport.h>
#include <omni/kit/ViewportTypes.h>

namespace omni
{
namespace kit
{

/**
 * Gets payload from UiDrawEventStream.
 *
 * @param e Event from UiDrawEventStream.
 * @param viewMtx The array to hold the data of view matrix. It must be big enough to store 16 doubles.
 * @param projMtx The array to hold the data of projection matrix. It must be big enough to store 16 doubles.
 * @param viewportRect The Float4 to hold the data of viewport rect.
 */
inline void getUiDrawPayloadFromEvent(const carb::events::IEvent& e,
                                      double* viewMtx,
                                      double* projMtx,
                                      carb::Float4& viewportRect)
{
    auto events = carb::dictionary::getCachedDictionaryInterface();

    for (size_t i = 0; i < 16; i++)
    {
        static const std::string viewMatrixPrefix("viewMatrix/");
        viewMtx[i] = events->get<double>(e.payload, (viewMatrixPrefix + std::to_string(i)).c_str());
    }

    for (size_t i = 0; i < 16; i++)
    {
        static const std::string projMatrixPrefix("projMatrix/");
        projMtx[i] = events->get<double>(e.payload, (projMatrixPrefix + std::to_string(i)).c_str());
    }

    for (size_t i = 0; i < 4; i++)
    {
        static const std::string viewportRectPrefix("viewportRect/");
        (&viewportRect.x)[i] = events->get<float>(e.payload, (viewportRectPrefix + std::to_string(i)).c_str());
    }
}

/**
 * Gets the default (first) IViewportWindow
 *
 * @return Default IViewportWindow
 */
inline IViewportWindow* getDefaultViewportWindow()
{
    auto viewport = carb::getCachedInterface<omni::kit::IViewport>();
    if (viewport)
    {
        return viewport->getViewportWindow(nullptr);
    }
    return nullptr;
}
}
}
