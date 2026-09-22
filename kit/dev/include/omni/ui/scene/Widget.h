// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Rectangle.h"

#include <cstdint>
#include <memory>
#include <vector>

OMNIUI_NAMESPACE_OPEN_SCOPE
class Frame;
OMNIUI_NAMESPACE_CLOSE_SCOPE

OMNIUI_SCENE_NAMESPACE_OPEN_SCOPE

class WindowPassThroughInputGesture;

/**
 * @brief The shape that contains the omni.ui widgets. It automatically creates
 * IAppWindow and transfers its content to the texture of the rectangle. It
 * interacts with the mouse and sends the mouse events to the underlying window,
 * so interacting with the UI on this rectangle is smooth for the user.
 */
class OMNIUI_SCENE_CLASS_API Widget : public Rectangle
{
    OMNIUI_SCENE_OBJECT(Widget);

public:
    enum class FillPolicy : uint8_t
    {
        eStretch = 0,
        ePreserveAspectFit,
        ePreserveAspectCrop
    };

    enum class UpdatePolicy : uint8_t
    {
        eOnDemand = 0,
        eAlways,
        eOnMouseHovered
    };

    OMNIUI_SCENE_API
    virtual ~Widget();

    /**
     * @brief Return the main frame of the widget.
     */
    OMNIUI_SCENE_API
    const std::shared_ptr<omni::ui::Frame>& getFrame();

    /**
     * @brief Rebuild and recapture the widgets at the next frame. If `frame` has `build_fn`, it will also be called.
     */
    OMNIUI_SCENE_API
    void invalidate();

    /**
     * @brief Define what happens when the source image has a different size than the item.
     */
    OMNIUI_PROPERTY(FillPolicy,
                    fillPolicy,
                    DEFAULT,
                    FillPolicy::ePreserveAspectFit,
                    READ,
                    getFillPolicy,
                    WRITE,
                    setFillPolicy,
                    PROTECTED,
                    NOTIFY,
                    _setFillPolicyChangedFn);

    /**
     * @brief Define when to redraw the widget.
     */
    OMNIUI_PROPERTY(UpdatePolicy,
                    updatePolicy,
                    DEFAULT,
                    UpdatePolicy::eOnMouseHovered,
                    READ,
                    getUpdatePolicy,
                    WRITE,
                    setUpdatePolicy,
                    PROTECTED,
                    NOTIFY,
                    _setUpdatePolicyChangedFn);

    /**
     * @brief The resolution scale of the widget.
     */
    OMNIUI_PROPERTY(float, resolutionScale, DEFAULT, 1.0f, READ, getResolutionScale, WRITE, setResolutionScale);

    /**
     * @brief The resolution of the widget framebuffer.
     */
    OMNIUI_PROPERTY(uint32_t, resolutionWidth, DEFAULT, 0, READ, getResolutionWidth, WRITE, setResolutionWidth);

    /**
     * @brief The resolution of the widget framebuffer.
     */
    OMNIUI_PROPERTY(uint32_t, resolutionHeight, DEFAULT, 0, READ, getResolutionHeight, WRITE, setResolutionHeight);

protected:
    /**
     * @brief Created an empty image
     */
    OMNIUI_SCENE_API
    Widget(Float width = 1.0, Float height = 1.0);

    OMNIUI_SCENE_API
    void _preDrawContent(
        const MouseInput& input, const Matrix44& projection, const Matrix44& view, float width, float height) override;

    OMNIUI_SCENE_API
    void _drawContent(const Matrix44& projection, const Matrix44& view) override;

    // Recursively subdivide the poly
    void _subdividePoly(size_t index, uint16_t levels);

    void _rebuildCache() override;

    void _validateImageProvider();

    float _computeResolutionWidth() const;
    float _computeResolutionHeight() const;

private:
    std::vector<Vector2> m_cachedUvs;

    // Widget resolution
    uint32_t m_imageWidth = 0;
    uint32_t m_imageHeight = 0;

    // How many frames since last invalidate
    uint32_t m_framesCounter = 0;

    // Gesture and Image Provider shared_ptr to use it as a gesture
    std::shared_ptr<WindowPassThroughInputGesture> m_inputGesture;
};

OMNIUI_SCENE_NAMESPACE_CLOSE_SCOPE
