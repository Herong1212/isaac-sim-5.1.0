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
#include "ValueModelHelper.h"

#include <memory>

OMNIUI_NAMESPACE_OPEN_SCOPE

/**
 * @brief A CheckBox is an option button that can be switched on (checked) or off (unchecked). Checkboxes are typically
 * used to represent features in an application that can be enabled or disabled without affecting others.
 *
 * The checkbox is implemented using the model-view pattern. The model is the central component of this system. It is
 * the application's dynamic data structure independent of the widget. It directly manages the data, logic, and rules of
 * the checkbox. If the model is not specified, the simple one is created automatically when the object is constructed.
 */
class OMNIUI_CLASS_API CheckBox : public Widget, public ValueModelHelper, public FontHelper
{
    OMNIUI_OBJECT(CheckBox)

public:
    OMNIUI_API
    ~CheckBox() override;

    /**
     * @brief Reimplemented the method to indicate the width hint that represents the preferred size of the widget.
     * Currently this widget can't be smaller than the size of the checkbox square.
     *
     * @see Widget::setComputedContentWidth
     */
    OMNIUI_API
    void setComputedContentWidth(float width) override;

    /**
     * @brief Reimplemented the method to indicate the height hint that represents the preferred size of the widget.
     * Currently this widget can't be smaller than the size of the checkbox square.
     *
     * @see Widget::setComputedContentHeight
     */
    OMNIUI_API
    void setComputedContentHeight(float height) override;

    /**
     * @brief Reimplemented the method from ValueModelHelper that is called when the model is changed.
     *
     * TODO: We can avoid it if we create templated ValueModelHelper that manages data.
     */
    OMNIUI_API
    void onModelUpdated() override;

    /**
     * @brief Reimplemented. Something happened with the style or with the parent style. We need to gerenerate the
     * cache.
     */
    OMNIUI_API
    void onStyleUpdated() override;

protected:
    /**
     * @brief CheckBox with specified model. If model is not specified, it's using the default one.
     */
    OMNIUI_API
    CheckBox(const std::shared_ptr<AbstractValueModel>& model = {});

    /**
     * @brief Reimplemented the rendering code of the widget.
     *
     * @see Widget::_drawContent
     */
    OMNIUI_API
    void _drawContent(float elapsedTime) override;

private:
    // The state of the checkbox. We need to cache it anyway. Because we can't query the model every frame because the
    // model can be written in python and query filesystem or USD. Of course, it can be cached on the Model level, but
    // it means we ask the user to cache it, which is not preferable. Right now, we allow the model to do very expensive
    // operations.
    bool m_value = false;
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
