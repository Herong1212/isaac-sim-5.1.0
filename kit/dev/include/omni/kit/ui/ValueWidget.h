// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "ModelWidget.h"

#include <functional>
#include <memory>
#include <string>
#include <utility>

namespace omni
{
namespace kit
{
namespace ui
{

template <class T>
class OMNI_KIT_UI_CLASS_API ValueWidget : public ModelWidget
{
public:
    ValueWidget(T value) : ModelWidget(), m_value(value)
    {
        this->text = text;
        auto model = createSimpleValueModel(Model::getNodeTypeForT<T>());
        model->setValue(m_modelRoot.c_str(), "", value);
        setModel(std::move(model), "");
    }

    void setValue(const T& v)
    {
        _setValue(v);
    }

    const T& getValue() const
    {
        return m_value;
    }

    bool isValueAmbiguous() const
    {
        return m_valueAmbiguous;
    }

    void setValueAmbiguous(bool state)
    {
        ModelChangeInfo info = { m_sender, false };

        m_valueAmbiguous = state;
        if (m_valueAmbiguous)
            m_model->setType(m_modelRoot.c_str(), "", ModelNodeType::eUnknown, info);
    }

    bool leftHanded;

    std::string text;

    std::function<void(const T&)> onChangedFn;

    std::function<void(const ValueWidget<T>*)> onRightClickFn;

    std::shared_ptr<Widget> tooltip;


protected:
    virtual void _onValueChange(){};

    void rightClickHandler()
    {
        carb::imgui::ImGui* imgui = getImGui();
        if (imgui->isItemHovered(0) && imgui->isMouseReleased(1))
        {
            if (onRightClickFn)
                onRightClickFn(this);
        }
    }

    void _setValue(const T& value, bool transient = false, bool force = false)
    {
        if (!almostEqual(value, m_value) || force || m_valueAmbiguous)
        {
            m_value = value;
            m_valueAmbiguous = false;
            this->_onValueChange();
            ModelChangeInfo info = { m_sender, transient };
            m_model->setValue(m_modelRoot.c_str(), "", m_value, 0, m_isTimeSampled, m_timeCode, info);
            if (onChangedFn)
                onChangedFn(m_value);
        }
    }

    virtual void _onModelValueChange() override
    {
        ModelValue<T> newValue = m_model->getValue<T>(m_modelRoot.c_str(), "", 0, m_isTimeSampled, m_timeCode);

        if (!almostEqual(newValue.value, m_value) || newValue.ambiguous != m_valueAmbiguous)
        {
            m_value = newValue.value;
            m_valueAmbiguous = newValue.ambiguous;
            this->_onValueChange();
            if (onChangedFn)
                onChangedFn(m_value);
        }
    }

    T m_value;
    bool m_valueAmbiguous;
};

template <class T>
class OMNI_KIT_UI_CLASS_API SimpleValueWidget : public ValueWidget<T>
{
public:
    SimpleValueWidget(const std::string& text, T value) : ValueWidget<T>(value), leftHanded(false), m_wasActive(false)
    {
        this->text = text;
    }

    bool leftHanded;

    std::string text;

    std::shared_ptr<Widget> tooltip;

    void draw(float dt) override
    {
        this->_processModelEvents();

        if (!this->m_visible)
            return;

        carb::imgui::ImGui* imgui = getImGui();
        carb::imgui::Font* font = this->m_font;

        if (font)
            imgui->pushFont(font);

        imgui->pushItemFlag(carb::imgui::kItemFlagDisabled, !this->m_enabled);
        imgui->pushStyleVarFloat(carb::imgui::StyleVar::eAlpha, this->m_enabled ? 1.0f : .6f);


        if (this->leftHanded)
        {
            _drawWidget(imgui, dt);
            _drawText(imgui);
        }
        else
        {
            _drawText(imgui);
            _drawWidget(imgui, dt);
        }

        this->rightClickHandler();

        imgui->popStyleVar();
        imgui->popItemFlag();

        if (font)
            imgui->popFont();
    }

protected:
    virtual bool _drawImGuiWidget(carb::imgui::ImGui* imgui, T& value) = 0;

    virtual bool _isTransientChangeSupported() const
    {
        return true;
    }

private:
    void _drawWidget(carb::imgui::ImGui* imgui, float dt)
    {
        if (this->m_label.empty())
        {
            this->m_label = "##hidelabel";
            this->m_label += this->m_uniqueId;
        }

        if (m_wasActive)
        {
            processImguiInputEvents();
        }

        predictActiveProcessImguiInput(this->m_label.c_str());

        float uiScale = imgui->getWindowDpiScale();
        imgui->pushItemWidth(calculateWidth(this->width) * uiScale);

        const bool isTransientChangeSupported = this->_isTransientChangeSupported();

        T v = this->getValue();
        if (this->_drawImGuiWidget(imgui, v))
        {
            this->_setValue(v, isTransientChangeSupported);
        }

        imgui->popItemWidth();

        m_wasActive = imgui->isItemActive();

        if (m_wasActive || this->m_isDragging)
            this->m_isDragging = handleDragging(this->m_draggedFn, Widget::shared_from_this(), this->m_isDragging);

        // Just finished editing -> force notify value with undo
        if (imgui->isItemDeactivatedAfterEdit() && isTransientChangeSupported)
        {
            this->_setValue(v, false, true);
        }

        if (this->tooltip && imgui->isItemHovered(0))
        {
            imgui->beginTooltip();
            this->tooltip->draw(dt);
            imgui->endTooltip();
        }
    }

    void _drawText(carb::imgui::ImGui* imgui)
    {
        if (this->text.size() > 0)
        {
            if (this->leftHanded)
                imgui->sameLine();
            imgui->text(this->text.c_str());
            if (!this->leftHanded)
                imgui->sameLine();
        }
    }

    bool m_wasActive;
};

}
}
}
