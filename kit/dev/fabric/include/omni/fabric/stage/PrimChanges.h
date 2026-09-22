// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/IFabric.h>
#include <omni/fabric/IPath.h>

#include <gsl/span>
#include <cstddef>

namespace omni
{
namespace fabric
{

struct AttrAndChangedIndices
{
    AttrNameAndType attr;

    // For which prims did this attribute change?
    bool allIndicesChanged;
    gsl::span<const size_t> changedIndices;
};

struct BucketChanges
{
    // For each attribute, which prims changed?
    std::vector<AttrAndChangedIndices> attrChangedIndices;
    gsl::span<const Path> pathArray;

    BucketChanges() = default;

    BucketChanges(BucketChangesC in) : pathArray({ in.pathArray.ptr, in.pathArray.elementCount })
    {
        size_t count = in.changedIndices.elementCount;
        attrChangedIndices.resize(count);
        for (size_t i = 0; i != count; i++)
        {
            const ConstChangedIndicesC& inAttrChanges = in.changedIndices.ptr[i];

            attrChangedIndices[i].attr = in.changedAttributes.ptr[i];
            attrChangedIndices[i].allIndicesChanged = inAttrChanges.allIndicesChanged;
            attrChangedIndices[i].changedIndices =
                gsl::span<const size_t>(inAttrChanges.changedIndices.ptr, inAttrChanges.changedIndices.elementCount);
        }
    }
};

class AddedPrimIndices
{
    // Which prims were added?
    gsl::span<const size_t> addedIndices;

public:
    AddedPrimIndices(AddedPrimIndicesC in)
    {
        addedIndices = gsl::span<const size_t>(in.addedIndices.ptr, in.addedIndices.elementCount);
    }

    size_t size() const
    {
        return addedIndices.size();
    }

    // This iterator first iterates over the deletedElements that were replaced
    // by new elements, then the contiguous range of elements added at the end
    // of the bucket
    struct iterator
    {
        using iterator_category = std::input_iterator_tag;
        using difference_type = size_t;
        using value_type = size_t;
        using reference = size_t;

        iterator(gsl::span<const size_t>::iterator _addedIndicesIterator,
                 gsl::span<const size_t>::iterator _addedIndicesEnd)
            : addedIndicesIterator(_addedIndicesIterator), addedIndicesEnd(_addedIndicesEnd)
        {
        }

        reference operator*() const
        {
            return *addedIndicesIterator;
        }

        iterator& operator++()
        {
            addedIndicesIterator++;
            return *this;
        }

        bool operator==(iterator other) const
        {
            return addedIndicesIterator == other.addedIndicesIterator;
        }

        bool operator!=(iterator other) const
        {
            return !(*this == other);
        }

        difference_type operator-(iterator other)
        {
            return addedIndicesIterator - other.addedIndicesIterator;
        }

    private:
        gsl::span<const size_t>::iterator addedIndicesIterator;
        gsl::span<const size_t>::iterator addedIndicesEnd;
    };

    iterator begin()
    {
        return iterator(addedIndices.begin(), addedIndices.end());
    }

    iterator end()
    {
        return iterator(addedIndices.end(), addedIndices.end());
    }
};

} // namespace fabric
} // namespace omni
