// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Api.h"
#include "Math.h"

#include <functional>
#include <map>
#include <memory>
#include <string>
#include <unordered_set>
#include <string>
#include <vector>

OMNIUI_SCENE_NAMESPACE_OPEN_SCOPE

class ManipulatorModelHelper;

/**
 * - Bridge to data.
 * - Operates with double and int arrays.
 * - No strings.
 * - No tree, it's a flat list of items.
 * - Manipulator requires the model has specific items.
 */
class OMNIUI_SCENE_CLASS_API AbstractManipulatorModel
{
public:
    class AbstractManipulatorItem
    {
    public:
        virtual ~AbstractManipulatorItem() = default;
    };

    using ItemChangedCallback =
        std::function<void(const AbstractManipulatorModel*, const AbstractManipulatorModel::AbstractManipulatorItem*)>;

    OMNIUI_SCENE_API
    virtual ~AbstractManipulatorModel();

    /**
     * @brief Returns the items that represents the identifier.
     */
    OMNIUI_SCENE_API
    virtual std::shared_ptr<const AbstractManipulatorItem> getItem(const std::string& identifier);

    /**
     * @brief Returns the float values of the item.
     */
    OMNIUI_SCENE_API
    virtual std::vector<Float> getAsFloats(const std::shared_ptr<const AbstractManipulatorItem>& item) = 0;

    /**
     * @brief Returns the int values of the item.
     */
    OMNIUI_SCENE_API
    virtual std::vector<int64_t> getAsInts(const std::shared_ptr<const AbstractManipulatorItem>& item) = 0;

    /**
     * @brief Sets the float values of the item.
     */
    OMNIUI_SCENE_API
    virtual void setFloats(const std::shared_ptr<const AbstractManipulatorItem>& item, std::vector<Float> value) = 0;

    /**
     * @brief Sets the int values of the item.
     */
    OMNIUI_SCENE_API
    virtual void setInts(const std::shared_ptr<const AbstractManipulatorItem>& item, std::vector<int64_t> value) = 0;

    /**
     * @brief Subscribe ManipulatorModelHelper to the changes of the model.
     *
     * We need to use regular pointers because we subscribe in the constructor
     * of the widget and unsubscribe in the destructor. In constructor smart
     * pointers are not available. We also don't allow copy and move of the
     * widget.
     */
    OMNIUI_SCENE_API
    void subscribe(ManipulatorModelHelper* manipulator);

    /**
     * @brief Unsubscribe the ItemModelHelper widget from the changes of the
     * model.
     */
    OMNIUI_SCENE_API
    void unsubscribe(ManipulatorModelHelper* manipulator);

    /**
     * @brief Adds the function that will be called every time the value
     * changes.
     *
     * @return The id of the callback that is used to remove the callback.
     */
    OMNIUI_SCENE_API
    uint32_t addItemChangedFn(ItemChangedCallback&& fn);

    /**
     * @brief Remove the callback by its id.
     *
     * @param id The id that addValueChangedFn returns.
     */
    OMNIUI_SCENE_API
    void removeItemChangedFn(uint32_t id);

protected:
    /**
     * @brief Called when any data of the model is changed. It will notify the subscribed widgets.
     *
     * @param item The item in the model that is changed. If it's NULL, the root is changed.
     */
    OMNIUI_SCENE_API
    void _itemChanged(const std::shared_ptr<const AbstractManipulatorItem>& item);

private:
    // All the widgets who use this model.
    std::unordered_set<ManipulatorModelHelper*> m_manipulators;

    // All the callbacks.
    std::vector<ItemChangedCallback> m_itemChangedCallbacks;

    // If the derived model doesn't want to create new items, the default
    // implementation will do it.
    std::map<std::string, std::shared_ptr<const AbstractManipulatorItem>> m_defaultItems;
};

OMNIUI_SCENE_NAMESPACE_CLOSE_SCOPE
