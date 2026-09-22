// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/FabricTypes.h>
#include <omni/fabric/stage/ChangeTracking.h>

#include <vector>
#include <gsl/span>

namespace omni
{
namespace fabric
{

template <typename T>
class Column
{
    gsl::span<T> data;

    std::vector<FineGrainedChangeTracker> fineGrainedChangeTrackers;

public:
    Column() : data()
    {
    }
    explicit Column(T* ptr, size_t count, const std::vector<FineGrainedChangeTracker>& _fineGrainedChangeTrackers)
        : data(ptr, count), fineGrainedChangeTrackers(_fineGrainedChangeTrackers)
    {
    }

    const T& getForRead(size_t index) const
    {
        // Don't set element dirty
        return data[index];
    }

    T& getForModify(size_t index)
    {
        for (FineGrainedChangeTracker& fineGrainedChangeTracker : fineGrainedChangeTrackers)
        {
            fineGrainedChangeTracker.setDirty(index);
        }
        return data[index];
    }

    size_t size() const
    {
        return data.size();
    }
};

template <typename T>
class Column<gsl::span<T>>
{
    std::vector<gsl::span<T>> data;

    std::vector<FineGrainedChangeTracker> fineGrainedChangeTrackers;

public:
    Column() : data(), fineGrainedChangeTrackers()
    {
    }
    explicit Column<gsl::span<T>>(ArrayPointersAndSizesWithTypeC arrayPointersAndSizes,
                                  const std::vector<FineGrainedChangeTracker>& _fineGrainedChangeTrackers)
        : data(arrayPointersAndSizes.elementCount), fineGrainedChangeTrackers(_fineGrainedChangeTrackers)
    {
        size_t primCount = arrayPointersAndSizes.elementCount;
        for (size_t i = 0; i != primCount; i++)
        {
            T* ptr = reinterpret_cast<T*>(arrayPointersAndSizes.arrayPtrs[i]);
            const size_t size = arrayPointersAndSizes.sizes[i];
            if (ptr == nullptr || size == 0)
            {
                data[i] = gsl::span<T>();
            }
            else
            {
                data[i] = gsl::span<T>(ptr, size);
            }
        }
    }

    gsl::span<const T> getForRead(size_t index) const
    {
        // Don't set element dirty
        return data[index];
    }

    gsl::span<T> getForModify(size_t index)
    {
        for (FineGrainedChangeTracker& fineGrainedChangeTracker : fineGrainedChangeTrackers)
        {
            fineGrainedChangeTracker.setDirty(index);
        }
        return data[index];
    }

    size_t size() const
    {
        return data.size();
    }
};

} // namespace fabric
}
