// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <cstdint>

namespace omni::usd::hydra
{

/// \note Forward declaration of internal implementation details.
enum class EngineCreationFlags : uint32_t;

/// \brief Simple 32 bit integer unique id for specific Hydra Engine instance.
/// \note Current implementation of Hydra Engine management (10.7.2024) is using unique id instead of direct container index.
///       Additional option is to provide ref counting unqiue id, so if some object is holding uid it will also hold reference count.
///       For now ref counting of Hydra Engine usage is traced by POD structure and simple mechanism of atomic counter. 
using HydraEngineUniqueId = uint32_t;

/// \brief default value for validation and error handling logic.
static constexpr HydraEngineUniqueId sHydraEngineInvalidUniqueId{ UINT32_MAX };
static constexpr uint32_t sHydraEngineInvalidIndex{ UINT32_MAX };
static constexpr uint32_t sHydraEngineInvalidDeviceMask{ 0U };
static constexpr uint32_t sHydraEngineInvalidTickRate{ 0U };
static constexpr uint32_t sHydraEngineInvalidCreationFlag { 0U };

/// \brief Configuration data for an hydra engine creation.
struct HydraEngineCreationConfig final
{
    /// \brief Unique creation flags.
    EngineCreationFlags flags{ static_cast<EngineCreationFlags>(sHydraEngineInvalidCreationFlag)};

    /// \brief Target update rate in Hz for worker thread.
    uint32_t tickRateInHz {sHydraEngineInvalidTickRate};

    /// \brief Determines what GPUs to be used for the hydra engine.
    /// \note If set to 0, then all GPUs in the DeviceGroup of the foundation is used.
    ///       deviceMask deprecates the setting "/renderer/{hydraengine_name}_context/activeDevice"
    ///       which overrides the mask for all engines.
    ///       For backward compatibility, the setting still works if deviceMask is set to 0.
    uint32_t deviceMask {sHydraEngineInvalidDeviceMask};

    /// \brief Configuration for mapping hydra engines is still using index as unique identifier. 
    uint32_t creationIndex{ sHydraEngineInvalidIndex };
};

/// \brief Existing Hydra Engine description view.
struct HydraEngineDesc final
{
    /// \note Not valid engine description will fail with returned false.
    constexpr inline bool isValid() const noexcept
    {
        return ((sHydraEngineInvalidUniqueId != uid) &&
                (nullptr != engineTypeName));
    }

    /// \brief Unique ID of specific engine instance.
    HydraEngineUniqueId uid {sHydraEngineInvalidUniqueId};

    /// \brief Active configuration of specific engine instance.
    HydraEngineCreationConfig config;

    /// \brief Engine type as text literal pointer, will be null in case data is invalid.
    const char* engineTypeName {nullptr};

    /// \brief Engine attached thread name.
    const char* threadName {nullptr};   
};

/// \brief Array of hydra engine unique ids.
struct HydraEngineUniqueIdArray final
{
    constexpr inline uint32_t maxSize() const noexcept
    {
        return sHydraEngineUniqueIdVectorMaxSize;
    }

    inline uint32_t size() const noexcept
    {
        return m_size;
    }

    inline uint32_t add(HydraEngineUniqueId uid) noexcept
    {
        if (m_size >= sHydraEngineUniqueIdVectorMaxSize)
        {
            return sHydraEngineInvalidIndex;
        }

        uint32_t const index{ m_size };
        m_size++;
        m_data[index] = uid;
        return index;
    }

    inline HydraEngineUniqueId getAt(uint32_t index) noexcept
    {
        if (index >= sHydraEngineUniqueIdVectorMaxSize)
        {
            return sHydraEngineInvalidIndex;
        }
        return m_data[index];
    }

    inline void clear() noexcept
    {
        m_size = 0U;
    }

private:

    static constexpr uint32_t sHydraEngineUniqueIdVectorMaxSize { 128U };
    uint32_t m_size{ 0U };
    HydraEngineUniqueId m_data[sHydraEngineUniqueIdVectorMaxSize];
};

} // omni::usd::hydra
