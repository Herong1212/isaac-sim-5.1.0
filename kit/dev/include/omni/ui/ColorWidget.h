// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "ItemModelHelper.h"
#include "Widget.h"

#include <omni/ui/windowmanager/IWindowCallbackManager.h>

#include <memory>

OMNIUI_NAMESPACE_OPEN_SCOPE

class AbstractItemModel;

/**
 * @brief The ColorWidget widget is a button that displays the color from the item model and can open a picker window to
 * change the color.
 */
class OMNIUI_CLASS_API ColorWidget : public Widget, public ItemModelHelper
{
    OMNIUI_OBJECT(ColorWidget)

public:
    OMNIUI_API
    ~ColorWidget() override;

    /**
     * @brief Reimplemented the method to indicate the width hint that represents the preferred size of the widget.
     * Currently this widget can't be smaller than the size of the ColorWidget square.
     *
     * @see Widget::setComputedContentWidth
     */
    OMNIUI_API
    void setComputedContentWidth(float width) override;

    /**
     * @brief Reimplemented the method to indicate the height hint that represents the preferred size of the widget.
     * Currently this widget can't be smaller than the size of the ColorWidget square.
     *
     * @see Widget::setComputedContentHeight
     */
    OMNIUI_API
    void setComputedContentHeight(float height) override;

    /**
     * @brief Reimplemented the method from ItemModelHelper that is called when the model is changed.
     *
     * @param item The item in the model that is changed. If it's NULL, the root is chaged.
     */
    OMNIUI_API
    void onModelUpdated(const std::shared_ptr<const AbstractItemModel::AbstractItem>& item) override;

    // TODO: Color space
    // TODO: Property for float/int
    // TODO: Property for disabling color picker
    // TODO: Property for disabling popup
    // TODO: Property for disabling alpha

protected:
    /**
     * @brief Construct ColorWidget
     */
    OMNIUI_API
    ColorWidget(const std::shared_ptr<AbstractItemModel>& model = {});

    /**
     * @brief Reimplemented the rendering code of the widget.
     *
     * @see Widget::_drawContent
     */
    OMNIUI_API
    void _drawContent(float elapsedTime) override;

private:
    void _drawPopup(float elapsedTime, ImGuiColorEditFlags flags);
    void _removePopup();

    // The cached state of the ColorWidget allows to query the model only if it's changed.
    size_t m_componentsNumber = 0;
    float m_colorBuffer[4] = { 0.0f };
    bool m_popupUsed = false;

    // The pointer to the popup window in the underlying windowing system.
    omni::ui::windowmanager::IWindowCallbackPtr m_uiWindow;
    omni::kit::IAppWindow* m_appWindow = nullptr;
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
