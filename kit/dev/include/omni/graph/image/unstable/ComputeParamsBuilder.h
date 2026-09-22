// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
//
// This ABI is unstable and subject to change
/*  _    _  _____ ______         _______  __     ______  _    _ _____     ______          ___   _   _____  _____  _____ _  __
   | |  | |/ ____|  ____|     /\|__   __| \ \   / / __ \| |  | |  __ \   / __ \ \        / / \ | | |  __ \|_   _|/ ____| |/ /
   | |  | | (___ | |__       /  \  | |     \ \_/ / |  | | |  | | |__) | | |  | \ \  /\  / /|  \| | | |__) | | | | (___ | ' /
   | |  | |\___ \|  __|     / /\ \ | |      \   /| |  | | |  | |  _  /  | |  | |\ \/  \/ / | . ` | |  _  /  | |  \___ \|  <
   | |__| |____) | |____   / ____ \| |       | | | |__| | |__| | | \ \  | |__| | \  /\  /  | |\  | | | \ \ _| |_ ____) | . \
    \____/|_____/|______| /_/    \_\_|       |_|  \____/ \____/|_|  \_\  \____/   \/  \/   |_| \_| |_|  \_\_____|_____/|_|\_|
*/

#pragma once

#include <carb/cpp/Variant.h>
#include <carb/renderer/Renderer.h>

#include <omni/fabric/IToken.h>
#include <omni/graph/core/GpuInteropEntryUserData.h>
#include <omni/graph/core/ogn/Database.h>
#include <omni/kit/renderer/IGpuFoundation.h>

#include <rtx/rendergraph/RenderGraphBuilder.h>
#include <rtx/rendergraph/RenderGraphTypes.h>
#include <rtx/resourcemanager/ResourceManager.h>
#include <rtx/resourcemanager/ResourceManagerTypes.h>
#include <rtx/hydra/HydraRenderResults.h>

#include "any.h"

#include <cstddef>
#include <cstring>
#include <functional>
#include <limits>
#include <unordered_map>
#include <utility>
#include <vector>

namespace omni
{
namespace graph
{
namespace image
{
namespace unstable
{

/**
 * @brief Structure for holding arbitrary parameters.
 *
 * The ComputeParams class is used to hold and access arbitrary parameters of various types.
 * It allows adding parameters with a specified key and retrieving parameters by their key and type.
 *
 * Example usage:
 * @code{.cpp}
 *   ComputeParams<std::string> params;
 *   params.add("param1", 42);
 *   params.add("param2", "hello");
 *   params.add("param3", 3.14);
 *
 *   int param1Value = params.get<int>("param1");
 *   std::string param2Value = params.get<std::string>("param2");
 *   double param3Value = params.get<double>("param3");
 * @endcode
 *
 * @tparam TKey The type of the key used to set and get the parameter values from the @ref ComputeParams object.
 * @sa ComputeParamsBuilder
 */
template <typename TKey>
class ComputeParams
{
public:

    /**
     * @brief Constructor.
     *
     * @param[in] initialCapacity The initial capacity of the container where the parameters are stored.
     */
    explicit ComputeParams(std::size_t initialCapacity = 32)
    {
        m_data.reserve(initialCapacity);
    }

    /**
     * @brief Adds a new entry in the parameter map.
     * If an element with the given key is already in the container, it is replaced.
     *
     * @tparam T The type of the value added to the object.
     * @param[in] key The unique identifier of a parameter value.
     * @param[in] value The value of the parameter.
     */
    template <typename T>
    void add(TKey const& key, T&& value)
    {
        m_data[key] = std::forward<T>(value);
    }

    /**
     * @brief Gets a value from the parameter map.
     *
     * The return type must match the type of the value stored for that key. If the type of the stored value does not match the requested type,
     * the function logs an error and terminates the program.
     *
     * @tparam T The type of the value extracted from the object.
     * @param[in] key The unique identifier of the parameter.
     * @return Returns the value of the specified type.
     * @exception std::out_of_range if there is no data for the given key.
     */
    template <typename T>
    T const& get(TKey const& key) const
    {
        return cpp17::any_cast<T const&>(m_data.at(key));
    }

    /**
     * @brief Gets a value from the parameter map.
     *
     * If there is no value for the given key, or if the value type is different from the requested type, returns nullptr.
     *
     * @tparam T The type of the value extracted from the object.
     * @param[in] key The unique identifier of the parameter.
     * @return Returns the value of the specified type.
     */
    template<typename T>
    T const* tryGet(TKey const& key) const noexcept
    {
        if (m_data.find(key) != m_data.end())
        {
            auto const& a = m_data.at(key);
            return cpp17::any_cast<T const>(&a);
        }
        return nullptr;
    }

    /**
     * @brief Checks if a key is present in the container.
     *
     * @param[in] key The unique identifier of the parameter.
     * @return Returns true if the key is found, otherwise returns false.
     */
    bool hasKey(TKey const& key) const noexcept
    {
        return m_data.find(key) != m_data.end();
    }

private:
    std::unordered_map<TKey, cpp17::any> m_data;
};

/**
 * @brief A builder class for constructing instances of the ComputeParams class.
 *
 * The ComputeParamsBuilder provides a fluent interface for building @ref ComputeParams objects.
 * It allows setting multiple parameters of different types and creates a @ref ComputeParams object
 * with the provided parameter values. The object is intended to be used from Omnigraph nodes.
 *
 * Example usage:
 * @code{.cpp}
 *   ComputeParams<std::string> params = ComputeParamsBuilder<std::string>{gpu, rp, db}
 *                             .addValue("param1", 42)
 *                             .addValue("param2", "hello")
 *                             .addValue("param3", 3.14)
 *                             .build();
 * @endcode
 *
 * The main purpose for this builder is to facilitate the sdheduling of CUDA tasks. For this purpose,
 * the builder provides some specialized APIs for adding input AOVs, for allocating new AOVs and for
 * scheduling the work on the GPU.
 *
 * Once built, the @ref ComputeParams instance can be passed to the CUDA task using the @ref scheduleCudaTask function.
 *
 * Alternatively, the builder can directly build the params and schedule the CUDA task in the same chain of method calls.
 *
 * Example usage for scheduling CUDA tasks:
 * @code{.cpp}
 *       ComputeParamsBuilder<std::string>{ gpu, rp, db }
 *           .addValue("multiplier", db.inputs.multiplier())
 *           .addInputTexture("inputAOV", db.inputs.inputAOV(),
 *               [](cudaMipmappedArray_t cudaPtr, carb::graphics::TextureDesc const* desc, ComputeParams<std::string>& params)
 *               {
 *                   params.add("width", desc->width);
 *                   params.add("height", desc->height);
 *               })
 *           .addOutputTexture("outputAOV", db.inputs.outputAOV(), db.inputs.width(), db.inputs.height(), "TestTexture")
 *           .scheduleCudaTask("TestCudaTask",
 *               [](ComputeParams<std::string>* data, cudaStream_t stream)
 *               {
 *                   auto multiplier = data->get<float>("multiplier");
 *                   auto inputAOV = data->get<cudaMipmappedArray_t>("inputAOV");
 *                   auto outputAOV = data->get<cudaMipmappedArray_t>("outputAOV");
 *                   auto width = data->get<uint32_t>("width");
 *                   auto height = data->get<uint32_t>("height");
 *
 *                   // ... call CUDA kernel
 *               });
 * @endcode
 *
 * Note: after building the ComputeParams of scheduling the CUDA task, the ComputeParamsBuilder instance cannot be modified anymore.
 * This restriction is imposed in order to provide the guarantee that the AOV pointers built by the builder are not invalidated by further
 * modifications of the render product through the builder API.
 *
 * @tparam TKey The type of the key used to set and get the parameter values from the @ref ComputeParams object.
 */
template<typename TKey>
class ComputeParamsBuilder
{

public:
    /**
     * @brief Callback invoked after extracting a texture AOV with a given token from the Render Product.
     * Allows adding additional parameters from the TextureDesc of the AOV, such as the width, height, etc.
    */
    using TextureDescCallback = std::function<void(cudaMipmappedArray_t, carb::graphics::TextureDesc const*, ComputeParams<TKey>&)>;
    /**
     * @brief Callback invoked after extracting a buffer AOV with a given token from the Render Product.
     * Allows adding additional parameters from the BufferDesc of the AOV, such as the bufferSize.
    */
    using BufferDescCallback = std::function<void(cudaMipmappedArray_t, carb::graphics::BufferDesc const*, ComputeParams<TKey>&)>;
    /**
     * @brief Callback invoked by the builder to explicitly allocate an AOV.
     * Allows explicit control over the parameters of the new AOV.
    */
    using AllocateAOVCallback = std::function<cudaMipmappedArray_t(ComputeParams<TKey> const&,
                                                                 omni::graph::core::GpuFoundationsInterfaces*,
                                                                 omni::usd::hydra::HydraRenderProduct*,
                                                                 rtx::resourcemanager::SyncScopeId,
                                                                 uint32_t)>;
    /**
     * @brief Callback invoked by the builder after the allocation of a new AOV.
     * Allows setting fabric attributes of the node.
    */
    using PostAllocateAOVCallback = std::function<void(cudaMipmappedArray_t)>;

private:

//! The type of the AOV parameter.
enum class AOVType
{
    //! Specifies that the parameter is a buffer AOV.
    Buffer,
    //! Specifies that the parameter is a texture AOV.
    Texture
};

//! The parameter data used to construct the final ComputeParams structure.
template <typename T>
struct AOVParams
{
    //! The type of the AOV.
    AOVType aovType;
    //! The key of the parameter.
    T key;
    //! The token of the AOV.
    omni::fabric::TokenC aovToken;
    union
    {
        //! The texture description used to create a new texture RenderVar.
        carb::graphics::TextureDesc textureDesc;
        //! The buffer description used to create a new buffer RenderVar.
        carb::graphics::BufferDesc bufferDesc;
    };
    //! The callback applied after the declaration of an input AOV.
    //! Allows users to set up additional parameters that are dependent on the properties of the AOV.
    carb::cpp::variant<TextureDescCallback, BufferDescCallback> inputAovCb;
    //! The callback to allocate a new AOV explicitly.
    AllocateAOVCallback allocateAOVCb;
    //! The callback invoked after a new AOV is allocated.
    //! Allows setting up the forwarding of the new AOV pointer to output node attributes.
    PostAllocateAOVCallback postAllocateCb;
};

public:
    /**
     * @brief Constructor.
     *
     * @param[in] gpu The GPU interface.
     * @param[in] rp The render product on which the CUDA computation is applied.
     * @param[in] db The node database.
     * @param[in] initialCapacity The initial capacity of the container where the parameters are stored.
     */
    ComputeParamsBuilder(
        omni::graph::core::GpuFoundationsInterfaces* gpu,
        omni::usd::hydra::HydraRenderProduct* rp,
        omni::graph::core::ogn::OmniGraphDatabase& db,
        std::size_t initialCapacity = 32)
        : m_gpu(gpu)
        , m_rp(rp)
        , m_db(db)
        , m_data(initialCapacity)
        , m_deviceIndex(s_invalidDeviceIndex)
        , m_buildError(BuildError::NoError)
    {
        m_inputAOVs.reserve(initialCapacity);
        m_outputAOVs.reserve(initialCapacity);
        m_outputAOVTokens.reserve(initialCapacity);
    }

    /**
     * @brief Set a parameter value of type TValue with the specified key.
     *
     * @tparam TValue The type of the parameter value.
     *
     * @param[in] key The unique identifier of the parameter value.
     * @param[in] value The parameter value.
     * @return Returns a reference of the ComputeParamsBuilder.
     */
    template<typename TValue>
    ComputeParamsBuilder& addValue(TKey const& key, TValue&& value)
    {
        m_data.add(key, value);
        return *this;
    }

    /**
     * @brief Add a texture AOV. The AOV is expected to be already allocated.
     *
     * @param[in] key The unique identifier of the parameter value.
     * @param[in] aovToken The token used to extract the AOV from the Render Product.
     * @param[in] cb Callback which can be used to add additional parameters from the texture description of the AOV.
     * @return Returns a reference of the ComputeParamsBuilder.
     */
    ComputeParamsBuilder& addInputTexture(TKey const& key, omni::fabric::TokenC aovToken, TextureDescCallback const& cb = nullptr)
    {
        m_inputAOVs.emplace_back(AOVParams<TKey>
        {
            /*.aovType =*/ AOVType::Texture,
            /*.key =*/ key,
            /*.aovToken =*/ aovToken
        });
        m_inputAOVs.back().inputAovCb = cb;
        return *this;
    }

    /**
     * @brief Add a buffer AOV. The AOV is expected to be already allocated.
     *
     * @param[in] key The unique identifier of the parameter value.
     * @param[in] aovToken The token used to extract the AOV from the Render Product.
     * @param[in] cb Callback which can be used to add additional parameters from the buffer description of the AOV.
     * @return Returns a reference of the ComputeParamsBuilder.
     */
    ComputeParamsBuilder& addInputBuffer(TKey const& key,
                                         omni::fabric::TokenC aovToken,
                                         BufferDescCallback const& cb = nullptr)
    {
        m_inputAOVs.emplace_back(AOVParams<TKey>{ /*.aovType =*/AOVType::Buffer,
                                                  /*.key =*/key,
                                                  /*.aovToken =*/aovToken });
        m_inputAOVs.back().inputAovCb = cb;
        return *this;
    }

    /**
     * @brief Allocates a new texture AOV which will be filled in the CUDA task.
     *
     * @param[in] key The unique identifier of the parameter value.
     * @param[in] aovToken The token used to extract the AOV from the Render Product.
     * @param[in] width The width of the allocated texture.
     * @param[in] height The height of the allocated texture.
     * @param[in] format The texture format.
     * @param[in] debugName A string used to identify the new AOV in the debugger.
     * @param[in] postAllocateCb A callback which allows the binding of the new AOV to an output attribute of a node.
     * @return Returns a reference of the ComputeParamsBuilder.
     */
    ComputeParamsBuilder& addOutputTexture(TKey const& key,
                                           omni::fabric::TokenC aovToken,
                                           uint32_t width,
                                           uint32_t height,
                                           carb::graphics::Format format,
                                           const char* debugName,
                                           PostAllocateAOVCallback const& postAllocateCb = nullptr)
    {
        declareOutputTexture(key, aovToken, width, height, format, 1, debugName, postAllocateCb);
        return *this;
    }

    /**
     * @brief Allocates a new texture AOV which will be filled in the CUDA task.
     *
     * @param[in] key The unique identifier of the parameter value.
     * @param[in] aovToken The token used to extract the AOV from the Render Product.
     * @param[in] width The width of the allocated texture.
     * @param[in] height The height of the allocated texture.
     * @param[in] format The texture format.
     * @param[in] mipCount The number of mips in the new texture.
     * @param[in] debugName A string used to identify the new AOV in the debugger.
     * @param[in] postAllocateCb A callback which allows the binding of the new AOV to an output attribute of a node.
     * @return Returns a reference of the ComputeParamsBuilder.
     */
    ComputeParamsBuilder& addOutputTexture(TKey const& key,
                                           omni::fabric::TokenC aovToken,
                                           uint32_t width,
                                           uint32_t height,
                                           carb::graphics::Format format,
                                           uint16_t mipCount,
                                           const char* debugName,
                                           PostAllocateAOVCallback const& postAllocateCb = nullptr)
    {
        declareOutputTexture(key, aovToken, width, height, format, mipCount, debugName, postAllocateCb);
        return *this;
    }

    /**
     * @brief Allocates a new texture AOV which will be filled in the CUDA task.
     *
     * Allows explicit definition and initialization of the AOV.
     *
     * @param[in] key The unique identifier of the parameter value.
     * @param[in] aovToken The token used to extract the AOV from the Render Product.
     * @param[in] callback The callback where the initialization of the AOV must be done.
     * @return Returns a reference of the ComputeParamsBuilder.
     */
    ComputeParamsBuilder& addOutputTexture(TKey const& key,
                                           omni::fabric::TokenC aovToken,
                                           AllocateAOVCallback const& callback)
    {
        m_outputAOVTokens.emplace_back(aovToken);
        m_outputAOVs.emplace_back(AOVParams<TKey>{ /*.aovType =*/AOVType::Texture,
                                                   /*.key =*/key,
                                                   /*.aovToken =*/aovToken });
        m_outputAOVs.back().allocateAOVCb = callback;
        return *this;
    }

    /**
     * @brief Allocates a new buffer AOV which will be filled in the CUDA task.
     *
     * @param[in] key The unique identifier of the parameter value.
     * @param[in] aovToken The token used to extract the AOV from the Render Product.
     * @param[in] bufferSize The size of the allocated buffer.
     * @param[in] debugName A string used to identify the new AOV in the debugger.
     * @param[in] postAllocateCb A callback which allows the binding of the new AOV to an output attribute of a node.
     * @return Returns a reference of the ComputeParamsBuilder.
     */
    ComputeParamsBuilder& addOutputBuffer(TKey const& key,
                                          omni::fabric::TokenC aovToken,
                                          uint32_t bufferSize,
                                          const char* debugName,
                                          PostAllocateAOVCallback const& postAllocateCb = nullptr)
    {
        m_outputAOVTokens.emplace_back(aovToken);
        m_outputAOVs.emplace_back(AOVParams<TKey>{
            /*.aovType =*/AOVType::Buffer,
            /*.key =*/key,
            /*.aovToken =*/aovToken,
        });
        m_outputAOVs.back().bufferDesc = { carb::graphics::kBufferUsageFlagExportShared, bufferSize, debugName, nullptr };
        m_outputAOVs.back().postAllocateCb = postAllocateCb;
        return *this;
    }

    /**
     * @brief Allocates a new buffer AOV which will be filled in the CUDA task.
     *
     * Allows explicit definition and initialization of the AOV.
     *
     * @param[in] key The unique identifier of the parameter value.
     * @param[in] aovToken The token used to extract the AOV from the Render Product.
     * @param[in] callback The callback where the initialization of the AOV must be done.
     * @return Returns a reference of the ComputeParamsBuilder.
     */
    ComputeParamsBuilder& addOutputBuffer(TKey const& key,
                                          omni::fabric::TokenC aovToken,
                                          AllocateAOVCallback const& callback)
    {
        m_outputAOVTokens.emplace_back(aovToken);
        m_outputAOVs.emplace_back(AOVParams<TKey>{ /*.aovType =*/AOVType::Buffer,
                                                   /*.key =*/key,
                                                   /*.aovToken =*/aovToken });
        m_outputAOVs.back().allocateAOVCb = callback;
        return *this;
    }

    /**
     * @brief Builds the final @ref ComputeParams structure.
     *
     * The following steps are performed when building the final params, in this order:
     * 1) The new AOVs are added to the Render Product
     * 2) The input AOVs (already allocated) are extracted from the Render Product
     * 3) The new AOVs are allocated
     *
     * This sequence ensures that all the AOV pointers in the resulting ComputeParams structure are valid.
     *
     * No further values can be added to the builder after this call.
     *
     * @return Returns the constructed ComputeParams object.
     */
    ComputeParams<TKey> build()
    {
        CARB_PROFILE_ZONE(carb::profiler::kCaptureMaskDefault, "ComputeParamsBuilder::build");

        if (!isValid())
            return m_data;

        // append the outputs first to avoid further structural changes which will invalidate the AOV pointers
        if (!m_outputAOVTokens.empty())
            appendUninitializedRenderVars(m_rp, m_outputAOVTokens);

        auto rmCtx = reinterpret_cast<rtx::resourcemanager::Context*>(m_gpu->resourceManagerContext);
        auto rm = reinterpret_cast<rtx::resourcemanager::ResourceManager*>(m_gpu->resourceManager);

        for (auto const& aovParams : m_inputAOVs)
        {
            auto aovPtr = omni::usd::hydra::getRenderVarFromProduct(m_rp, aovParams.aovToken.token);
            if (aovPtr == nullptr)
            {
                m_db.logWarning("Missing RenderVar %s", m_db.tokenToString(aovParams.aovToken));
                continue;
            }

            if (aovPtr->resource == nullptr)
            {
                m_db.logWarning("RenderVar %s is an invalid resource.", m_db.tokenToString(aovParams.aovToken));
                continue;
            }

            const uint32_t deviceIndex = rm->getFirstDeviceIndex(*rmCtx, *aovPtr->resource);
            if (m_deviceIndex != deviceIndex)
            {
                if (m_deviceIndex == s_invalidDeviceIndex)
                {
                    m_deviceIndex = deviceIndex;
                }
                else
                {
                    m_db.logWarning("RenderVar %s has an inconsistent device index (%lu/%lu).",
                                    m_db.tokenToString(aovParams.aovToken), static_cast<unsigned long>(deviceIndex),
                                    static_cast<unsigned long>(m_deviceIndex));
                    m_buildError = BuildError::InconsistentDeviceIndex;
                    break;
                }
            }

            auto cudaPtr = (cudaMipmappedArray_t)rm->getCudaMipmappedArray(*aovPtr->resource, m_deviceIndex);
            switch (aovParams.aovType)
            {
            case AOVType::Texture:
            {
                if (carb::cpp::holds_alternative<TextureDescCallback>(aovParams.inputAovCb))
                {
                    const auto textureDesc = rm->getTextureDesc(*rmCtx, aovPtr->resource);
                    auto cb = carb::cpp::get<TextureDescCallback>(aovParams.inputAovCb);
                    if (cb)
                        cb(cudaPtr, textureDesc, m_data);
                }
            }
            break;
            case AOVType::Buffer:
            {
                if (carb::cpp::holds_alternative<BufferDescCallback>(aovParams.inputAovCb))
                {
                    const auto bufferDesc = rm->getBufferDesc(aovPtr->resource);
                    auto cb = carb::cpp::get<BufferDescCallback>(aovParams.inputAovCb);
                    if (cb)
                        cb(cudaPtr, bufferDesc, m_data);
                }
            }
            break;
            }
            m_data.add(aovParams.key, cudaPtr);
        }

        if (m_buildError != BuildError::NoError)
        {
            return m_data;
        }

        // the device index is not set, get the index of the first device render variable
        if (m_deviceIndex == s_invalidDeviceIndex)
        {
            for (uint32_t i = 0; i < m_rp->renderVarCnt; i++)
            {
                if (m_rp->vars[i].isRpResource)
                {
                    m_deviceIndex = rm->getFirstDeviceIndex(*rmCtx, *m_rp->vars[i].resource);
                    break;
                }
            }
            // the render product has no device render variable, use the render product device index
            if (m_deviceIndex == s_invalidDeviceIndex)
            {
                m_deviceIndex = carb::graphics::DeviceMask(m_rp->deviceMask).getFirstIndex();
            }
        }

        auto iRenderGraph = reinterpret_cast<gpu::rendergraph::IRenderGraph*>(m_gpu->renderGraph);
        auto rgBuilder = reinterpret_cast<rtx::rendergraph::RenderGraphBuilder*>(m_gpu->renderGraphBuilder);
        auto renderGraph = iRenderGraph->getRenderGraph(m_deviceIndex);
        const auto syncScopeId = rgBuilder->getRenderGraphDesc(*renderGraph).syncScopeId;

        for (auto const& aovParams : m_outputAOVs)
        {
            cudaMipmappedArray_t ptr = 0;
            if (aovParams.allocateAOVCb != nullptr)
            {
                // custom AOV allocation
                auto cb = aovParams.allocateAOVCb;
                ptr = cb(m_data, m_gpu, m_rp, syncScopeId, m_deviceIndex);
            }
            else
            {
                // standard AOV allocation
                switch (aovParams.aovType)
                {
                case AOVType::Texture:
                    ptr = (cudaMipmappedArray_t)allocateRenderVarTexture(
                        m_gpu, m_rp, syncScopeId, m_deviceIndex, aovParams.aovToken, aovParams.textureDesc);
                    break;
                case AOVType::Buffer:
                    ptr = (cudaMipmappedArray_t)allocateRenderVarBuffer(
                        m_gpu, m_rp, syncScopeId, m_deviceIndex, aovParams.aovToken, aovParams.bufferDesc);
                    break;
                default:
                    break;
                }
            }
            m_data.add(aovParams.key, ptr);
            if (aovParams.postAllocateCb != nullptr)
                aovParams.postAllocateCb(ptr);
        }

        return m_data;
    }

    /**
     * @brief Builds the final @ref ComputeParams structure and schedules the CUDA task.
     *
     * No further values can be added to the builder after this call.
     *
     * @param[in] renderOpName The name of the render op in the render graph.
     * @param[in] computeCuda The entry point to the CUDA computation kernel.
     * @return Returns true if the builder is valid and the CUDA task was scheduled, otherwise returns false.
     */
    bool scheduleCudaTask(const char* renderOpName,
                          std::function<void(ComputeParams<TKey>*, cudaStream_t)> const& computeCuda);

    /**
     * @brief Builds the final ComputeParams structure and schedules the CUDA task.
     *
     * Allows validation of the ComputeParams before scheduling the CUDA task.
     * No further values can be added to the builder after this call.
     *
     * @param[in] renderOpName The name of the render op in the render graph.
     * @param[in] computeCuda The entry point to the CUDA computation kernel.
     * @param[in] validateCb A callback to validate the parameters before scheduling the CUDA task.
     * @return Returns true if the builder is valid, the params are validated by the user callback
     * and the CUDA task was scheduled, otherwise returns false.
     */
    bool scheduleCudaTask(
        const char* renderOpName,
        std::function<void(ComputeParams<TKey>*, cudaStream_t)> const& computeCuda,
        std::function<bool(ComputeParams<TKey> const&)> const& validateCb
    );

    /**
     * @brief Checks if this instance is initialized correctly, with valid RenderProduct and GPU interface pointers.
     * @return Returns true if the instance is valid, otherwise returns false.
     */
    bool isValid() const
    {
        if (!m_gpu || !m_rp || (m_buildError != BuildError::NoError))
        {
            CARB_LOG_WARN_ONCE("ComputeParamsBuilder: invalid RenderProduct inputs");
            return false;
        }

        return true;
    }

private:

    void declareOutputTexture(TKey const& key,
                              omni::fabric::TokenC aovToken,
                              uint32_t width,
                              uint32_t height,
                              carb::graphics::Format format,
                              uint16_t mipCount,
                              const char* debugName,
                              PostAllocateAOVCallback const& postAllocateCb)
    {
        m_outputAOVTokens.emplace_back(aovToken);
        m_outputAOVs.emplace_back(AOVParams<TKey>{ /*.aovType =*/AOVType::Texture,
                                                   /*.key =*/key,
                                                   /*.aovToken =*/aovToken });
        m_outputAOVs.back().textureDesc = { carb::graphics::TextureType::e2D,
                                            carb::graphics::kTextureUsageFlagShaderResourceStorage |
                                                carb::graphics::kTextureUsageFlagShaderResource |
                                                carb::graphics::kTextureUsageFlagExportShared,
                                            width,
                                            height,
                                            1,
                                            mipCount,
                                            format,
                                            carb::graphics::SampleCount::e1x,
                                            { { 0, 0, 0, 0 }, nullptr },
                                            debugName,
                                            nullptr };
        m_outputAOVs.back().postAllocateCb = postAllocateCb;
    }

    static void appendUninitializedRenderVars(omni::usd::hydra::HydraRenderProduct* rp,
                                              const std::vector<omni::fabric::TokenC>& renderVarTokens)
    {
        using TokenC = omni::fabric::TokenC;

        // filter already existing aovs
        std::vector<TokenC> filteredRenderVarTokens;
        filteredRenderVarTokens.reserve(renderVarTokens.size());
        for (const auto token : renderVarTokens)
        {
            if (!omni::usd::hydra::getRenderVarFromProduct(rp, token.token))
            {
                filteredRenderVarTokens.emplace_back(token);
            }
        }

        using namespace omni::usd::hydra;
        const size_t numRenderVars = filteredRenderVarTokens.size();
        HydraRenderVar* newVars = new HydraRenderVar[rp->renderVarCnt + numRenderVars];
        const size_t varArraySize = sizeof(HydraRenderVar) * rp->renderVarCnt;
        std::memcpy(newVars, rp->vars, varArraySize);
        for (size_t i = 0; i < numRenderVars; ++i)
        {
            newVars[rp->renderVarCnt + i].aov = filteredRenderVarTokens[i].token;
            newVars[rp->renderVarCnt + i].isRpResource = true;
            newVars[rp->renderVarCnt + i].resource = nullptr;
            newVars[rp->renderVarCnt + i].isBufferRpResource = true;
        }
        delete[] rp->vars;
        rp->vars = newVars;
        rp->renderVarCnt += static_cast<uint32_t>(numRenderVars);
    }

    static uint64_t allocateRenderVarBuffer(omni::graph::core::GpuFoundationsInterfaces* gpu,
                                            omni::usd::hydra::HydraRenderProduct* rp,
                                            rtx::resourcemanager::SyncScopeId syncScopeId,
                                            uint32_t deviceIndex,
                                            omni::fabric::TokenC deviceRenderVarToken,
                                            carb::graphics::BufferDesc const& buffDesc)
    {
        auto rmCtx = reinterpret_cast<rtx::resourcemanager::Context*>(gpu->resourceManagerContext);
        auto rm = reinterpret_cast<rtx::resourcemanager::ResourceManager*>(gpu->resourceManager);

        using namespace carb::graphics;

        auto deviceRenderVar = omni::usd::hydra::getRenderVarFromProduct(rp, deviceRenderVarToken.token);
        CARB_ASSERT(deviceRenderVar && deviceRenderVar->isRpResource && deviceRenderVar->isBufferRpResource);
        if (!deviceRenderVar || !deviceRenderVar->isRpResource || !deviceRenderVar->isBufferRpResource)
        {
            return 0;
        }

        const rtx::resourcemanager::ResourceDesc resourceDesc = { rtx::resourcemanager::ResourceMode::ePooled,
                                                                  MemoryLocation::eDevice,
                                                                  rtx::resourcemanager::ResourceCategory::eOtherBuffer,
                                                                  rtx::resourcemanager::kResourceUsageFlagCudaShared,
                                                                  DeviceMask::getDeviceMaskFromIndex(deviceIndex),
                                                                  deviceIndex,
                                                                  syncScopeId };

        CARB_ASSERT(!deviceRenderVar->resource);
        if (!deviceRenderVar->resource)
        {
            deviceRenderVar->resource =
                buffDesc.size > 0 ? rm->getResourceFromBufferDesc(*rmCtx, buffDesc, resourceDesc) : nullptr;
        }

        auto cudaDevicePointer =
            deviceRenderVar->resource ? rm->getCudaDevicePointer(*deviceRenderVar->resource, deviceIndex) : nullptr;

        return reinterpret_cast<uint64_t>(cudaDevicePointer);
    }

    static uint64_t allocateRenderVarTexture(omni::graph::core::GpuFoundationsInterfaces* gpu,
                                             omni::usd::hydra::HydraRenderProduct* rp,
                                             rtx::resourcemanager::SyncScopeId syncScopeId,
                                             uint32_t deviceIndex,
                                             omni::fabric::TokenC deviceRenderVarToken,
                                             carb::graphics::TextureDesc const& texDesc)
    {
        auto rmCtx = reinterpret_cast<rtx::resourcemanager::Context*>(gpu->resourceManagerContext);
        auto rm = reinterpret_cast<rtx::resourcemanager::ResourceManager*>(gpu->resourceManager);

        using namespace carb::graphics;

        auto deviceRenderVar = omni::usd::hydra::getRenderVarFromProduct(rp, deviceRenderVarToken.token);
        CARB_ASSERT(deviceRenderVar && deviceRenderVar->isRpResource && deviceRenderVar->isBufferRpResource);
        if (!deviceRenderVar || !deviceRenderVar->isRpResource || !deviceRenderVar->isBufferRpResource)
        {
            return 0;
        }

        const rtx::resourcemanager::ResourceDesc resDesc = { rtx::resourcemanager::ResourceMode::ePooled,
                                                             carb::graphics::MemoryLocation::eDevice,
                                                             rtx::resourcemanager::ResourceCategory::eOtherTexture,
                                                             rtx::resourcemanager::kResourceUsageFlagCudaShared,
                                                             carb::graphics::DeviceMask::getDeviceMaskFromIndex(
                                                                 deviceIndex),
                                                             deviceIndex,
                                                             syncScopeId };

        deviceRenderVar->resource = rm->getResourceFromTextureDesc(*rmCtx, texDesc, resDesc);
        deviceRenderVar->isBufferRpResource = false;

        auto cudaDevicePointer =
            deviceRenderVar->resource ? rm->getCudaDevicePointer(*deviceRenderVar->resource, deviceIndex) : nullptr;
        return reinterpret_cast<uint64_t>(cudaDevicePointer);
    }

private:
    omni::graph::core::GpuFoundationsInterfaces* m_gpu; //!< The GPU interfaces
    omni::usd::hydra::HydraRenderProduct* m_rp; //!< The render product
    omni::graph::core::ogn::OmniGraphDatabase& m_db; //!< The database of the node that created the builder.
    std::vector<AOVParams<TKey>> m_inputAOVs; //!< The list of input AOVs to be added to the CUDA params.
    std::vector<AOVParams<TKey>> m_outputAOVs; //!< The list of output AOVs to be added to the CUDA params.
    std::vector<omni::fabric::TokenC> m_outputAOVTokens; //!< The tokens of the output AOVs.
    ComputeParams<TKey> m_data; //!< The instance of @ref ComputeParams
    uint32_t m_deviceIndex; //!< The index of the device on which the cuda task is scheduled.
    /**
     * @brief Encodes any errors encountered during an invocation of the @ref build method.
     */
    enum class BuildError
    {
        //! No error was encountered during the build of the @ref ComputeParams instance.
        NoError,
        //! The error code when two or more AOVs have a different device index in the same render product.
        InconsistentDeviceIndex
    };
    BuildError m_buildError; //!< The status of the build.

    //! The default value of the uninitialized device index.
    static constexpr uint32_t s_invalidDeviceIndex = std::numeric_limits<uint32_t>::max();

};

namespace
{
#ifndef DOXYGEN_BUILD
// Temporary structure for passing the params and the computeCuda callback to the cudaInterop lambda.
template <typename TParams>
struct UserData
{
    ComputeParams<TParams>* params; //!< The params instance.
    std::function<void(ComputeParams<TParams>*, cudaStream_t)> computeCuda; //!< The cuda function.
};
#endif // DOXYGEN_BUILD
} // namespace

/**
 * @brief Schedule a CUDA task on the post render graph.
 *
 * @param[in] gpu The GPU interface.
 * @param[in] rp The render product on which the CUDA computation is applied.
 * @param[in] deviceIndex The device index on which the CUDA task is scheduled.
 * @param[in] computeParams The parameters of the computation.
 * @param[in] renderOpName The name of the render op in the render graph.
 * @param[in] computeCuda The CUDA computation entry point.
 * @tparam TParams The concrete type of the CUDA compute params.
 */
template <typename TParams>
inline void scheduleCudaTask(omni::graph::core::GpuFoundationsInterfaces* gpu,
                             omni::usd::hydra::HydraRenderProduct* rp,
                             uint32_t deviceIndex,
                             ComputeParams<TParams> const& computeParams,
                             const char* renderOpName,
                             std::function<void(ComputeParams<TParams>*, cudaStream_t)> const& computeCuda)
{
    CARB_ASSERT(gpu);
    CARB_ASSERT(rp);

    auto iRenderGraph = reinterpret_cast<gpu::rendergraph::IRenderGraph*>(gpu->renderGraph);
    auto rgBuilder = reinterpret_cast<rtx::rendergraph::RenderGraphBuilder*>(gpu->renderGraphBuilder);
    auto renderGraph = iRenderGraph->getRenderGraph(deviceIndex);

    auto computeParamsPtr = new ComputeParams<TParams>(std::move(computeParams));
    auto cudaData = new UserData<TParams>{ computeParamsPtr, computeCuda };

    const rtx::rendergraph::ParamBlockRefs paramBlockRefs{ 0, {} };
    rtx::rendergraph::RenderOpParams* renderOpParams = rgBuilder->createParams(*renderGraph, paramBlockRefs);
    rtx::rendergraph::addRenderOpLambdaEx(
        *rgBuilder, *renderGraph, renderOpName, renderOpParams, rtx::rendergraph::kRenderOpFlagNoAnnotation,
        [rgBuilder, cudaData, computeCuda](rtx::rendergraph::RenderOpInputCp renderOpInput)
        {
            renderOpInput->graphicsMux->cmdCudaInterop(
                renderOpInput->commandList,
                [](cudaStream_t cudaStream, void* userData) -> void
                {
                    auto cudaData = reinterpret_cast<UserData<TParams>*>(userData);
                    auto params = cudaData->params;
                    auto computeCuda = cudaData->computeCuda;
                    computeCuda(params, cudaStream);
                    delete params;
                    delete cudaData;
                },
                cudaData, carb::graphicsmux::CudaInteropFlags::eNone);
        });
}

template<typename TKey>
inline bool ComputeParamsBuilder<TKey>::scheduleCudaTask(const char* renderOpName,
                                                         std::function<void(ComputeParams<TKey>*, cudaStream_t)> const& computeCuda)
{
    CARB_PROFILE_ZONE(carb::profiler::kCaptureMaskDefault, "ComputeParamsBuilder::scheduleCudaTask");

    if (!isValid())
        return false;

    auto computeParams = build();
    omni::graph::image::unstable::scheduleCudaTask(m_gpu, m_rp, m_deviceIndex, computeParams, renderOpName, computeCuda);
    return true;
}

template <typename TKey>
inline bool ComputeParamsBuilder<TKey>::scheduleCudaTask(
    const char* renderOpName,
    std::function<void(ComputeParams<TKey>*, cudaStream_t)> const& computeCuda,
    std::function<bool(ComputeParams<TKey> const&)> const& validateCb)
{
    if (!isValid())
        return false;

    auto computeParams = build();
    if (validateCb && validateCb(computeParams))
    {
        omni::graph::image::unstable::scheduleCudaTask(
            m_gpu, m_rp, m_deviceIndex, computeParams, renderOpName, computeCuda);
        return true;
    }

    return false;
}

} // namespace unstable
} // namespace image
} // namespace graph
} // namespace omni
