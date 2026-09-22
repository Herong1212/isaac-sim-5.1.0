// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <carb/profiler/Profile.h>
#include <vector>
#include <zlib.h>
#ifdef COMPRESSION_USE_BLOSC
#include <blosc.h>
#endif

namespace omni
{
namespace compression
{

enum class CompressionLibrary
{
    Zlib,
#ifdef COMPRESSION_USE_BLOSC
    Blosc,
#endif
    Default = Zlib
};

// TODO: add more error types...
enum class CompressionResult
{
    Success = 0,
    CompressionError = 1,
    SizeError = 2,
};

enum class Level
{
    BestCompression,
    BestSpeed,
    LibraryDefault,
    Default = LibraryDefault
};

inline int toZlibLevel(Level level)
{
    switch (level)
    {
    case Level::BestCompression:
        return Z_BEST_COMPRESSION;
    case Level::BestSpeed:
        return Z_BEST_SPEED;
    case Level::LibraryDefault:
        return Z_DEFAULT_COMPRESSION;
    }
    return Z_DEFAULT_COMPRESSION;
}

#ifdef COMPRESSION_USE_BLOSC
inline void toBloscParams(Level level, int& outLevel, int& outShuffle)
{
    switch (level)
    {
    case Level::BestCompression:
        outLevel = 9;
        outShuffle = BLOSC_BITSHUFFLE;
        break;
    case Level::BestSpeed:
        outLevel = 1;
        outShuffle = BLOSC_NOSHUFFLE;
        break;
    case Level::LibraryDefault:
        // from the examples
        outLevel = 5;
        outShuffle = 1;
        break;
    }
}
#endif

inline size_t maximumSupportedSize(CompressionLibrary lib)
{
    switch (lib)
    {
    case CompressionLibrary::Zlib:
        return (size_t)std::numeric_limits<uLongf>::max();
#ifdef COMPRESSION_USE_BLOSC
    case CompressionLibrary::Blosc:
        return (size_t)std::numeric_limits<int>::max();
#endif
    }
    return 0;
}

inline CompressionResult compressArrayZlib(const void* source_data,
                                           size_t source_length,
                                           void* destination,
                                           size_t& destination_length,
                                           Level level = Level::BestCompression)
{
    if (source_length > maximumSupportedSize(CompressionLibrary::Zlib))
    {
        destination_length = 0;
        return CompressionResult::SizeError;
    }

    uLongf destination_length_u = (uLongf)destination_length;
    int return_value = compress2((Bytef*)destination, &destination_length_u, (const Bytef*)source_data,
                                 (uLongf)source_length, toZlibLevel(level));
    destination_length = (size_t)destination_length_u;
    return return_value == Z_OK ? CompressionResult::Success : CompressionResult::CompressionError;
}

inline CompressionResult compressArray(const void* source_data,
                                      size_t source_length,
                                      void* destination,
                                      size_t& destination_length,
                                      Level level = Level::BestCompression,
                                      CompressionLibrary lib = CompressionLibrary::Default)
{
    switch (lib)
    {
    case CompressionLibrary::Zlib:
        return compressArrayZlib(source_data, source_length, destination, destination_length, level);
#ifdef COMPRESSION_USE_BLOSC
    case CompressionLibrary::Blosc:
    {
        if (source_length > maximumSupportedSize(lib))
        {
            destination_length = 0;
            return CompressionResult::SizeError;
        }

        int clevel = 5, shuffle = 1;
        toBloscParams(level, clevel, shuffle);
        int compressed_size = blosc_compress(clevel, shuffle, sizeof(uint8_t), source_length, source_data, destination, destination_length);
        if (compressed_size <= 0)
        {
            return CompressionResult::CompressionError;
        }
        destination_length = (size_t)compressed_size;
        return CompressionResult::Success;
    }
#endif
    default:
        return compressArrayZlib(source_data, source_length, destination, destination_length, level);
    }
}

inline size_t compressionBound(size_t source_length, CompressionLibrary lib = CompressionLibrary::Default)
{
    switch (lib)
    {
    case CompressionLibrary::Zlib:
        return compressBound(uLongf(source_length));
#ifdef COMPRESSION_USE_BLOSC
    case CompressionLibrary::Blosc:
        return source_length + BLOSC_MAX_OVERHEAD;
#endif
    default:
        return source_length;
    }
}

// Compresses an array
// - source_data: pointer to source data
// - source_length: length of the source data in bytes
// - destination: vector to store the results, it is resized to store the output and the header data
//                the size of the output is stored at the beginning as size_t, after the user header (see header_length)
// - header_length: optional extra space to allocate at the beginning of destination for user data
inline CompressionResult compressVector(const void* source_data,
                                        size_t source_length,
                                        std::vector<uint8_t>& destination,
                                        size_t header_length = 0,
                                        Level level = Level::Default,
                                        CompressionLibrary lib = CompressionLibrary::Default)
{
    CARB_PROFILE_ZONE(1, "compressVector");
    if (source_length > maximumSupportedSize(lib))
    {
        return CompressionResult::SizeError;
    }

    size_t destination_length = compressionBound(source_length);
    destination.resize(destination_length + sizeof(size_t) + header_length);

    CompressionResult return_value = compressArray(source_data, source_length, destination.data() + sizeof(size_t) + header_length, destination_length, level, lib);
    destination.resize(destination_length + sizeof(size_t) + header_length);
    *(size_t*)(destination.data() + header_length) = source_length;
    return return_value;
}

inline CompressionResult uncompressArrayZlib(const void* source_data,
                                           size_t source_length,
                                           void* destination,
                                           size_t& destination_length)
{
    if (source_length > maximumSupportedSize(CompressionLibrary::Zlib))
    {
        destination_length = 0;
        return CompressionResult::SizeError;
    }

    uLongf destination_length_u = (uLongf)destination_length;
    int return_value = uncompress((Bytef*)destination, &destination_length_u, (const Bytef*)source_data, uLongf(source_length));
    destination_length = (size_t)destination_length_u;
    return return_value == Z_OK ? CompressionResult::Success : CompressionResult::CompressionError;
}

inline CompressionResult decompressArray(const void* source_data,
                                       size_t source_length,
                                       void* destination,
                                       size_t& destination_length,
                                       CompressionLibrary lib = CompressionLibrary::Default)
{
    if (source_length > maximumSupportedSize(lib))
    {
        destination_length = 0;
        return CompressionResult::SizeError;
    }

    switch (lib)
    {
    case CompressionLibrary::Zlib:
        return uncompressArrayZlib(source_data, source_length, destination, destination_length);
#ifdef COMPRESSION_USE_BLOSC
    case CompressionLibrary::Blosc:
    {
        int decompressed_size = blosc_decompress(source_data, destination, destination_length);
        if (decompressed_size < 0)
        {
            return CompressionResult::CompressionError;
        }
        destination_length = (size_t)decompressed_size;
        return CompressionResult::Success;
    }
#endif
    default:
        return uncompressArrayZlib(source_data, source_length, destination, destination_length);
    }
}

inline CompressionResult decompressVector(const void* source_data,
                                          size_t source_length,
                                          std::vector<uint8_t>& destination,
                                          CompressionLibrary lib = CompressionLibrary::Default)
{
    CARB_PROFILE_ZONE(1, "decompressVector");
    if (source_length > maximumSupportedSize(lib))
    {
        return CompressionResult::SizeError;
    }

    size_t destination_length = *(size_t*)source_data;
    destination.resize(destination_length);
    CompressionResult return_value = decompressArray((uint8_t*)source_data + sizeof(size_t), source_length - sizeof(size_t), destination.data(), destination_length, lib);
    destination.resize(destination_length);
    return return_value;
}

#ifdef COMPRESSION_USE_BLOSC

inline int compressionInitBlosc(const char* compressor = "lz4hc", const int nThreads = 16)
{
    blosc_init();
    blosc_set_nthreads(nThreads);

    return blosc_set_compressor(compressor);
}

#endif

inline void compressionInit(CompressionLibrary lib = CompressionLibrary::Default)
{
    switch (lib)
    {
    case CompressionLibrary::Zlib:
        // do nothing
        break;
#ifdef COMPRESSION_USE_BLOSC
    case CompressionLibrary::Blosc:
        compressionInitBlosc();
        break;
#endif
    }
}

inline void compressionDestroy(CompressionLibrary lib = CompressionLibrary::Default)
{
    switch (lib)
    {
    case CompressionLibrary::Zlib:
        // do nothing
        break;
#ifdef COMPRESSION_USE_BLOSC
    case CompressionLibrary::Blosc:
        blosc_destroy();
        break;
#endif
    }
}

// wrapper around the C-style API for more convenient use
template<CompressionLibrary lib>
class Compression
{
public:
    Compression()
    {
        omni::compression::compressionInit(lib);
    }

    ~Compression()
    {
        omni::compression::compressionDestroy(lib);
    }

    inline size_t compressionBound(size_t source_length) const
    {
        return omni::compression::compressionBound(source_length, lib);
    }

    inline size_t maximumSupportedSize() const
    {
        return omni::compression::maximumSupportedSize(lib);
    }

    inline CompressionResult compressArray(const void* source_data,
                                           size_t source_length,
                                           void* destination,
                                           size_t& destination_length,
                                           Level level = Level::BestCompression) const
    {
        return omni::compression::compressArray(source_data, source_length, destination, destination_length, level, lib);
    }

    inline CompressionResult compressVector(const void* source_data,
                                            size_t source_length,
                                            std::vector<uint8_t>& destination,
                                            size_t header_length = 0,
                                            Level level = Level::Default) const
    {
        return omni::compression::compressVector(source_data, source_length, destination, header_length, level, lib);
    }

    inline CompressionResult decompressArray(const void* source_data,
                                             size_t source_length,
                                             void* destination,
                                             size_t& destination_length) const
    {
        return omni::compression::decompressArray(source_data, source_length, destination, destination_length, lib);
    }

    inline CompressionResult decompressVector(const void* source_data,
                                              size_t source_length,
                                              std::vector<uint8_t>& destination) const
    {
        return omni::compression::decompressVector(source_data, source_length, destination, lib);
    }
};

} // namespace compression
} // namespace omni
