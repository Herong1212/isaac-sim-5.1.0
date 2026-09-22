// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "FontHelper.h"
#include "MenuItem.h"

#include <string>

OMNIUI_NAMESPACE_OPEN_SCOPE

/**
 * @brief The Separator class provides blank space.
 *
 * Normally, it's used to create separator line in the UI elements
 */
class OMNIUI_CLASS_API Separator : public MenuItem, public FontHelper
{
    OMNIUI_OBJECT(Separator)

public:
    OMNIUI_API
    ~Separator() override;


    /**
     * @brief It's called when the style is changed. It should be propagated to children to make the style cached and
     * available to children.
     */
    OMNIUI_API
    void cascadeStyle() override;

protected:
    /**
     * @brief Construct Separator
     */
    OMNIUI_API
    Separator(const std::string& text = "");

    /**
     * @brief Reimplemented the rendering code of the widget.
     *
     * @see Widget::_drawContent
     */
    OMNIUI_API
    void _drawContent(float elapsedTime) override;

private:
    void _drawContentCompatibility(float elapsedTime);

    /**
     * @brief Resolves padding from style and from the underlying draw system.
     */
    void _resolvePaddingCompatibility(float& paddingX, float& paddingY) const;
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
