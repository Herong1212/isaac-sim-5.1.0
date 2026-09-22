// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Widget.h"

#include <memory>
#include <vector>

OMNIUI_NAMESPACE_OPEN_SCOPE

/**
 * @brief The container is an abstract widget that can hold one or several child widgets.
 *
 * The user is allowed to add or replace child widgets. If the widget has multiple children internally (like Button) and
 * the user doesn't have access to them, it's not necessary to use this class.
 */
class OMNIUI_CLASS_API Container : public Widget
{
public:
    OMNIUI_API
    ~Container() override;

    /**
     * @brief Adds widget to this container in a manner specific to the container. If it's allowed to have one
     * sub-widget only, it will be overwriten.
     */
    virtual void addChild(std::shared_ptr<Widget> widget);

    /**
     * @brief Removes the container items from the container.
     */
    virtual void clear(){}

protected:
    friend class Inspector;

    OMNIUI_API
    Container();

    /**
     * @brief Return the list of children for the Container, only used by Inspector and for debug/inspection
     * perspective.
     */
    OMNIUI_API
    virtual const std::vector<std::shared_ptr<Widget>> _getChildren() const { return {}; }

    class DrawCallData;
    DrawCallData* m_drawCallData = nullptr;
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
