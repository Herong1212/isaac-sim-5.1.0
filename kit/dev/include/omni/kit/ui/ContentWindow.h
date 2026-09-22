// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Widget.h"

#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a ContentWindow.
 */
class OMNI_KIT_UI_CLASS_API ContentWindow : public Widget
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ContentWindow);

    /**
     * Constructor.
     */
    OMNI_KIT_UI_API ContentWindow();

    OMNI_KIT_UI_API ContentWindow(uint32_t width, uint32_t height);

    /**
     * Destructor.
     */
    OMNI_KIT_UI_API ~ContentWindow() override;

    /**
     * @see Widget::getType
     */
    OMNI_KIT_UI_API WidgetType getType() override;

    /**
     * @see Widget::draw
     */
    void draw(float elapsedTime) override;

    OMNI_KIT_UI_API virtual void refresh();

    OMNI_KIT_UI_API virtual void getSelectedTreeNodePaths(std::string* protocol,
                                                          std::string* realUrl,
                                                          std::string* contentUrl);
    OMNI_KIT_UI_API virtual void getSelectedFileNodePaths(std::string* protocol,
                                                          std::string* realUrl,
                                                          std::string* contentUrl);

    OMNI_KIT_UI_API virtual void setFilter(const std::string& regex);

    OMNI_KIT_UI_API virtual void navigateTo(const std::string& path);

protected:
    ContentWindowWidget* m_contentWindowWidget = nullptr;
};
}
}
}
