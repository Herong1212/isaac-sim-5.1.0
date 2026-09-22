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


#include <carb/Interface.h>

#include <omni/String.h>
#include <omni/sensors/cuda/CudaHelperMath.h>

#include <GenericModelOutputTypes.h>

namespace omni
{
namespace sensors
{
namespace ml
{

struct AtmosOperatorCfg
{
    omni::string probModelPath{};
    omni::string pointModelPath{};
    uint64_t maxElements{ 0UL };
    uint32_t seed{ 0x1234 };
};

struct AtmosParameter
{
    // Just optical thickness for now
    long opticalThickness{ 11l };
};


class IAtmosOperator : public carb::IObject
{
public:
    virtual ~IAtmosOperator(){};
    virtual void init(const AtmosOperatorCfg& cfg, const cudaStream_t stream = 0) = 0;
    virtual void setAtmosParameter(const AtmosParameter& param, const cudaStream_t stream = 0) = 0;
    // In place forward pass -> reinterpreted cast is enough here
    virtual void forward(omni::sensors::GenericModelOutput* output, const cudaStream_t stream = 0) = 0;
};

using IAtmosOperatorPtr = carb::ObjectPtr<IAtmosOperator>;


class IAtmosOperatorFactory
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::ml::IAtmosOperatorFactory", 0, 1)

    /**
     * @brief
     * @return a model object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the model
     */
    virtual IAtmosOperatorPtr createInstance() = 0;
};

} // namespace ml
} // namespace sensors
} // namespace omni
