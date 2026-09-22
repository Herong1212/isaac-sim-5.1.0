// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IDirtyID2.h"

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{

OMNI_DECLARE_INTERFACE(IDirtyID3);

// ====================================================================================================
/*
     _____          _   _       _     _    _
    |  __ \        | \ | |     | |   | |  | |
    | |  | | ___   |  \| | ___ | |_  | |  | |___  ___
    | |  | |/ _ \  | . ` |/ _ \| __| | |  | / __|/ _ \
    | |__| | (_) | | |\  | (_) | |_  | |__| \__ \  __/
    |_____/ \___/  |_| \_|\___/ \__|  \____/|___/\___|
*/
// The DirtyId interface exposes the implementation details of change tracking system for bundles.
// This functionality is exposed to allow old interfaces such as BundlePrims to function.
// Eventually this interface is going to be removed, once BundlePrims is fully deprecated.
// ====================================================================================================


// Identifier of the bundle write scope.
// This is always larger than 0.
using BundleWriteScopeId = int;

class IDirtyID3_abi : public omni::core::Inherits<IDirtyID2, OMNI_TYPE_ID("omni.graph.core.IDirtyID3")>
{
protected:
    //! @brief Opens a thread-local scope to ensure that a bundle is only made dirty once.
    //! @return An identifier of the scope.
    virtual BundleWriteScopeId open_abi() noexcept = 0;

    //! @brief Closes a previously opened scope.
    //! Each call to open must be balanced with a call to close.
    //! Please use the BundleWriteBlock API helper to do this robustly.
    //! @param id The identifier that was returned by open.
    //! @return Success if closed successfully, Fail when the scope was not open
    virtual omni::core::Result close_abi(BundleWriteScopeId id) noexcept = 0;
};

}
}
}
}

#include "IDirtyID3.gen.h"

OMNI_DEFINE_INTERFACE_API(omni::graph::core::unstable::IDirtyID3)
{
};
