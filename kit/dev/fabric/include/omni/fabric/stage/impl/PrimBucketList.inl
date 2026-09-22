// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

// PrimBucketList implementation starts here
namespace omni
{
namespace fabric
{

PrimBucketList::PrimBucketList(PrimBucketListId id, PrimBucketListOwnership ownership)
    : m_primBucketListId(id)
{
    if (m_primBucketListId != kInvalidPrimBucketListId)
    {
        switch (ownership)
        {
        case PrimBucketListOwnership::eOwned:
            // handles are created with refcount of 1, so skip the increment if we own it
            CARB_ASSERT(sIPrimBucketList()->debugGetRefCount(m_primBucketListId) == 1);
            break;

        case PrimBucketListOwnership::eDetached:
            // we can make no checks here, it's entirely up to the calling code to manage the refcount
            break;

        case PrimBucketListOwnership::eShared:
            // add a reference because we are sharing it (this and/or the Id was copied)
            sIPrimBucketList()->addRef(m_primBucketListId);
        }
    }
}

PrimBucketList::~PrimBucketList()
{
    if (m_primBucketListId != kInvalidPrimBucketListId)
        sIPrimBucketList()->release(m_primBucketListId);
}

PrimBucketList::PrimBucketList(const PrimBucketList& other)
{
    m_primBucketListId = other.m_primBucketListId;

    if (m_primBucketListId != kInvalidPrimBucketListId)
        sIPrimBucketList()->addRef(m_primBucketListId);
}

PrimBucketList& PrimBucketList::operator=(const PrimBucketList& other)
{
    if (m_primBucketListId != other.m_primBucketListId)
    {
        if (m_primBucketListId != kInvalidPrimBucketListId)
            sIPrimBucketList()->release(m_primBucketListId);

        m_primBucketListId = other.m_primBucketListId;

        if (m_primBucketListId != kInvalidPrimBucketListId)
            sIPrimBucketList()->addRef(m_primBucketListId);
    }
    return *this;
}

PrimBucketList::PrimBucketList(PrimBucketList&& other)
{
    m_primBucketListId = other.m_primBucketListId;

    other.m_primBucketListId = kInvalidPrimBucketListId;
}

PrimBucketList& PrimBucketList::operator=(PrimBucketList&& other)
{
    if (m_primBucketListId != other.m_primBucketListId)
    {
        if (m_primBucketListId != kInvalidPrimBucketListId)
            sIPrimBucketList()->release(m_primBucketListId);

        m_primBucketListId = other.m_primBucketListId;

        other.m_primBucketListId = kInvalidPrimBucketListId;
    }
    return *this;
}

PrimBucketListId PrimBucketList::getId() const
{
    return m_primBucketListId;
}

size_t PrimBucketList::bucketCount() const
{
    return sIPrimBucketList()->getBucketCount(m_primBucketListId);
}

size_t PrimBucketList::size() const
{
    return sIPrimBucketList()->getBucketCount(m_primBucketListId);
}

void PrimBucketList::print() const
{
    return sIPrimBucketList()->print(m_primBucketListId);
}

omni::fabric::IPrimBucketList* PrimBucketList::sIPrimBucketList()
{
    return carb::getCachedInterface<omni::fabric::IPrimBucketList>();
}

BucketChanges ChangedPrimBucketList::getChanges(size_t index) const
{
    BucketChangesC bucketChangesC = sIPrimBucketList()->getChanges(m_primBucketListId, index);
    return BucketChanges(bucketChangesC);
}

AddedPrimIndices ChangedPrimBucketList::getAddedPrims(size_t index) const
{
    AddedPrimIndicesC addedPrimIndicesC = sIPrimBucketList()->getAddedPrims(m_primBucketListId, index);
    return AddedPrimIndices(addedPrimIndicesC);
}

PrimBucketListId PrimBucketList::reset()
{
    PrimBucketListId out = m_primBucketListId;
    m_primBucketListId = kInvalidPrimBucketListId;
    return out;
}

PrimBucketListId PrimBucketList::detach()
{
    PrimBucketListId out = m_primBucketListId;
    m_primBucketListId = kInvalidPrimBucketListId;
    return out;
}

void PrimBucketList::attach(PrimBucketListId id)
{
    if (m_primBucketListId != kInvalidPrimBucketListId)
        sIPrimBucketList()->release(m_primBucketListId);

    m_primBucketListId = id;
}

void PrimBucketList::release()
{
    if (m_primBucketListId != kInvalidPrimBucketListId)
        sIPrimBucketList()->release(m_primBucketListId);

    m_primBucketListId = kInvalidPrimBucketListId;
}

bool PrimBucketList::checkLeaks()
{
    return sIPrimBucketList()->checkLeaks();
}

inline BucketId PrimBucketList::getBucketId(uint32_t idx) const
{
    return sIPrimBucketList()->getBucketId(m_primBucketListId, idx);
}

ChangedPrimBucketList::ChangedPrimBucketList(PrimBucketListId id, PrimBucketListOwnership ownership)
    : PrimBucketList(id, ownership)
{
}

} // namespace fabric
} // namespace omni
