// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "AbstractMultiField.h"

#include <memory>

OMNIUI_NAMESPACE_OPEN_SCOPE

/**
 * @brief MultiFloatField is the widget that has a sub widget (FloatField) per model item.
 *
 * It's handy to use it for multi-component data, like for example, float3 or color.
 */
class OMNIUI_CLASS_API MultiFloatField : public AbstractMultiField
{
    OMNIUI_OBJECT(MultiFloatField)

protected:
    /**
     * Constructor.
     */
    OMNIUI_API
    MultiFloatField(const std::shared_ptr<AbstractItemModel>& model = {});

    /**
     * @brief Create the widget with the model provided.
     */
    OMNIUI_API
    std::shared_ptr<Widget> _createField(const std::shared_ptr<AbstractValueModel>& model) override;

    /**
     * @brief Called to assign the new model to the widget created with `_createField`
     */
    OMNIUI_API
    void _setFieldModel(std::shared_ptr<Widget>& widget, const std::shared_ptr<AbstractValueModel>& model) override;
};

/**
 * @brief MultiIntField is the widget that has a sub widget (IntField) per model item.
 *
 * It's handy to use it for multi-component data, like for example, int3.
 */
class OMNIUI_CLASS_API MultiIntField : public AbstractMultiField
{
    OMNIUI_OBJECT(MultiIntField)

protected:
    /**
     * Constructor.
     */
    OMNIUI_API
    MultiIntField(const std::shared_ptr<AbstractItemModel>& model = {});

    /**
     * @brief Create the widget with the model provided.
     */
    OMNIUI_API
    std::shared_ptr<Widget> _createField(const std::shared_ptr<AbstractValueModel>& model) override;

    /**
     * @brief Called to assign the new model to the widget created with `_createField`
     */
    OMNIUI_API
    void _setFieldModel(std::shared_ptr<Widget>& widget, const std::shared_ptr<AbstractValueModel>& model) override;
};

/**
 * @brief MultiStringField is the widget that has a sub widget (StringField) per model item.
 *
 * It's handy to use it for string arrays.
 */
class OMNIUI_CLASS_API MultiStringField : public AbstractMultiField
{
    OMNIUI_OBJECT(MultiStringField)

protected:
    /**
     * Constructor.
     */
    OMNIUI_API
    MultiStringField(const std::shared_ptr<AbstractItemModel>& model = {});

    /**
     * @brief Create the widget with the model provided.
     */
    OMNIUI_API
    std::shared_ptr<Widget> _createField(const std::shared_ptr<AbstractValueModel>& model) override;

    /**
     * @brief Called to assign the new model to the widget created with `_createField`
     */
    OMNIUI_API
    void _setFieldModel(std::shared_ptr<Widget>& widget, const std::shared_ptr<AbstractValueModel>& model) override;
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
