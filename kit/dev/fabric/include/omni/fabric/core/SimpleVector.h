// Copyright (c) 2019-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>
#include "Defines.h"
#include "Intrinsics.h"

#include <cstdint>
#include <cstdlib>
#include <cmath>
#include <algorithm>
#include <memory>

namespace omni
{
namespace fabric
{

// raw_ptr
//
// Purpose: A variant of std::unique_ptr doing no initialization of the memory, but still relying on unique_ptr.
//
// Design:
//   - Limited to trivial types
//   - No memory initialization
//   - Not transferable, not-copyable, but explicitly tradable

template <typename T>
constexpr bool raw_ptr_supported_type = std::is_trivial<T>::value && std::is_pod<T>::value;

template <class T>
struct raw_ptr
{
    using type_t = T;
    static_assert(raw_ptr_supported_type<T>);
    T* get() const
    {
        return ptr.get();
    }
    T* operator->() const
    {
        return ptr.get();
    }
    void reset() noexcept
    {
        ptr = nullptr;
    }
    void reset(T* x) noexcept
    {
        ptr.reset(x);
    }
    void reset(size_t n) noexcept
    {
        ptr.reset(n ? (T*)malloc(sizeof(T) * n) : nullptr);
    }
    void swap(raw_ptr<T>& other) noexcept
    {
        ptr.swap(other.ptr);
    }
    T* trade(T* x) noexcept
    {
        T* tmp = ptr.release();
        ptr.reset(x);
        return tmp;
    }
    raw_ptr() = default;
    raw_ptr(const raw_ptr<T>& other) = delete;
    raw_ptr(const raw_ptr<T>&& other)
    {
        ptr = std::move(other.ptr);
    }
    raw_ptr<T>& operator=(const raw_ptr<T>& other) = delete;
    raw_ptr<T>& operator=(raw_ptr<T>&& other)
    {
        ptr = std::move(other.ptr);
        return *this;
    }

private:
    static auto checker_()
    {
        static_assert(sizeof(raw_ptr<T>) == sizeof(void*));
    }
    struct free_delete
    {
        void operator()(T* x)
        {
            ::free(x);
        }
    };
    std::unique_ptr<T, free_delete> ptr;
};


// SimpleVector
//
// Purpose: A variant of std::vector doing no initialization of the memory
//
// Design:
//   - Limited to trivial types
//   - No memory initialization
//   - Not transferable, not-copyable

template <typename T>
constexpr bool SimpleVectorSupportedType = std::is_trivial<T>::value && std::is_pod<T>::value;

template <typename T>
struct SimpleVector
{
    using type_t = T;
    static_assert(SimpleVectorSupportedType<T>);

    struct Scratchpad
    {
        T* origin;
        T* curr;
        T* end;
        SimpleVector<T>* v;
        void write(const T& value);
        size_t commit() const;
    };

    void clear();
    T* data() const;
    size_t size() const;
    size_t capacity() const;
    size_t remaining_capacity() const;
    bool empty() const;
    void resize(size_t n);
    void reserve(size_t n);
    void grow();
    void grow(size_t n);
    void shrink_to_fit();
    void resize_to_full_capacity();
    void reset(size_t n);
    void swap(SimpleVector& other);
    void move(SimpleVector&& other);
    T* push_back(const T& value);
    T* allocate_back(size_t n);
    T* first() const;
    T* last() const;
    T* begin() const;
    T* end() const;
    T* at(size_t index) const;
    T& operator[](size_t index);
    const T& operator[](size_t index) const;

    Scratchpad scribble();

    SimpleVector() : sz(0), cap(0)
    {
    }
    SimpleVector(size_t n);
    SimpleVector(size_t n, const T value);
    SimpleVector(const SimpleVector& other) = delete;
    SimpleVector(SimpleVector&& other);

    SimpleVector& operator=(const SimpleVector& other) = delete;
    SimpleVector& operator=(SimpleVector&& other);

protected:
    raw_ptr<T> base;
    size_t sz;
    size_t cap;
};


template <typename T>
inline void SimpleVector<T>::clear()
{
    sz = 0;
}

template <typename T>
inline T* SimpleVector<T>::data() const
{
    return base.get();
}

template <typename T>
inline size_t SimpleVector<T>::size() const
{
    return sz;
}

template <typename T>
inline size_t SimpleVector<T>::capacity() const
{
    return cap;
}

template <typename T>
inline size_t SimpleVector<T>::remaining_capacity() const
{
    return cap - sz;
}

template <typename T>
inline bool SimpleVector<T>::empty() const
{
    return sz == 0;
}

template <typename T>
inline void SimpleVector<T>::grow()
{
    const size_t new_cap = std::max(cap * 2ull, 256ull);
    reserve(new_cap);
}

template <typename T>
inline void SimpleVector<T>::grow(size_t n)
{
    reserve(cap + n);
}

template <typename T>
inline void SimpleVector<T>::resize(size_t n)
{
    CARB_ASSERT(cap >= sz);
    CARB_ASSERT(sz == 0 || base.get());
    if (n > cap)
    {
        size_t new_cap = std::max(cap * 2ull, 256ull);
        while (new_cap < n)
            new_cap <<= 1;
        reserve(new_cap);
        sz = n;
    }
    else if (n != sz)
    {
        sz = n;
    }
    CARB_ASSERT(cap >= sz);
    CARB_ASSERT(sz == 0 || base.get());
}

template <typename T>
inline void SimpleVector<T>::reserve(size_t n)
{
    CARB_ASSERT(cap >= sz);
    CARB_ASSERT(sz == 0 || base.get());
    if (n > cap)
    {
        raw_ptr<T> new_base;
        new_base.reset(n);
        if (sz)
            std::memcpy(new_base.get(), base.get(), sizeof(T) * sz);
        base.swap(new_base);
        cap = n;
    }
    CARB_ASSERT(cap >= sz);
    CARB_ASSERT(sz == 0 || base.get());
}

template <typename T>
inline void SimpleVector<T>::resize_to_full_capacity()
{
    resize(cap);
}

template <typename T>
inline void SimpleVector<T>::reset(size_t n)
{
    CARB_ASSERT(cap >= sz);
    CARB_ASSERT(sz == 0 || base.get());
    if (sz != n || cap != n)
    {
        if (n == 0)
        {
            base.reset();
        }
        else if (cap != n)
        {
            raw_ptr<T> new_base;
            new_base.reset(n);
            const size_t cpy_sz = std::min(n, sz);
            if (cpy_sz)
                std::memcpy(new_base.get(), base.get(), sizeof(T) * cpy_sz);
            base.swap(new_base);
        }

        sz = cap = n;
    }
    CARB_ASSERT(cap >= sz);
    CARB_ASSERT(sz == 0 || base.get());
}

template <typename T>
inline void SimpleVector<T>::shrink_to_fit()
{
    reset(sz);
}

template <typename T>
inline T* SimpleVector<T>::allocate_back(size_t n)
{
    const size_t s0 = sz;
    resize(sz + n);
    return base.get() + s0;
}

template <typename T>
inline T* SimpleVector<T>::push_back(const T& value)
{
    T* pv = allocate_back(1);
    *pv = value;
    return pv;
}

template <typename T>
inline T* SimpleVector<T>::at(size_t index) const
{
    CARB_ASSERT(index < sz);
    return base.get() + index;
}

template <typename T>
inline T& SimpleVector<T>::operator[](size_t index)
{
    CARB_ASSERT(index < sz);
    return *(base.get() + index);
}

template <typename T>
inline const T& SimpleVector<T>::operator[](size_t index) const
{
    CARB_ASSERT(index < sz);
    return *(base.get() + index);
}

template <typename T>
inline T* SimpleVector<T>::first() const
{
    return sz ? base.get() : nullptr;
}

template <typename T>
inline T* SimpleVector<T>::last() const
{
    return sz ? base.get() + (sz - 1) : nullptr;
}

template <typename T>
inline T* SimpleVector<T>::begin() const
{
    return first();
}

template <typename T>
inline T* SimpleVector<T>::end() const
{
    return sz ? base.get() + sz : nullptr;
}

template <typename T>
inline SimpleVector<T>::SimpleVector(size_t n)
{
    base.reset(n);
    sz = cap = n;
}

template <typename T>
inline SimpleVector<T>::SimpleVector(size_t n, const T value)
{
    base.reset(n);
    T* p = base.get();
    const T* e = p + n;
    while (e < p)
        *p++ = value;
    sz = cap = n;
}

template <typename T>
inline typename SimpleVector<T>::Scratchpad SimpleVector<T>::scribble()
{
    Scratchpad sp;
    sp.origin = sp.curr = base.get() + sz;
    sp.end = base.get() + cap;
    sp.v = this;
    return sp;
}

template <typename T>
inline void SimpleVector<T>::Scratchpad::write(const T& value)
{
    if (curr == end)
    {
        const size_t opos = origin - v->base.get();
        const size_t cpos = curr - v->base.get();
        CARB_ASSERT(v->sz == opos);
        v->sz = cpos; // hack the size to extend the memcpy to the scratchpad
        v->grow();
        v->sz = opos;
        origin = v->base.get() + opos;
        curr = v->base.get() + cpos;
        end = v->base.get() + v->cap;
    }
    *curr++ = value;
}

template <typename T>
inline size_t SimpleVector<T>::Scratchpad::commit() const
{
    v->sz = curr - v->base.get();
    CARB_ASSERT(v->cap >= v->sz);
    CARB_ASSERT(v->sz == 0 || v->base.get());
    return curr - origin;
}

template <typename T>
inline void SimpleVector<T>::swap(SimpleVector& other)
{
    base.swap(other.base);
    std::swap(sz, other.sz);
    std::swap(cap, other.cap);
}

template <typename T>
inline void SimpleVector<T>::move(SimpleVector&& other)
{
    base = std::move(other.base);
    sz = other.sz;
    cap = other.cap;

    other.base.reset();
    other.sz = other.cap = 0;
}

template <typename T>
inline SimpleVector<T>::SimpleVector(SimpleVector<T>&& other)
{
    move(std::move(other));
}

template <typename T>
inline SimpleVector<T>& SimpleVector<T>::operator=(SimpleVector<T>&& other)
{
    move(std::move(other));
    return *this;
}

} // namespace fabric
} // namespace omni
