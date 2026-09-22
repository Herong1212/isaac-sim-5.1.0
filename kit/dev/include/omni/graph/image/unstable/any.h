// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <typeinfo>
#include <type_traits>
#include <utility>

namespace omni
{
namespace graph
{
namespace image
{
namespace unstable
{
namespace cpp17
{

// The class describes a type-safe container of a single value of any copy-constructible type.

// This class is a not quite standards conformant implementation of std::any.
// It does not support everything std::any supports, and the API is limited to
// a subset that is actually used currently in the project.
// For example, it is missing constructors using std::in_place_type_t<ValueType>
// disambiguation tags and std::make_any. Additionally, this implementation *does not throw exceptions*.
// Instead, it asserts and logs errors when casts fail.

// The long term intention is we will move to a C++17 compiler, and import the std
// version of this class, removing this code from our codebase. Therefore it is very important that this class
// doesn't do anything that the std can't, though the opposite is permissible.
class any final
{
public:
    any()
        : vtable(nullptr)
    {
    }

    any(const any& rhs)
        : vtable(rhs.vtable)
    {
        if (rhs.has_value())
        {
            rhs.vtable->copy(rhs.storage, this->storage);
        }
    }

    any(any&& rhs) noexcept
        : vtable(rhs.vtable)
    {
        if (rhs.has_value())
        {
            rhs.vtable->move(rhs.storage, this->storage);
            rhs.vtable = nullptr;
        }
    }

    ~any()
    {
        this->reset();
    }

    template<typename ValueType, typename = typename std::enable_if<!std::is_same<typename std::decay<ValueType>::type, any>::value>::type>
    any(ValueType&& value)
    {
        static_assert(std::is_copy_constructible<
            typename std::decay<ValueType>::type>::value,
                "T needs to be copy constructible");
        this->construct(std::forward<ValueType>(value));
    }

    any& operator=(const any& rhs)
    {
        any(rhs).swap(*this);
        return *this;
    }

    any& operator=(any&& rhs) noexcept
    {
        any(std::move(rhs)).swap(*this);
        return *this;
    }

    template<typename ValueType, typename = typename std::enable_if<!std::is_same<typename std::decay<ValueType>::type, any>::value>::type>
    any& operator=(ValueType&& value)
    {
        static_assert(std::is_copy_constructible<
            typename std::decay<ValueType>::type>::value,
                "T needs to be copy constructible");
        any(std::forward<ValueType>(value)).swap(*this);
        return *this;
    }

    void reset() noexcept
    {
        if (has_value())
        {
            this->vtable->destroy(storage);
            this->vtable = nullptr;
        }
    }

    bool has_value() const noexcept
    {
        return this->vtable != nullptr;
    }

    const std::type_info& type() const noexcept
    {
        return !has_value() ? typeid(void) : this->vtable->type();
    }

    void swap(any& rhs) noexcept
    {
        if (this->vtable != rhs.vtable)
        {
            any tmp(std::move(rhs));

            rhs.vtable = this->vtable;
            if (this->vtable != nullptr)
            {
                this->vtable->move(this->storage, rhs.storage);
            }

            this->vtable = tmp.vtable;
            if (tmp.vtable != nullptr)
            {
                tmp.vtable->move(tmp.storage, this->storage);
                tmp.vtable = nullptr;
            }
        }
        else
        {
            if (this->vtable != nullptr)
            {
                this->vtable->swap(this->storage, rhs.storage);
            }
        }
    }

private:

    union storage_union
    {
        using stack_storage_t = typename std::aligned_storage<2 * sizeof(void*), std::alignment_of<void*>::value>::type;

        void* dynamic;
        stack_storage_t stack;
    };

    struct vtable_type
    {
        const std::type_info& (*type)() noexcept;

        void(*destroy)(storage_union&) noexcept;
        void(*copy)(const storage_union& src, storage_union& dest);
        void(*move)(storage_union& src, storage_union& dest) noexcept;
        void(*swap)(storage_union& lhs, storage_union& rhs) noexcept;
    };

    template<typename T>
    struct vtable_dynamic
    {
        static const std::type_info& type() noexcept
        {
            return typeid(T);
        }

        static void destroy(storage_union& storage) noexcept
        {
            delete reinterpret_cast<T*>(storage.dynamic);
        }

        static void copy(const storage_union& src, storage_union& dest)
        {
            dest.dynamic = new T(*reinterpret_cast<const T*>(src.dynamic));
        }

        static void move(storage_union& src, storage_union& dest) noexcept
        {
            dest.dynamic = src.dynamic;
            src.dynamic = nullptr;
        }

        static void swap(storage_union& lhs, storage_union& rhs) noexcept
        {
            std::swap(lhs.dynamic, rhs.dynamic);
        }
    };

    template<typename T>
    struct vtable_stack
    {
        static const std::type_info& type() noexcept
        {
            return typeid(T);
        }

        static void destroy(storage_union& storage) noexcept
        {
            reinterpret_cast<T*>(&storage.stack)->~T();
        }

        static void copy(const storage_union& src, storage_union& dest)
        {
            new (&dest.stack) T(reinterpret_cast<const T&>(src.stack));
        }

        static void move(storage_union& src, storage_union& dest) noexcept
        {
            new (&dest.stack) T(std::move(reinterpret_cast<T&>(src.stack)));
            destroy(src);
        }

        static void swap(storage_union& lhs, storage_union& rhs) noexcept
        {
            storage_union tmp_storage;
            move(rhs, tmp_storage);
            move(lhs, rhs);
            move(tmp_storage, lhs);
        }
    };

    template<typename T>
    struct requires_allocation :
        std::integral_constant<bool,
        !(std::is_nothrow_move_constructible<T>::value
            && sizeof(T) <= sizeof(storage_union::stack) &&
                std::alignment_of<T>::value <= std::alignment_of<
                    storage_union::stack_storage_t>::value)>
    {};

    template<typename T>
    static vtable_type* vtable_for_type()
    {
        using VTableType = typename std::conditional<requires_allocation<T>::value, vtable_dynamic<T>, vtable_stack<T>>::type;
        static vtable_type table =
        {
            VTableType::type,
            VTableType::destroy,
            VTableType::copy, VTableType::move,
            VTableType::swap,
        };
        return &table;
    }

protected:
    template<typename T>
    friend const T* any_cast(const any* operand) noexcept;
    template<typename T>
    friend T* any_cast(any* operand) noexcept;

    bool is_typed(const std::type_info& t) const
    {
        return is_same(this->type(), t);
    }

    static bool is_same(const std::type_info& a, const std::type_info& b)
    {
        return a == b;
    }

    template<typename T>
    const T* cast() const noexcept
    {
        return requires_allocation<typename std::decay<T>::type>::value ?
            reinterpret_cast<const T*>(storage.dynamic) :
                reinterpret_cast<const T*>(&storage.stack);
    }

    template<typename T>
    T* cast() noexcept
    {
        return requires_allocation<typename std::decay<T>::type>::value ?
            reinterpret_cast<T*>(storage.dynamic) :
                reinterpret_cast<T*>(&storage.stack);
    }

private:
    storage_union storage;
    vtable_type* vtable;

    template<typename ValueType, typename T>
    typename std::enable_if<requires_allocation<T>::value>::type
        do_construct(ValueType&& value)
    {
        storage.dynamic = new T(std::forward<ValueType>(value));
    }

    template<typename ValueType, typename T>
    typename std::enable_if<!requires_allocation<T>::value>::type
        do_construct(ValueType&& value)
    {
        new (&storage.stack) T(std::forward<ValueType>(value));
    }

    template<typename ValueType>
    void construct(ValueType&& value)
    {
        using T = typename std::decay<ValueType>::type;

        this->vtable = vtable_for_type<T>();

        do_construct<ValueType, T>(std::forward<ValueType>(value));
    }
};

namespace detail
{
    template<typename ValueType>
    inline ValueType any_cast_move_if_true(typename std::remove_reference<ValueType>::type* p, std::true_type)
    {
        return std::move(*p);
    }

    template<typename ValueType>
    inline ValueType any_cast_move_if_true(typename std::remove_reference<ValueType>::type* p, std::false_type)
    {
        return *p;
    }
}

template<typename ValueType>
inline ValueType any_cast(const any& operand)
{
    using T = typename std::add_const<typename std::remove_reference<ValueType>::type>::type;
    auto p = any_cast<T>(&operand);
    if (p == nullptr)
    {
        CARB_LOG_ERROR("cpp17::any: Unable to cast value of type %s to type %s", operand.type().name(), typeid(T).name());
    }
    return *p;
}

template<typename ValueType>
inline ValueType any_cast(any& operand)
{
    using T = typename std::remove_reference<ValueType>::type;
    auto p = any_cast<T>(&operand);
    if (p == nullptr)
    {
        CARB_LOG_ERROR("cpp17::any: Unable to cast value of type %s to type %s", operand.type().name(), typeid(T).name());
    }
    return *p;
}

template<typename ValueType>
inline ValueType any_cast(any&& operand)
{
    using can_move = std::integral_constant<bool,
        std::is_move_constructible<ValueType>::value
        && !std::is_lvalue_reference<ValueType>::value>;
    using T = typename std::remove_reference<ValueType>::type;

    auto p = any_cast<T>(&operand);
    if (p == nullptr)
    {
        CARB_LOG_ERROR("cpp17::any: Unable to cast value of type %s to type %s", operand.type().name(), typeid(T).name());
    }
    return detail::any_cast_move_if_true<ValueType>(p, can_move());
}

template<typename ValueType>
inline const ValueType* any_cast(const any* operand) noexcept
{
    using T = typename std::decay<ValueType>::type;

    if (operand && operand->is_typed(typeid(T)))
        return operand->cast<ValueType>();

    return nullptr;
}

template<typename ValueType>
inline ValueType* any_cast(any* operand) noexcept
{
    using T = typename std::decay<ValueType>::type;

    if (operand && operand->is_typed(typeid(T)))
        return operand->cast<ValueType>();

    return nullptr;
}

} // namespace cpp17
} // namespace unstable
} // namespace image
} // namespace graph
} // namespace omni
