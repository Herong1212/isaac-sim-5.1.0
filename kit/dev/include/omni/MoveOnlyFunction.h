// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include "../carb/Defines.h"

#ifndef DOXYGEN_BUILD

#    define OMNI_MOF 1

#    include "detail/MoveOnlyFunctionImpl.h"
#    define OMNI_MOF_CV const
#    include "detail/MoveOnlyFunctionImpl.h"
#    define OMNI_MOF_REF &
#    include "detail/MoveOnlyFunctionImpl.h"
#    define OMNI_MOF_REF &&
#    define OMNI_MOF_MOVE std::move
#    include "detail/MoveOnlyFunctionImpl.h"
#    define OMNI_MOF_CV const
#    define OMNI_MOF_REF &
#    include "detail/MoveOnlyFunctionImpl.h"
#    define OMNI_MOF_CV const
#    define OMNI_MOF_REF &&
#    define OMNI_MOF_MOVE std::move
#    include "detail/MoveOnlyFunctionImpl.h"

// Until MSVC is updated it must have separate specializations for noexcept(true)
// and noexcept(false).
// Once it's updated noexcept can be inferred from a template argument:
//      template <typename Ret, typename... Args, bool Noex>
//      class move_only_function<Ret(Args...) OMNI_MOF_CV OMNI_MOF_REF noexcept(Noex)>
#    define OMNI_MOF_NOEX noexcept
#    include "detail/MoveOnlyFunctionImpl.h"
#    define OMNI_MOF_CV const
#    define OMNI_MOF_NOEX noexcept
#    include "detail/MoveOnlyFunctionImpl.h"
#    define OMNI_MOF_REF &
#    define OMNI_MOF_NOEX noexcept
#    include "detail/MoveOnlyFunctionImpl.h"
#    define OMNI_MOF_REF &&
#    define OMNI_MOF_MOVE std::move
#    define OMNI_MOF_NOEX noexcept
#    include "detail/MoveOnlyFunctionImpl.h"
#    define OMNI_MOF_CV const
#    define OMNI_MOF_REF &
#    define OMNI_MOF_NOEX noexcept
#    include "detail/MoveOnlyFunctionImpl.h"
#    define OMNI_MOF_CV const
#    define OMNI_MOF_REF &&
#    define OMNI_MOF_MOVE std::move
#    define OMNI_MOF_NOEX noexcept
#    include "detail/MoveOnlyFunctionImpl.h"

#    undef OMNI_MOF

#endif
