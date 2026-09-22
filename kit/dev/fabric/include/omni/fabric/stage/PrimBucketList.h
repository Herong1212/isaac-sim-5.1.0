// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Framework.h>
#include <carb/Interface.h>
#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
#include <omni/fabric/PrimChanges.h>
#include <carb/logging/Log.h>

#include <omni/fabric/Type.h>
#include <gsl/span>

#include <map>
#include <stdint.h>

#include "carb/cpp/Optional.h"
using carb::cpp::optional;

namespace omni
{
namespace fabric
{

// findPrims() returns a list of buckets of prims, represented by PrimBucketList.
struct PrimBucketList
{
    // Increments and decrements (destroy on zero) of the referenced PrimBucketListImpl
    explicit inline PrimBucketList(PrimBucketListId id = kInvalidPrimBucketListId,
                                   PrimBucketListOwnership ownership = PrimBucketListOwnership::eShared);
    inline ~PrimBucketList();

    // Copy operators.  Will increase the ref count on the given id.
    inline PrimBucketList(const PrimBucketList& other);
    inline PrimBucketList& operator=(const PrimBucketList& other);
    
    // Move operators. Will not increase the ref count on the source id
    // will decrement the ref count on the held id. 
    inline PrimBucketList(PrimBucketList&& other);
    inline PrimBucketList& operator=(PrimBucketList&& other);

    // PrimBucketList is opaque, you have to use the getAttributesArray methods
    // of StageReaderWriter, StageAtTime or StageAtTimeInterval to read the
    // attributes of its elements.
    inline size_t bucketCount() const;
    inline size_t size() const;
    inline void print() const;

    inline PrimBucketListId getId() const;

    // Releases the id from this instance of the PrimBucketList
    // This means that when the c++ object is destructed it WILL NOT 
    // invoke the release call on the id.  The user is thus responsible for 
    // either creating a new primbucketlist object to release this id
    // later, or manually doing so with the abi interfaces... 
    [[deprecated]] inline PrimBucketListId reset();

    // Releases the id from this instance of the PrimBucketList
    // This means that when the c++ object is destructed it WILL NOT
    // invoke the release call on the id.  The user is thus responsible for
    // either creating a new primbucketlist object to release this id
    // later, or manually doing so with the abi interfaces...
    inline PrimBucketListId detach();

    // Attach a detached id
    inline void attach(PrimBucketListId id);

    // Release the id, releasing a reference to the retained internal object
    inline void release();

    // Check for leaking implementation objects behind the public API
    // Returns true if there are still implementation objects allocated
    inline static bool checkLeaks();

    // retrieves the BucketId for a given bucket in this list
    inline BucketId getBucketId(uint32_t idx) const;
protected:
    inline static omni::fabric::IPrimBucketList* sIPrimBucketList();

    PrimBucketListId m_primBucketListId;

    friend class StageAtTimeInterval;
    friend class StageReaderWriter;
};

// ChangedPrimBucketList is a PrimBucketList that has changes stored for a
// particular listener. It is returned by StageReaderWriter::getChanges().
struct ChangedPrimBucketList : public PrimBucketList
{
    explicit inline ChangedPrimBucketList(PrimBucketListId id = kInvalidPrimBucketListId,
                                          PrimBucketListOwnership ownership = PrimBucketListOwnership::eShared);

    inline BucketChanges getChanges(size_t index) const;
    inline AddedPrimIndices getAddedPrims(size_t index) const;

    friend class StageReaderWriter;
};

} // namespace fabric
} // namespace omni


#include <omni/fabric/stage/impl/PrimBucketList.inl>
