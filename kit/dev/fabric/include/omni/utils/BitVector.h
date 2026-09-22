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
#include <carb/Types.h>
#include <carb/tasking/ITasking.h>
#include <omni/utils/BitScan.h>
#include <omni/utils/SmallVector.h>
#include <omni/utils/Atomic.h>

namespace omni
{
    //----------------------------------------------------------------------------------------------------------------------------------------------------------------
    // A bitvector for fast lock-free manipulation of bits
    template<typename StorageType>
    struct BitVectorBase
    {
        constexpr static size_t BITS_WORD = 64;
        constexpr static size_t BITS_WORD_MINUS_ONE = 63;

        // reserve capacity for a given number of bits
        void reserve(size_t capacity);
        // resize to a given number of bits and set all values beyond the current size to the new value
        void resize(size_t size, bool newValue);

        size_t capacity() const;
        size_t size() const;

        // returns the value of a given bit
        bool get(size_t index) const;
        // sets a new bit and returns the old value
        bool set(size_t index, bool value);
        // sets a new bit atomically and returns the previous value so that e.g. a cleared value that becomes set only returns false a single time
        bool setAtomic(size_t index, bool value);
        // sets all values
        void setAll(bool value);
        // sets all values within a range
        template<bool useAtomicAccess = false>
        void setRange(size_t start, size_t count, bool value);
        // runs functor on all set bits void(size_t idx)
        template<typename T>
        void forEachSet(T callback) const;
        // runs functor on all cleared bits void(size_t idx)
        template<typename T>
        void forEachCleared(T callback) const;
        // runs functor on all set bits from multiple threads
        template<typename T>
        void forEachSetParallel(T callback) const;
        template<typename T>
        void forEachSetParallel(T callback, std::vector<size_t>& indexVectorStorage) const;

        // finds the first set bit starting at the startindex
        size_t findFirst(size_t startIndex) const;
        // true if no bit is set
        bool isEmpty() const;
        // count the number of set bits
        size_t countSet() const;

        // returns the whole word of bits for a given bit index (not word index)
        const uint64_t& getWord(size_t index) const;
        // returns the next set bit in the word at or after the given bit index
        inline bool findNextInWord(size_t& idx) const;
        // returns the next bit index for a word with a bit set starting at the word of the provided bit index
        inline size_t findNextWord(size_t idx) const;
        // returns the next bit index + BITS_WORD_MINUS_ONE for a word with a bit set in reverse order starting at the word of the provided bit index
        // returns 0 if no word was found
        // note that the resulting index + BITS_WORD_MINUS_ONE can be >= size()
        inline size_t findNextWordRev(size_t idx) const;
        // computes the required storage for a given bit capacity
        static size_t computeStorage(size_t capacity);
        // relocate the data to another storage with a new capacity
        void reserveAndRelocate(size_t capacity, StorageType&& storage);
        // get access to the raw storage
        const StorageType& getStorage() const;
        // get access to the raw storage
        StorageType& getStorage();
    private:
        // returns the byte offset for a given bit index
        size_t getWordOffsetInBytes(size_t index) const;
        // non-const version of getWord
        uint64_t& getWord(size_t index);
        // clear the bits in the last word beyond size()
        void maskEnd();

        StorageType m_storage;
        // current size in bits of the vector
        size_t m_size = 0;
        // current max capacity in bits of the vector
        size_t m_capacity = 0;
    public:
        // utils
        struct BitVectorIterator
        {
            const BitVectorBase<StorageType>& array;
            size_t idx;

            BitVectorIterator(const BitVectorBase<StorageType>& array_, size_t startIndex)
                : array(array_)
                , idx(startIndex)
            {
                findFirst();
            }

            BitVectorIterator(const BitVectorBase<StorageType>& array_)
                : array(array_)
                , idx(array.size())
            {
            }

            bool operator!=(const BitVectorIterator& other) const { CARB_ASSERT(&other.array == &this->array); return idx != other.idx; }
            size_t operator*() const { return idx; }

            BitVectorIterator& operator++()
            {
                findNext();
                return *this;
            }

            void findFirst()
            {
                idx = array.findNextWord(idx);
                array.findNextInWord(idx);
            }

            void findNext()
            {
                idx++;
                if (!array.findNextInWord(idx) && (idx < array.size()))
                {
                    findFirst();
                }
            }
        };

        inline BitVectorIterator begin() { return { *this, 0 }; }
        inline BitVectorIterator end() { return { *this }; }
    };

    template<typename StorageType>
    inline void BitVectorBase<StorageType>::reserve(size_t capacity)
    {
        StorageType newStorage;
        reserveAndRelocate(capacity, std::move(newStorage));
    }

    template<typename StorageType>
    inline void BitVectorBase<StorageType>::reserveAndRelocate(size_t capacity, StorageType&& newStorage)
    {
        newStorage.resize(uint32_t(CARB_ROUNDUP(capacity, BITS_WORD) / BITS_WORD));
        size_t wordsToCopy = std::min(newStorage.size(), m_storage.size());
        if (wordsToCopy)
        {
            size_t offsetInBytes = getWordOffsetInBytes(0);
            size_t sizeInBytes = CARB_ROUNDUP(wordsToCopy * BITS_WORD, BITS_WORD) / BITS_WORD * sizeof(uint64_t);
            CARB_ASSERT(offsetInBytes < newStorage.size() * sizeof(uint64_t));
            CARB_ASSERT(offsetInBytes < m_storage.size() * sizeof(uint64_t));
            CARB_ASSERT(offsetInBytes + sizeInBytes <= newStorage.size() * sizeof(uint64_t));
            CARB_ASSERT(offsetInBytes + sizeInBytes <= m_storage.size() * sizeof(uint64_t));
            memcpy((uint8_t*)newStorage.data() + offsetInBytes, (const uint8_t*)m_storage.data() + offsetInBytes, sizeInBytes);
        }
        m_storage = std::move(newStorage);
        m_capacity = capacity;
    }

    template<typename StorageType>
    inline const StorageType& BitVectorBase<StorageType>::getStorage() const
    {
        return m_storage;
    }

    template<typename StorageType>
    inline StorageType& BitVectorBase<StorageType>::getStorage()
    {
        return m_storage;
    }

    template<typename StorageType>
    inline size_t BitVectorBase<StorageType>::getWordOffsetInBytes(size_t index) const
    {
        return index / BITS_WORD * sizeof(uint64_t);
    }

    template<typename StorageType>
    inline void BitVectorBase<StorageType>::resize(size_t size, bool newValue)
    {
        if (size > m_capacity)
        {
            reserve(std::max(size, m_capacity * 2));
        }
        m_storage.resize(uint32_t(CARB_ROUNDUP(size, BITS_WORD) / BITS_WORD), 0);
        size_t oldSize = m_size;
        m_size = size;
        if (size > oldSize)
        {
            setRange(oldSize, size - oldSize, newValue);
        }
        else if (size && (size < oldSize))
        {
            // clear the bits past the size when we shrink. when we grow there can never be bits past the new size because words are initialized to 0 above
            maskEnd();
        }
    }

    template<typename StorageType>
    inline void BitVectorBase<StorageType>::maskEnd()
    {
        // make sure everything after size in the last word is zero
        uint64_t endMask = ((uint64_t(1) << (size() & BITS_WORD_MINUS_ONE)) - 1);
        if (endMask)
        {
            m_storage.back() &= endMask;
        }
    }

    template<typename StorageType>
    inline size_t BitVectorBase<StorageType>::capacity() const
    {
        return m_storage.capacity() * BITS_WORD;
    }

    template<typename StorageType>
    inline size_t BitVectorBase<StorageType>::size() const
    {
        return m_size;
    }

    template<typename StorageType>
    inline bool BitVectorBase<StorageType>::get(size_t index) const
    {
        CARB_ASSERT(index < m_size);
        uint64_t mask = uint64_t(1) << (index & BITS_WORD_MINUS_ONE);
        return (getWord(index) & mask) > 0;
    }

    template<typename StorageType>
    inline bool BitVectorBase<StorageType>::set(size_t index, bool value)
    {
        CARB_ASSERT(index < m_size);
        uint64_t& data = getWord(index);
        uint64_t mask = uint64_t(1) << (index & BITS_WORD_MINUS_ONE);
        bool oldValue = (data & mask) > 0;
        data = (data & ~mask) + (value ? mask : 0);
        return oldValue;
    }

    template<typename StorageType>
    inline bool BitVectorBase<StorageType>::setAtomic(size_t index, bool value)
    {
        CARB_ASSERT(index < m_size);
        uint64_t& data = getWord(index);
        uint64_t mask = uint64_t(1) << (index & BITS_WORD_MINUS_ONE);
        std::atomic<uint64_t>* dataPtr = (std::atomic<uint64_t>*)&data;
        uint64_t oldData = dataPtr->load(std::memory_order_relaxed);
        bool isSet = (oldData & mask) != 0;
        if (value)
        {
            // before performing a fetch or which can be slow, check if the bit isn't already set
            if (!isSet)
            {
                oldData = dataPtr->fetch_or(mask);
            }
        }
        else
        {
            // before performing a fetch and which can be slow, check if the bit isn't already cleared
            if (isSet)
            {
                oldData = dataPtr->fetch_and(~mask);
            }
        }
        return (oldData & mask) > 0;
    }

    template<typename StorageType>
    inline void BitVectorBase<StorageType>::setAll(bool value)
    {
        uint64_t mask = value ? ~uint64_t(0) : 0;

        if (size())
        {
            uint64_t* startWord = &getWord(0);
            uint64_t* endWord = &getWord(size() - 1);
            for (; startWord <= endWord; startWord++)
                *startWord = mask;

            maskEnd();
        }
    }

    template<typename StorageType>
    template<bool useAtomicAccess>
    inline void BitVectorBase<StorageType>::setRange(size_t start, size_t count, bool value)
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
            uint64_t& startData = m_storage[uint32_t(startWord)];
            modifyAtomicValue<useAtomicAccess>(startData, [&](uint64_t val) { return (val & (startMask | endMask)) + (valueMask & ~(startMask | endMask)); });
        }
        else
        {
            uint64_t& startData = m_storage[uint32_t(startWord)];
            modifyAtomicValue<useAtomicAccess>(startData, [&](uint64_t val) { return (val & (startMask)) + (valueMask & ~(startMask)); });

            if (~endMask)
            {
                uint64_t& endData = m_storage[uint32_t(endWord)];
                modifyAtomicValue<useAtomicAccess>(endData, [&](uint64_t val) { return (val & (endMask)) + (valueMask & ~(endMask)); });
            }

            size_t innerStartWord = startWord + 1;
            for (size_t w = innerStartWord; w < endWord; w++)
            {
                uint64_t& data = m_storage[uint32_t(w)];
                data = valueMask;
            }
        }
    }

    template<typename StorageType>
    inline const uint64_t& BitVectorBase<StorageType>::getWord(size_t index) const
    {
        static constexpr uint64_t emptyWord = 0;
        const uint32_t storageIndex = static_cast<uint32_t>(index / BITS_WORD);
        return storageIndex < m_storage.size() ? m_storage[storageIndex] : emptyWord;
    }

    template<typename StorageType>
    inline uint64_t& BitVectorBase<StorageType>::getWord(size_t index)
    {
        static uint64_t emptyWord = 0;
        emptyWord = 0;

        const uint32_t storageIndex = static_cast<uint32_t>(index / BITS_WORD);
        return storageIndex < m_storage.size() ? m_storage[storageIndex] : emptyWord;
    }

    template<typename StorageType>
    inline bool BitVectorBase<StorageType>::isEmpty() const
    {
        const uint64_t* wordPtr = &getWord(0);
        for (size_t idx = 0; idx < size(); wordPtr++, idx += BITS_WORD)
        {
            if (*wordPtr)
            {
                return false;
            }
        }

        return true;
    }

    // counts the number of bits set
    template<typename StorageType>
    inline size_t BitVectorBase<StorageType>::countSet() const
    {
        size_t bitCount = 0;
        size_t start = 0;
        size_t count = size();
        const uint64_t* wordPtr = &getWord(start);
        for (size_t idx = 0; idx < count; wordPtr++)
        {
            uint64_t currentWord = *wordPtr;
            if (!currentWord)
            {
                idx += BITS_WORD;
                continue;
            }
            bitCount += carb::math::popCount(currentWord);
            idx += BITS_WORD;
        }

        return bitCount;
    }

    template<typename StorageType>
    template<typename T>
    inline void BitVectorBase<StorageType>::forEachSet(T callback) const
    {
        size_t start = 0;
        size_t count = size();
        const uint64_t* wordPtr = &getWord(start);
        for (size_t idx = 0; idx < count; wordPtr++)
        {
            uint64_t currentWord = *wordPtr;
            if (!currentWord)
            {
                idx += BITS_WORD;
                continue;
            }
            while (currentWord)
            {
                int32_t bitIdx = findLsb(currentWord);
                callback(idx + bitIdx);
                currentWord &= ~(uint64_t(1) << bitIdx);
            }
            idx += BITS_WORD;
        }
    }

    template<typename StorageType>
    template<typename T>
    inline void BitVectorBase<StorageType>::forEachCleared(T callback) const
    {
        size_t start = 0;
        size_t count = size();
        const uint64_t* wordPtr = &getWord(start);
        for (size_t idx = 0; idx < count; wordPtr++)
        {
            uint64_t currentWord = *wordPtr;
            currentWord = ~currentWord;
            if (!currentWord)
            {
                idx += BITS_WORD;
                continue;
            }

            if (count - idx < BITS_WORD)
            {
                // make sure to mask off the last bits as the inverting above will have set them
                currentWord &= ~(uint64_t(-1) << (count - idx));
            }

            while (currentWord)
            {
                int32_t bitIdx = findLsb(currentWord);
                callback(idx + bitIdx);
                currentWord &= ~(uint64_t(1) << bitIdx);
            }
            idx += BITS_WORD;
        }
    }

    template<typename StorageType>
    inline size_t BitVectorBase<StorageType>::computeStorage(size_t capacity)
    {
        return CARB_ROUNDUP(capacity, BITS_WORD) / BITS_WORD;
    }

    template<typename StorageType>
    inline size_t BitVectorBase<StorageType>::findNextWord(size_t idx) const
    {
        size_t maxSize = size();
        while ((idx < maxSize) && (getWord(idx) == 0))
            idx += BITS_WORD;

        return std::min(idx, maxSize);
    }

    template<typename StorageType>
    inline size_t BitVectorBase<StorageType>::findNextWordRev(size_t idx) const
    {
        size_t maxSize = size();
        idx = std::min(idx, maxSize - 1);            
        idx = idx & ~BITS_WORD_MINUS_ONE;
        size_t result = 0;
        while (true)
        {
            if (getWord(idx) != 0)
            {
                result = idx + BITS_WORD_MINUS_ONE;
                break;
            }
            else if ((idx == 0))
            {
                break;
            }
            idx -= BITS_WORD;
        }
        return result;
    }

    template<typename StorageType>
    inline bool BitVectorBase<StorageType>::findNextInWord(size_t& idx) const
    {
        if ((idx >= size()))
            return false;

        uint64_t mask = ~((uint64_t(1) << (idx & BITS_WORD_MINUS_ONE)) - 1);
        if ((getWord(idx) & mask) == 0)
        {
            // nothing in whole word, can just skip
            idx = std::min((idx & ~BITS_WORD_MINUS_ONE) + BITS_WORD, size());
            return false;
        }
        else
        {
            uint64_t mask = ~((uint64_t(1) << (idx & BITS_WORD_MINUS_ONE)) - 1);
            int32_t bitIdx = findLsb(getWord(idx) & mask);
            idx = std::min(bitIdx >= 0 ? (idx & ~BITS_WORD_MINUS_ONE) + bitIdx : (idx & ~BITS_WORD_MINUS_ONE) + BITS_WORD, size());
            return bitIdx >= 0;
        }
    }

    template<typename StorageType>
    inline size_t BitVectorBase<StorageType>::findFirst(size_t startIndex) const
    {
        // check first word
        if (findNextInWord(startIndex))
        {
            return startIndex;
        }

        // skip words
        startIndex = findNextWord(startIndex);

        // check in current word
        if (findNextInWord(startIndex))
        {
            return startIndex;
        }
        else
        {
            return size();
        }
    }

    template<typename StorageType>
    template<typename T>
    inline void BitVectorBase<StorageType>::forEachSetParallel(T callback, std::vector<size_t>& indices) const
    {
        indices.clear();
        forEachSet([&indices](size_t idx) { indices.push_back(idx); });

        carb::tasking::ITasking* tasking = carb::getCachedInterface<carb::tasking::ITasking>();
        CARB_ASSERT(tasking);
        tasking->applyRangeBatch(indices.size(), 0, [&indices, &callback](size_t idx, size_t end) {
            for (; idx != end; ++idx)
                callback(indices[idx]);
            });
    }

    template<typename StorageType>
    template<typename T>
    inline void BitVectorBase<StorageType>::forEachSetParallel(T callback) const
    {
        std::vector<size_t> indices;
        indices.reserve(1024);
        forEachSetParallel(callback, indices);
    }

    using BitVector = BitVectorBase<std::vector<uint64_t>>;

    template<uint32_t InplaceStorageSize>
    using InplaceBitVector = BitVectorBase<SmallVector<uint64_t, InplaceStorageSize>>;
}
