// Copyright (c) 2020-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BezierCurve.h"
#include "Circle.h"
#include "Ellipse.h"
#include "Line.h"
#include "Rectangle.h"
#include "Triangle.h"

#include <algorithm>
#include <memory>
#include <utility>

OMNIUI_NAMESPACE_OPEN_SCOPE

/**
 * @brief The free widget is the widget that is independent of the layout. It means it is stuck to other widgets.
 * When initializing, it's necessary to provide two widgets, and the shape is drawn from one widget position to
 * the another.
 */
template <typename T>
class OMNIUI_CLASS_API FreeShape : public T
{
    /**
     * @brief Reimplemented the method to indicate the width hint that represents the preferred size of the widget.
     * It always returns 0 because FreeShape is layout-free.
     */
    OMNIUI_API
    void setComputedContentWidth(float height) override
    {
        // This Widget doesn't modify the layout as it's a free-floating shape.
        T::setComputedContentWidth(0.0f);
    }

    /**
     * @brief Reimplemented the method to indicate the height hint that represents the preferred size of the widget.
     * It always returns 0 because FreeShape is layout-free.
     */
    OMNIUI_API
    void setComputedContentHeight(float height) override
    {
        // This Widget doesn't modify the layout as it's a free-floating shape.
        T::setComputedContentHeight(0.0f);
    }

protected:
    /**
     * @brief Initialize the the shape with bounds limited to the positions of the given widgets.
     *
     * @param start The bound corder is in the center of this given widget.
     * @param end The bound corder is in the center of this given widget.
     */
    OMNIUI_API
    FreeShape(std::shared_ptr<Widget> start, std::shared_ptr<Widget> end)
        : m_startPointWidget{ start }, m_endPointWidget{ end }
    {
        m_bbox.min[0] = 0.0f;
        m_bbox.min[1] = 0.0f;
        m_bbox.max[0] = 0.0f;
        m_bbox.max[1] = 0.0f;
    }

    /**
     * @brief Reimplemented the rendering code of the shape.
     *
     * @see Widget::_drawContent
     */
    OMNIUI_API
    void _drawContent(float elapsedTime) override
    {
        auto startPointWidget = m_startPointWidget.lock();
        auto endPointWidget = m_endPointWidget.lock();
        if (!startPointWidget || !endPointWidget)
        {
            return;
        }

        // Shape bound corners. 0.5 to have the point in the middle of the widget.
        float startX = startPointWidget->getScreenPositionX() + startPointWidget->getComputedWidth() * 0.5f;
        float startY = startPointWidget->getScreenPositionY() + startPointWidget->getComputedHeight() * 0.5f;
        float endX = endPointWidget->getScreenPositionX() + endPointWidget->getComputedWidth() * 0.5f;
        float endY = endPointWidget->getScreenPositionY() + endPointWidget->getComputedHeight() * 0.5f;

        m_bbox.min[0] = std::min(startX, endX) - this->getScreenPositionX();
        m_bbox.min[1] = std::min(startY, endY) - this->getScreenPositionY();
        m_bbox.max[0] = std::max(startX, endX) - this->getScreenPositionX();
        m_bbox.max[1] = std::max(startY, endY) - this->getScreenPositionY();

        // Cache these for use in other methods
        this->m_startPoint = { startX, startY };
        this->m_shapeSize = { endX - startX, endY - startY };

        this->_drawShapeShadow(elapsedTime, startX, startY, this->m_shapeSize.x, this->m_shapeSize.y);
        this->_drawShape(elapsedTime, startX, startY, this->m_shapeSize.x, this->m_shapeSize.y);
    }

    OMNIUI_API
    Widget::BoundingBox _getInteractionBBox() const override
    {
        return m_bbox;
    }

    // Weak pointers to the widgets the shape should stick to.
    std::weak_ptr<Widget> m_startPointWidget;
    std::weak_ptr<Widget> m_endPointWidget;
    // Track our bounding box for mouse events, because we set computed width/height to zero.
    Widget::BoundingBox m_bbox;
};

#define _OMNIUI_DEFINE_FREE_SHAPE(name, parent)                                                                        \
    class name : public FreeShape<parent>                                                                              \
    {                                                                                                                  \
        OMNIUI_OBJECT(name)                                                                                            \
                                                                                                                       \
    protected:                                                                                                         \
        OMNIUI_API                                                                                                     \
        name(std::shared_ptr<Widget> start, std::shared_ptr<Widget> end)                                               \
            : FreeShape<parent>{ std::move(start), std::move(end) }                                                    \
        {                                                                                                              \
        }                                                                                                              \
    }

_OMNIUI_DEFINE_FREE_SHAPE(FreeBezierCurve, BezierCurve);
_OMNIUI_DEFINE_FREE_SHAPE(FreeCircle, Circle);
_OMNIUI_DEFINE_FREE_SHAPE(FreeEllipse, Ellipse);
_OMNIUI_DEFINE_FREE_SHAPE(FreeLine, Line);
_OMNIUI_DEFINE_FREE_SHAPE(FreeRectangle, Rectangle);
_OMNIUI_DEFINE_FREE_SHAPE(FreeTriangle, Triangle);

#undef _OMNIUI_DEFINE_FREE_SHAPE

OMNIUI_NAMESPACE_CLOSE_SCOPE
