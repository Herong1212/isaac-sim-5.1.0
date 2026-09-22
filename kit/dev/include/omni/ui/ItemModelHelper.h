// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "AbstractItemModel.h"

#include <memory>

OMNIUI_NAMESPACE_OPEN_SCOPE

class AbstractItemModel;

/**
 * @brief The ItemModelHelper class provides the basic functionality for item widget classes.
 *
 * TODO: It's very similar to ValueModelHelper. We need to template it. It's not templated now because we need a good
 * solution for pybind11. Pybind11 doesn't like templated classes.
 */
class OMNIUI_CLASS_API ItemModelHelper
{
public:
    OMNIUI_API
    virtual ~ItemModelHelper();

    /**
     * @brief Called by the model when the model value is changed. The class should react to the changes.
     *
     * @param item The item in the model that is changed. If it's NULL, the root is chaged.
     */
    OMNIUI_API
    virtual void onModelUpdated(const std::shared_ptr<const AbstractItemModel::AbstractItem>& item) = 0;

    /**
     * @brief Set the current model.
     */
    OMNIUI_API
    virtual void setModel(const std::shared_ptr<AbstractItemModel>& model);

    /**
     * @brief Returns the current model.
     */
    OMNIUI_API
    virtual const std::shared_ptr<AbstractItemModel>& getModel() const;

protected:
    OMNIUI_API
    ItemModelHelper(const std::shared_ptr<AbstractItemModel>& model);

private:
    std::shared_ptr<AbstractItemModel> m_model = {};
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
