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

#include <memory>
#include <string>

OMNIUI_NAMESPACE_OPEN_SCOPE

/**
 * @brief The MenuItemCollection is the menu that unchecks children when one of
 * them is checked
 */
class OMNIUI_CLASS_API MenuItemCollection : public Menu
{
    OMNIUI_OBJECT(MenuItemCollection)

public:
    OMNIUI_API
    ~MenuItemCollection() override;

    /**
     * @brief Adds the menu. We subscribe to the `checked` changes and uncheck
     * others.
     */
    void addChild(std::shared_ptr<Widget> widget) override;

protected:
    /**
     * @brief Construct MenuItemCollection
     */
    OMNIUI_API
    MenuItemCollection(const std::string& text = "");
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
