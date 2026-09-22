// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Api.h"
#include "ValueModelHelper.h"

#include <memory>
#include <utility>
#include <vector>

OMNIUI_NAMESPACE_OPEN_SCOPE

class RadioButton;

/**
 * @brief Radio Collection is a class that groups RadioButtons and coordinates their state.
 *
 * It makes sure that the choice is mutually exclusive, it means when the user selects a radio button, any previously
 * selected radio button in the same collection becomes deselected.
 *
 * @see RadioButton
 */
class OMNIUI_CLASS_API RadioCollection : public ValueModelHelper
{

public:
    OMNIUI_API
    ~RadioCollection();

    // We need it to make sure it's created as a shared pointer.
    template <typename... Args>
    static std::shared_ptr<RadioCollection> create(Args&&... args)
    {
        /* make_shared doesn't work because the constructor is protected: */
        /* auto ptr = std::make_shared<This>(std::forward<Args>(args)...); */
        /* TODO: Find the way to use make_shared */
        return std::shared_ptr<RadioCollection>{ new RadioCollection{ std::forward<Args>(args)... } };
    }

    /**
     * @brief Called by the model when the model value is changed. The class should react to the changes.
     *
     * Reimplemented from ValueModelHelper
     */
    OMNIUI_API
    void onModelUpdated() override;

protected:
    /**
     * @brief Constructs RadioCollection
     */
    OMNIUI_API
    RadioCollection(const std::shared_ptr<AbstractValueModel>& model);

private:
    friend class RadioButton;

    /**
     * @brief this methods add a radio button to the collection, generally it is called directly by the button itself
     * when the collection is setup on the button
     */
    OMNIUI_API
    void _addRadioButton(const std::shared_ptr<RadioButton>& button);

    /**
     * @brief Called then the user clicks one of the buttons in this collection.
     */
    OMNIUI_API
    void _clicked(const RadioButton* button);

    // The list of the radio button that are part of this collection.
    //
    // RadioButton keeps the shared pointer to this collection, and here the collection keeps the pointer to the
    // RadioButton. To avoid circular dependency, we use weak pointers from this side because of the Python API. We
    // never require the user to keep a Python object and do all the work that is related to the object's life. It means
    // the user can create UI like this, and the created objects will not be immediately removed with Python garbage
    // collector:
    //
    //    with ui.HStack():
    //        ui.Label("Hello")
    //        ui.Label("World")
    //
    // The RadioCollection is not a widget, and to make sure the collection will not be removed right after it's
    // created, we use shared pointers in RadioButtons and not here, which makes them the owners of the collection.
    std::vector<std::weak_ptr<RadioButton>> m_radioButtons;
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
