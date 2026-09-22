// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>

#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/Enums.h>
#include <omni/fabric/core/FabricTypes.h>
#include <omni/fabric/core/span.h>

#include <stdint.h>

namespace omni
{
namespace fabric
{

struct IObjectDirectory
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IObjectDirectory", 1, 0);

    void(CARB_ABI* clear)(FabricId fabricId);
    bool(CARB_ABI* empty)(FabricId fabricId);
    void(CARB_ABI* reserve)(FabricId fabricId, size_t, size_t);
    uint64_t(CARB_ABI* getTipRevision)(FabricId fabricId);
    size_t(CARB_ABI* countPaths)(FabricId fabricId);
    size_t(CARB_ABI* countTokens)(FabricId fabricId);
    void(CARB_ABI* registerPaths)(FabricId fabricId, SpanOf<const PathC> paths);
    void(CARB_ABI* registerTokens)(FabricId fabricId, SpanOf<const TokenC> tokens);
    size_t(CARB_ABI* store)(FabricId fabricId, SpanOf<uint8_t> outBuffer);
    size_t(CARB_ABI* load)(FabricId fabricId, SpanOf<const uint8_t> buffer);
};

} // namespace fabric
} // namespace omni
