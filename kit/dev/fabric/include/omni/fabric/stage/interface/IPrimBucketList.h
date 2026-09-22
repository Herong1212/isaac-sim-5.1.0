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

#include <omni/fabric/core/AttrNameAndType.h>
#include <omni/fabric/core/Enums.h>
#include <omni/fabric/core/FabricTypes.h>
#include <omni/fabric/core/IdTypes.h>
#include <omni/fabric/core/Ordered_Set.h>
#include <omni/fabric/core/FabricTime.h>
#include <omni/fabric/core/interface/IPath.h>

#include <stdint.h>

namespace omni
{
namespace fabric
{

struct IPrimBucketList
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IPrimBucketList", 0, 5);

    CARB_DEPRECATED("Use the release function instead for consistency")
    void(CARB_ABI* destroy)(PrimBucketListId primBucketListId);
    size_t(CARB_ABI* getBucketCount)(PrimBucketListId primBucketListId);
    void(CARB_ABI* print)(PrimBucketListId primBucketListId);
    BucketChangesC(CARB_ABI* getChanges)(PrimBucketListId changeListId, size_t index);
    AddedPrimIndicesC(CARB_ABI* getAddedPrims)(PrimBucketListId changeListId, size_t index);

    void (CARB_ABI* addRef)(PrimBucketListId primBucketListId);
    void (CARB_ABI* release)(PrimBucketListId primBucketListId);
    size_t (CARB_ABI* debugGetRefCount)(PrimBucketListId primBucketListId);
    bool (CARB_ABI* checkLeaks)();

    BucketId (CARB_ABI* getBucketId)(PrimBucketListId primBucketListId, size_t index);
};

} // namespace fabric
} // namespace omni
