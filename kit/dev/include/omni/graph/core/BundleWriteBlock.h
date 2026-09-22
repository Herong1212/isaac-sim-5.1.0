// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/dirtyid/IDirtyID3.h>
#include <omni/graph/core/ComputeGraph.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{

//! RAII helper to robustly open/close a bundle write scope
class BundleWriteBlock
{
    ObjectPtr<IDirtyID3> iDirtyID3;
    BundleWriteScopeId scopeId;

public:
    explicit BundleWriteBlock(GraphContextObj const& context, bool open = true) noexcept
        : iDirtyID3{ omni::cast<IDirtyID3>(carb::getCachedInterface<ComputeGraph>()->getDirtyIDInterface(context)) },
          scopeId{ open ? iDirtyID3->open() : 0 }
    {
    }

    BundleWriteBlock(BundleWriteBlock&& block) noexcept : iDirtyID3{ std::move(block.iDirtyID3) }, scopeId{ block.scopeId }
    {
        block.iDirtyID3 = nullptr;
        block.scopeId = 0;
    }

    ~BundleWriteBlock() noexcept
    {
        if (scopeId)
        {
            iDirtyID3->close(scopeId);
        }
    }

    BundleWriteBlock& operator=(BundleWriteBlock&&) = delete;
    BundleWriteBlock(BundleWriteBlock const&) = delete;
    BundleWriteBlock& operator=(BundleWriteBlock const&) = delete;
};

}
}
}
}
