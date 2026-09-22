// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Button.h"
#include "ValueModelHelper.h"

#include <memory>

OMNIUI_NAMESPACE_OPEN_SCOPE

/**
 * @brief ToolButton is functionally similar to Button, but provides a model that determines if the button is checked.
 * This button toggles between checked (on) and unchecked (off) when the user clicks it.
 */
class OMNIUI_CLASS_API ToolButton : public Button, public ValueModelHelper
{
    OMNIUI_OBJECT(ToolButton)

public:
    OMNIUI_API
    ~ToolButton() override;

    /**
     * @brief Reimplemented from ValueModelHelper. It's called when the model is changed.
     */
    OMNIUI_API
    void onModelUpdated() override;

protected:
    /**
     * @brief Construct a checkable button with the model. If the bodel is not provided, then the default model is
     * created.
     *
     * @param model The model that determines if the button is checked.
     */
    OMNIUI_API
    ToolButton(const std::shared_ptr<AbstractValueModel>& model = {});

    /**
     * @brief Reimplemented the rendering code of the widget.
     *
     * @see Widget::_drawContent
     */
    OMNIUI_API
    void _drawContent(float elapsedTime) override;

private:
    /**
     * @brief Reimplemented from InvisibleButton. Called then the user clicks this button. We don't use `m_clickedFn`
     * because the user can set it. If we are using it in our internal code and the user overrides it, the behavior of
     * the button will be changed.
     */
    OMNIUI_API
    void _clicked() override;

    // Flag to call onModelUpdated
    bool m_modelUpdated = false;
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
