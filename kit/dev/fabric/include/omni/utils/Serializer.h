// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

#pragma once

#include <omni/utils/SmallVector.h>

#include <type_traits>
#include <vector>
#include <utility>

namespace omni
{

template <typename SerializerT, typename ValueT>
void customWrite(SerializerT& serializer, ValueT& value)
{
    customSerialize(serializer, false, value);
}

template <typename SerializerT, typename ValueT>
void customRead(SerializerT& serializer, ValueT& value)
{
    customSerialize(serializer, true, value);
}

template <typename SerializerT, typename ValueT>
void customWrite(SerializerT& serializer, std::vector<ValueT>& valueVector)
{
    serializer.write(valueVector.size());
    for (ValueT& value : valueVector)
    {
        customSerialize(serializer, false, value);
    }
}

template <typename SerializerT, typename ValueT>
void customRead(SerializerT& serializer, std::vector<ValueT>& valueVector)
{
    size_t size = 0;
    serializer.read(size);
    // TODO(chen): size verification
    //             verifySize() won't actually work, as sizeof(T) != actual stored data size
    valueVector.resize(size);
    for (ValueT& value : valueVector)
    {
        customSerialize(serializer, true, value);
    }
}

// simple byte serializer used to serialize/deserialize simple structures
template<typename Allocator, bool readOnly>
struct ByteSerializer
{
    using DataPtr = typename std::conditional<readOnly, const uint8_t*, uint8_t*>::type;

    ByteSerializer() = default;
    ByteSerializer(const ByteSerializer&) = delete;
    ByteSerializer(ByteSerializer&&) = default;
    ByteSerializer& operator=(const ByteSerializer&) = delete;
    ByteSerializer& operator=(ByteSerializer&&) = default;

    DataPtr start = nullptr;
    DataPtr current = nullptr;
    DataPtr end = nullptr;

    template<typename T>
    void write(const std::vector<T>& value);
    template<typename T, std::size_t N>
    void write(const omni::SmallVector<T, N>& value);
    template<typename FirstT, typename SecondT>
    void write(const std::pair<FirstT, SecondT>& value);

    void write(const std::string& value)
    {
        static_assert(!readOnly, "Cannot write to readonly serializer");

        write(value.length());
        write(value.c_str(), value.length());
    }

    void write(const char* value)
    {
        static_assert(!readOnly, "Cannot write to readonly serializer");

        size_t len = value ? strlen(value) : 0;
        write(len + 1);
        write(value, len + 1);
    }

    template<typename T>
    void write(const T& value)
    {
        static_assert(!readOnly, "Cannot write to readonly serializer");
        static_assert(!std::is_array<T>(), "Can only serialize non array types");

        if (verifySize(sizeof(value)))
        {
            *(T*)current = value;
        }
        current += sizeof(T);
    }

    void write(const void* data, size_t size)
    {
        static_assert(!readOnly, "Cannot write to readonly serializer");

        if (verifySize(size))
        {
            memcpy(current, data, size);
        }
        current += size;
    }

    template<typename T>
    void writeArray(const T* ptr, size_t elemCount)
    {
        static_assert(!readOnly, "Cannot write to readonly serializer");

        write(elemCount);
        if (verifySize(sizeof(T) * elemCount))
        {
            memcpy(current, ptr, sizeof(T) * elemCount);
        }
        current += sizeof(T) * elemCount;
    }

    template<typename T>
    void read(std::vector<T>& value);
    template<typename T, std::size_t N>
    void read(omni::SmallVector<T, N>& value);
    template<typename FirstT, typename SecondT>
    void read(std::pair<FirstT, SecondT>& value);
    template <typename T, std::size_t N>
    void read(T(&value)[N]);
    template <typename T, std::size_t N>
    void write(T(&value)[N]);

    void read(std::string& value)
    {
        size_t size = 0;
        read(size);
        // make sure we fail before we potentially do a dangerously large allocation
        if (!verifySize(size))
        {
            // but still act as if we read the data
            current += size;
            return;
        }
        value.resize(size);
        if (size)
        {
            read(&value[0], value.length());
        }
    }

    void read(const char*& value)
    {
        size_t size = 0;
        read(size);
        if (verifySize(size))
        {
            value = (const char*)current;
        }
        else
        {
            value = nullptr;
        }
        current += size;
    }

    template<typename T>
    void read(T& value)
    {
        static_assert(std::is_trivially_copyable<T>::value, "Can only serialize pod types");
        static_assert(!std::is_array<T>(), "Can only serialize non array types");

        if (verifySize(sizeof(value)))
        {
            value = *(const T*)current;
        }
        current += sizeof(T);
    }

    void read(void* data, size_t size)
    {
        if (verifySize(size))
        {
            memcpy(data, current, size);
        }
        current += size;
    }

    bool verifySize(size_t size)
    {
        // current ptr is allowed to go past end ptr, so calculations here should avoid
        // subtraction between the two
        if (uintptr_t(end) < uintptr_t(current + size))
        {
            return derived().grow(size_t(current + size - end));
        }
        return true;
    }

    template<typename T, bool isReadOnly = readOnly>
    void serialize(bool loading, T& value, std::enable_if_t<isReadOnly, bool> = true)
    {
        static_assert(!std::is_same<char*, T>(), "Cannot serialize non-const char*");
        if (loading)
        {
            read(value);
        }
    }

    template<typename T, bool isReadOnly = readOnly>
    void serialize(bool loading, T& value, std::enable_if_t<!isReadOnly, bool> = true)
    {
        static_assert(!std::is_same<char*, T>(), "Cannot serialize non-const char*");
        if (loading)
        {
            read(value);
        }
        else
        {
            write(value);
        }
    }

    template<typename T, bool isReadOnly = readOnly>
    void customSerialize(bool loading, T& value, std::enable_if_t<isReadOnly, bool> = true)
    {
        if (loading)
        {
            customRead(*this, value);
        }
    }

    template<typename T, bool isReadOnly = readOnly>
    void customSerialize(bool loading, T& value, std::enable_if_t<!isReadOnly, bool> = true)
    {
        if (loading)
        {
            customRead(*this, value);
        }
        else
        {
            customWrite(*this, value);
        }
    }

    // allows serializing of non-pod classes when that is desired
    template<typename T, bool isReadOnly = readOnly>
    void serializeUnsafe(bool loading, T& value, std::enable_if_t<isReadOnly, bool> = true)
    {
        if (loading)
        {
            read(&value, sizeof(T));
        }
    }

    // allows serializing of non-pod classes when that is desired
    template<typename T, bool isReadOnly = readOnly>
    void serializeUnsafe(bool loading, T& value, std::enable_if_t<!isReadOnly, bool> = true)
    {
        if (loading)
        {
            read(&value, sizeof(T));
        }
        else
        {
            write(&value, sizeof(T));
        }
    }

    template<typename PtrT, bool isReadOnly = readOnly>
    void serializeBuffer(bool loading, const PtrT*& data, size_t& dataSize, std::enable_if_t<isReadOnly, bool> = true)
    {
        if (loading)
        {
            read(dataSize);
            verifySize(dataSize);
            data = (const PtrT*)current;
            current += dataSize;
        }
    }

    template<typename PtrT, bool isReadOnly = readOnly>
    void serializeBuffer(bool loading, const PtrT*& data, size_t& dataSize, std::enable_if_t<!isReadOnly, bool> = true)
    {
        if (loading)
        {
            read(dataSize);
            verifySize(dataSize);
            data = (const PtrT*)current;
            current += dataSize;
        }
        else
        {
            write(dataSize);
            verifySize(dataSize);
            write(data, dataSize);
        }
    }

    // serializeBufferCopy copies data to a given buffer
    // as opposed to serializeBuffer above which when loading outputs a pointer to memory
    template<bool isReadOnly = readOnly>
    void serializeBufferCopy(bool loading, void* data, size_t& dataSize, std::enable_if_t<isReadOnly, bool> = true)
    {
        if (loading)
        {
            read(dataSize);
            verifySize(dataSize);
            read(data, dataSize);
        }
    }

    template<bool isReadOnly = readOnly>
    void serializeBufferCopy(bool loading, void* data, size_t& dataSize, std::enable_if_t<!isReadOnly, bool> = true)
    {
        if (loading)
        {
            read(dataSize);
            verifySize(dataSize);
            read(data, dataSize);
        }
        else
        {
            write(dataSize);
            verifySize(dataSize);
            write(data, dataSize);
        }
    }

    size_t getCurrentPos() const
    {
        return current - start;
    }

    bool hasError() const
    {
        return current > end;
    }

    Allocator& derived() { return *(Allocator*)this; }
};

template<typename T>
bool is_pod_and_not_pointer()
{
    return std::is_trivially_copyable<T>::value && !std::is_pointer<T>::value;
}

template<typename Allocator, bool readOnly>
template<typename T>
void ByteSerializer<Allocator, readOnly>::write(const std::vector<T>& value)
{
    static_assert(!readOnly, "Cannot write to readonly serializer");

    write(value.size());
    if (is_pod_and_not_pointer<T>())
    {
        write(value.data(), sizeof(T) * value.size());
    }
    else
    {
        for (const T& val : value)
        {
            write(val);
        }
    }
}

template<typename Allocator, bool readOnly>
template<typename T, std::size_t N>
void ByteSerializer<Allocator, readOnly>::write(const omni::SmallVector<T, N>& value)
{
    static_assert(!readOnly, "Cannot write to readonly serializer");

    write(value.size());
    if (is_pod_and_not_pointer<T>())
    {
        write(value.data(), sizeof(T) * value.size());
    }
    else
    {
        for (const T& val : value)
        {
            write(val);
        }
    }
}

template<typename Allocator, bool readOnly>
template<typename FirstT, typename SecondT>
void ByteSerializer<Allocator, readOnly>::write(const std::pair<FirstT, SecondT>& value)
{
    write(value.first);
    write(value.second);
}

template <typename Allocator, bool readOnly>
template <typename T>
void ByteSerializer<Allocator, readOnly>::read(std::vector<T>& value)
{
    size_t size = 0;
    read(size);

    // make sure we fail before we potentially do a dangerously large allocation
    size_t sizeCheck = is_pod_and_not_pointer<T>() ? (size * sizeof(T)) : size;
    if (!verifySize(sizeCheck))
    {
        // but still act as if we read the data
        current += sizeCheck;
        return;
    }
    value.resize(size);

    if (is_pod_and_not_pointer<T>())
    {
        read(value.data(), sizeof(T) * value.size());
    }
    else
    {
        for (T& val : value)
        {
            read(val);
        }
    }
}

template <typename Allocator, bool readOnly>
template <typename T, std::size_t N>
void ByteSerializer<Allocator, readOnly>::read(omni::SmallVector<T, N>& value)
{
    omni::SmallVectorBase::size_type size = 0;
    read(size);

    // make sure we fail before we potentially do a dangerously large allocation
    omni::SmallVectorBase::size_type sizeCheck = is_pod_and_not_pointer<T>() ? (size * sizeof(T)) : size;
    if (!verifySize(sizeCheck))
    {
        // but still act as if we read the data
        current += sizeCheck;
        return;
    }
    value.resize(size);

    if (is_pod_and_not_pointer<T>())
    {
        read(value.data(), sizeof(T) * value.size());
    }
    else
    {
        for (T& val : value)
        {
            read(val);
        }
    }
}

template <typename Allocator, bool readOnly>
template<typename FirstT, typename SecondT>
void ByteSerializer<Allocator, readOnly>::read(std::pair<FirstT, SecondT>& value)
{
    read(value.first);
    read(value.second);
}

template <typename Allocator, bool readOnly>
template <typename T, std::size_t N>
void ByteSerializer<Allocator, readOnly>::write(T(&value)[N])
{
    // make sure we fail before we potentially do a dangerously large allocation
    static_assert(!readOnly, "Cannot write to readonly serializer");
    write(value, N * sizeof(T));
}

template <typename Allocator, bool readOnly>
template <typename T, std::size_t N>
void ByteSerializer<Allocator, readOnly>::read(T(&value)[N])
{
    std::size_t size = N * sizeof(T);
    read(value, size);
}

template<bool readOnly>
struct ExternalSerializer : ByteSerializer<ExternalSerializer<readOnly>, readOnly>
{
    using BaseT = ByteSerializer<ExternalSerializer, readOnly>;
    ExternalSerializer(typename BaseT::DataPtr data, size_t size)
    {
        this->start = this->current = data;
        this->end = data + size;
    }

    bool grow(size_t size)
    {
        // cannot grow the fixed size buffer, we overflowed
        return false;
    }

    const uint8_t* getData() const
    {
        return this->start;
    }
};

struct VectorSerializer : ByteSerializer<VectorSerializer, false>
{
    VectorSerializer(size_t reservedSize = 1024)
        : ByteSerializer<VectorSerializer, false>{}
    {
        grow(reservedSize);
    }

    bool grow(size_t size)
    {
        data.resize(std::max(data.size() + size, size_t(data.size() * 2)));
        size_t currentPos = getCurrentPos();
        this->start = &data[0];
        this->current = &data[currentPos];
        this->end = this->start + data.size();
        return true;
    }

    const uint8_t* getData() const
    {
        return data.data();
    }

    std::vector<uint8_t> data;
};

template<size_t FixedSize>
struct FixedSerializer : ExternalSerializer<false>
{
    FixedSerializer()
        : ExternalSerializer<false>(data, FixedSize)
    {
    }

    const uint8_t* getData() const
    {
        return data;
    }

    uint8_t data[FixedSize];
};

} // namespace omni
