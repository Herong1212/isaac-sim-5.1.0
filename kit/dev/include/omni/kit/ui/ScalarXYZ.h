// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Image.h"
#include "ValueWidget.h"

#include <memory>
#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a ScalarXYZ widget.
 */
class OMNI_KIT_UI_CLASS_API ScalarXYZ : public ValueWidget<carb::Double3>
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ScalarXYZ);

    OMNI_KIT_UI_API ScalarXYZ(const char* displayFormat,
                              float speed,
                              double wrapValue,
                              double minValue,
                              double maxValue,
                              double deadZone = 0.0,
                              carb::Double3 value = {});

    OMNI_KIT_UI_API ~ScalarXYZ();

    /**
     * @see Widget::getType
     */
    OMNI_KIT_UI_API WidgetType getType() override;

    /**
     * Draws the scalar, used for drawing when allocated by other classes
     *
     * @param v x,y,z to draw
     * @return true if dirty
     */
    OMNI_KIT_UI_API bool drawScalar(carb::Double3& v, bool& afterEdit, bool hasX = true, bool hasY = true, bool hasZ = true);

    OMNI_KIT_UI_API double wrapScalar(double value) const;
    OMNI_KIT_UI_API double deadzoneScalar(double value) const;

    std::string displayFormat;
    float dragSpeed;
    double wrapValue;
    double deadZone;
    double minVal;
    double maxVal;

    void draw(float elapsedTime) override;

    void setSkipYposUpdate(bool skip)
    {
        m_skipYposUpdate = skip;
    }

private:
    enum class Images
    {
        eX,
        eY,
        eZ,
        eCount
    };

    std::shared_ptr<Image> m_images[static_cast<size_t>(Images::eCount)];

    std::string m_labelY;
    std::string m_labelZ;
    bool m_skipYposUpdate = false;

    const char* m_filenames[static_cast<size_t>(Images::eCount)] = { "/resources/icons/transform_x.png",
                                                                     "/resources/icons/transform_y.png",
                                                                     "/resources/icons/transform_z.png" };
};
}
}
}
