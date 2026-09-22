// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Api.h"
#include "Math.h"

#include <omni/ui/Property.h>

#include <memory>
#include <string>

namespace omni
{
namespace kit
{
namespace renderer
{
struct IRendererTextureOptions;
}
}
}

OMNIUI_NAMESPACE_OPEN_SCOPE
class ImageProvider;
OMNIUI_NAMESPACE_CLOSE_SCOPE

OMNIUI_SCENE_NAMESPACE_OPEN_SCOPE

class SceneView;

/**
 * @brief The helper class for the widgets that are working with image, e.g. sc.Image and sc.TexturedMesh.
 */
class OMNIUI_SCENE_CLASS_API ImageHelper
{
public:
    static omni::kit::renderer::IRendererTextureOptions getTextureOptions();

    virtual std::shared_ptr<ImageProvider> const& getImageProvider() const = 0;
    virtual void setImageProvider(std::shared_ptr<ImageProvider> const& v) = 0;

    virtual std::string const& getSourceUrl() const = 0;
    virtual void setSourceUrl(const std::string& url) = 0;

    /**
     * @brief The resolution for rasterization of svg and for ImageProvider.
     */
    OMNIUI_PROPERTY(uint32_t, imageWidth, DEFAULT, 0, READ, getImageWidth, WRITE, setImageWidth);

    /**
     * @brief The resolution of rasterization of svg and for ImageProvider.
     */
    OMNIUI_PROPERTY(uint32_t, imageHeight, DEFAULT, 0, READ, getImageHeight, WRITE, setImageHeight);

protected:
    ImageHelper();
    virtual ~ImageHelper();

    void _prepareDrawContent(
        const Matrix44& projection, const Matrix44& view, bool& cacheIsDirty, void** texture, void** resource);

    void _sourceUrlChanged();
    void _providerChanged();

    float _computeImageWidth(float width) const;
    float _computeImageHeight(float height) const;

    // Image resolution cache
    float m_textureWidthCache = 0.0f;
    float m_textureHeightCache = 0.0f;

private:
    bool hasTextureOptions() const;

    std::unique_ptr<omni::kit::renderer::IRendererTextureOptions> m_textureOptions;
    bool m_sourceUrlChangedInternallyFlag = false;
};

OMNIUI_SCENE_NAMESPACE_CLOSE_SCOPE
