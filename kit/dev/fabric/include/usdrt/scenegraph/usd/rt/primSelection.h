// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file usdrt/scenegraph/usd/rt/primSelection.h
//!
//! @brief Provides RtPrimSelection class, for efficiently processing sets of prims

#include <omni/fabric/FabricTypes.h>
#include <usdrt/scenegraph/interface/IRtPrimSelection106_4.h>
#include <usdrt/scenegraph/usd/usd/common.h>

// nvcc doesn't like usdrt::SdfPath
#ifndef __CUDACC__
#include <usdrt/scenegraph/usd/sdf/path.h>
#endif

#ifndef DOXYGEN_BUILD
#    if defined(__CUDACC__)
#        define CUDA_CALLABLE __host__ __device__
#    else
#        define CUDA_CALLABLE
#    endif
#endif

namespace usdrt
{

using AttributeRef = batch::AttributeRef;

//! The RtPrimSelection class represents a subset of a stage's prims, and allows you to
//! efficiently process them on CPU or GPU using the fabric::batch API.
//!
//! It provides:
//! - a batch::View from which you can construct a batch::ViewIterator to
//!   iterate over the data on CPU or GPU.
//! - a method to convert attribute names and types to AttributeRefs, which you
//!   need to get attributes from the batch::ViewIterator.
//! - a method to get the number of prims in the view without creating a
//!   batch::ViewIterator. When processing prims on GPU you typically use the
//!   CPU to spawn a set of GPU threads, for example one thread per prim. This
//!   method allows you to do this without the expense of creating a
//!   batch::ViewIterator on both CPU and GPU.
//!
//! To create an RtPrimSelection, use UsdStage::GetDataView(), which allows you to
//! specify which of the stage's prims you want to include in the view.
class RtPrimSelection
{
public:
    //! Convert an attribute name and type to an AttributeRef, which you need
    //! to get attributes from the batch::ViewIterator.
    AttributeRef GetRef(SdfValueTypeName type, const TfToken& name) const;

    //! Get a batch::View that represents this view. From this you can
    //! construct a batch::ViewIterator to iterate over the data on CPU or GPU.
    omni::fabric::batch::View GetBatchView() const;

    //! Get the number of prims in the view without creating a
    //! batch::ViewIterator.
    //! When processing prims on GPU you typically use the CPU to spawn a set
    //! of GPU threads, for example one thread per prim. This method allows you
    //! to do this without the expense of creating a batch::ViewIterator on
    //! both CPU and GPU.
    size_t GetCount() const;

#ifndef __CUDACC__

    //! Get the paths represented by the selection
    //! if wantPaths=true was set during selection creation.
    //! If wantPaths=false (the default) during selection
    //! creation, this will return an empty vector.
    std::vector <usdrt::SdfPath> GetPaths() const;
#endif

    //! Allows a selection to be reused across frames.
    //! If Fabric topology has changed since the last call to this method
    //! this will re-generate
    //! the internally-held Batch view and return true.
    //! If Fabric topology was not changed since the last call to this method,
    //! this will just mark the selected attributes as dirty in Fabric
    //! and return false.
    //! In either case, downstream consumers of Fabric change tracking
    //! will know the writable attributes of this selection were potentially
    //! modified.
    bool PrepareForReuse() const;

    omni::core::ObjectPtr<usdrt::IRtPrimSelection> m_selection;
};

inline omni::fabric::batch::AttributeRef RtPrimSelection::GetRef(SdfValueTypeName type, const TfToken& name) const
{
    omni::fabric::batch::AttributeRef ref = m_selection->getRef(static_cast<TokenC>(name), TypeC(type));

    return ref;
}

inline size_t RtPrimSelection::GetCount() const
{
    return m_selection->getBatchView().count();
}

inline omni::fabric::batch::View RtPrimSelection::GetBatchView() const
{
    return m_selection->getBatchView();
}

#ifndef __CUDACC__
inline std::vector<usdrt::SdfPath> RtPrimSelection::GetPaths() const
{
    auto selection106_4 = omni::core::cast<IRtPrimSelection106_4>(m_selection.get());
    if (!selection106_4)
    {
        return std::vector<usdrt::SdfPath>();    
    }
    const uint32_t count = static_cast<uint32_t>(GetCount());

    if (!count)
    {
        return std::vector<usdrt::SdfPath>();    
    }

    std::vector<omni::fabric::PathC> asPathC(count);

    if (!selection106_4->getPaths(asPathC.data(), count))
    {
        return std::vector<usdrt::SdfPath>();
    }

    const std::vector<usdrt::SdfPath> result(asPathC.begin(), asPathC.end());

    return result;
}
#endif

inline bool RtPrimSelection::PrepareForReuse() const
{
    auto selection106_4 = omni::core::cast<IRtPrimSelection106_4>(m_selection.get());
    if (selection106_4)
    {
        return selection106_4->prepareForReuse();
    }

    return false;
}

}
