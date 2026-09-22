// Copyright (c) 2021-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Object.h"
#include "ShapeGesture.h"

#include <chrono>
#include <functional>

OMNIUI_SCENE_NAMESPACE_OPEN_SCOPE

/**
 * @brief The gesture that provides a way to capture click mouse event.
 */
class OMNIUI_SCENE_CLASS_API ClickGesture : public ShapeGesture
{
    OMNIUI_GESTURE_OBJECT(ClickGesture)

public:
    OMNIUI_SCENE_API
    ~ClickGesture();

    /**
     * @brief Called before processing to determine the state of the gesture.
     */
    OMNIUI_SCENE_API
    void preProcess(const Matrix44& projection, const Matrix44& view) override;

    /**
     * @brief Process the gesture and call callbacks if necessary.
     */
    OMNIUI_SCENE_API
    void process() override;

    /**
     * @brief Called if the callback is not set when the user releases the mouse
     * button.
     */
    OMNIUI_SCENE_API
    virtual void onEnded();

    /**
     * @brief Set the internal state of the gesture. It's the way to cancel,
     * prevent, or restore the gesture.
     */
    OMNIUI_SCENE_API
    virtual void setState(GestureState state);

    /**
     * @brief The mouse button this gesture is watching.
     */
    OMNIUI_PROPERTY(uint32_t, mouseButton, DEFAULT, 0, READ, getMouseButton, WRITE, setMouseButton);

    /**
     * @brief The modifier that should be pressed to trigger this gesture.
     */
    OMNIUI_PROPERTY(uint32_t, modifiers, DEFAULT, UINT32_MAX, READ, getModifiers, WRITE, setModifiers);

    /**
     * @brief Called when the user releases the button.
     */
    OMNIUI_CALLBACK(OnEnded, void, AbstractShape const*);

protected:
    // We need this delay to be able to finish double click if it exists
    static constexpr int64_t kGestureWaitForEnd = 100;

    /**
     * @brief Constructs an gesture to track when the user clicked the mouse.
     *
     * @param onEnded Function that is called when the user clicked the mouse
     * button.
     */
    OMNIUI_SCENE_API
    ClickGesture(std::function<void(AbstractShape const*)> onEnded = nullptr);

    /**
     * @brief The core implementation of preProcess to specify the number of clicks to use.
     *
     * @param nClicks The number of clicks (single / double) this gesture represents.
     */
    OMNIUI_SCENE_API
    void clickPreProcess(const Matrix44& projection, const Matrix44& view, uint32_t nClicks);

    Vector3 m_itemLastPoint = Vector3{ 0.0 };
    Vector3 m_rayLastPoint = Vector3{ 0.0 };

    // We need it because the gesture is triggered with a delay.
    std::chrono::steady_clock::time_point m_startedAt;

    // Flag that indicates the state when the gesture is about to ended.
    bool m_readyForEnd = false;
};

OMNIUI_SCENE_NAMESPACE_CLOSE_SCOPE
