// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Api.h"
#include "Model.h"

#include <memory>
#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

class OMNI_KIT_UI_CLASS_API BroadcastModel : public Model
{
public:
    using TargetId = uint32_t;

    OMNI_KIT_UI_API virtual TargetId addTarget(const std::shared_ptr<Model>& model,
                                               const std::string& pathPrefixOrigin,
                                               const std::string& pathPrefixNew) = 0;

    OMNI_KIT_UI_API virtual void removeTarget(TargetId) = 0;
};


OMNI_KIT_UI_API std::unique_ptr<BroadcastModel> createBroadcastModel();


}
}
}
