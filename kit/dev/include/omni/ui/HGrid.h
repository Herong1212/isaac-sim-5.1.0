// Copyright (c) 2018-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Api.h"
#include "Grid.h"

OMNIUI_NAMESPACE_OPEN_SCOPE

/**
 * @brief Shortcut for Grid{eLeftToRight}. The grid grows from left to right with the widgets placed.
 *
 * @see Grid
 */
class OMNIUI_CLASS_API HGrid : public Grid
{
    OMNIUI_OBJECT(HGrid)

public:
    OMNIUI_API
    ~HGrid() override;

protected:
    /**
     * @brief Construct a grid that grow from left to right with the widgets placed.
     */
    OMNIUI_API
    HGrid();
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
