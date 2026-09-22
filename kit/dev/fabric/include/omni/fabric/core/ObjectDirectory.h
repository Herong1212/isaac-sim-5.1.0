// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/core/Enums.h>
#include <omni/fabric/core/span.h>
#include <omni/fabric/core/FabricTypes.h>

namespace omni
{
namespace fabric
{

struct IObjectDirectory;

struct ObjectDirectory
{
    ObjectDirectory(FabricId fabricId);

    void clear() const;
    bool empty() const;
    void reserve(size_t nPaths, size_t nTokens) const;

    uint64_t getTipRevision() const;

    size_t countPaths() const;
    size_t countTokens() const;

    void registerPaths(SpanOf<const PathC> paths);
    void registerTokens(SpanOf<const TokenC> tokens);
    uint64_t store(SpanOf<uint8_t> outBuffer) const;
    size_t load(SpanOf<const uint8_t> buffer);

private:
    FabricId m_fabricId;
    IObjectDirectory* m_interface;
};


// Directory P2P synchronization over IPC
//
// Purposes
//  o Unidirectional sync up of paths and tokens from node A to node B
//         DirectoryStore/A -> DirectoryLoad/B
//  o Bidirection sync up of paths and tokens between nodes A and B
//         DirectoryStore/A -> DirectoryLoad/B
//         DirectoryLoad/A  <- DirectoryStore/B

struct DirectoryNode
{
    struct SyncUpBlob
    {
        std::vector<uint8_t> chunkBytes;
    };
};

struct DirectoryStore : public DirectoryNode
{
    struct Pending
    {
        std::vector<Path> paths;
        std::vector<Token> tokens;
    };

    std::unique_ptr<ObjectDirectory> directory;
    uint64_t lastStoreRevision = 0;
    Pending pending;

    void push(Path pathc);
    void push(Token tokenc);
    void store(SyncUpBlob& sending);
};


} // namespace fabric
} // namespace omni

#include "impl/ObjectDirectory.inl"
