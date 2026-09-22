// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "ScalarXYZ.h"
#include "ValueWidget.h"

#include <memory>
#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

inline Mat44 getIdentityMat44()
{
    static Mat44 kIdentityMat44;
    kIdentityMat44.rows[0] = { 1, 0, 0, 0 };
    kIdentityMat44.rows[1] = { 0, 1, 0, 0 };
    kIdentityMat44.rows[2] = { 0, 0, 1, 0 };
    kIdentityMat44.rows[3] = { 0, 0, 0, 1 };
    return kIdentityMat44;
}

/**
 * Defines a transform widget.
 */
class OMNI_KIT_UI_CLASS_API Transform : public ValueWidget<Mat44>
{
public:
    static const WidgetType kType = CARB_HASH_STRING("Transform");

    OMNI_KIT_UI_API Transform(const char* posDisplayFormat = "%0.1f",
                              float posSpeed = 1.0f,
                              float posWrapValue = 0.0f,
                              float posMinValue = 0.0f,
                              float posMaxValue = 0.0f,
                              const char* rotDisplayFormat = "%0.1f",
                              float rotSpeed = 1.0f,
                              float rotWrapValue = 0.0f,
                              float rotMinValue = 0.0f,
                              float rotMaxValue = 0.0f,
                              Mat44 value = getIdentityMat44());

    OMNI_KIT_UI_API ~Transform();

    OMNI_KIT_UI_API WidgetType getType() override;

    void draw(float elapsedTime) override;

private:
    std::string m_labelRotation;
    std::string m_labelScale;

    enum class Types
    {
        ePosition,
        eRotation,
        eScale,
        eCount
    };
    std::shared_ptr<ScalarXYZ> m_scalar[static_cast<size_t>(Types::eCount)];
};

}
}
}
