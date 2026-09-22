// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Widget.h"

#include <functional>

OMNIUI_NAMESPACE_OPEN_SCOPE

/**
 * @brief The InvisibleButton widget provides a transparent command button.
 */
class OMNIUI_CLASS_API InvisibleButton : public Widget
{
    OMNIUI_OBJECT(InvisibleButton)

public:
    OMNIUI_API
    ~InvisibleButton() override;

    /**
     * @brief Sets the function that will be called when when the button is activated (i.e., pressed down then released
     * while the mouse cursor is inside the button).
     */
    OMNIUI_CALLBACK(Clicked, void);

protected:
    /**
     * Constructor.
     */
    OMNIUI_API
    InvisibleButton();

    /**
     * @brief Reimplemented the rendering code of the widget.
     *
     * @see Widget::_drawContent
     */
    OMNIUI_API
    void _drawContent(float elapsedTime) override;

private:
    /**
     * @brief Called then the user clicks this button.
     */
    OMNIUI_API
    virtual void _clicked();

    std::function<void()> m_clickedFn;
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
