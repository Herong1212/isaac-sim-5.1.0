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

#include <memory>
#include <vector>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines the base class for layouts.
 */

class OMNI_KIT_UI_CLASS_API ContainerBase : public Widget
{
public:
    OMNI_KIT_UI_API ContainerBase();

    OMNI_KIT_UI_API ~ContainerBase() override;

    OMNI_KIT_UI_API void draw(float elapsedTime) override;

protected:
    carb::Float2 m_childSpacing = { 8, 4 };
    std::vector<std::shared_ptr<Widget>> m_children;

    OMNI_KIT_UI_API virtual size_t _getChildCount() const;

    OMNI_KIT_UI_API virtual std::shared_ptr<Widget> _getChildAt(size_t index) const;

    OMNI_KIT_UI_API virtual std::shared_ptr<Widget> _addChild(std::shared_ptr<Widget> widget);

    OMNI_KIT_UI_API virtual void _removeChild(std::shared_ptr<Widget> widget);

    OMNI_KIT_UI_API virtual void _clear();
};

class OMNI_KIT_UI_CLASS_API Container : public ContainerBase
{
public:
    OMNI_KIT_UI_API Container();

    OMNI_KIT_UI_API ~Container() override;

    OMNI_KIT_UI_API virtual carb::Float2 getChildSpacing() const;

    OMNI_KIT_UI_API virtual void setChildSpacing(const carb::Float2& childSpacing);

    OMNI_KIT_UI_API size_t getChildCount() const;

    OMNI_KIT_UI_API std::shared_ptr<Widget> getChildAt(size_t index) const;

    OMNI_KIT_UI_API std::shared_ptr<Widget> addChild(std::shared_ptr<Widget> widget);

    template <class T, typename... Args>
    std::shared_ptr<T> emplaceChild(Args&&... args);

    OMNI_KIT_UI_API void removeChild(std::shared_ptr<Widget> widget);

    OMNI_KIT_UI_API void clear();

protected:
    carb::Float2 m_childSpacing = { 8, 4 };
};

}
}
}
