// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <imgui/imgui.h>

#include "Frame.h"
#include "ScrollBarPolicy.h"

#include <cstdint>
#include <limits>
#include <memory>

OMNIUI_NAMESPACE_OPEN_SCOPE

struct CanvasFramePrivate;

/**
 * @brief CanvasFrame is a widget that allows the user to pan and zoom its children with a mouse. It has a layout
 * that can be infinitely moved in any direction.
 */
class OMNIUI_CLASS_API CanvasFrame : public Frame
{
    OMNIUI_OBJECT(CanvasFrame)

public:
    OMNIUI_API
    ~CanvasFrame() override;

    /**
     * @brief Reimplemented the method to indicate the width hint that represents the preferred size of the widget.
     *
     * @see Widget::setComputedContentWidth
     */
    OMNIUI_API
    void setComputedContentWidth(float width) override;

    /**
     * @brief Reimplemented the method to indicate the height hint that represents the preferred size of the widget.
     *
     * @see Widget::setComputedContentHeight
     */
    OMNIUI_API
    void setComputedContentHeight(float height) override;

    /**
     * @brief Transforms screen-space X to canvas-space X
     */
    OMNIUI_API
    float screenToCanvasX(float x) const;

    /**
     * @brief Transforms screen-space Y to canvas-space Y
     */
    OMNIUI_API
    float screenToCanvasY(float y) const;

    /**
     * @brief Specify the mouse button and key to pan the canvas.
     */
    OMNIUI_API
    void setPanKeyShortcut(uint32_t mouseButton, carb::input::KeyboardModifierFlags keyFlag);

    /**
     * @brief Specify the mouse button and key to zoom the canvas.
     */
    OMNIUI_API
    void setZoomKeyShortcut(uint32_t mouseButton, carb::input::KeyboardModifierFlags keyFlag);

    /**
     * @brief The horizontal offset of the child item.
     */
    OMNIUI_PROPERTY(float, panX, DEFAULT, 0.0f, READ, getPanX, WRITE, setPanX, NOTIFY, setPanXChangedFn);

    /**
     * @brief The vertical offset of the child item.
     */
    OMNIUI_PROPERTY(float, panY, DEFAULT, 0.0f, READ, getPanY, WRITE, setPanY, NOTIFY, setPanYChangedFn);

    /**
     * @brief The zoom level of the child item.
     */
    OMNIUI_PROPERTY(float, zoom, DEFAULT, 1.0f, READ, getZoom, WRITE, setZoom, NOTIFY, setZoomChangedFn);

    /**
     * @brief The zoom minimum of the child item.
     */
    OMNIUI_PROPERTY(float, zoomMin, DEFAULT, 0.0f, READ, getZoomMin, WRITE, setZoomMin, NOTIFY, setZoomMinChangedFn);

    /**
     * @brief The zoom maximum of the child item.
     */
    OMNIUI_PROPERTY(float, zoomMax, DEFAULT, std::numeric_limits<float>::max(), READ, getZoomMax, WRITE, setZoomMax, NOTIFY, setZoomMaxChangedFn);

    /**
     * @brief When true, zoom is smooth like in Bifrost even if the user is using mouse wheel that doesn't provide
     * smooth scrolling.
     */
    OMNIUI_PROPERTY(bool, smoothZoom, DEFAULT, false, READ, isSmoothZoom, WRITE, setSmoothZoom);

    /**
     * @brief Provides a convenient way to make the content draggable and zoomable.
     */
    OMNIUI_PROPERTY(bool, draggable, DEFAULT, true, READ, isDraggable, WRITE, setDraggable);

    /**
     * @brief This boolean property controls the behavior of CanvasFrame. When
     * set to true, the widget will function in the old way. When set to false,
     * the widget will use a newer and faster implementation. This variable is
     * included as a transition period to ensure that the update does not break
     * any existing functionality. Please be aware that the old behavior may be
     * deprecated in the future, so it is recommended to set this variable to
     * false once you have thoroughly tested the new implementation.
     */
    OMNIUI_PROPERTY(bool,
                    compatibility,
                    DEFAULT,
                    true,
                    READ,
                    isCompatibility,
                    WRITE,
                    setCompatibility,
                    PROTECTED,
                    NOTIFY,
                    _setCompatibilityChangedFn);

protected:
    /**
     * @brief Constructs CanvasFrame
     */
    OMNIUI_API
    CanvasFrame();

    /**
     * @brief Reimplemented the rendering code of the widget.
     *
     * @see Widget::_drawContent
     */
    OMNIUI_API
    void _drawContent(float elapsedTime) override;

    /**
     * @brief Returns true to let the children widgets know they are in scalable
     * environment.
     *
     * @return bool - true
     */
    OMNIUI_API bool _isParentCanvasFrame() const override;


private:
    /**
     * @brief This function contains the drawing code for the old behavior of
     * the widget. It's only called when the 'compatibility' variable is set to
     * true. This function is included as a transition period to ensure that the
     * update does not break any existing functionality. Please be aware that
     * the old behavior may be deprecated in the future.
     */
    void _drawContentCompatibility(float elapsedTime);

    // True when the user pans the child. We need it to know if the user did it on the previous frame to be able to
    // continue panning outside of the widget.
    bool m_panActive = false;

    // That's how the pan is initiated
    uint32_t m_panMouseButton;
    carb::input::KeyboardModifierFlags m_panKeyFlag;

    // That's how the zoom is initiated
    uint32_t m_zoomMouseButton;
    carb::input::KeyboardModifierFlags m_zoomKeyFlag;

    // focus position for mouse move scrolling zoom
    ImVec2 m_focusPosition;

    // flag to show whether the mouse moving zoom is active
    bool m_zoomMoveActive = false;

    // The real zoom, we need it to make the zoom smooth when scrolling with mouse.
    float m_zoomSmooth;

    // Return the zoom with limits cap
    float _getZoom(float zoom);

    std::unique_ptr<CanvasFramePrivate> m_prv;

    // only mouse click inside the CanvasFrame considers the signal of checking the pan and zoom
    bool m_panStarted = false;
    bool m_zoomStarted = false;
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
