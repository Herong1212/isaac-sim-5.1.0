// Copyright (c) 2019-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "DocAbstractManipulatorModel.h"

OMNIUI_PROTECT_PYBIND11_OBJECT(OMNIUI_SCENE_NS::AbstractManipulatorModel, AbstractManipulatorModel);
OMNIUI_PROTECT_PYBIND11_OBJECT(OMNIUI_SCENE_NS::AbstractManipulatorModel::AbstractManipulatorItem,
                               AbstractManipulatorItem);

#define OMNIUI_PYBIND_INIT_AbstractManipulatorModel
#define OMNIUI_PYBIND_KWARGS_DOC_AbstractManipulatorModel
