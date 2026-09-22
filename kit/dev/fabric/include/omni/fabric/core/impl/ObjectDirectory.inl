// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include "../interface/IObjectDirectory.h"

namespace omni::fabric
{

inline ObjectDirectory::ObjectDirectory(FabricId fabricId)
{
    m_interface = carb::getCachedInterface<IObjectDirectory>();
    CARB_ASSERT(m_interface);
    m_fabricId = fabricId;
}

inline uint64_t ObjectDirectory::getTipRevision() const
{
    return m_interface->getTipRevision(m_fabricId);
}

inline void ObjectDirectory::clear() const
{
    m_interface->clear(m_fabricId);
}

inline bool ObjectDirectory::empty() const
{
    return m_interface->empty(m_fabricId);
}

inline void ObjectDirectory::reserve(size_t nPaths, size_t nTokens) const
{
    m_interface->reserve(m_fabricId, nPaths, nTokens);
}

inline size_t ObjectDirectory::countPaths() const
{
    return m_interface->countPaths(m_fabricId);
}

inline size_t ObjectDirectory::countTokens() const
{
    return m_interface->countTokens(m_fabricId);
}

inline void ObjectDirectory::registerPaths(SpanOf<const PathC> paths)
{
    m_interface->registerPaths(m_fabricId, paths);
}

inline void ObjectDirectory::registerTokens(SpanOf<const TokenC> tokens)
{
    m_interface->registerTokens(m_fabricId, tokens);
}

inline size_t ObjectDirectory::store(SpanOf<uint8_t> outBuffer) const
{
    return m_interface->store(m_fabricId, outBuffer);
}

inline size_t ObjectDirectory::load(SpanOf<const uint8_t> buffer)
{
    return m_interface->load(m_fabricId, buffer);
}



inline void DirectoryStore::push(Path path)
{
    pending.paths.push_back(path);
}

inline void DirectoryStore::push(Token token)
{
    pending.tokens.push_back(token);
}

inline void DirectoryStore::store(SyncUpBlob& snd)
{
    CARB_ASSERT(directory);

    const size_t cap = snd.chunkBytes.capacity();
    snd.chunkBytes.resize(cap);

    static_assert(sizeof(Path) == sizeof(PathC));
    static_assert(sizeof(Token) == sizeof(TokenC));

    auto buffer = make_spanOf<uint8_t>(snd.chunkBytes);
    const size_t sz = directory->store(buffer);

    snd.chunkBytes.resize(sz);

    if(sz > cap)
    {
        buffer = make_spanOf<uint8_t>(snd.chunkBytes);
        const size_t szz = directory->store(buffer);
        CARB_ASSERT(szz == sz);
    }
}

} // namespace omni::fabric
