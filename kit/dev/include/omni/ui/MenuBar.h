// Copyright (c) 2020-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Menu.h"

OMNIUI_NAMESPACE_OPEN_SCOPE

/**
 * @brief The MenuBar class provides a MenuBar at the top of the Window, could also be the MainMenuBar of the MainWindow
 *
 * it can only contain Menu, at the moment there is no way to remove item appart from clearing it all together
 */
class OMNIUI_CLASS_API MenuBar : public Menu
{
    OMNIUI_OBJECT(MenuBar)

public:
    OMNIUI_API
    ~MenuBar() override;

protected:
    /**
     * @brief Construct MenuBar
     */
    OMNIUI_API
    MenuBar(bool mainMenuBar = false);

    /**
     * @brief Reimplemented the rendering code of the widget.
     *
     * Draw the content.
     *
     * @see Widget::_drawContent
     */
    OMNIUI_API
    void _drawContent(float elapsedTime) override;

private:
    void _drawContentCompatibility(float elapsedTime);

    bool m_mainMenuBar = { false };
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
