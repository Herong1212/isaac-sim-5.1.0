// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Implementation detail

// Note! Intentionally without include guards
// This file is counterpart to PushBadMacros.h

#pragma pop_macro("vsprintf")
#pragma pop_macro("snprintf")
#pragma pop_macro("vsnprintf")
#pragma pop_macro("vfscanf")
#pragma pop_macro("vscanf")
#pragma pop_macro("vsscanf")
// If something is popped here, it should be pushed in PushBadMacros.h
