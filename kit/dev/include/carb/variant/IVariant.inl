// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "VariantUtils.h"
#include "Translator.inl"
#include "VariantUtils.inl"
#include "VariantTypes.inl"

namespace carb
{
namespace variant
{

inline VariantArrayPtr IVariant::createArray(const Variant* p, size_t count)
{
    return carb::stealObject(internalCreateArray(p, count));
}

inline VariantMapPtr IVariant::createMap()
{
    return carb::stealObject(internalCreateMap());
}

} // namespace variant
} // namespace carb
