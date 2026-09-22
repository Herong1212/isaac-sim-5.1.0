// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <imgui/imgui.h>

#include "StyleProperties.h"
#include "Frame.h"
#include "Widget.h"

#include <cstdint>

OMNIUI_NAMESPACE_OPEN_SCOPE

struct ShapeStyleSnapshot;

/**
 * @brief The Shape widget provides a base class for all the Shape Widget
 * currently implemented are Rectangle, Circle, Triangle, Line
 * TODO: those need to have a special draw override to deal with intersection better
 */
class OMNIUI_CLASS_API Shape : public Widget
{
    OMNIUI_OBJECT(Shape)

public:
    OMNIUI_API
    ~Shape() override;

    /**
     * @brief Determines which style entry the shape should use for the background. It's very useful when we need to use
     * a custom color. For example, when we draw the triangle for a collapsable frame, we use "color" instead of
     * "background_color".
     */
    OMNIUI_PROPERTY(StyleColorProperty,
                    backgroundColorProperty,
                    DEFAULT,
                    StyleColorProperty::eBackgroundColor,
                    READ,
                    getBackgroundColorProperty,
                    WRITE,
                    setBackgroundColorProperty);

    /**
     * @brief Determines which style entry the shape should use for the border color.
     */
    OMNIUI_PROPERTY(StyleColorProperty,
                    borderColorProperty,
                    DEFAULT,
                    StyleColorProperty::eBorderColor,
                    READ,
                    getBorderColorProperty,
                    WRITE,
                    setBorderColorProperty);

    /**
     * @brief Determines which style entry the shape should use for the shadow color.
     */
    OMNIUI_PROPERTY(StyleColorProperty,
                    shadowColorProperty,
                    DEFAULT,
                    StyleColorProperty::eShadowColor,
                    READ,
                    getShadowColorProperty,
                    WRITE,
                    setShadowColorProperty);

protected:
    OMNIUI_API
    Shape();

    OMNIUI_API
    void _drawContent(float elapsedTime) override;

    OMNIUI_API
    void _drawShapeShadow(float elapsedTime, float x, float y, float width, float height);

    virtual void _drawShape(float elapsedTime, float x, float y, float width, float height){}
    virtual void _drawShadow(
        float elapsedTime,
        float x,
        float y,
        float width,
        float height,
        uint32_t shadowColor,
        float dpiScale,
        ImVec2 shadowOffset,
        float shadowThickness,
        uint32_t shadowFlag){}

    /**
     * @brief Segment-circle intersection.
     * Follows closely https://stackoverflow.com/questions/1073336/circle-line-segment-collision-detection-algorithm
     *
     * @param p1 start of line
     * @param p2 end of line
     * @param center center of circle
     * @param r radius
     * @return true intersects
     * @return false doesn't intersect
     */
    static bool _intersects(float p1X, float p1Y, float p2X, float p2Y, float centerX, float centerY, float r);

    ImVec2 m_startPoint;
    ImVec2 m_shapeSize;
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
