// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file Module.h
//!
//! @brief Helpers for writing modules/plugins based on @ref omni::graph::exec.
#pragma once

#include <omni/graph/exec/unstable/PassRegistry.h>

//! Helper macro to ensure EF features are enabled in the current module/plugin.
//!
//! This macro should be called from either @c carbOnPluginStartup or @c onStarted.
//!
//! If your module/plugin registers EF nodes or passes, you must call this macro.
//!
//! For Kit-based extensions, rather than calling this macro, call OMNI_KIT_EXEC_CORE_ON_MODULE_STARTED(), which will
//! call this macro on your behalf.
#define OMNI_GRAPH_EXEC_ON_MODULE_STARTED(moduleName_) omni::graph::exec::unstable::registerModulePasses()

//! Helper macro to ensure EF features are safely disabled when the current module/plugin unloads.
//!
//! This macro should be called from either @c carbOnPluginShutdown or @c onUnload.
//!
//! If your module/plugin registers EF nodes or passes, you must call this macro.
//!
//! For Kit-based extensions, rather than calling this macro, call OMNI_KIT_EXEC_CORE_ON_MODULE_UNLOAD(), which will
//! call this macro on your behalf.
#define OMNI_GRAPH_EXEC_ON_MODULE_UNLOAD() omni::graph::exec::unstable::deregisterModulePasses()
