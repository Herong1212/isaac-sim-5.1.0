// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/core/Fabric.h>
#include <omni/fabric/core/FabricSampleStorage.h>

namespace omni
{
namespace fabric
{
class FabricRenderingView
{
public:
    FabricRenderingView()
    {
    }
    FabricRenderingView(SampleIndex initialIndex) : m_fabricSampleStorage(initialIndex)
    {
    }
    FabricRenderingView(FabricId srcFabricId, Span<FabricCopyFilter> filters, bool editable, SampleIndex initialIndex)
        : m_fabricSampleStorage(srcFabricId, filters, editable, initialIndex)
    {
    }

    FabricRenderingView(SampleIndex initialIndex,
                        OnAddSampleCallback sample,
                        OnSetUneditableCallback edit,
                        bool executeSampleCallback,
                        bool executeUneditableCallback)
        : m_fabricSampleStorage(initialIndex,
            std::move(sample), std::move(edit),
            executeSampleCallback, executeUneditableCallback)
    {
    }

    FabricRenderingView(FabricId srcFabricId,
                        Span<FabricCopyFilter> filters,
                        bool editable,
                        SampleIndex initialIndex,
                        OnAddSampleCallback sample,
                        OnSetUneditableCallback edit,
                        bool executeSampleCallback,
                        bool executeUneditableCallback)
        : m_fabricSampleStorage(srcFabricId, filters, editable, initialIndex,
            std::move(sample), std::move(edit),
            executeSampleCallback, executeUneditableCallback)
    {
    }

    ~FabricRenderingView()
    {
    }

    FabricId GetWriteableFabricId()
    {
        return kInvalidFabricId;
    }

    FabricSampleStorage m_fabricSampleStorage;
    SampleIndex m_initialIndex;
    // TODO: ChangeTracker SideCar
};
} // namespace fabric
} // namespace omni