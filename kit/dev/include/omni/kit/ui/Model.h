// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Api.h"
#include "Common.h"

#include <carb/events/IEvents.h>

#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

namespace omni
{


namespace kit
{
namespace ui
{
enum class ModelNodeType
{
    eUnknown,
    eObject,
    eArray,
    eString,
    eBool,
    eNumber
};

enum class ModelEventType
{
    eNodeAdd,
    eNodeRemove,
    eNodeTypeChange,
    eNodeValueChange
};

struct ModelChangeInfo
{
    carb::events::SenderId sender = carb::events::kGlobalSenderId;
    bool transient = false;
};

template <class T>
struct ModelValue
{
    T value;
    bool ambiguous;
};

class OMNI_KIT_UI_CLASS_API Model
{
public:
    Model() = default;

    // PART 1: Get
    OMNI_KIT_UI_API virtual ModelNodeType getType(const char* path, const char* meta = "") = 0;
    OMNI_KIT_UI_API virtual ModelValue<std::string> getValueAsString(
        const char* path, const char* meta = "", size_t index = 0, bool isTimeSampled = false, double time = -1.0) = 0;
    OMNI_KIT_UI_API virtual ModelValue<bool> getValueAsBool(
        const char* path, const char* meta = "", size_t index = 0, bool isTimeSampled = false, double time = -1.0) = 0;
    OMNI_KIT_UI_API virtual ModelValue<double> getValueAsNumber(
        const char* path, const char* meta = "", size_t index = 0, bool isTimeSampled = false, double time = -1.0) = 0;

    virtual size_t getKeyCount(const char* path, const char* meta = "")
    {
        return 0;
    }
    virtual std::string getKey(const char* path, const char* meta, size_t index)
    {
        return "";
    }

    virtual size_t getArraySize(const char* path, const char* meta = "")
    {
        return 0;
    }

    // PART 2: Set
    virtual void beginChangeGroup()
    {
    }
    virtual void endChangeGroup()
    {
    }

    virtual void setType(const char* path, const char* meta, ModelNodeType type, const ModelChangeInfo& info = {})
    {
    }

    OMNI_KIT_UI_API virtual void setValueString(const char* path,
                                                const char* meta,
                                                std::string value,
                                                size_t index = 0,
                                                bool isTimeSampled = false,
                                                double time = -1.0,
                                                const ModelChangeInfo& info = {}) = 0;
    OMNI_KIT_UI_API virtual void setValueBool(const char* path,
                                              const char* meta,
                                              bool value,
                                              size_t index = 0,
                                              bool isTimeSampled = false,
                                              double time = -1.0,
                                              const ModelChangeInfo& info = {}) = 0;
    OMNI_KIT_UI_API virtual void setValueNumber(const char* path,
                                                const char* meta,
                                                double value,
                                                size_t index = 0,
                                                bool isTimeSampled = false,
                                                double time = -1.0,
                                                const ModelChangeInfo& info = {}) = 0;

    OMNI_KIT_UI_API virtual void setArraySize(const char* path,
                                              const char* meta,
                                              size_t size,
                                              bool isTimeSampled = false,
                                              double time = -1.0,
                                              const ModelChangeInfo& info = {})
    {
    }

    // PART 3: signals
    OMNI_KIT_UI_API void signalChange(const char* path, const char* meta, ModelEventType type, const ModelChangeInfo& info);

    virtual void onSubscribeToChange(const char* path, const char* meta, carb::events::IEventStream*)
    {
    }
    virtual void onUnsubscribeToChange(const char* path, const char* meta, carb::events::IEventStream*)
    {
    }


    OMNI_KIT_UI_API void subscribeToChange(const char* path, const char* meta, carb::events::IEventStream*);
    OMNI_KIT_UI_API void unsubscribeToChange(const char* path, const char* meta, carb::events::IEventStream*);

    // HELPERS:
    template <class T>
    OMNI_KIT_UI_API ModelValue<T> getValue(
        const char* path, const char* meta, size_t index = 0, bool isTimeSampled = false, double time = -1.0);

    template <class T>
    OMNI_KIT_UI_API void setValue(const char* path,
                                  const char* meta,
                                  T value,
                                  size_t index = 00,
                                  bool isTimeSampled = false,
                                  double time = -1.0,
                                  const ModelChangeInfo& info = {});


    template <class T>
    OMNI_KIT_UI_API static ModelNodeType getNodeTypeForT();

    OMNI_KIT_UI_API virtual ~Model(){};

private:
    std::unordered_map<std::string, std::vector<carb::events::IEventStream*>> m_pathChangeListeners;
};

template <>
inline ModelValue<bool> Model::getValue(const char* path, const char* meta, size_t index, bool isTimeSampled, double time)
{
    return getValueAsBool(path, meta, index, isTimeSampled, time);
}

template <>
inline ModelValue<std::string> Model::getValue(
    const char* path, const char* meta, size_t index, bool isTimeSampled, double time)
{
    return getValueAsString(path, meta, index, isTimeSampled, time);
}

template <>
inline ModelValue<double> Model::getValue(const char* path, const char* meta, size_t index, bool isTimeSampled, double time)
{
    return getValueAsNumber(path, meta, index, isTimeSampled, time);
}

template <>
inline ModelValue<float> Model::getValue(const char* path, const char* meta, size_t index, bool isTimeSampled, double time)
{
    auto v = getValue<double>(path, meta, index, isTimeSampled, time);
    return { static_cast<float>(v.value), v.ambiguous };
}

template <>
inline ModelValue<int32_t> Model::getValue(const char* path, const char* meta, size_t index, bool isTimeSampled, double time)
{
    auto v = getValue<double>(path, meta, index, isTimeSampled, time);
    return { static_cast<int32_t>(v.value), v.ambiguous };
}

template <>
inline ModelValue<uint32_t> Model::getValue(const char* path, const char* meta, size_t index, bool isTimeSampled, double time)
{
    auto v = getValue<double>(path, meta, index, isTimeSampled, time);
    return { static_cast<uint32_t>(v.value), v.ambiguous };
}

template <>
inline ModelValue<carb::Int2> Model::getValue(const char* path, const char* meta, size_t, bool isTimeSampled, double time)
{
    auto v0 = getValue<int32_t>(path, meta, 0, isTimeSampled, time);
    auto v1 = getValue<int32_t>(path, meta, 1, isTimeSampled, time);
    return { carb::Int2{ v0.value, v1.value }, v0.ambiguous || v1.ambiguous };
}

template <>
inline ModelValue<carb::Double2> Model::getValue(const char* path, const char* meta, size_t, bool isTimeSampled, double time)
{
    auto v0 = getValue<double>(path, meta, 0, isTimeSampled, time);
    auto v1 = getValue<double>(path, meta, 1, isTimeSampled, time);
    return { carb::Double2{ v0.value, v1.value }, v0.ambiguous || v1.ambiguous };
}

template <>
inline ModelValue<carb::Double3> Model::getValue(const char* path, const char* meta, size_t, bool isTimeSampled, double time)
{
    auto v0 = getValue<double>(path, meta, 0, isTimeSampled, time);
    auto v1 = getValue<double>(path, meta, 1, isTimeSampled, time);
    auto v2 = getValue<double>(path, meta, 2, isTimeSampled, time);
    return { carb::Double3{ v0.value, v1.value, v2.value }, v0.ambiguous || v1.ambiguous || v2.ambiguous };
}

template <>
inline ModelValue<carb::Double4> Model::getValue(const char* path, const char* meta, size_t, bool isTimeSampled, double time)
{
    auto v0 = getValue<double>(path, meta, 0, isTimeSampled, time);
    auto v1 = getValue<double>(path, meta, 1, isTimeSampled, time);
    auto v2 = getValue<double>(path, meta, 2, isTimeSampled, time);
    auto v3 = getValue<double>(path, meta, 3, isTimeSampled, time);
    return { carb::Double4{ v0.value, v1.value, v2.value, v3.value },
             v0.ambiguous || v1.ambiguous || v2.ambiguous || v3.ambiguous };
}

template <>
inline ModelValue<carb::ColorRgb> Model::getValue(const char* path, const char* meta, size_t, bool isTimeSampled, double time)
{
    auto v0 = getValue<float>(path, meta, 0, isTimeSampled, time);
    auto v1 = getValue<float>(path, meta, 1, isTimeSampled, time);
    auto v2 = getValue<float>(path, meta, 2, isTimeSampled, time);
    return { carb::ColorRgb{ v0.value, v1.value, v2.value }, v0.ambiguous || v1.ambiguous || v2.ambiguous };
}

template <>
inline ModelValue<carb::ColorRgba> Model::getValue(const char* path, const char* meta, size_t, bool isTimeSampled, double time)
{
    auto v0 = getValue<float>(path, meta, 0, isTimeSampled, time);
    auto v1 = getValue<float>(path, meta, 1, isTimeSampled, time);
    auto v2 = getValue<float>(path, meta, 2, isTimeSampled, time);
    auto v3 = getValue<float>(path, meta, 3, isTimeSampled, time);
    return { carb::ColorRgba{ v0.value, v1.value, v2.value, v3.value },
             v0.ambiguous || v1.ambiguous || v2.ambiguous || v3.ambiguous };
}

template <>
inline ModelValue<Mat44> Model::getValue(const char* path, const char* meta, size_t, bool isTimeSampled, double time)
{
    ModelValue<Mat44> res;
    res.ambiguous = false;
    for (size_t i = 0; i < 16; i++)
    {
        auto v = getValue<double>(path, meta, i, isTimeSampled, time);
        *(&res.value.rows[0].x + i) = v.value;
        res.ambiguous |= v.ambiguous;
    }
    return res;
}

template <>
inline void Model::setValue(const char* path,
                            const char* meta,
                            bool value,
                            size_t index,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setValueBool(path, meta, value, index, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>
inline void Model::setValue(const char* path,
                            const char* meta,
                            std::string value,
                            size_t index,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setValueString(path, meta, value, index, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>
inline void Model::setValue(const char* path,
                            const char* meta,
                            double value,
                            size_t index,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setValueNumber(path, meta, value, index, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>
inline void Model::setValue(const char* path,
                            const char* meta,
                            float value,
                            size_t index,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setValueNumber(path, meta, static_cast<double>(value), index, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>
inline void Model::setValue(const char* path,
                            const char* meta,
                            int32_t value,
                            size_t index,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setValueNumber(path, meta, static_cast<double>(value), index, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>
inline void Model::setValue(const char* path,
                            const char* meta,
                            uint32_t value,
                            size_t index,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setValueNumber(path, meta, static_cast<double>(value), index, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>

inline void Model::setValue(const char* path,
                            const char* meta,
                            carb::Int2 value,
                            size_t,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setArraySize(path, meta, 2);
    this->setValue(path, meta, value.x, 0, isTimeSampled, time, info);
    this->setValue(path, meta, value.y, 1, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>
inline void Model::setValue(const char* path,
                            const char* meta,
                            carb::Double2 value,
                            size_t,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setArraySize(path, meta, 2, isTimeSampled, time);
    this->setValue(path, meta, value.x, 0, isTimeSampled, time, info);
    this->setValue(path, meta, value.y, 1, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>
inline void Model::setValue(const char* path,
                            const char* meta,
                            carb::Double3 value,
                            size_t,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setArraySize(path, meta, 3, isTimeSampled, time);
    this->setValue(path, meta, value.x, 0, isTimeSampled, time, info);
    this->setValue(path, meta, value.y, 1, isTimeSampled, time, info);
    this->setValue(path, meta, value.z, 2, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>
inline void Model::setValue(const char* path,
                            const char* meta,
                            carb::Double4 value,
                            size_t,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setArraySize(path, meta, 4, isTimeSampled, time);
    this->setValue(path, meta, value.x, 0, isTimeSampled, time, info);
    this->setValue(path, meta, value.y, 1, isTimeSampled, time, info);
    this->setValue(path, meta, value.z, 2, isTimeSampled, time, info);
    this->setValue(path, meta, value.w, 3, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>
inline void Model::setValue(const char* path,
                            const char* meta,
                            carb::ColorRgb value,
                            size_t,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setArraySize(path, meta, 3, isTimeSampled, time);
    this->setValue(path, meta, value.r, 0, isTimeSampled, time, info);
    this->setValue(path, meta, value.g, 1, isTimeSampled, time, info);
    this->setValue(path, meta, value.b, 2, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>
inline void Model::setValue(const char* path,
                            const char* meta,
                            carb::ColorRgba value,
                            size_t,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setArraySize(path, meta, 4, isTimeSampled, time);
    this->setValue(path, meta, value.r, 0, isTimeSampled, time, info);
    this->setValue(path, meta, value.g, 1, isTimeSampled, time, info);
    this->setValue(path, meta, value.b, 2, isTimeSampled, time, info);
    this->setValue(path, meta, value.a, 3, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>
inline void Model::setValue(const char* path,
                            const char* meta,
                            ui::Mat44 value,
                            size_t,
                            bool isTimeSampled,
                            double time,
                            const ModelChangeInfo& info)
{
    this->beginChangeGroup();
    this->setArraySize(path, meta, 16, isTimeSampled, time);
    for (size_t i = 0; i < 16; i++)
        this->setValue(path, meta, *(&value.rows[0].x + i), i, isTimeSampled, time, info);
    this->endChangeGroup();
}

template <>
inline ModelNodeType Model::getNodeTypeForT<std::string>()
{
    return ModelNodeType::eString;
}

template <>
inline ModelNodeType Model::getNodeTypeForT<bool>()
{
    return ModelNodeType::eBool;
}

template <>
inline ModelNodeType Model::getNodeTypeForT<double>()
{
    return ModelNodeType::eNumber;
}

template <>
inline ModelNodeType Model::getNodeTypeForT<float>()
{
    return ModelNodeType::eNumber;
}

template <>
inline ModelNodeType Model::getNodeTypeForT<int32_t>()
{
    return ModelNodeType::eNumber;
}

template <>
inline ModelNodeType Model::getNodeTypeForT<uint32_t>()
{
    return ModelNodeType::eNumber;
}

template <>
inline ModelNodeType Model::getNodeTypeForT<carb::Int2>()
{
    return ModelNodeType::eArray;
}

template <>
inline ModelNodeType Model::getNodeTypeForT<carb::Double2>()
{
    return ModelNodeType::eArray;
}

template <>
inline ModelNodeType Model::getNodeTypeForT<carb::Double3>()
{
    return ModelNodeType::eArray;
}

template <>
inline ModelNodeType Model::getNodeTypeForT<carb::Double4>()
{
    return ModelNodeType::eArray;
}

template <>
inline ModelNodeType Model::getNodeTypeForT<carb::ColorRgb>()
{
    return ModelNodeType::eArray;
}

template <>
inline ModelNodeType Model::getNodeTypeForT<carb::ColorRgba>()
{
    return ModelNodeType::eArray;
}

template <>
inline ModelNodeType Model::getNodeTypeForT<Mat44>()
{
    return ModelNodeType::eArray;
}


// Default Value Model

std::unique_ptr<Model> createSimpleValueModel(ModelNodeType valueType);


}
}
}
