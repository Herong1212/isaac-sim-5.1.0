// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <unordered_map>

#include <carb/Defines.h>
#include <carb/logging/Log.h>
#include <omni/fabric/AttrNameAndType.h>

#include <omni/fabric/batch/forward.h>
#include <omni/fabric/batch/Types.h>

namespace omni
{
namespace fabric
{
namespace batch
{

// Specifies attribute and tag filters.
//
// As the user specifies attributes and tags, BatchFilter returns an AttributeRef for any attribute that requires read
// or write access. The user should save these AttributeRefs. They are used in combination with a View to access
// attribute data.
//
// Defining of a BatchFilter (and storing the related AttributeRefs) need only be done once per Batch, if desired.
// AttributeRef lifetime is tied to BatchFilter lifetime. Defining a BatchFilter does not immediately incur side-effects
// within a Fabric cache.
//
//
// Using these BatchFilter methods will cause topology changes to occur dynamically during *View Generation* on behalf
// of the user:
//
// - createAttribute()
// - createTag()
//
// Batches with any BatchFilter that uses these methods are sometimes referred to as a "self-mutating Batch".
// Internally, they are marked by a special flag, requiresDynamicViews.
//
// These methods exist as a convenience for the user, so if this convenience is valuable, by all means use it! This is
// not a warning message to deter use.
//
// The takeaway is to be mindful that this class of BatchFilter has very different performance characteristics:
//
// - Additional cost will be observed in *View Generation* as well as run times
// - There may be more performance variance frame-to-frame
// - A Batch flagged requiresDynamicViews may perform very differently than a Batch flagged !requiresDynamicViews. This
// is not an apples-to-apples comparison.
//
struct BatchFilter
{
    // Will require the Batch to only include prims that have nameAndType attribute available for reading
    AttributeRef readAttribute(const omni::fabric::AttrNameAndType& nameAndType);

    // Will require the Batch to only include prims that have nameAndType attribute available for writing
    AttributeRef writeAttribute(const omni::fabric::AttrNameAndType& nameAndType);

    // Will require the Batch to only include prims that have nameAndType attribute available for reading and writing
    AttributeRef readWriteAttribute(const omni::fabric::AttrNameAndType& nameAndType);

    // Will require the Batch to only include prims that do not currently have the nameAndType attribute.
    // Executing the Batch will create the nameAndType attribute for these prims, implicitly rebucketing them withing
    // Fabric internal data.
    // Executing the Batch will acquire write access to the newly created attribute, made available within the Lambda's
    // implementation.
    //
    // IMPLICITLY SETS requiresDynamicViews.
    AttributeRef createAttribute(const omni::fabric::AttrNameAndType& nameAndType);

    // Will require the Batch to exclude prims that have the nameAndType attribute.
    AttributeRef excludeAttribute(const omni::fabric::AttrNameAndType& nameAndType);

    // Will require the Batch to only include prims that have nameAndType tag
    void includeTag(const omni::fabric::AttrNameAndType& nameAndType);

    // Will require the Batch to exclude prims that have the nameAndType tag
    void excludeTag(const omni::fabric::AttrNameAndType& nameAndType);

    // Will require the Batch to only include prims that do not currently have the nameAndType tag.
    // Executing the Batch will create the nameAndType tag for these prims, implicitly rebucketing them withing
    // Fabric internal data.
    //
    // IMPLICITLY SETS requiresDynamicViews.
    void createTag(const omni::fabric::AttrNameAndType& nameAndType);

    // Returns the AttributeRef associated with the given nameAndType, if it has already been added.
    // Otherwise, returns ATTRIBUTE_REF_INVALID.
    AttributeRef findRef(const omni::fabric::AttrNameAndType& nameAndType) const;

    // Users can provide a size hint to the number of options they plan on adding
    void reserve(const size_t count);

private:
    friend struct omni::fabric::batch::detail::Batch;
    friend struct Schema;

    using Options = AttributeSpecification;

    AttributeRef addOptions(Options&& options);

    using OptionsMap = std::unordered_map<omni::fabric::AttrNameAndType, Options>;

    AttributeRef nextRef = 0;
    OptionsMap optionsMap;
};

} // namespace batch
} // namespace fabric
} // namespace omni

#include "impl/BatchFilter.inl"
