// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

//! @file
//!
//! @brief Material Manager utility


#include <carb/Framework.h>
#include <carb/logging/Log.h>

#include <omni/sensors/cuda/CudaHelperDecl.h>
#include <omni/String.h>
#include <omni/sensors/materials/IMaterial.h>

#include <algorithm>
#include <cuda.h>
#include <cuda_runtime_api.h>
#include <fstream>
#include <map>
#include <memory>
#include <nvrtc.h>
#include <set>
#include <string>
#include <vector>

#define PRINT_GENERATED_SOURCE 0
#define PRINT_PTX 0
#define WRITE_CUBIN 0
#define LOG_NVRTC_OUTPUT 0


namespace omni
{
namespace sensors
{
namespace materials
{

/**
 * @brief used in a MaterialMap to provide the name of a material and *optionally*, a sensors material config.
 */
struct MaterialDesc
{
    omni::string type; /**< material implementation to execute. (i.e. Core or RetroReflective)*/
    std::shared_ptr<IMaterialConfig> config; /**< opaque pointer to a struct that inherits from IMaterialConfig */

    MaterialDesc() = default;

    MaterialDesc(omni::string type_, std::shared_ptr<IMaterialConfig> config_) : type{ type_ }, config{ config_ }
    {
    }

    MaterialDesc& operator=(omni::string type_)
    {
        type = type_;
        return *this;
    }

    template <typename TConfig>
    MaterialDesc& operator=(std::shared_ptr<TConfig>&& config_)
    {
        config = config_;
        return *this;
    }

    template <typename TName, typename TConfig>
    MaterialDesc& operator=(std::pair<TName, TConfig> params)
    {
        type = params.first;
        config = std::make_shared<TConfig>(std::move(params.second));
        return *this;
    }

    template <typename TConfig>
    TConfig* getConfigAs()
    {
        return dynamic_cast<TConfig*>(config.get());
    }

    template <typename TConfig>
    const TConfig* getConfigAs() const
    {
        return dynamic_cast<const TConfig*>(config.get());
    }
};

using MaterialMap = std::map<uint32_t, MaterialDesc>;

/**
 * @brief an interface managing the main entry hit shader, multiple material
 * Bidirectional Scattering Distribution Functions (BSDF) shaders, and the infrastructure
 * for executing specific material BSDFs from a supplied index in the main hit shader
 * routine.
 *
 */
class MaterialManager
{
public:
    /**
     * LaunchCfg, structure that contains data for launching main hit shader
     * within the processReturns method
     */
    struct LaunchCfg
    {
        dim3 blocksPerGrid;
        dim3 threadsPerBlock;
        cudaStream_t cudaStream;
        unsigned int sharedMemBytes{ 0 };
        int cudaDevice;
    };

    MaterialManager(){};

    ~MaterialManager()
    {
        resetMaterialManager();
    }

    void resetMaterialManager()
    {
        if (m_dEntryPointUserData)
        {
            CUDA_CALL(cudaFree(m_dEntryPointUserData));
        }
        for (auto& context : m_matContexts)
        {
            CUDA_CALL(cudaFreeHost(context));
        }
        if (m_module)
        {
            CUDA_DRIVER_CALL(cuModuleUnload(m_module));
        }
        m_matContexts.clear();

        m_initialized = false;
        m_interfaces.clear();
        m_matPtxStrings.clear();
        m_matEntryPointNames.clear();
        m_matContexts.clear();
        m_matContextSizes.clear();
        m_matIds.clear();
        m_hitShaderPtxString.clear();
        m_hitShaderEntryPointName.clear();
        m_shaderTablePtxString.clear();
        m_entryPointUserDataSize = 0;
    }

    /**
     * @brief method for determining whether the material manager has been initialized
     * @return bool
     */
    bool initialized() const
    {
        return m_initialized;
    }

    /**
     * @brief Initializes the material manager instance
     * @param materialMap Map index and material description
     * @param hitShaderPtxString The main hit shader kernel in PTX compiled format
     * @param entryPointName Entry point name of main hit shader to call
     * @param entryPointUserDataSize Size of user data to be copied to device side for main hit shader kernel
     * @param cudaDevice Device id to use for material shader generation and cuda memory operations
     * @return bool
     */
    bool init(const MaterialMap& materialMap,
              const omni::string& hitShaderPtxString,
              const omni::string& entryPointName,
              size_t entryPointUserDataSize,
              int cudaDevice)
    {
        if (!m_initialized)
        {
            // TODO: AE - validate the map config

            // search for all who implement IMaterial and acquire the interfaces
            const uint32_t numInterfaces = carb::getFramework()->getInterfacesCount<IMaterial>();
            m_interfaces.resize(numInterfaces);
            carb::getFramework()->acquireInterfaces(m_interfaces.data(), static_cast<uint32_t>(m_interfaces.size()));


            for (const auto& entry : materialMap)
            {
                auto matId = entry.first;
                auto& matDesc = entry.second;

                auto matHash = carb::hashString(matDesc.type.c_str());

                auto itr = std::find_if(m_interfaces.begin(), m_interfaces.end(),
                                        [matHash](IMaterial* iface)
                                        {
                                            uint64_t hash = iface->getHash();
                                            return hash == matHash;
                                        });

                if (itr != m_interfaces.end())
                {
                    addMaterial(*itr, matId, matDesc.config.get());
                }
                else
                {
                    CARB_LOG_ERROR("Material %s cannot be resolved", matDesc.type.c_str());
                    return false;
                }
            }

            // add hit shader
            m_hitShaderPtxString = hitShaderPtxString.c_str();
            m_hitShaderEntryPointName = entryPointName.c_str();
            m_entryPointUserDataSize = entryPointUserDataSize;

            // allocate device blob for entrypoint user data
            cudaSetDevice(cudaDevice);
            CUDA_CALL(cudaMalloc(&m_dEntryPointUserData, m_entryPointUserDataSize));

            // build and compile the shader table
            generateAndCompileShaderTable();

            buildCudaModule();

            m_initialized = true;
        }

        return true;
    }

    /**
     * @brief updates a given material in the material manager
     * @param materialIF Resolved material to be created and stored in the material manager
     * @param matId The material id that uniquely identifies a specific material BSDF
     * @param materialConfig (optional)
     * @return void
     */
    void updateMaterials(const MaterialMap& materialMap)
    {
        if (!m_initialized)
        {
            CARB_LOG_ERROR("Material manager is not initialized");
            return;
        }

        for (const auto& entry : materialMap)
        {
            auto matId = entry.first;
            auto& matDesc = entry.second;
            const IMaterialConfig* materialConfig{ matDesc.config.get() };

            auto matHash = carb::hashString(matDesc.type.c_str());

            auto itr = std::find_if(m_interfaces.begin(), m_interfaces.end(),
                                    [matHash](IMaterial* iface)
                                    {
                                        uint64_t hash = iface->getHash();
                                        return hash == matHash;
                                    });

            if ((itr != m_interfaces.end()) && (matId < m_matIds.size() - 1))
            {
                IMaterial* materialIF = *itr;

                // get ptx program and entrypoint
                size_t programSize, entryPointNameSize;
                materialIF->getBSDFProgramSizeInfo(programSize, entryPointNameSize);
                omni::string program, entryPointName;
                program.resize(programSize);
                entryPointName.resize(entryPointNameSize);
                materialIF->getBSDFProgram(&program[0], &entryPointName[0]);
                m_matPtxStrings[matId] = program.c_str();
                m_matEntryPointNames[matId] = entryPointName.c_str();

                // get context
                CUDA_CALL(cudaFreeHost(m_matContexts[matId]));
                size_t contextSize = materialIF->getContextSize(materialConfig);
                m_matContexts[matId] = nullptr;
                m_matContextSizes[matId] = contextSize;
                CUDA_CALL(cudaMallocHost(&(m_matContexts[matId]), contextSize));
                materialIF->getContext(m_matContexts[matId], materialConfig);
            }
            else
                CARB_LOG_ERROR("Material %s cannot be resolved", matDesc.type.c_str());
        }

        // build and compile the shader table
        generateAndCompileShaderTable();

        buildCudaModule();
    }

    /**
     * @brief launches the main hit shader kernel for core sensor and material processing
     * @param launchCfg configuration structure for data required to launch main hit shader
     * @param userData user data copied to device side and used within main hit shader
     * @return bool
     */
    bool processReturns(const LaunchCfg& launchCfg, void* userData)
    {
        bool ret = true;
        if (m_entryPointUserDataSize == 0)
        {
            CARB_LOG_ERROR("Cannot Launch kernel hit shader, entry data has not been resolved");
            ret = false;
        }
        else
        {
            cudaSetDevice(launchCfg.cudaDevice);
            CUDA_CALL(cudaMemcpyAsync(m_dEntryPointUserData, userData, m_entryPointUserDataSize, cudaMemcpyHostToDevice,
                                      launchCfg.cudaStream));

            std::vector<void*> kernelParams;
            kernelParams.push_back((void*)&m_dEntryPointUserData);

            CUDA_DRIVER_CALL(cuLaunchKernel(m_hitShaderEntryPoint, launchCfg.blocksPerGrid.x, launchCfg.blocksPerGrid.y,
                                            launchCfg.blocksPerGrid.z, launchCfg.threadsPerBlock.x,
                                            launchCfg.threadsPerBlock.y, launchCfg.threadsPerBlock.z,
                                            launchCfg.sharedMemBytes, launchCfg.cudaStream, &kernelParams[0], nullptr));
        }
        return ret;
    }

private:
    /**
     * @brief Adds a material resolved in the init method into material manager that is later executed from
     * processMaterialById
     * @param materialIF Resolved material to be created and stored in the material manager
     * @param matId The material id that uniquely identifies a specific material BSDF
     * @param materialConfig (optional)
     * @return void
     */
    void addMaterial(IMaterial* materialIF, const uint32_t matId, const IMaterialConfig* materialConfig)
    {
        // get ptx program and entrypoint
        size_t programSize, entryPointNameSize;
        materialIF->getBSDFProgramSizeInfo(programSize, entryPointNameSize);
        omni::string program, entryPointName;
        program.resize(programSize);
        entryPointName.resize(entryPointNameSize);
        materialIF->getBSDFProgram(&program[0], &entryPointName[0]);
        m_matPtxStrings.emplace_back(program.c_str());
        m_matEntryPointNames.emplace_back(entryPointName.c_str());
        // get context
        size_t contextSize = materialIF->getContextSize(materialConfig);
        m_matContexts.push_back(nullptr);
        m_matContextSizes.emplace_back(contextSize);
        CUDA_CALL(cudaMallocHost(&(m_matContexts.back()), contextSize));
        materialIF->getContext(m_matContexts.back(), materialConfig);
        // Add matId
        m_matIds.emplace_back(matId);
    }

    /**
     * @brief method for generating and compiling all materials in material manager
     * and generating a shader table
     * @return void
     */
    void generateAndCompileShaderTable()
    {
        // To avoid duplicate entry point declarations
        std::set<uint64_t> declaredEntryPoints;

        // 1. Generate source code for the material shader table
        std::string src = "typedef void (*bsdf_func)(void* , void*, void*);\n";

        // 1.1 Forward declare the entry points for each BSDF

        bool declRequired = false;
        for (unsigned int idx = 0; idx < m_matEntryPointNames.size(); ++idx)
        {
            auto epHash = carb::hashString(m_matEntryPointNames[idx].c_str());
            std::tie(std::ignore, declRequired) = declaredEntryPoints.insert(epHash);

            if (declRequired)
            {
                src += "__device__ void ";
                src += std::string(m_matEntryPointNames[idx].c_str());
                src += "(void* , void*, void*);\n";
            }

            uint8_t* hContextTemp = reinterpret_cast<uint8_t*>(m_matContexts[idx]);
            src += "__device__ unsigned char " + std::string(m_matEntryPointNames[idx].c_str()) + "_Context_" +
                   std::to_string(idx) + "[] = {";
            for (unsigned int byteIdx = 0; byteIdx < m_matContextSizes[idx]; ++byteIdx)
            {
                if (byteIdx != 0)
                {
                    src += ", ";
                }
                src += std::to_string(hContextTemp[byteIdx]);
            }
            src += "};\n";
        }


        // 1.2 Statically declare an array of function pointers
        src += "__device__ bsdf_func materialBSDFs[] = {";
        uint32_t idx = 0;
        for (const auto& ep : m_matEntryPointNames)
        {
            if (idx != 0)
            {
                src += ", ";
            }
            src += std::string(ep.c_str());
            ++idx;
        }
        src += "};\n";

        // 1.3 Statically declare an array of material context pointers
        src += "__device__ void* materialCTXs[] = {";
        idx = 0;
        for (const auto& ep : m_matEntryPointNames)
        {
            if (idx != 0)
            {
                src += ", ";
            }
            src += "(void*)" + std::string(ep.c_str()) + "_Context_" + std::to_string(idx);
            ++idx;
        }
        src += "};\n";

        src += "__device__ unsigned int matIdToIdxMap[] = {";
        idx = 0;
        for (const uint32_t id : m_matIds)
        {
            if (idx != 0)
            {
                src += ", ";
            }
            src += std::to_string(id);
            ++idx;
        }
        src += "};\n";

        src += R"(

            __device__ inline unsigned short int binarySearch(unsigned int arr[], const unsigned int x, int l, int r)
            {
                while (l <= r) {
                    unsigned short int m = l + (r - l) / 2;

                    // Check if x is present at mid
                    if (arr[m] == x)
                        return m;

                    // If x greater, ignore left half
                    if (arr[m] < x)
                        l = m + 1;

                    // If x is smaller, ignore right half
                    else
                        r = m - 1;
                }

                // if we reach here, then element was
                // not present
                return 0;
            }

            __device__ inline unsigned short int getIndexFromMatId(const unsigned int materialId)
            {
                return binarySearch( matIdToIdxMap, materialId, 0, sizeof(matIdToIdxMap)/sizeof(unsigned int)-1 );
            }

        )";

        src += R"(__device__ void processMaterialById(void* outBlob, void* inBlob, unsigned int materialId)
    	    {
                unsigned int baseMatId = materialId & 0xFF;
                unsigned short int index = getIndexFromMatId(baseMatId);
                bsdf_func bsdf = materialBSDFs[index];
                void* context = materialCTXs[index];
                bsdf(outBlob,inBlob, context);
    	    }

            __device__ void* getMatCtx(unsigned int materialId)
            {
                unsigned int baseMatId = materialId & 0xFF;
                unsigned short int index = getIndexFromMatId(baseMatId);
                return materialCTXs[index];
            }
            )";


        if (PRINT_GENERATED_SOURCE)
        {
            printf("Shader table source:\n %s\n", src.c_str());
        }

        nvrtcProgram program;
        NVRTC_CALL(nvrtcCreateProgram(&program, src.c_str(), "ShaderTable", 0, nullptr, nullptr));

        std::vector<omni::string> options;
        options.push_back(omni::string("-dc"));

        std::vector<const char*> compileOptPtrs;
        for (size_t i = 0; i < options.size(); i++)
        {
            compileOptPtrs.push_back(options[i].c_str());
        }
#if (LOG_NVRTC_OUTPUT == 0)
        NVRTC_CALL(nvrtcCompileProgram(program, static_cast<int>(compileOptPtrs.size()), (char**)&compileOptPtrs[0]));
#else
        if (nvrtcCompileProgram(program, static_cast<int>(compileOptPtrs.size()), (char**)&compileOptPtrs[0]) !=
            NVRTC_SUCCESS)
        {
            omni::string programLog;
            NVRTC_PROGRAM_LOG(program, programLog);
            CARB_LOG_ERROR("Failed to compile material shader table:\n%s", programLog.c_str());
        }
#endif

        // Grab the PTX and store it into the local object
        size_t ptxSize = 0;
        NVRTC_CALL(nvrtcGetPTXSize(program, &ptxSize));
        std::vector<char> ptxtmp(ptxSize);
        NVRTC_CALL(nvrtcGetPTX(program, &ptxtmp[0]));
        m_shaderTablePtxString = omni::string(&ptxtmp[0]);

        NVRTC_CALL(nvrtcDestroyProgram(&program));
    }

    /**
     * @brief method for Just In Time compiling for the shader table and hit shader
     * into a cuda module.
     * @return void
     */
    void buildCudaModule()
    {
        cudaFree(0);
        CUlinkState linkState;

        std::vector<CUjit_option> optionNames;
        std::vector<void*> optionValues;

        if (optionNames.size() != optionValues.size())
        {
            printf("ERROR: jit option names and value vectors have different sizes\n");
        }

        constexpr size_t errorLogBufferCapacity = 16000;

        omni::string jitLog;
        jitLog.resize(errorLogBufferCapacity, '\0');

        optionNames.push_back(CU_JIT_ERROR_LOG_BUFFER);
        optionValues.push_back((void*)&jitLog[0]);

        optionNames.push_back(CU_JIT_ERROR_LOG_BUFFER_SIZE_BYTES);
        optionValues.push_back((void*)errorLogBufferCapacity);

        CUDA_DRIVER_CALL(cuLinkCreate((unsigned int)optionNames.size(), &optionNames[0], &optionValues[0], &linkState));

        std::set<uint64_t> linkedEntryPoints;
        bool linkRequired = false;
        for (size_t i = 0; i < m_matEntryPointNames.size(); i++)
        {
            auto epHash = carb::hashString(m_matEntryPointNames[i].c_str());
            std::tie(std::ignore, linkRequired) = linkedEntryPoints.insert(epHash);
            if (!linkRequired)
            {
                continue;
            }

            if (PRINT_PTX)
            {
                printf("\n\n=-=-=-=\n\n%s:\n %s\n", m_matEntryPointNames[i].c_str(), m_matPtxStrings[i].c_str());
            }
            CUDA_DRIVER_CALL(cuLinkAddData(linkState, CU_JIT_INPUT_PTX, (void*)m_matPtxStrings[i].c_str(),
                                           m_matPtxStrings[i].size(), m_matEntryPointNames[i].c_str(), 0, nullptr,
                                           nullptr));
        }

        if (m_shaderTablePtxString.size() > 0)
        {
            if (PRINT_PTX)
            {
                printf("Shader Table PTX:\n%s\n", m_shaderTablePtxString.c_str());
            }
            CUDA_DRIVER_CALL(cuLinkAddData(linkState, CU_JIT_INPUT_PTX, (void*)m_shaderTablePtxString.c_str(),
                                           m_shaderTablePtxString.size(), "Shader Table PTX", 0, nullptr, nullptr));
        }

        if (m_hitShaderPtxString.size() > 0)
        {
            if (PRINT_PTX)
            {
                printf("Kernel PTX:\n%s\n", m_hitShaderPtxString.c_str());
            }
            CUDA_DRIVER_CALL(cuLinkAddData(linkState, CU_JIT_INPUT_PTX, (void*)m_hitShaderPtxString.c_str(),
                                           m_hitShaderPtxString.size(), "Kernel PTX", 0, nullptr, nullptr));
        }

        void* cubinOut = nullptr;
        size_t cubinSize = 0;
        CUDA_DRIVER_CALL(cuLinkComplete(linkState, &cubinOut, &cubinSize));

        CUDA_DRIVER_CALL(cuModuleLoadData(&m_module, cubinOut));

        if (WRITE_CUBIN)
        {
            std::ofstream debugFile("debug.cubin", std::ios::out | std::ios::binary);
            debugFile.write((const char*)cubinOut, cubinSize);
            debugFile.close();
        }

        CUDA_DRIVER_CALL(cuModuleGetFunction(&m_hitShaderEntryPoint, m_module, m_hitShaderEntryPointName.c_str()));

        CUDA_DRIVER_CALL(cuLinkDestroy(linkState));
    }


private:
    bool m_initialized{ false }; /**< specifies whether the material manager is initialized before use */

    std::vector<IMaterial*> m_interfaces; /**< vector of IMaterials registered with carb framework */

    std::vector<omni::string> m_matPtxStrings; /**< PTX strings of individual material cuda kernels */
    std::vector<omni::string> m_matEntryPointNames; /**< entry point function names corresponding to PTX kernel */
    std::vector<void*> m_matContexts; /**< Context data passed into Material cuda kernel corresponding to PTX kernel */
    std::vector<size_t> m_matContextSizes; /**< Size of context data */
    std::vector<uint32_t> m_matIds; /**< Index corresponding to specific material PTX kernels */


    omni::string m_hitShaderPtxString; /**< Main PTX hit program that performs sensor processing and calls material
                                         kernels */
    omni::string m_hitShaderEntryPointName; /**< Entry name for kernel of main hit shader PTX */

    omni::string m_shaderTablePtxString; /**< Shader table PTX string to be compiled from all stored materials */

    CUfunction m_hitShaderEntryPoint; /**< The entry point to launch the main hit shader kernel */

    size_t m_entryPointUserDataSize;
    void* m_dEntryPointUserData{ nullptr };

    CUmodule m_module{ nullptr }; /**< Module corresponding main hit shader and loaded into the current context */
};

} // namespace materials
} // namespace sensors
} // namespace omni
