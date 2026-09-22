// Copyright (c) 2021-2025, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "usd_decl.h"

#include <usdrt/scenegraph/usd/sdf/assetPath.h>


namespace usdrt
{

inline bool UsdAttribute::HasValue() const
{
    if (!m_attribute)
    {
        return false;
    }

    return m_attribute->hasValue();
}

inline bool UsdAttribute::HasAuthoredValue() const
{
    if (!m_attribute)
    {
        return false;
    }

    return m_attribute->hasAuthoredValue();
}

inline SdfValueTypeName UsdAttribute::GetTypeName() const
{
    if (!m_attribute)
    {
        return SdfValueTypeName();
    }

    return SdfValueTypeName(Type(m_attribute->getTypeName()));
}

template <typename T>
inline bool UsdAttribute::Get(T* value, UsdTimeCode time) const
{
    // TODO - how does timecode map here?
    // simulation frame? totally ignored?
    if (!m_attribute)
    {
        return false;
    }

    omni::fabric::ConstSpanC ptrAndSize = m_attribute->getValue();

    if (sizeof(T) != ptrAndSize.elementSize)
    {
        return false;
    }
    *value = *reinterpret_cast<const T*>(ptrAndSize.ptr);

    return true;
}

template <>
inline bool UsdAttribute::Get(std::string* value, UsdTimeCode time) const
{
    // TODO - how does timecode map here?
    // simulation frame? totally ignored?
    if (!m_attribute)
    {
        return false;
    }

    omni::fabric::ConstSpanC ptrAndSize = m_attribute->getValue();

    if (sizeof(char) != ptrAndSize.elementSize)
    {
        return false;
    }
    const char* strPtr = reinterpret_cast<const char*>(ptrAndSize.ptr);
    *value = std::string(strPtr, ptrAndSize.elementCount);

    return true;
}

template <>
inline bool UsdAttribute::Get(SdfAssetPath* value, UsdTimeCode time) const
{
    // TODO - how does timecode map here?
    // simulation frame? totally ignored?
    if (!m_attribute)
    {
        return false;
    }

    omni::fabric::ConstSpanC ptrAndSize = m_attribute->getValue();

    if (sizeof(omni::fabric::TokenC) * 2 != ptrAndSize.elementSize)
    {
        return false;
    }

    const void* assetPathPtr = reinterpret_cast<const void*>(ptrAndSize.ptr);
    *value = SdfAssetPath::CreateFromFabric(assetPathPtr);

    return true;
}

template <typename T>
inline bool UsdAttribute::Get(VtArray<T>* value, UsdTimeCode time) const
{
    // TODO - how does timecode map here?
    // simulation frame? totally ignored?
    if (!m_attribute)
    {
        return false;
    }

    auto stage105 = omni::core::cast<IRtStage105>(m_attribute->getStage().get());
    *value = VtArray<T>(
        stage105->getStageReaderWriterId(), m_attribute->getPrimPath(), m_attribute->getName());
    stage105->done();

    return true;
}

template <>
inline bool UsdAttribute::Get(VtArray<SdfAssetPath>* value, UsdTimeCode time) const
{
    // TODO - how does timecode map here?
    // simulation frame? totally ignored?
    if (!m_attribute)
    {
        return false;
    }

    omni::fabric::ConstSpanC ptrAndSize = m_attribute->getValue();

    if (sizeof(omni::fabric::TokenC) * 2 != ptrAndSize.elementSize)
    {
        return false;
    }

    if (ptrAndSize.elementCount == 0)
    {
        value->reset();
        return true;
    }

    // Note that this is making a localized VtArray, but the data contained within is small,
    // and asset arrays are generally not very long in practice, so it's a
    // workable solution
    value->resize(ptrAndSize.elementCount);

    for (size_t i = 0; i < ptrAndSize.elementCount; ++i)
    {
        const void* assetPathPtr = reinterpret_cast<const void*>(ptrAndSize.ptr + i * ptrAndSize.elementSize);
        (*value)[i] = SdfAssetPath::CreateFromFabric(assetPathPtr);
    }

    return true;
}

template <typename T>
inline bool UsdAttribute::Set(const T& value, UsdTimeCode time)
{
    if (!m_attribute)
    {
        return false;
    }

    omni::fabric::SpanC ptrAndSize = m_attribute->setValue();

    if (sizeof(T) != ptrAndSize.elementSize)
    {
        return false;
    }

    *reinterpret_cast<T*>(ptrAndSize.ptr) = value;

    return true;
}

template <>
inline bool UsdAttribute::Set(const std::string& value, UsdTimeCode time)
{
    if (!m_attribute)
    {
        return false;
    }

    omni::fabric::SpanC ptrAndSize = m_attribute->setValue();

    if (sizeof(char) != ptrAndSize.elementSize)
    {
        return false;
    }

    if (ptrAndSize.elementCount != value.size())
    {
        m_attribute->setValueNewArraySize(value.size());
        ptrAndSize = m_attribute->setValue();

        if (ptrAndSize.elementCount != value.size())
        {
            // sanity check, this should not be possible
            return false;
        }
    }

    std::copy(value.c_str(), value.c_str() + value.size(), reinterpret_cast<char*>(ptrAndSize.ptr));

    return true;
}

template <>
inline bool UsdAttribute::Set(const SdfAssetPath& value, UsdTimeCode time)
{
    if (!m_attribute)
    {
        return false;
    }

    omni::fabric::SpanC ptrAndSize = m_attribute->setValue();

    if (sizeof(omni::fabric::TokenC) * 2 != ptrAndSize.elementSize)
    {
        return false;
    }

    omni::fabric::IToken* iToken = carb::getCachedInterface<omni::fabric::IToken>();
    if (!iToken)
    {
        return false;
    }

    const omni::fabric::TokenC assetPath = value._GetAssetPathC();
    const omni::fabric::TokenC resolvedPath = value._GetResolvedPathC();

    // Increment refcount here, once the SdfAssetPath destructs
    // it will decrement the refcount of these tokens, but Fabric
    // needs to maintain them since it's holding them.
    iToken->addRef(assetPath);
    iToken->addRef(resolvedPath);

    reinterpret_cast<omni::fabric::TokenC*>(ptrAndSize.ptr)[0] = assetPath;
    reinterpret_cast<omni::fabric::TokenC*>(ptrAndSize.ptr)[1] = resolvedPath;

    return true;
}

template <typename T>
inline bool UsdAttribute::Set(const VtArray<T>& value, UsdTimeCode time)
{
    if (!m_attribute)
    {
        return false;
    }

    // Note: If value has GPU data, Cuda memcpy happens in python bindings py_set_array helper.
    if (!value.GetGpuData())
    {
        omni::fabric::SpanC ptrAndSize = m_attribute->setValue();
        if (sizeof(T) != ptrAndSize.elementSize)
        {
            return false;
        }
        if (ptrAndSize.elementCount != value.size())
        {
            m_attribute->setValueNewArraySize(value.size());
            ptrAndSize = m_attribute->setValue();

            if (ptrAndSize.elementCount != value.size())
            {
                // sanity check, this should not be possible
                return false;
            }
        }
        std::copy(value.cdata(), value.cdata() + value.size(), reinterpret_cast<T*>(ptrAndSize.ptr));
    }

    return true;
}

template <>
inline bool UsdAttribute::Set(const VtArray<std::string>& value, UsdTimeCode time)
{
    // TODO - implement once Fabric supports string[] - OM-45631
    return false;
}

template <>
inline bool UsdAttribute::Set(const VtArray<SdfAssetPath>& value, UsdTimeCode time)
{
    if (!m_attribute)
    {
        return false;
    }

    if (value.GetGpuData())
    {
        // This should not be possible
        return false;
    }

    omni::fabric::SpanC ptrAndSize = m_attribute->setValue();

    if (sizeof(omni::fabric::TokenC) * 2 != ptrAndSize.elementSize)
    {
        return false;
    }

    if (ptrAndSize.elementCount != value.size())
    {
        m_attribute->setValueNewArraySize(value.size());
        ptrAndSize = m_attribute->setValue();

        if (ptrAndSize.elementCount != value.size())
        {
            // sanity check, this should not be possible
            return false;
        }
    }

    if (value.size() == 0)
    {
        return true;
    }


    omni::fabric::IToken* iToken = carb::getCachedInterface<omni::fabric::IToken>();
    if (!iToken)
    {
        return false;
    }

    for (size_t i = 0; i < value.size(); ++i)
    {
        const omni::fabric::TokenC assetPath = value[i]._GetAssetPathC();
        const omni::fabric::TokenC resolvedPath = value[i]._GetResolvedPathC();

        // Increment refcount here, once the VtArray<SdfAssetPath> destructs
        // it will decrement the refcount of these tokens, but Fabric
        // needs to maintain them since it's holding them.
        iToken->addRef(assetPath);
        iToken->addRef(resolvedPath);

        reinterpret_cast<omni::fabric::TokenC*>(ptrAndSize.ptr)[i * 2 + 0] = assetPath;
        reinterpret_cast<omni::fabric::TokenC*>(ptrAndSize.ptr)[i * 2 + 1] = resolvedPath;
    }

    return true;
}

// UsdObject methods
inline bool UsdAttribute::IsValid() const
{
    if (!m_attribute)
    {
        return false;
    }

    return m_attribute->isValid();
}

inline UsdStageRefPtr UsdAttribute::GetStage() const
{
    if (!m_attribute)
    {
        return UsdStageRefPtr(nullptr);
    }

    UsdStageRefPtr stage(new UsdStage{ m_attribute->getStage() });
    return stage;
}

inline UsdPrim UsdAttribute::GetPrim() const
{
    if (!m_attribute)
    {
        return UsdPrim{ nullptr };
    }

    return UsdPrim{ m_attribute->getPrim() };
}

inline const TfToken UsdAttribute::GetName() const
{
    if (!m_attribute)
    {
        return TfToken();
    }

    return TfToken(m_attribute->getName());
}

inline SdfPath UsdAttribute::GetPath() const
{
    if (!m_attribute)
    {
        return SdfPath();
    }

    return SdfPath(m_attribute->getPrimPath(), TfToken(m_attribute->getName()));
}

inline const SdfPath UsdAttribute::GetPrimPath() const
{
    if (!m_attribute)
    {
        return SdfPath();
    }

    return SdfPath(m_attribute->getPrimPath());
}

// UsdProperty methods
inline TfToken UsdAttribute::GetBaseName() const
{
    if (!m_attribute)
    {
        return TfToken();
    }

    return TfToken(m_attribute->getBaseName()->getBuffer());
}

inline TfToken UsdAttribute::GetNamespace() const
{
    if (!m_attribute)
    {
        return TfToken();
    }

    return TfToken(m_attribute->getNamespace()->getBuffer());
}

inline std::vector<std::string> UsdAttribute::SplitName() const
{
    if (!m_attribute)
    {
        return std::vector<std::string>();
    }

    return m_attribute->splitName();
}

inline UsdAttribute::operator bool() const
{
    return IsValid();
}

// Querying and Editing Connections
inline bool UsdAttribute::AddConnection(const SdfPath& source, UsdListPosition position) const
{
    if (!m_attribute)
    {
        return false;
    }

    union
    {
        UsdListPosition wrapper;
        ListPosition iface;
    };

    wrapper = position;

    auto attr105 = omni::core::cast<IRtAttribute105>(m_attribute.get());
    return attr105->addConnection(omni::fabric::Connection(source), iface);
}

inline bool UsdAttribute::RemoveConnection(const SdfPath& source) const
{
    if (!m_attribute)
    {
        return false;
    }

    auto attr105 = omni::core::cast<IRtAttribute105>(m_attribute.get());
    return attr105->removeConnection(omni::fabric::Connection(source));
}

inline bool UsdAttribute::SetConnections(const SdfPathVector& sources) const
{
    if (!m_attribute)
    {
        return false;
    }

    // Do nothing for now. Mutliple sources not supported in fabric.
    if (sources.size() != 1)
    {
        return false;
    }

    std::vector<omni::fabric::Connection> connections;
    connections.reserve(sources.size());
    for (const SdfPath& source : sources)
    {
        connections.push_back(omni::fabric::Connection(source));
    }

    auto attr105 = omni::core::cast<IRtAttribute105>(m_attribute.get());
    return attr105->setConnections(connections.data(), (uint32_t)connections.size());
}

inline bool UsdAttribute::ClearConnections() const
{
    if (!m_attribute)
    {
        return false;
    }

    auto attr105 = omni::core::cast<IRtAttribute105>(m_attribute.get());
    return attr105->clearConnections();
}

inline bool UsdAttribute::GetConnections(SdfPathVector* sources) const
{
    if (!m_attribute)
    {
        return false;
    }

    auto attr105 = omni::core::cast<IRtAttribute105>(m_attribute.get());
    const uint32_t numConnections = attr105->numConnections();
    if (numConnections == 0)
    {
        sources->resize(0);
        return true;
    }

    std::vector<omni::fabric::Connection> connections(numConnections);
    const bool result = attr105->getConnections(connections.data(), numConnections);

    sources->resize(numConnections);
    for (size_t i = 0; i < numConnections; ++i)
    {
        (*sources)[i] = SdfPath(connections[i]);
    }
    return result;
}

inline bool UsdAttribute::HasAuthoredConnections() const
{
    if (!m_attribute)
    {
        return false;
    }

    auto attr105 = omni::core::cast<IRtAttribute105>(m_attribute.get());
    return attr105->hasAuthoredConnections();
}

inline bool UsdAttribute::IsCpuDataValid() const
{
    auto attr105 = omni::core::cast<IRtAttribute105>(m_attribute.get());

    return attr105->isCpuDataValid();
}

inline bool UsdAttribute::IsGpuDataValid() const
{
    auto attr105 = omni::core::cast<IRtAttribute105>(m_attribute.get());

    return attr105->isGpuDataValid();
}

inline bool UsdAttribute::SyncDataToGpu() const
{
    auto attr105 = omni::core::cast<IRtAttribute105>(m_attribute.get());

    return attr105->updateGpuDataFromCpu();
}

inline bool UsdAttribute::SyncDataToCpu() const
{
    auto attr105 = omni::core::cast<IRtAttribute105>(m_attribute.get());

    return attr105->updateCpuDataFromGpu();
}

inline bool UsdAttribute::InvalidateGpuData() const
{
    m_attribute->setValue();

    return !IsGpuDataValid();
}

inline bool UsdAttribute::InvalidateCpuData() const
{
    m_attribute->setValueGpu();

    return !IsCpuDataValid();
}

static_assert(std::is_standard_layout<UsdAttribute>::value, "UsdAttribute must be standard layout");

} // namespace usdrt
