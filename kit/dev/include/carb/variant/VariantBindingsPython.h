// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include "../BindingsPythonUtils.h"
#include "IVariant.h"
#include "VariantUtils.h"

#include "../extras/EnvironmentVariable.h"

namespace carb
{
namespace variant
{

// PyObjectVTable for python variant types
struct PyObjectVTable
{
    static_assert(sizeof(py::object) == sizeof(void*), "Bad assumption");

    static void Destructor(VariantData* self) noexcept
    {
        try
        {
            py::object* p = reinterpret_cast<py::object*>(&self->data);
            py::gil_scoped_acquire gil;
            p->~object();
        }
        catch (...)
        {
        }
    }
    static VariantData Copy(const VariantData* self) noexcept
    {
        const py::object* p = reinterpret_cast<const py::object*>(&self->data);
        VariantData d{ self->vtable, nullptr };
        try
        {
            py::gil_scoped_acquire gil;
            new (&d.data) py::object(*p);
        }
        catch (...)
        {
        }
        return d;
    }
    static bool Equals(const VariantData* self, const VariantData* other) noexcept
    {
        if (self->vtable == other->vtable)
        {
            CARB_ASSERT(self->vtable == get());
            const py::object* pself = reinterpret_cast<const py::object*>(&self->data);
            const py::object* pother = reinterpret_cast<const py::object*>(&other->data);
            try
            {
                py::gil_scoped_acquire gil;
                return pself->is(*pother) || pself->equal(*pother);
            }
            catch (...)
            {
                return false;
            }
        }

        // Try to convert us into the other type since it's not a python type
        VariantData temp;
        if (traits::convertTo(*self, other->vtable, temp))
        {
            bool b = traits::equals(temp, *other);
            traits::destruct(temp);
            return b;
        }

        return false;
    }
    static omni::string ToString(const VariantData* self) noexcept
    {
        const py::object* pself = reinterpret_cast<const py::object*>(&self->data);
        try
        {
            py::gil_scoped_acquire gil;
            auto str = py::str(*pself).cast<std::string>();
            return omni::string(str);
        }
        catch (...)
        {
            return omni::string(omni::formatted, "py::object:%p", pself->ptr());
        }
    }
#pragma push_macro("min")
#undef min
#pragma push_macro("max")
#undef max
    template <class T>
    static bool Convert(const py::object& val, void*& out) noexcept
    {
        Translator<T> t{};
        py::gil_scoped_acquire gil;
        // try native type conversion
        try
        {
            out = t.data(val.cast<T>());
            return true;
        }
        catch (...)
        {
        }
        // Try to convert string to type.
        // NOTE: we arguably shouldn't really do this. We only do it because the old Events 1.0 IEvent python bindings
        // used IDictionary, which would magically convert between requested types. Therefore we only do this if the
        // type is actually a string. And we do this largely in the same way as IDictionary string conversion.
        if (py::isinstance<py::str>(val))
        {
            auto str = val.cast<std::string>();
            if constexpr (std::is_same_v<bool, T>)
            {
                // Check numeric
                char* end;
                double v = strtod(str.c_str(), &end);
                if (*end == '\0')
                {
                    out = t.data(v != 0.0);
                    return true;
                }
                // Convert to lowercase
                std::transform(str.begin(), str.end(), str.begin(), [](char c) { return (char)std::tolower(c); });
                out = t.data(str == "true");
                return true;
            }
            else if constexpr (std::is_floating_point_v<T>)
            {
                char* end;
                double v = strtod(str.c_str(), &end);
                if (*end == '\0')
                {
                    out = t.data((T)v);
                    return true;
                }
            }
            else if constexpr (std::is_signed_v<T>)
            {
                char* end;
                errno = 0;
                int64_t v = strtoll(str.c_str(), &end, 10);
                if (*end == '\0' && errno != ERANGE)
                {
                    if (v <= int64_t(std::numeric_limits<T>::max()) && v >= int64_t(std::numeric_limits<T>::min()))
                    {
                        out = t.data((T)v);
                        return true;
                    }
                }
            }
            else
            {
                static_assert(std::is_arithmetic_v<T> && std::is_unsigned_v<T>, "Missing conversion handler");
                char* end;
                errno = 0;
                uint64_t v = strtoull(str.c_str(), &end, 10);
                if (*end == '\0' && errno != ERANGE)
                {
                    if (v <= uint64_t(std::numeric_limits<T>::max()))
                    {
                        out = t.data((T)v);
                        return true;
                    }
                }
            }
        }
        return false;
    }
#pragma pop_macro("max")
#pragma pop_macro("min")
    static bool ConvertArray(const py::object& self, void*& out)
    {
        Translator<VariantArrayPtr> t{};
        auto seq = self.cast<py::sequence>();
        auto array = getCachedInterface<IVariant>()->createArray();
        array->reserve(seq.size());
        for (size_t i = 0; i != seq.size(); ++i)
            array->push_back(Variant(py::object(seq[i])));
        out = t.data(array);
        return true;
    }
    static bool ConvertMap(const py::object& self, void*& out)
    {
        Translator<VariantMapPtr> t{};
        auto map = getCachedInterface<IVariant>()->createMap();
        auto dict = self.cast<py::dict>();
        for (auto& pair : dict)
        {
            (*map)[Variant(pair.first.cast<py::object>())] = Variant(pair.second.cast<py::object>());
        }
        out = t.data(map);
        return true;
    }
    static bool ConvertPair(const py::object& self, void*& out)
    {
        Translator<std::pair<Variant, Variant>> t{};
        auto seq = self.cast<py::sequence>();
        std::pair<Variant, Variant> pair;
        if (seq.size() >= 1)
            pair.first = Variant(py::object(seq[0]));
        if (seq.size() >= 2)
            pair.second = Variant(py::object(seq[1]));
        out = t.data(pair);
        return true;
    }
    static bool ConvertCharPtr(const py::object& self, void*& out)
    {
        if (py::isinstance<py::str>(self))
        {
            Py_ssize_t size;
            auto str = PyUnicode_AsUTF8AndSize(self.ptr(), &size);
            out = const_cast<char*>(str);
            return out != nullptr;
        }
        return false;
    }
    static bool ConvertString(const py::object& self, void*& out)
    {
        Translator<omni::string> t{};
        auto str = py::str(self).cast<std::string>();
        out = t.data(omni::string(str.data(), str.size()));
        return true;
    }
    static bool ConvertTo(const VariantData* self, const VTable* newtype, VariantData* target) noexcept
    {
        const py::object* pself = reinterpret_cast<const py::object*>(&self->data);
        static std::unordered_map<RString, bool (*)(const py::object&, void*&)> converters{
            { eBool, Convert<bool> },       { eUInt8, Convert<uint8_t> },   { eUInt16, Convert<uint16_t> },
            { eUInt32, Convert<uint32_t> }, { eUInt64, Convert<uint64_t> }, { eInt8, Convert<int8_t> },
            { eInt16, Convert<int16_t> },   { eInt32, Convert<int32_t> },   { eInt64, Convert<int64_t> },
            { eFloat, Convert<float> },     { eDouble, Convert<double> },   { eVariantArray, ConvertArray },
            { eVariantMap, ConvertMap },    { eVariantPair, ConvertPair },  { eCharPtr, ConvertCharPtr },
            { eString, ConvertString },
        };
        auto iter = converters.find(newtype->typeName);
        auto call = [&] {
            try
            {
                py::gil_scoped_acquire gil;
                return iter->second(*pself, target->data);
            }
            catch (...)
            {
            }
            return false;
        };
        if (iter != converters.end() && call())
        {
            auto iface = getCachedInterface<IVariant>();
            CARB_ASSERT(iface, "Failed to acquire interface IVariant");
            target->vtable = iface->getVTable(iter->first);
            return true;
        }
        return false;
    }
    static size_t Hash(const VariantData* self) noexcept
    {
        const py::object* pself = reinterpret_cast<const py::object*>(&self->data);
        try
        {
            VariantData vd = {};
            bool converted = false;
            auto v = getCachedInterface<variant::IVariant>();
            // Python hashing doesn't work the same as Carbonite hashing, so try type conversions first.
            py::gil_scoped_acquire gil;
            if (py::isinstance<py::bool_>(*pself))
                converted = ConvertTo(self, v->getVTable(eBool), &vd);
            else if (py::isinstance<py::int_>(*pself))
                converted = ConvertTo(self, v->getVTable(eInt64), &vd) || ConvertTo(self, v->getVTable(eUInt64), &vd);
            else if (py::isinstance<py::float_>(*pself))
                converted = ConvertTo(self, v->getVTable(eDouble), &vd);
            else if (py::isinstance<py::str>(*pself))
                converted = ConvertTo(self, v->getVTable(eString), &vd);
            if (!converted)
                // Failed to convert, so fall back to the python hash
                return (size_t)py::hash(*pself);
            CARB_SCOPE_EXIT
            {
                traits::destruct(vd);
            };
            return traits::hash(vd);
        }
        catch (...)
        {
            return size_t(pself);
        }
    }
    static const VTable* get() noexcept
    {
        static const VTable v{
            sizeof(VTable), RString("py::object"), Destructor, Copy, Equals, ToString, ConvertTo, Hash
        };
        return &v;
    }
};

// Translator for python
template <>
struct Translator<py::object, void>
{
    static_assert(sizeof(py::object) == sizeof(void*), "Bad assumption");

    RString type() const noexcept
    {
        static const RString t("py::object");
        return t;
    }
    void* data(py::object o) const noexcept
    {
        void* d{};
        py::gil_scoped_acquire gil;
        new (&d) py::object(std::move(o));
        return d;
    }
    py::object value(void* d) const noexcept
    {
        py::object* p = reinterpret_cast<py::object*>(&d);
        py::gil_scoped_acquire gil;
        return *p;
    }
};

inline void definePythonModule(py::module& m)
{
    static bool typeRegistered = false;
    static LoadHookHandle loadHook = kInvalidLoadHook;

    // We need to register our PyObject variant type, so either do it immediately if IVariant is available, or defer
    // until IVariant is loaded.
    IVariant* v = getFramework()->tryAcquireExistingInterface<IVariant>();
    if (v)
    {
        v->registerType(PyObjectVTable::get());
        typeRegistered = true;

        // If we see `v` unload, we reset our typeRegistered flag
        getFramework()->addReleaseHook(v, [](void*, void*) { typeRegistered = false; }, nullptr);
    }
    else if (loadHook == kInvalidLoadHook)
    {
        // IVariant isn't available yet, so we'll register our type if/when it loads in the future
        loadHook = getFramework()->addLoadHook<IVariant>(
            nullptr,
            [](const PluginDesc&, void*) {
                if (auto v = getFramework()->tryAcquireInterface<IVariant>())
                {
                    if (!typeRegistered)
                    {
                        v->registerType(PyObjectVTable::get());
                        typeRegistered = true;
                        getFramework()->removeLoadHook(std::exchange(loadHook, kInvalidLoadHook));
                        // If we see `v` unload, we reset our typeRegistered flag
                        getFramework()->addReleaseHook(v, [](void*, void*) { typeRegistered = false; }, nullptr);
                    }
                }
            },
            nullptr);
    }

    defineInterfaceClass<IVariant>(m, "IVariant", "acquire_variant_interface");
}

} // namespace variant
} // namespace carb
