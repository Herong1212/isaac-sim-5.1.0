// Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <vector>
#include <atomic>
#include <algorithm>
#include <array>
#include <carb/Types.h>
#include <carb/tasking/ITasking.h>
#include <omni/utils/BitScan.h>
#include <omni/utils/Atomic.h>

namespace omni
{
    //--------------------------------------------------------------------------------------------------------
    // A hierarchical bit vector
    // Instead of just storing a flat list of bits, the hierarchical bitvector stores multiple levels of bits (depending on the overall capacity)
    // The lowest level is just the flat bits, while each higher level indicates whether any bit is set within the lower level bits represented by the higher level.
    // This allows fast iteration of sparsely set bits and fast clearing of the whole bitvector.
    // Schematic for 4 bits per "word" and WORDSPERGROUPSHIFT=0 - real vector has 64
    // level 0: 1111 1111 0000 0001 0000 0000 0100 0000 0000 0000 0000 0000 0100 0000 0000 0000
    // level 1:                1101                0010                0000                1000
    // level 2:                                                                            1101
    // Traversal to find a set bit then starts at level2, descends down on each set bit and iterates the whole word before ascending again.
    // This means that only the (smaller) higher levels need to be relocated when the capacity grows.
    struct HiBitVector
    {
        using Storage = std::vector<uint64_t>; // could be made a template argument if necessary, e.g. to use a reserved vector as storage

        constexpr static size_t BITS_WORD = 64;
        constexpr static size_t BITS_WORD_MINUS_ONE = 63;
        constexpr static size_t WORDSPERGROUPSHIFT = 2;
        constexpr static size_t WORDSPERGROUP = 1 << WORDSPERGROUPSHIFT; // words per group determines how many words are merged together into a single bit in the next hierarchy level (see comments above)
        constexpr static size_t WORDSPERGROUPSHIFT_VALUE = WORDSPERGROUPSHIFT;
        constexpr static size_t C_MAX_LEVELS = 2;
        constexpr static size_t C_MIN_CAPACITY = 1024;

        // reserve storage for a given number of bits
        void reserve(size_t capacity);
        // resize the vector to the given size, filling new values with the newValue
        void resize(size_t size, bool newValue);

        // retrieve the current capacity in bits
        size_t capacity() const;
        // retrieve the current size in bits
        size_t size() const;
        // get the value of a given bit index
        bool get(size_t index) const;
        // sets a new bit and returns the old value
        bool set(size_t index, bool value);
        // sets a new bit atomically and returns the previous value so that e.g. a cleared value that becomes set only returns false a single time
        bool setAtomic(size_t index, bool value);
        // marks a new bit true atomically and returns the previous value so that e.g. a cleared value that becomes set only returns false a single time
        bool markAtomic(size_t index);
        // sets all values
        void setAll(bool value);
        // sets all values within a range
        template<bool useAtomicAccess = false>
        void setRange(size_t start, size_t count, bool value);
        // runs functor on all set bits void(size_t idx)
        template<typename T>
        void forEachSet(T callback) const;
        // runs functor on all set bits from multiple threads
        template<typename T>
        void forEachSetParallel(T callback) const;
        // whether any bit is set
        bool isEmpty() const;
        // counts the number of bits set
        size_t countSet() const;

        // access to the storage words based on the bit-index (not word index)
        uint64_t getWord(size_t index) const;
        uint64_t getWord(size_t index, size_t level) const;

        // finds the first set bit given a startindex for the search, using the hierarchy 
        size_t findFirst(size_t startIndex) const;
        // computes the storage in storage words (uint64_t) required for the given capacity
        static size_t computeStorage(size_t capacity);
        // relocate the data to another storage with a new capacity
        void reserveAndRelocate(size_t capacity, Storage&& storage);
    private:
        bool setInternal(size_t index, bool value, size_t level);
        bool setAtomicInternal(size_t index, bool value, size_t level);
        inline bool markAtomicInternal(size_t index, size_t level);
        // clear the bits in the last word beyond size()
        void maskEnd();
        uint64_t& getWordWrite(size_t index);

        // bit data storage
        Storage m_storage;
        // current size of the vector in bits
        size_t m_size = 0;
        // current max capacity of the vector in bits
        size_t m_capacity = 0;
        // number of hierarchical levels inside the bit storage
        size_t m_levels = 0;
        // helper to store the number of bit-words per hierarchy level
        std::array<size_t, C_MAX_LEVELS> m_wordCount;
        // helper to store the index of the starting word for each hiearchy level
        std::array<size_t, C_MAX_LEVELS> m_startWord;

    public:
        // utils
        struct HiBitArrayIterator
        {
            const HiBitVector& array;
            size_t idx;

            HiBitArrayIterator(const HiBitVector& array_, size_t startIndex)
                : array(array_)
                , idx(startIndex)
            {
                findFirst();
            }

            HiBitArrayIterator(const HiBitVector& array_)
                : array(array_)
                , idx(array.size())
            {
            }

            bool operator!=(const HiBitArrayIterator& other) const { CARB_ASSERT(&other.array == &this->array); return idx != other.idx; }
            size_t operator*() const { return idx; }

            HiBitArrayIterator& operator++()
            {
                findNext();
                return *this;
            }

            bool findNextInWord()
            {
                if ((idx >= array.size()))
                    return false;

                // TODO - use intrinsics __builtin_ctzl(bitset)
                uint64_t mask = ~((uint64_t(1) << (idx & BITS_WORD_MINUS_ONE)) - 1);
                if ((array.getWord(idx) & mask) == 0)
                {
                    // nothing in whole word, can just skip
                    idx = std::min((idx & ~BITS_WORD_MINUS_ONE) + BITS_WORD, array.size());
                    return false;
                }
                else
                {
                    int32_t bitIdx = findLsb(array.getWord(idx) & mask);
                    idx = std::min(bitIdx >= 0 ? (idx & ~BITS_WORD_MINUS_ONE) + bitIdx : (idx & ~BITS_WORD_MINUS_ONE) + BITS_WORD, array.size());
                    return bitIdx >= 0;
                }
            }

            void findFirst()
            {
                idx = array.findFirst(idx);
            }

            void findNext()
            {
                idx++;
                if (!findNextInWord() && (idx < array.size()))
                {
                    findFirst();
                }
            }
        };

        inline HiBitArrayIterator begin() { return { *this, 0 }; }
        inline HiBitArrayIterator end() { return { *this }; }
    };

    inline void HiBitVector::reserve(size_t capacity)
    {
        Storage newStorage;
        reserveAndRelocate(capacity, std::move(newStorage));
    }

    inline size_t HiBitVector::computeStorage(size_t capacity)
    {
        // calculate the start locations of the hierarchy levels
        size_t wordCount = CARB_ROUNDUP(capacity, BITS_WORD) / BITS_WORD;
        size_t totalWordCount = wordCount;
        size_t newLevels = 1;
        while ((wordCount >= WORDSPERGROUP * BITS_WORD) && (newLevels < C_MAX_LEVELS))
        {
            wordCount = (wordCount + (WORDSPERGROUP * BITS_WORD - 1)) / (WORDSPERGROUP * BITS_WORD);
            totalWordCount += wordCount;
            newLevels++;
        }
        return totalWordCount;

    }

    inline void HiBitVector::resize(size_t size, bool newValue)
    {
        if (size > m_capacity)
        {
            reserve(std::max(size, m_capacity * 2 + C_MIN_CAPACITY));
        }
        size_t oldSize = m_size;
        m_size = size;
        if (size > oldSize)
        {
            setRange(oldSize, size - oldSize, newValue);
        }
        // we need to always clear the end because bits might be left untouched by large prior resizing that only cleared the bits in the previous tail word
        maskEnd();
    }

    inline size_t HiBitVector::capacity() const
    {
        return m_capacity;
    }

    inline size_t HiBitVector::size() const
    {
        return m_size;
    }

    inline bool HiBitVector::get(size_t index) const
    {
        CARB_ASSERT(index < m_size);
        return (m_storage[index / BITS_WORD] & (uint64_t(1) << (index & BITS_WORD_MINUS_ONE))) > 0;
    }

    inline bool HiBitVector::set(size_t index, bool value)
    {
        CARB_ASSERT(index < m_size);
        return setInternal(index, value, 0);
    }

    inline bool HiBitVector::markAtomic(size_t index)
    {
        CARB_ASSERT(index < m_size);
        return markAtomicInternal(index, 0);
    }

    inline bool HiBitVector::setAtomic(size_t index, bool value)
    {
        CARB_ASSERT(index < m_size);
        return setAtomicInternal(index, value, 0);
    }

    template<bool useAtomicAccess>
    inline void HiBitVector::setRange(size_t start, size_t count, bool value)
    {
        if (!count)
        {
            return;
        }

        CARB_ASSERT(start < m_size);
        CARB_ASSERT(start + count <= m_size);

        size_t startWord = start / BITS_WORD;
        size_t endWord = (start + count) / BITS_WORD;

        uint64_t startMask = ((uint64_t(1) << (start & BITS_WORD_MINUS_ONE)) - 1);
        uint64_t endMask = ~((uint64_t(1) << ((start + count) & BITS_WORD_MINUS_ONE)) - 1);
        uint64_t valueMask = value ? ~uint64_t(0) : 0;

        if (startWord == endWord)
        {
            uint64_t& startData = m_storage[startWord];
            modifyAtomicValue<useAtomicAccess>(startData, [&](uint64_t val) { return (val & (startMask | endMask)) + (valueMask & ~(startMask | endMask)); });
        }
        else
        {
            uint64_t& startData = m_storage[startWord];
            modifyAtomicValue<useAtomicAccess>(startData, [&](uint64_t val) { return (val & (startMask)) + (valueMask & ~(startMask)); });

            if (~endMask)
            {
                uint64_t& endData = m_storage[endWord];
                modifyAtomicValue<useAtomicAccess>(endData, [&](uint64_t val) { return (val & (endMask)) + (valueMask & ~(endMask)); });
            }

            size_t innerStartWord = startWord + 1;
            for (size_t w = innerStartWord; w < endWord; w++)
            {
                uint64_t& data = m_storage[w];
                data = valueMask;
            }
        }

        if (value && count && (m_levels > 1))
        {
            // iterate all the bits represented by this range in the next level
            size_t endIndex = start + count - 1;
            for (size_t w = (startWord / WORDSPERGROUP); w <= (endIndex / BITS_WORD) / WORDSPERGROUP; w++)
            {
                if (useAtomicAccess)
                {
                    setAtomicInternal(w + m_startWord[1] * BITS_WORD, true, 1);
                }
                else
                {
                    setInternal(w + m_startWord[1] * BITS_WORD, true, 1);
                }
            }
        }
    }

    inline bool HiBitVector::setInternal(size_t index, bool value, size_t level)
    {
        uint64_t& data = m_storage[index / BITS_WORD];
        uint64_t mask = uint64_t(1) << (index & BITS_WORD_MINUS_ONE);
        bool oldValue = (data & mask) > 0;
        data = (data & ~mask) + (value ? mask : 0);
        if (value && !oldValue && (level + 1 < m_levels))
        {
            // flag wasn't set previously, propagate upwards
            setInternal(m_startWord[level + 1] * BITS_WORD + ((index / BITS_WORD - m_startWord[level]) / WORDSPERGROUP), true, level + 1);
        }
        return oldValue;
    }

    inline bool HiBitVector::markAtomicInternal(size_t index, size_t level)
    {
        uint64_t& data = m_storage[index / BITS_WORD];
        uint64_t mask = uint64_t(1) << (index & BITS_WORD_MINUS_ONE);
        auto dataPtr = makeAtomic(data);
        uint64_t oldData = 0;
        oldData = dataPtr.load(std::memory_order_relaxed);
        if ((oldData & mask) != mask)
        {
            oldData = dataPtr.fetch_or(mask, std::memory_order_relaxed);
            if (((oldData & mask) == 0) && (level + 1 < m_levels))
            {
                // flag wasn't set previously, propagate upwards
                markAtomicInternal(m_startWord[level + 1] * BITS_WORD + ((index / BITS_WORD - m_startWord[level]) / WORDSPERGROUP), level + 1);
            }
        }
        return (oldData & mask) > 0;
    }

    inline bool HiBitVector::setAtomicInternal(size_t index, bool value, size_t level)
    {
        uint64_t& data = m_storage[index / BITS_WORD];
        uint64_t mask = uint64_t(1) << (index & BITS_WORD_MINUS_ONE);
        auto dataPtr = makeAtomic(data);
        uint64_t oldData = 0;
        if (value)
        {
            oldData = dataPtr.load(std::memory_order_relaxed);
            if ((oldData & mask) != mask)
            {
                oldData = dataPtr.fetch_or(mask, std::memory_order_relaxed);
                if (((oldData & mask) == 0) && (level + 1 < m_levels))
                {
                    // flag wasn't set previously, propagate upwards
                    setAtomicInternal(m_startWord[level + 1] * BITS_WORD + ((index / BITS_WORD - m_startWord[level]) / WORDSPERGROUP), true, level + 1);
                }
            }
        }
        else
        {
            oldData = dataPtr.load(std::memory_order_relaxed);
            if ((oldData & mask) != 0)
            {
                oldData = dataPtr.fetch_and(~mask, std::memory_order_relaxed);
            }
            // TODO - could potentially propagate cleared state upwards
        }
        return (oldData & mask) > 0;
    }

    inline void HiBitVector::maskEnd()
    {
        // make sure everything after size in the last word is zero
        uint64_t endMask = ((uint64_t(1) << (size() & BITS_WORD_MINUS_ONE)) - 1);
        if (endMask)
        {
            getWordWrite(size() - 1) &= endMask;
        }
    }    

    inline void HiBitVector::setAll(bool value)
    {
        if (CARB_UNLIKELY(!m_size))
        {
            return;
        }

        if (value || (m_levels == 1))
        {
            uint64_t mask = value ? ~uint64_t(0) : 0;
            for (size_t i = 0; i < m_storage.size(); i++)
                m_storage[i] = mask;

            maskEnd();
        }
        else
        {
            size_t currentIdx[C_MAX_LEVELS];
            size_t currentEnd[C_MAX_LEVELS];
            memset(currentIdx, 0, sizeof(currentIdx));
            memset(currentEnd, 0, sizeof(currentEnd));
            size_t currentLevel = m_levels - 1;
            currentIdx[currentLevel] = m_startWord[currentLevel];
            currentEnd[currentLevel] = m_startWord[currentLevel] + m_wordCount[currentLevel];
            while (currentLevel < m_levels)
            {
                while ((currentIdx[currentLevel] < currentEnd[currentLevel]) && !m_storage[currentIdx[currentLevel]])
                {
                    currentIdx[currentLevel]++;
                }

                if (currentIdx[currentLevel] < currentEnd[currentLevel])
                {
                    size_t oldIdx = currentIdx[currentLevel];
                    m_storage[currentIdx[currentLevel]] = 0;
                    currentIdx[currentLevel]++;

                    const size_t childLevel = currentLevel - 1;
                    const size_t childLevelStartWord =
                        m_startWord[childLevel] + (oldIdx - m_startWord[currentLevel]) * WORDSPERGROUP * BITS_WORD;
                    const size_t childLevelEndWord =
                        std::min(childLevelStartWord + WORDSPERGROUP * BITS_WORD, m_startWord[childLevel] + m_wordCount[childLevel]);

                    if (currentLevel == 1)
                    {
                        // directly clear level 0
                        const size_t wordsToClear = childLevelEndWord - childLevelStartWord;
                        memset(&m_storage[childLevelStartWord], 0, sizeof(uint64_t) * wordsToClear);
                    }
                    else
                    {
                        CARB_ASSERT(currentLevel > 0);
                        currentIdx[currentLevel - 1] = childLevelStartWord;
                        currentEnd[currentLevel - 1] = childLevelEndWord;
                        currentLevel--;
                    }
                }
                else
                {
                    currentLevel++;
                }
            }
        }
    }

    inline uint64_t HiBitVector::getWord(size_t index) const
    {
        return m_storage[index / BITS_WORD];
    }

    inline uint64_t& HiBitVector::getWordWrite(size_t index)
    {
        return m_storage[index / BITS_WORD];
    }

    inline size_t HiBitVector::findFirst(size_t startIndex) const
    {
        for (size_t i = 0; i < m_levels;)
        {
            size_t level = m_levels - 1 - i;
            // Each level stores 4 words per group and 64 bits per word, hence 1 << (2 + 6)
            size_t levelSize = (uint64_t(1) << ((WORDSPERGROUPSHIFT_VALUE + 6) * level));
            size_t bitIndexRemainder = startIndex & (levelSize - 1);
            size_t bitIndex = startIndex / levelSize;
            size_t endIndex = std::min(bitIndex + WORDSPERGROUP * BITS_WORD, (m_size + levelSize - 1) / levelSize);

            while ((bitIndex < endIndex) && !m_storage[m_startWord[level] + bitIndex / BITS_WORD])
            {
                bitIndex += BITS_WORD;
                bitIndexRemainder = 0;
            }

            if (bitIndex < endIndex)
            {
                int32_t currentBitIdx = bitIndex & BITS_WORD_MINUS_ONE;
                int32_t bitIdx = findLsb(m_storage[m_startWord[level] + bitIndex / BITS_WORD] >> currentBitIdx);
                if (bitIdx >= 0)
                {
                    bitIndex += bitIdx;
                    bitIndexRemainder = bitIdx ? 0 : bitIndexRemainder; // if we skipped a bit here, the remainder for the next lower level is 0 as we restart at the first bit of that level
                }
                else
                {
                    bitIndex = endIndex;
                }
            }

            // clearing of bits is not propagated upwards, so we need to skip back up and search for the next bit if a lower level doesn't contain any bits
            if (bitIndex >= endIndex)
            {
                startIndex = bitIndex * levelSize;
                if ((startIndex >= m_size) || !i)
                {
                    return m_size;
                }
                // go up one level
                i--;
                continue;
            }

            startIndex = bitIndex * levelSize + bitIndexRemainder;
            i++;
        }

        return startIndex;
    }

    template<typename T>
    inline void HiBitVector::forEachSet(T callback) const
    {
        if (CARB_UNLIKELY(!m_size))
        {
            return;
        }

        size_t currentIdx[C_MAX_LEVELS];
        size_t currentEnd[C_MAX_LEVELS];
        for (size_t i = 0; i < m_levels; i++)
        {
            currentIdx[i] = 0;
            currentEnd[i] = 0;
        }
        uint64_t currentWordStorage[C_MAX_LEVELS];
        for (size_t i = 0; i < m_levels; i++)
        {
            currentWordStorage[i] = 0;
        }
        size_t currentLevel = m_levels - 1;
        currentEnd[currentLevel] = m_wordCount[currentLevel] * BITS_WORD;
        while (currentLevel < m_levels)
        {
            size_t bitIndex = currentIdx[currentLevel];
            if (!currentWordStorage[currentLevel])
            {
                // find new word
                while ((bitIndex < currentEnd[currentLevel]) && !m_storage[m_startWord[currentLevel] + bitIndex / BITS_WORD])
                {
                    bitIndex += BITS_WORD;
                }

                currentWordStorage[currentLevel] = bitIndex < currentEnd[currentLevel] ? m_storage[m_startWord[currentLevel] + bitIndex / BITS_WORD] : 0;
            }

            if (bitIndex < currentEnd[currentLevel])
            {
                // found a word with a set bit
                uint64_t currentWord = currentWordStorage[currentLevel];
                if (currentLevel == 0)
                {
                    if (bitIndex >= size())
                    {
                        // reached the end
                        return;
                    }

                    // lowest level, so call the callback for each set bit
                    while (currentWord)
                    {
                        int32_t bitIdx = findLsb(currentWord);
                        CARB_ASSERT(bitIndex + bitIdx < m_size);
                        callback(bitIndex + bitIdx);
                        currentWord &= ~(uint64_t(1) << bitIdx);
                    }
                    currentWordStorage[currentLevel] = 0;
                    currentIdx[currentLevel] = bitIndex + BITS_WORD;
                }
                else
                {
                    // find first bit and descend a level
                    int32_t bitIdx = findLsb(currentWord);
                    CARB_ASSERT(bitIdx != -1); // we must have found something in this word, otherwise we would have skipped the word before
                    currentWordStorage[currentLevel] &= ~(uint64_t(1) << bitIdx); // mask the bit from the current word
                    currentIdx[currentLevel] = bitIndex;
                    if (!currentWordStorage[currentLevel])
                    {
                        currentIdx[currentLevel] += BITS_WORD;
                    }

                    currentLevel--;
                    currentWordStorage[currentLevel] = 0;
                    currentIdx[currentLevel] = (bitIndex + bitIdx) * WORDSPERGROUP * BITS_WORD;
                    currentEnd[currentLevel] = std::min(currentIdx[currentLevel] + WORDSPERGROUP * BITS_WORD, m_wordCount[currentLevel] * BITS_WORD);
                }
            }
            else
            {
                currentLevel++;
            }
        }
    }

    // counts the number of bits set
    inline size_t HiBitVector::countSet() const
    {
        size_t count = 0;
        forEachSet([&](size_t idx) { count++; });
        return count;
    }

    template<typename T>
    inline void HiBitVector::forEachSetParallel(T callback) const
    {
        std::vector<size_t> indices;
        indices.reserve(1024);
        forEachSet([&indices](size_t idx) { indices.push_back(idx); });

        carb::tasking::ITasking* tasking = carb::getCachedInterface<carb::tasking::ITasking>();
        CARB_ASSERT(tasking);
        tasking->applyRangeBatch(indices.size(), 0, [&indices, &callback](size_t idx, size_t end) {
            for (; idx != end; ++idx)
                callback(indices[idx]);
        });
    }

    inline void HiBitVector::reserveAndRelocate(size_t capacity, Storage&& newStorage)
    {
        std::array<size_t, C_MAX_LEVELS> newWordCount;
        std::array<size_t, C_MAX_LEVELS> newStartWord;

        // calculate the start locations of the hierarchy levels
        size_t wordCount = CARB_ROUNDUP(capacity, BITS_WORD) / BITS_WORD;
        size_t totalWordCount = wordCount;
        size_t remainingWordCount = wordCount;
        size_t startLocation = wordCount;
        newWordCount[0] = wordCount;
        newStartWord[0] = 0;
        size_t newLevels = 1;
        while ((remainingWordCount >= WORDSPERGROUP * BITS_WORD) && (newLevels < C_MAX_LEVELS))
        {
            newWordCount[newLevels] = (remainingWordCount + (WORDSPERGROUP * BITS_WORD - 1)) / (WORDSPERGROUP * BITS_WORD);
            newStartWord[newLevels] = startLocation;
            totalWordCount += newWordCount[newLevels];
            startLocation += newWordCount[newLevels];
            newLevels++;
            remainingWordCount = newWordCount[newLevels - 1];
        }
        newStorage.resize(totalWordCount, 0);
        size_t wordsToCopy = std::min(newStorage.size(), m_storage.size());
        if (wordsToCopy)
        {
            memcpy(newStorage.data(), m_storage.data(), sizeof(uint64_t) * wordsToCopy);
        }

        // now copy the hierarchy masks to their new location
        uint64_t* source = m_storage.data();
        uint64_t* dest = newStorage.data();

        for (size_t i = 1; i < m_levels; i++)
        {
            // start from the highest level as it will move to the end of the new capacity
            size_t level = m_levels - i;

            // copy the words that already existed
            for (size_t n = 0; n < m_wordCount[level]; n++)
            {
                // start from the back as the target might overlap the source
                size_t word = m_wordCount[level] - 1 - n;
                dest[newStartWord[level] + word] = source[m_startWord[level] + word];
            }
            // clear the rest
            for (size_t n = m_wordCount[level]; n < newWordCount[level]; n++)
            {
                dest[newStartWord[level] + n] = 0;
            }
        }

        // initialize new levels from their lower levels
        for (size_t level = std::max(size_t(1), m_levels); level < newLevels; level++)
        {
            for (size_t n = 0; n < newWordCount[level]; n++)
            {
                uint64_t word = 0;

                for (size_t m = 0; m < BITS_WORD; m++)
                {
                    const size_t lowerLevelWordGroupOffset = n * WORDSPERGROUP * BITS_WORD + m * WORDSPERGROUP;
                    if (lowerLevelWordGroupOffset >= newWordCount[level - 1])
                    {
                        break;
                    }

                    bool isSet = false;
                    for (size_t d = 0; (d < WORDSPERGROUP) && !isSet; d++)
                    {
                        const size_t lowerLevelWordOffset = lowerLevelWordGroupOffset + d;

                        if (lowerLevelWordOffset >= newWordCount[level - 1])
                        {
                            break;
                        }

                        isSet |= dest[newStartWord[level - 1] + lowerLevelWordOffset] > 0;
                    }
                    word |= isSet ? (uint64_t(1) << m) : 0;
                }

                dest[newStartWord[level] + n] = word;
            }
        }

        m_levels = newLevels;
        m_startWord = newStartWord;
        m_wordCount = newWordCount;
        m_capacity = wordCount * BITS_WORD;
        m_storage = std::move(newStorage);
    }

    inline bool HiBitVector::isEmpty() const
    {
        for (size_t i = 0; i < m_wordCount[m_levels - 1]; i++)
        {
            if (m_storage[m_startWord[m_levels - 1] + i])
                return false;
        }

        return true;
    }
} // namespace omni
