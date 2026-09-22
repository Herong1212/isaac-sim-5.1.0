// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>
#include <carb/Types.h>

namespace carb
{
namespace scenerenderer    
{
typedef uint32_t PrimitiveListFlags;
}
}

namespace omni
{
namespace renderer
{
typedef uint32_t SimplexBuffer;
typedef uint32_t RenderInstanceBuffer;

struct SimplexPoint
{
    carb::Float3    position;
    uint32_t        color;
    float           width;
};

/// Invalid billboardId
const uint32_t kInvalidBillboardId = 0xFFFFffff;

struct IDebugDraw
{
    CARB_PLUGIN_INTERFACE("omni::renderer::IDebugDraw", 1, 2)

    /// Invalid buffer return value
    enum InvalidBuffer
    {
        eInvalidBuffer = 0
    };

    /// Draw a line - actual implementation
    /// \note Life time of a line is one frame
    ///
    /// \param startPos     Line start position
    /// \param startColor   Line start color in argb format
    /// \param startWidth   Line start width
    /// \param endPos       Line end position
    /// \param endColor     Line end color in argb format
    /// \param endWidth     Line end width
    void(CARB_ABI* internalDrawLine)(const carb::Float3& startPos,
                             uint32_t startColor,
                             float startWidth,
                             const carb::Float3& endPos,
                             uint32_t endColor,
                             float endWidth);

    /// Draw a line without width
    /// \note Life time of a line is one frame
    ///
    /// \param startPos     Line start position
    /// \param startColor   Line start color in argb format    
    /// \param endPos       Line end position
    /// \param endColor     Line end color in argb format    
    void drawLine(const carb::Float3& startPos, uint32_t startColor, const carb::Float3& endPos, uint32_t endColor)
    {
        internalDrawLine(startPos, startColor, 1.0f, endPos, endColor, 1.0f);
    }

    /// Draw a line
    /// \note Life time of a line is one frame
    ///
    /// \param startPos     Line start position
    /// \param startColor   Line start color in argb format
    /// \param startWidth   Line start width
    /// \param endPos       Line end position
    /// \param endColor     Line end color in argb format
    /// \param endWidth     Line end width
    void drawLine(const carb::Float3& startPos, uint32_t startColor, float startWidth, const carb::Float3& endPos, uint32_t endColor, float endWidth)
    {
        internalDrawLine(startPos, startColor, startWidth, endPos, endColor, endWidth);
    }

    /// Draw lines buffer
    /// \note Life time of a line is one frame
    ///
    /// \param pointsBuffer Buffer of points (expected size is 2xnumLines)
    /// \param numLines     Number of lines in the buffer
    void(CARB_ABI* drawLines)(const SimplexPoint* pointsBuffer, uint32_t numLines);

    /// Draw a point
    /// \note Life time of a point is one frame
    ///
    /// \param pointPos     Point position
    /// \param pointColor   Point color in argb format
    /// \param pointWidth   Point width (diameter)
    void(CARB_ABI* internalDrawPoint)(const carb::Float3& pointPos, uint32_t pointColor, float pointWidth);

    /// Draw a point
    /// \note Life time of a point is one frame
    ///
    /// \param pointPos     Point position
    /// \param pointColor   Point color in argb format
    /// \param pointWidth   Point width (diameter)
    void drawPoint(const carb::Float3& pointPos, uint32_t pointColor, float pointWidth = 1.0f)
    {
        internalDrawPoint(pointPos, pointColor, pointWidth);
    }

    /// Draw points buffer
    /// \note Life time of a point is one frame
    ///
    /// \param pointsBuffer Buffer of points (expected size is numPoints)
    /// \param numPoints    Number of points in the buffer
    void(CARB_ABI* drawPoints)(const SimplexPoint* pointsBuffer, uint32_t numPoints);

    /// Draw a sphere - internal implementation
    /// \note Life time of a sphere is one frame
    ///
    /// \param spherePos    Sphere positions
    /// \param sphereRadius Sphere radius
    /// \param sphereColor  Sphere color in argb format
    /// \param lineWidth    Line width
    /// \param tesselation  Sphere tesselation
    void(CARB_ABI* internalDrawSphere)(const carb::Float3& spherePos, float sphereRadius, uint32_t sphereColor, float lineWidth, uint32_t tesselation);

    /// Draw a sphere
    /// \note Life time of a sphere is one frame
    ///
    /// \param spherePos    Sphere positions
    /// \param sphereRadius Sphere radius
    /// \param sphereColor  Sphere color in argb format
    /// \param lineWidth    Line width
    /// \param tesselation  Sphere tesselation
    void drawSphere(const carb::Float3& spherePos, float sphereRadius, uint32_t sphereColor, float lineWidth = 1.0f, uint32_t tesselation = 32)
    {
        internalDrawSphere(spherePos, sphereRadius, sphereColor, lineWidth, tesselation);
    }

    /// Draw a box - internal implementation
    /// \note Life time of a box is one frame
    ///
    /// \param boxPos       Box position
    /// \param boxRotation  Box rotation (quaternion)
    /// \param boxSize      Box size - extent
    /// \param boxColor     Box color in argb format
    /// \param lineWidth    Line width    
    void(CARB_ABI* internalDrawBox)(
        const carb::Float3& boxPos, const carb::Float4& boxRotation, const carb::Float3& boxSize, uint32_t boxColor, float lineWidth);

    /// Draw a box
    /// \note Life time of a box is one frame
    ///
    /// \param boxPos       Box position
    /// \param boxRotation  Box rotation (quaternion)
    /// \param boxSize      Box size - extent
    /// \param boxColor     Box color in argb format
    /// \param lineWidth    Line width
    void drawBox(const carb::Float3& boxPos, const carb::Float4& boxRotation, const carb::Float3& boxSize, uint32_t boxColor, float lineWidth = 1.0f)
    {
        internalDrawBox(boxPos, boxRotation, boxSize, boxColor, lineWidth);
    }

    /// Allocate line buffer
    ///
    /// \param              preallocatedBufferSize preallocated buffer size (number of lines expected)
    /// \returns            Line buffer handle
    SimplexBuffer(CARB_ABI* allocateLineBuffer)(size_t preallocatedBufferSize);

    /// Deallocate line buffer
    ///
    /// \param bufferHandle Line buffer to deallocate
    void(CARB_ABI* deallocateLineBuffer)(SimplexBuffer bufferHandle);

    /// Set line to a buffer
    ///
    /// \param buffer       Line buffer
    /// \param index        Index in buffer (if index is larger then preallocatedBufferSize, size will increase)
    /// \param startPos     Line start position
    /// \param startColor   Line start color in argb format
    /// \param startWidth   Line start width
    /// \param endPos       Line end position
    /// \param endColor     Line end color in argb format
    /// \param endWidth     Line end width
    void(CARB_ABI* internalSetLine)(SimplexBuffer buffer,
                            size_t index,
                            const carb::Float3& startPos,
                            uint32_t startColor,
                            float startWidth,
                            const carb::Float3& endPos,
                            uint32_t endColor,
                            float endWidth);

    /// Set line to a buffer without width
    ///
    /// \param buffer       Line buffer
    /// \param index        Index in buffer (if index is larger then preallocatedBufferSize, size will increase)
    /// \param startPos     Line start position
    /// \param startColor   Line start color in argb format    
    /// \param endPos       Line end position
    /// \param endColor     Line end color in argb format    
    void setLine(SimplexBuffer buffer,
        size_t index,
        const carb::Float3& startPos,
        uint32_t startColor,
        const carb::Float3& endPos,
        uint32_t endColor)
    {
        internalSetLine(buffer, index, startPos, startColor, 1.0f, endPos, endColor, 1.0f);
    }

    /// Set line to a buffer
    ///
    /// \param buffer       Line buffer
    /// \param index        Index in buffer (if index is larger then preallocatedBufferSize, size will increase)
    /// \param startPos     Line start position
    /// \param startColor   Line start color in argb format
    /// \param startWidth   Line start width
    /// \param endPos       Line end position
    /// \param endColor     Line end color in argb format
    /// \param endWidth     Line end width
    void setLine(SimplexBuffer buffer,
        size_t index,
        const carb::Float3& startPos,
        uint32_t startColor,
        float startWidth,
        const carb::Float3& endPos,
        uint32_t endColor,
        float endWidth)
    {
        internalSetLine(buffer, index, startPos, startColor, startWidth, endPos, endColor, endWidth);
    }

    /// Set point within a point buffer
    ///
    /// \param buffer       Point buffer
    /// \param index        Index in buffer (if index is larger than current buffer size, size will increase)
    /// \param position     Point position
    /// \param color        Point color
    /// \param width        Point size
    void(CARB_ABI* setPoint)(SimplexBuffer handle, size_t index, const carb::Float3& position, uint32_t color, float width);

    /// Allocate render instance buffer
    ///
    /// \param handle       Line buffer to instance
    /// \param preallocatedBufferSize preallocated buffer size
    /// \returns            Render instance buffer handle
    RenderInstanceBuffer(CARB_ABI* allocateRenderInstanceBuffer)(SimplexBuffer handle, size_t preallocatedSize);

    /// Update render instance buffer
    ///
    /// \param buffer       Render instance buffer
    /// \param index        Index in buffer (if index is larger then preallocatedBufferSize, size will increase)
    /// \param matrix       Instance transformation matrix - 4x4 matrix - 16 floats
    /// \param color        Instance color, final color is interpolated with PrimitiveVertex.color based on alpha (in
    /// argb format)
    /// \param uid          unique identifier to map PrimitiveListInstance back to prim for picking.
    void(CARB_ABI* internalSetRenderInstance)(RenderInstanceBuffer buffer, size_t index, const float* matrix, uint32_t color, uint32_t uid);

    /// Update render instance buffer without uid
    ///
    /// \param buffer       Render instance buffer
    /// \param index        Index in buffer (if index is larger then preallocatedBufferSize, size will increase)
    /// \param matrix       Instance transformation matrix - 4x4 matrix - 16 floats
    /// \param color        Instance color, final color is interpolated with PrimitiveVertex.color based on alpha (in
    /// argb format)    
    void setRenderInstance(
        RenderInstanceBuffer buffer, size_t index, const float* matrix, uint32_t color)
    {
        internalSetRenderInstance(buffer, index, matrix, color, 0);
    }

    /// Update render instance buffer
    ///
    /// \param buffer       Render instance buffer
    /// \param index        Index in buffer (if index is larger then preallocatedBufferSize, size will increase)
    /// \param matrix       Instance transformation matrix - 4x4 matrix - 16 floats
    /// \param color        Instance color, final color is interpolated with PrimitiveVertex.color based on alpha (in
    /// argb format)
    /// \param uid          unique identifier to map PrimitiveListInstance back to prim for picking.
    void setRenderInstance(
        RenderInstanceBuffer buffer, size_t index, const float* matrix, uint32_t color, uint32_t uid)
    {
        internalSetRenderInstance(buffer, index, matrix, color, uid);
    }

    /// Deallocate render instance buffer
    ///
    /// \param handle       Render instance buffer to deallocate
    void(CARB_ABI* deallocateRenderInstanceBuffer)(RenderInstanceBuffer buffer);

    /// Allocate point buffer
    ///
    /// \param preallocateBufferSize Preallocated buffer size (number of points expected)
    /// \returns            Point buffer handle
    SimplexBuffer(CARB_ABI* allocatePointBuffer)(size_t preallocatedBufferSize);

    /// Deallocate point buffer
    ///
    /// \param bufferHandle Point buffer to deallocate
    void(CARB_ABI* deallocatePointBuffer)(SimplexBuffer bufferHandle);

    /// Allocate line buffer
    ///
    /// \param              preallocatedBufferSize preallocated buffer size (number of lines expected)
    /// \param              flags flags to be used when create primitive list
    /// \returns            Line buffer handle
    SimplexBuffer(CARB_ABI* allocateLineBufferEx)(size_t preallocatedBufferSize,
                                                  carb::scenerenderer::PrimitiveListFlags flags);

    /// Allocate point buffer
    ///
    /// \param preallocateBufferSize Preallocated buffer size (number of points expected)
    /// \param              flags flags to be used when create primitive list 
    /// \returns            Point buffer handle
    SimplexBuffer(CARB_ABI* allocatePointBufferEx)(size_t preallocatedBufferSize,
                                                   carb::scenerenderer::PrimitiveListFlags flags);

    /// Add billboard asset
    /// \note The asset is valid for the whole duration
    ///
    /// \param textureAssetName     Full path to the texture asset
    /// \return Return assetid
    uint32_t (CARB_ABI* addBillboardAsset)(const char* textureAssetName);

    /// Update billboard asset
    ///
    /// \param assetId      AssetId for billboard identification
    /// \param scale        New scale
    /// \isConstantScale    Constant scale hint
    void (CARB_ABI* updateBillboardAsset)(uint32_t assetId, double scale, bool isConstantScale);

    /// Add billboard instance
    ///
    /// \param assetId      AssetId for billboard identification
    /// \param billboardUid BillboardUid - see context get Uid for selection
    /// \param tr           Transformation matrix for the billboard instance, 4x4 float matrix
    /// \return Return id for the current billboard instance
    uint32_t (CARB_ABI* addBillboard)(uint32_t assetId, uint32_t billboardUid, const float* tr);

    /// Update billboard instance
    ///
    /// \param assetId      AssetId for billboard identification
    /// \param billboardId  Billboard id of the instance
    /// \param tr           Transformation matrix for the billboard instancem 4x4 float matrix
    void (CARB_ABI* updateBillboard)(uint32_t assetId, uint32_t billboardId, const float* tr);

    /// Remove billboard instance
    ///
    /// \param assetId      AssetId for billboard identification
    /// \param billboardId  Billboard id of the instance
    /// \return Returns the swapped position, last item of the array is swapped with this Id,
    /// use the returned Id to update the instances in your database
    uint32_t (CARB_ABI* removeBillboard)(uint32_t assetId, uint32_t billboardId);

    /// Clear billboard instances for given asset
    ///
    /// \param assetId      AssetId for billboard identification
    void (CARB_ABI* clearBillboardInstances)(uint32_t assetId);

    /// Remove render instance on given index
    /// 
    /// \param handle       Render instance buffer handle
    /// \param index        Index in the buffer
    bool (CARB_ABI* removeRenderInstance)(omni::renderer::RenderInstanceBuffer handle, size_t index);

    /// Remove debug lines on given range of indices from the vertex array
    ///
    /// \param handle       Render instance buffer handle
    /// \param startIndex   Starting line index in the vertex buffer
    /// \param endIndex     Ending line index in the vertex buffer
    bool (CARB_ABI* removeLines)(omni::renderer::SimplexBuffer handle, size_t startIndex, size_t endIndex);
};

} // namespace renderer
} // namespace omni
