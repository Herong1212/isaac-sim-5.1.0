// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Container.h"
#include "Model.h"

#include <memory>
#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 *
 */
class OMNI_KIT_UI_CLASS_API ModelWidget : public ContainerBase
{
public:
    OMNI_KIT_UI_API ModelWidget();
    OMNI_KIT_UI_API virtual ~ModelWidget();


    OMNI_KIT_UI_API void setModel(const std::shared_ptr<Model>& model,
                                  const std::string& root = "",
                                  bool isTimeSampled = false,
                                  double timeCode = -1.0);

    std::shared_ptr<Model> getModel() const
    {
        return m_model;
    }

    const std::string& getModelRoot() const
    {
        return m_modelRoot;
    }

    const carb::events::IEventStream* getModelStream() const
    {
        return m_modelEvents.get();
    }

    void draw(float dt) override
    {
        this->_processModelEvents();
        ContainerBase::draw(dt);
    }

    bool isTimeSampled() const
    {
        return m_isTimeSampled;
    }

    double getTimeCode() const
    {
        return m_timeCode;
    }

    void processModelEvents()
    {
        _processModelEvents();
    }

protected:
    bool _processModelEvents();

    virtual void _onModelValueChange()
    {
    }

    virtual void _onModelNodeChange()
    {
    }

    carb::events::IEventStreamPtr m_modelEvents;
    std::shared_ptr<Model> m_model;
    std::string m_modelRoot;
    bool m_isTimeSampled{ false };
    double m_timeCode{ -1.0 };
    carb::events::SenderId m_sender;
};
}
}
}
