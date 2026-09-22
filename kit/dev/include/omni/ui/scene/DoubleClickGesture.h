// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "ClickGesture.h"
#include "Object.h"

#include <functional>

OMNIUI_SCENE_NAMESPACE_OPEN_SCOPE

/**
 * @brief The gesture that provides a way to capture double clicks.
 */
class OMNIUI_SCENE_CLASS_API DoubleClickGesture : public ClickGesture
{
    OMNIUI_GESTURE_OBJECT(DoubleClickGesture)

public:
    OMNIUI_SCENE_API
    ~DoubleClickGesture();

    /**
     * @brief Called before processing to determine the state of the gesture.
     */
    OMNIUI_SCENE_API
    void preProcess(const Matrix44& projection, const Matrix44& view) override;

protected:
    /**
     * @brief Construct the gesture to track double clicks
     *
     * @param onEnded Called when the user double clicked
     */
    OMNIUI_SCENE_API
    DoubleClickGesture(std::function<void(AbstractShape const*)> onEnded = nullptr);
};

OMNIUI_SCENE_NAMESPACE_CLOSE_SCOPE
