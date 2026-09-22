// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <vector>

#include "Defines.h"

#ifdef _WIN32
#    define WINDOWS_LEAN_AND_MEAN
#    include <windows.h>
#    undef min
#    undef max
#    include <intrin.h>
#endif

namespace omni
{
namespace fabric
{
namespace batch
{

// This file contains helper implementations of bit arrays. They are not special in any way.
//
// TODO: Does carb:: provide something similar?
struct BitArrayBase
{
    static BATCH_SHARED_API inline uint32_t mask(const uint32_t index)
    {
        return (1 << (index & 31));
    }

    static BATCH_SHARED_API inline void set(uint32_t* const data, const size_t wordCount, const uint32_t index)
    {
        const size_t wordIndex = index >> 5;
        BATCH_ASSERT(data);
        BATCH_ASSERT(wordIndex < wordCount);
        data[wordIndex] |= mask(index);
    }

    static BATCH_SHARED_API inline void reset(uint32_t* const data, const size_t wordCount, const uint32_t index)
    {
        const size_t wordIndex = index >> 5;
        BATCH_ASSERT(data);
        BATCH_ASSERT(wordIndex < wordCount);
        data[wordIndex] &= ~mask(index);
    }

    static BATCH_SHARED_API inline bool test(const uint32_t* const data, const size_t wordCount, const uint32_t index)
    {
        const size_t wordIndex = index >> 5;
        BATCH_ASSERT(data);
        BATCH_ASSERT(wordIndex < wordCount);
        return data[wordIndex] & mask(index);
    }

    static BATCH_SHARED_API inline void resetRangeInclusive(uint32_t* const data,
                                                            const size_t wordCount,
                                                            const uint32_t begin,
                                                            const uint32_t end)
    {
        BATCH_ASSERT(data);

        const uint32_t firstWord = begin >> 5;
        const uint32_t lastWord = end >> 5;

        if (firstWord == lastWord)
        {
            const uint32_t mask = (~(UINT32_MAX << ((end & 31) - (begin & 31) + 1))) << (begin & 31);
            data[firstWord] |= mask;
        }
        else if (firstWord < lastWord)
        {
            {
                const uint32_t mask = (~(UINT32_MAX << (31 - (begin & 31) + 1))) << (begin & 31);
                data[firstWord] &= ~mask;
            }
            {
                const uint32_t mask = (~(UINT32_MAX << ((end & 31) + 1)));
                data[lastWord] &= ~mask;
            }
            if (lastWord - firstWord > 1)
            {
                memset(&data[firstWord + 1], 0, ((lastWord - firstWord) - 1) * sizeof(uint32_t));
            }
        }
    }

    static BATCH_SHARED_API inline void setRangeInclusive(uint32_t* const data,
                                                          const size_t wordCount,
                                                          const uint32_t begin,
                                                          const uint32_t end)
    {
        BATCH_ASSERT(data);

        const uint32_t firstWord = begin >> 5;
        const uint32_t lastWord = end >> 5;

        if (firstWord == lastWord)
        {
            const uint32_t mask = (~(UINT32_MAX << ((end & 31) - (begin & 31) + 1))) << (begin & 31);
            data[firstWord] |= mask;
        }
        else if (firstWord < lastWord)
        {
            {
                const uint32_t mask = (~(UINT32_MAX << (31 - (begin & 31) + 1))) << (begin & 31);
                data[firstWord] |= mask;
            }
            {
                const uint32_t mask = (~(UINT32_MAX << ((end & 31) + 1)));
                data[lastWord] |= mask;
            }
            if (lastWord - firstWord > 1)
            {
                memset(&data[firstWord + 1], UINT32_MAX, ((lastWord - firstWord) - 1) * sizeof(uint32_t));
            }
        }
    }

    static BATCH_SHARED_API inline void resetAll(uint32_t* const data, const size_t wordCount)
    {
        BATCH_ASSERT(data);
        memset(data, 0, wordCount * sizeof(uint32_t));
    }

    static BATCH_SHARED_API inline void setAll(uint32_t* const data, const size_t wordCount)
    {
        BATCH_ASSERT(data);
        memset(data, UINT32_MAX, wordCount * sizeof(uint32_t));
    }

    static BATCH_SHARED_API size_t findFirstUnset(uint32_t* const data, const size_t wordCount)
    {
#ifdef _WIN32
#    define CLZ32(OUT, V)                                                                                              \
        do                                                                                                             \
        {                                                                                                              \
            DWORD z;                                                                                                   \
            OUT = _BitScanReverse(&z, V) ? 31 - z : 32;                                                                \
        } while (0)
#elif defined(__linux__) // #ifdef _WIN32
#    define CLZ32(OUT, V)                                                                                              \
        do                                                                                                             \
        {                                                                                                              \
            OUT = V ? __builtin_clz(V) : 32;                                                                           \
        } while (0)
#elif __CUDACC__
#    define CLZ32(OUT, V)                                                                                              \
        do                                                                                                             \
        {                                                                                                              \
            OUT = V ? __clz(V) : 32;                                                                                   \
        } while (0)
#else
#    error "Unsupported platform"
#endif

        for (size_t w = 0; w < wordCount; ++w)
        {
            if (data[w] != UINT32_MAX)
            {
                uint32_t lz;
                CLZ32(lz, data[w]);
                return lz + (w << 5);
            }
        }

        return SIZE_MAX;
#undef CLZ32
    }
};

template <size_t BIT_COUNT_REQUESTED>
struct BitArray
{
    static constexpr size_t BIT_COUNT = alignUp(BIT_COUNT_REQUESTED, 32);
    static constexpr size_t WORD_COUNT = (BIT_COUNT >> 5);

    BATCH_SHARED_API inline size_t bitCount() const
    {
        return BIT_COUNT;
    }

    BATCH_SHARED_API inline size_t wordCount() const
    {
        return WORD_COUNT;
    }

    BATCH_SHARED_API inline void set(const uint32_t index)
    {
        BitArrayBase::set(data, WORD_COUNT, index);
    }

    BATCH_SHARED_API inline void reset(const uint32_t index)
    {
        BitArrayBase::reset(data, WORD_COUNT, index);
    }

    BATCH_SHARED_API inline bool test(const uint32_t index) const
    {
        return BitArrayBase::test(data, WORD_COUNT, index);
    }

    BATCH_SHARED_API inline void resetRangeInclusive(const uint32_t begin, const uint32_t end)
    {
        BitArrayBase::resetRangeInclusive(data, WORD_COUNT, begin, end);
    }

    BATCH_SHARED_API inline void setRangeInclusive(const uint32_t begin, const uint32_t end)
    {
        BitArrayBase::setRangeInclusive(data, WORD_COUNT, begin, end);
    }

    BATCH_SHARED_API inline void resetAll()
    {
        BitArrayBase::resetAll(data, WORD_COUNT);
    }

    BATCH_SHARED_API inline void setAll()
    {
        BitArrayBase::setAll(data, WORD_COUNT);
    }

    BATCH_SHARED_API inline size_t findFirstUnset()
    {
        return BitArrayBase::findFirstUnset(data, WORD_COUNT);
    }

    uint32_t data[WORD_COUNT];
};

struct BitArrayDynamic : public BitArrayBase
{
    inline BitArrayDynamic(const size_t bitCount = 32) : buffer(alignUp(bitCount, 32))
    {
    }

    inline size_t bitCount() const
    {
        return wordCount() << 5;
    }

    inline size_t wordCount() const
    {
        return buffer.size();
    }

    inline void set(const uint32_t index)
    {
        growIfNeeded(index + 1);
        BitArrayBase::set(buffer.data(), buffer.size(), index);
    }

    inline void reset(const uint32_t index)
    {
        growIfNeeded(index + 1);
        BitArrayBase::reset(buffer.data(), buffer.size(), index);
    }

    inline bool test(const uint32_t index) const
    {
        return index < bitCount() ? BitArrayBase::test(buffer.data(), buffer.size(), index) : false;
    }

    inline void resetRangeInclusive(const uint32_t begin, const uint32_t end)
    {
        BATCH_ASSERT(begin <= end);
        growIfNeeded(end + 1);
        BitArrayBase::resetRangeInclusive(buffer.data(), buffer.size(), begin, end);
    }

    inline void setRangeInclusive(const uint32_t begin, const uint32_t end)
    {
        BATCH_ASSERT(begin <= end);
        growIfNeeded(end + 1);
        BitArrayBase::setRangeInclusive(buffer.data(), buffer.size(), begin, end);
    }

    inline void resetAll()
    {
        BitArrayBase::resetAll(buffer.data(), buffer.size());
    }

    inline void setAll()
    {
        BitArrayBase::setAll(buffer.data(), buffer.size());
    }

    inline size_t findFirstUnset()
    {
        return BitArrayBase::findFirstUnset(buffer.data(), buffer.size());
    }

    inline void growIfNeeded(const size_t bitCount)
    {
        const size_t newSize = alignUp(bitCount, 32);
        if (newSize > buffer.size())
        {
            buffer.resize(newSize);
        }
    }

    inline void resize(const size_t bitCount)
    {
        const size_t newSize = alignUp(bitCount, 32);
        if (newSize != buffer.size())
        {
            buffer.resize(newSize);
        }
    }

    std::vector<uint32_t> buffer;
};

} // namespace batch
} // namespace fabric
} // namespace omni
