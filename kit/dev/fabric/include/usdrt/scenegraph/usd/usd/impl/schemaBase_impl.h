// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "usd_decl.h"

namespace usdrt
{

inline UsdSchemaBase::UsdSchemaBase(const UsdPrim& prim) : m_prim(prim), m_primPath(prim.GetPath())
{
    /* NOTHING */
}

inline UsdSchemaBase::UsdSchemaBase(const UsdSchemaBase& schema)
    : m_prim(schema.m_prim), m_primPath(schema.m_primPath), _tfTypeToken(schema._tfTypeToken)
{
    /* NOTHING YET */
}

/*virtual*/
inline UsdSchemaBase::~UsdSchemaBase()
{
    // This only exists to avoid memory leaks in derived classes which may
    // define new members.
}

inline UsdPrim UsdSchemaBase::GetPrim() const
{
    return m_prim;
}

inline SdfPath UsdSchemaBase::GetPath() const
{
    return m_primPath;
}

inline const TfToken UsdSchemaBase::_GetTfTypeToken() const
{
    const static TfToken token("UsdSchemaBase");
    return token;
}

inline bool UsdSchemaBase::_IsCompatible() const
{
    // schema base is compatible with any valid prim
    return true;
}

}
