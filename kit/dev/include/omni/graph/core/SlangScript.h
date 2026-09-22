// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Framework.h>
#include <carb/graphics/Graphics.h>

#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/base/tf/token.h>
#include <pxr/base/tf/type.h>
#include <pxr/usd/sdf/path.h>
#include <omni/graph/core/PostUsdInclude.h>

#include <slang/include/slang.h>

#include <slang/include/slang-com-ptr.h>

#define SLANG_PRELUDE_NAMESPACE CPPPrelude
#include <string>
#include <vector>

#include <slang/include/slang-cpp-types.h>

namespace omni
{
namespace graph
{
namespace core
{

struct SlangScript
{
    // A ResizeSpec allows the user to set (using USD) the size of an output
    // array to the size of an input array
    struct ResizeSpec
    {
        std::string outputArray;
        std::string inputArray;
    };

    std::vector<ResizeSpec> resizeSpec;

    // Whether to run on CPU or GPU
    gpucompute::Target target;

    // Compiler output
    gpucompute::Shader* shader = nullptr;
    gpucompute::ComputeCompiler* compiler = nullptr;

    SlangScript(const char* codeString,
                gpucompute::Target target,
                const std::vector<ResizeSpec>& resizeSpec,
                carb::graphics::Device* device);

    ~SlangScript()
    {
        if (shader)
            compiler->destroyShader(*shader);
    }
};
}
}
}
