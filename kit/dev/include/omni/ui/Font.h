// Copyright (c) 2019-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Api.h"

OMNIUI_NAMESPACE_OPEN_SCOPE

/**
 * @brief List of all font sizes
 */
enum class FontStyle
{
    eNone,

    /**
     * @brief 14
     */
    eNormal,

    /**
     * @brief 16
     */
    eLarge,

    /**
     * @brief 12
     */
    eSmall,

    /**
     * @brief 18
     */
    eExtraLarge,

    /**
     * @brief 20
     */
    eXXL,

    /**
     * @brief 22
     */
    eXXXL,

    /**
     * @brief 10
     */
    eExtraSmall,

    /**
     * @brief 8
     */
    eXXS,

    /**
     * @brief 6
     */
    eXXXS,

    /**
     * @brief 66
     */
    eUltra,

    eCount
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
