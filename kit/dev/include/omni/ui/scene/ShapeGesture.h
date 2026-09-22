// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "AbstractGesture.h"
#include "AbstractShape.h"

#include <unordered_set>

OMNIUI_SCENE_NAMESPACE_OPEN_SCOPE

/**
 * @brief The base class for the gestures to provides a way to capture mouse
 * events in 3d scene.
 */
class OMNIUI_SCENE_CLASS_API ShapeGesture : public AbstractGesture
{
public:
    OMNIUI_SCENE_API
    ~ShapeGesture() override;

    /**
     * @brief Called by scene to process the mouse inputs and do intersections
     * with shapes. It can be an entry point to simulate the mouse input.
     *
     * @todo We probably don't need projection-view here. We can get it from
     * manager.
     */
    OMNIUI_SCENE_API
    void dispatchInput(const MouseInput& input,
                       const Matrix44& projection,
                       const Matrix44& view,
                       const Vector2& frameSize) override;

    /**
     * @brief Returns the relevant shape driving the gesture.
     */
    OMNIUI_SCENE_API
    const AbstractShape* getSender() const override;

    OMNIUI_SCENE_API
    const GesturePayload* getGesturePayload() const override;

    OMNIUI_SCENE_API
    const GesturePayload* getGesturePayload(GestureState state) const override;

    OMNIUI_SCENE_API
    virtual const MouseInput& getRawInput() const;

protected:
    friend class AbstractShape;

    OMNIUI_SCENE_API
    ShapeGesture();

    // Last mouse event.
    MouseInput m_input;

    // Last frame size
    Vector2 m_frameSize;

private:
    void _assignItem(AbstractShape* item);
    void _dischargeItem(AbstractShape* item);

    AbstractShape* m_currentShape = nullptr;

    std::unordered_set<AbstractShape*> m_items;
};

OMNIUI_SCENE_NAMESPACE_CLOSE_SCOPE
