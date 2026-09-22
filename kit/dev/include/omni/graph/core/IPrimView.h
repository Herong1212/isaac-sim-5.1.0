// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/core/IObject.h>
#include <omni/graph/core/Type.h>




namespace omni
{

namespace fabric
{
struct PathC;
}

namespace graph
{
namespace core
{

//! Declare the IPrimView interface definition
OMNI_DECLARE_INTERFACE(IPrimView);

//! Data type to use for a reference to an IPrimView interface definition
using IPrimViewPtr = omni::core::ObjectPtr<IPrimView>;

/**
 * PrimView is an interface that provides a view to a set of prims for use with OmniGraph instancing.
 *  
 * The prim view provides both a list of prims, and a layout of which prims can be treated as consecutive data in fabric
 *
 * 
 */
class IPrimView_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.graph.core.IPrimView")>
{
protected:


    /**
     * Returns the number of prims in this view.
     * @return the total number of prims in this view, regardless of the segments
     */
    virtual size_t getPrimCount_abi() noexcept = 0;

    /**
     * Returns a readonly pointer to a list of prims, stored as Paths. 
     *
     * The returned list may be used to access consective prims. If the given prim is part of a segment of size n
     * the returned pointer should be valid for all prims in that segment.
     * For example if there are two segments of prims listed:
     *      segment 0 starts at prim 0 and has 5 prims.
     *      segment 1 starts at prim 5 and contains 10 prims.
     * Calling getPrim path on segment index:
     *      0 returns a pointer to segments [0, 5)
     *      3 returns a pointer to segments [3, 5)    
     *      4 returns a pointer to segment 4 only (i.e. [4,5))
     *      5 returns a pointer to segments [5, 15)
     *      10 returns a pointer to segments [10, 15)
     * 
     * @param[in] index - the index of the prim to retrieve.
     * @returns A pointer to the prim path for prim at the given index. If the index is out of range
     *          returns nullptr. 
     * 
     */
    virtual OMNI_ATTR("no_py") omni::fabric::PathC const* const getPrimPath_abi(size_t index) noexcept = 0;

    /**
     * Returns the number of segments in the view. 
     * @return the number of segments in the view. 
     */
    virtual OMNI_ATTR("no_py") size_t getSegmentCount_abi() noexcept = 0;

    /**
     * Returns the number of prims in the segment at the given index
     *
     * @params[in] index The index of the segment to query
     * @returns The number of prims in the segment or 0 if the index is out of range.
     */
    virtual OMNI_ATTR("no_py") size_t getSegmentSize_abi(size_t index) noexcept = 0;

    /**
     * Call this method to refresh the prim view. Use this method to test if the view has changed.
     *
     * @returns true, if the segments or prim paths have updated since the previous call. 
     */
    virtual OMNI_ATTR("no_py") bool refreshView_abi() noexcept = 0;

    /**
     * Called to bind the prim view to a fabric id. 
     *
     * @params[in] The fabric Id to bind to. 
     */
    virtual OMNI_ATTR("no_py") void bind_abi(omni::fabric::FabricId fabricId) noexcept = 0;
};

}
}
}


#include "IPrimView.gen.h"
