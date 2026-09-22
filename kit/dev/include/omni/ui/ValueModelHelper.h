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

#include <cstdint>
#include <memory>

OMNIUI_NAMESPACE_OPEN_SCOPE

class AbstractValueModel;

/**
 * @brief The ValueModelHelper class provides the basic functionality for value widget classes.
 *
 * ValueModelHelper class is the base class for every standard widget that uses a AbstractValueModel.
 * ValueModelHelper is an abstract class and itself cannot be instantiated. It provides a standard interface for
 * interoperating with models.
 */
class OMNIUI_CLASS_API ValueModelHelper
{
public:
    OMNIUI_API
    virtual ~ValueModelHelper();

    /**
     * @brief Called by the model when the model value is changed. The class should react to the changes.
     */
    OMNIUI_API
    virtual void onModelUpdated() = 0;

    /**
     * @brief Set the current model.
     */
    OMNIUI_API
    virtual void setModel(const std::shared_ptr<AbstractValueModel>& model);

    /**
     * @brief Returns the current model.
     */
    OMNIUI_API
    virtual const std::shared_ptr<AbstractValueModel>& getModel() const;

protected:
    OMNIUI_API
    ValueModelHelper(const std::shared_ptr<AbstractValueModel>& model);

private:
    std::shared_ptr<AbstractValueModel> m_model = {};
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
