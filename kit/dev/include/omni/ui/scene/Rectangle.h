// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "AbstractShape.h"
#include "Math.h"
#include "Object.h"

#include <array>
#include <memory>
#include <vector>

OMNIUI_SCENE_NAMESPACE_OPEN_SCOPE

class OMNIUI_SCENE_CLASS_API Rectangle : public AbstractShape
{
    OMNIUI_SCENE_OBJECT(Rectangle);

public:
    class RectangleGesturePayload : public AbstractGesture::GesturePayload
    {
    public:
        Float s = 0.0;
        Float t = 0.0;

        Float movedS = 0.0;
        Float movedT = 0.0;
        Vector3 moved = Vector3{ 0.0 };
    };

    OMNIUI_SCENE_API
    virtual ~Rectangle();

    OMNIUI_SCENE_API
    void intersect(const Vector3 origin,
                   const Vector3 direction,
                   const Vector2 mouse,
                   const Matrix44& projection,
                   const Matrix44& view,
                   GestureState state) override;

    /**
     * @brief Contains all the information about the intersection
     */
    OMNIUI_SCENE_API
    const RectangleGesturePayload* getGesturePayload() const override;

    /**
     * @brief Contains all the information about the intersection at the specific state
     */
    OMNIUI_SCENE_API
    const RectangleGesturePayload* getGesturePayload(GestureState state) const override;

    /**
     * @brief The distance in pixels from mouse pointer to the shape for the intersection.
     */
    OMNIUI_SCENE_API
    Float getIntersectionDistance() const override;

    /**
     * @brief The size of the rectangle
     */
    OMNIUI_PROPERTY(Float, width, READ, getWidth, WRITE, setWidth, PROTECTED, NOTIFY, _setWidthChangedFn);

    /**
     * @brief The size of the rectangle
     */
    OMNIUI_PROPERTY(Float, height, READ, getHeight, WRITE, setHeight, PROTECTED, NOTIFY, _setHeightChangedFn);

    /**
     * @brief The thickness of the line
     */
    OMNIUI_PROPERTY(
        float, thickness, DEFAULT, 1.0, READ, getThickness, WRITE, setThickness, PROTECTED, NOTIFY, _setThicknessChangedFn);

    /**
     * @brief The thickness of the line for the intersection
     */
    OMNIUI_PROPERTY(float,
                    intersectionThickness,
                    DEFAULT,
                    0.0,
                    READ,
                    getIntersectionThickness,
                    WRITE,
                    setIntersectionThickness,
                    PROTECTED,
                    NOTIFY,
                    _setIntersectionThicknessChangedFn);

    /**
     * @brief The color of the line
     */
    OMNIUI_PROPERTY(
        Color4, color, DEFAULT, Color4{ 1.0 }, READ, getColor, WRITE, setColor, PROTECTED, NOTIFY, _setColorChangedFn);

    /**
     * @brief When true, it's a line. When false it's a mesh.
     */
    OMNIUI_PROPERTY(
        bool, wireframe, DEFAULT, false, READ, isWireframe, WRITE, setWireframe, PROTECTED, NOTIFY, _setWireframeChangedFn);

    /**
     * @brief The axis the rectangle is perpendicular to
     */
    OMNIUI_PROPERTY(uint8_t, axis, DEFAULT, 2, READ, getAxis, WRITE, setAxis, PROTECTED, NOTIFY, _setAxisChangedFn);

protected:
    /**
     * @brief Construct a rectangle with predefined size.
     *
     * @param width The size of the rectangle
     * @param height The size of the rectangle
     */
    OMNIUI_SCENE_API
    Rectangle(Float width = 1.0, Float height = 1.0);

    OMNIUI_SCENE_API
    void _drawContent(const Matrix44& projection, const Matrix44& view) override;

    void _dirtyCache();
    virtual void _rebuildCache();

    std::unique_ptr<RectangleGesturePayload> m_lastGesturePayload;
    std::array<std::unique_ptr<RectangleGesturePayload>, static_cast<uint32_t>(GestureState::eCount)> m_itersections;

    // Cache to avoid computation every frame
    std::vector<Vector3> m_cachedPoints;
    std::vector<Color4> m_cachedColors;
    std::vector<uint32_t> m_cachedVertexIndices;
    std::vector<uint32_t> m_cachedVertexCounts;
    std::vector<float> m_cachedThicknesses;
    bool m_cacheIsDirty = true;

    bool m_intersectionThicknessExplicitlyChanged = false;
};

OMNIUI_SCENE_NAMESPACE_CLOSE_SCOPE
