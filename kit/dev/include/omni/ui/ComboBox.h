// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "FontHelper.h"
#include "ItemModelHelper.h"
#include "Object.h"
#include "Property.h"
#include "Widget.h"

#include <cstdint>
#include <memory>
#include <string>
#include <vector>

OMNIUI_NAMESPACE_OPEN_SCOPE

class AbstractItemModel;

/**
 * @brief The ComboBox widget is a combined button and a drop-down list.
 *
 * A combo box is a selection widget that displays the current item and can pop up a list of selectable items.
 *
 * The ComboBox is implemented using the model-view pattern. The model is the central component of this system. The root
 * of the item model should contain the index of currently selected items, and the children of the root include all the
 * items of the combo box.
 */
class OMNIUI_CLASS_API ComboBox : public Widget, public ItemModelHelper, public FontHelper
{
    OMNIUI_OBJECT(ComboBox)

public:
    OMNIUI_API
    ~ComboBox() override;

    /**
     * @brief Reimplemented the method to indicate the width hint that represents the preferred size of the widget.
     * Currently this widget can't be smaller than the size of the ComboBox square.
     *
     * @see Widget::setComputedContentWidth
     */
    OMNIUI_API
    void setComputedContentWidth(float width) override;

    /**
     * @brief Reimplemented the method to indicate the height hint that represents the preferred size of the widget.
     * Currently this widget can't be smaller than the size of the ComboBox square.
     *
     * @see Widget::setComputedContentHeight
     */
    OMNIUI_API
    void setComputedContentHeight(float height) override;

    /**
     * @brief Reimplemented. Something happened with the style or with the parent style. We need to update the saved
     * font.
     */
    OMNIUI_API
    void onStyleUpdated() override;

    /**
     * @brief Reimplemented the method from ItemModelHelper that is called when the model is changed.
     *
     * @param item The item in the model that is changed. If it's NULL, the root is chaged.
     */
    OMNIUI_API
    void onModelUpdated(const std::shared_ptr<const AbstractItemModel::AbstractItem>& item) override;

    /**
     * @brief Determines if it's necessary to hide the text of the ComboBox.
     */
    OMNIUI_PROPERTY(bool, arrowOnly, DEFAULT, false, READ, isArrowOnly, WRITE, setArrowOnly);

protected:
    /**
     * @brief Construct ComboBox
     *
     * @param model The model that determines if the button is checked.
     */
    OMNIUI_API
    ComboBox(const std::shared_ptr<AbstractItemModel>& model = {});

    /**
     * @brief Reimplemented the rendering code of the widget.
     *
     * @see Widget::_drawContent
     */
    OMNIUI_API
    void _drawContent(float elapsedTime) override;

private:
    // The cached state of the ComboBox allows to query the model only if it's changed.
    int64_t m_currentIndex = 0;
    std::vector<std::string> m_items;
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
