// Copyright (c) 2019-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindAbstractGesture.h"
#include "DocShapeGesture.h"

OMNIUI_PROTECT_PYBIND11_OBJECT(OMNIUI_SCENE_NS::ShapeGesture, ShapeGesture);

#define OMNIUI_PYBIND_INIT_ShapeGesture OMNIUI_PYBIND_INIT_AbstractGesture
#define OMNIUI_PYBIND_KWARGS_DOC_ShapeGesture OMNIUI_PYBIND_KWARGS_DOC_AbstractGesture
