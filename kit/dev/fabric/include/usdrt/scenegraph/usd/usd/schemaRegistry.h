// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once
//! @file
//!
//! @brief TODO
//!
//!

/// \file usd/schemaRegistry.h

#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/interface/IRtSchemaRegistry.h>

namespace usdrt
{


//! @class UsdSchemaRegistry
//!
//! Singleton registry that provides access to schema type information and
//! the prim definitions for registered Usd "IsA" and applied API schema
//! types. It also contains the data from the generated schemas that is used
//! by prim definitions to provide properties and fallbacks.
class UsdSchemaRegistry
{
public:
    //! Get the schema registry instance.
    static UsdSchemaRegistry GetInstance()
    {
        return UsdSchemaRegistry();
    }

    //! Get the schema type name for given @p schemaType.
    //! @returns Returns a TfToken for the type name of the USD schema.
    //! @note This differs from USD. In USD, the expected return type
    //! is TfType. Here, we use TfToken instead as USDRT does not implement
    //! its own TfType.
    template <class SchemaType>
    static TfToken GetSchemaTypeName()
    {
        return SchemaType::_GetStaticTfType();
    }

    //! Check if the given schema name inherits from UsdTyped.
    //! @param primType TfToken for the schema type name.
    //! @returns Returns true if the prim type @p primType inherits from @ref UsdTyped.
    //! @note This differs from USD. In USD, the expected type for @p primType
    //! is TfType. Here, we use TfToken instead as USDRT does not implement
    //! its own TfType.
    //! @note This differs from USD. This function cannot be static with the
    //! USDRT `isA` implementation.
    bool IsTyped(const TfToken& primType);

    //! Check if the given schema name is a concrete schema.
    //! @param primType TfToken for the schema type name.
    //! @returns Returns true if the prim type \p primType is instantiable
    //! in scene description.
    bool IsConcrete(const TfToken& primType) const;

    //! Check if the given schema type is an applied api schema type.
    //! @param apiSchemaType  TfToken for the schema type name.
    //! @returns Returns true if @p apiSchemaType is an applied API schema type.
    bool IsAppliedAPISchema(const TfToken& apiSchemaType) const;

    //! Check if the given schema type is a multiple-apply API schema type.
    //! @param apiSchemaType  TfToken for the schema type name.
    //! @returns Returns true if @p apiSchemaType is a multiple-apply API schema type.
    bool IsMultipleApplyAPISchema(const TfToken& apiSchemaType) const;

    //! Check if @p schemaType is a known schema within the registry.
    //! @param schemaType TfToken name for the schema to validate.
    //! @returns Returns true is @p schemaType is an unknown schema.
    //! @note this is an additional API function in place of querying the TfType system.
    bool IsUnknown(const TfToken& schemaType) const;

    //! Check if the given @p sourceTypeName type is or inherits from @p queryTypeName.
    //!
    //! Schema full name or alias can be given.
    //!
    //! Usage example to check if UsdGeomCube is an instance of UsdTyped.
    //! @code
    //! UsdSchemaRegistry::GetInstance().IsA("UsdGeomCube", "UsdTyped")()
    //! @endcode
    //!
    //! @param sourceTypeName The base schema type name for this query.
    //! @param queryTypeName The schema type name we are asking about.
    //! @returns Returns true if the sourceTypeName is an instance of the queryTypeName.
    //! @note This is an additional API function to take the place of having to query the TfType system.
    bool IsA(const TfToken& sourceTypeName, const TfToken& queryTypeName) const;

    //! Get the schema type name alias from the given name by
    //! querying the underlying Usd TfType system.
    //!
    //! This is used when applying or querying schema names as Fabric
    //! applies schemas with alias only. USDRT supports querying and
    //! applying using either name.
    //!
    //! If @p name is already the alias, this function will still query
    //! the TfType system and return the alias.
    //!
    //! @param name the full schema type name or alias.
    //! @returns the TfToken for the schema alias.
    //! @note This is an additional API not present in USD to take place of implementing a
    //! TfType system. Since this queries the underlying Usd TfType system, we assume
    //! that the USDRT schema is also a registered USD schema.
    TfToken GetAliasFromName(const TfToken& name) const;

    // Schema Types

    //! Check if the given @p SchemaType type is or inherits from @p QuerySchemaType.
    //!
    //! Schema full name or alias can be given.
    //!
    //! Usage example to check if UsdGeomCube is an instance of UsdTyped.
    //! @code
    //! UsdSchemaRegistry::GetInstance().IsA<UsdGeomCube, UsdTyped>()
    //! @endcode
    //!
    //! @tparam SchemaType Base schema type for this query.
    //! @tparam QuerySchemaType Schema type we are asking about.
    //! @returns Returns true if the @p SchemaType is an instance of the @p QuerySchemaType.
    //! @note This is an additional API function to take the place of having to query the TfType system.
    template <typename SchemaType, typename QuerySchemaType>
    bool IsA() const
    {
        return IsA(SchemaType::_GetStaticTfType(), QuerySchemaType::_GetStaticTfType());
    };

    //! Check if the given @p sourceTypeName is or inherits from @p SchemaType.
    //!
    //! Schema full name or alias can be given.
    //!
    //! Usage example to check if UsdGeomCube is an instance of UsdTyped.
    //! @code
    //! UsdSchemaRegistry::GetInstance().IsA<UsdTyped>("Cube"))
    //! @endcode
    //!
    //! @param sourceTypeName Base schema type for this query.
    //! @tparam SchemaType Schema type we are asking about.
    //! @returns Returns true if the @p sourceTypeName is an instance of the @p SchemaType.
    //! @note This is an additional API function to take the place of having to query the TfType system.
    template <typename SchemaType>
    bool IsA(TfToken sourceTypeName) const
    {
        return IsA(sourceTypeName, SchemaType::_GetStaticTfType());
    };

    //! Boolean operator
    //! @returns Return true if the schema registry is initialized.
    explicit operator bool() const;

private:
    omni::core::ObjectPtr<usdrt::IRtSchemaRegistry> m_schemaRegistry;

    UsdSchemaRegistry();

    bool _IsA(const TfToken& sourceTypeName, const TfToken& queryTypeName) const;
};

inline UsdSchemaRegistry::UsdSchemaRegistry()
{
    m_schemaRegistry = omni::core::createType<usdrt::IRtSchemaRegistry>()->initRegistry();
}

inline bool UsdSchemaRegistry::_IsA(const TfToken& sourceTypeName, const TfToken& queryTypeName) const
{
    return m_schemaRegistry->isA(omni::fabric::TokenC(sourceTypeName), omni::fabric::TokenC(queryTypeName));
}

inline bool UsdSchemaRegistry::IsA(const TfToken& sourceTypeName, const TfToken& queryTypeName) const
{
    if (!m_schemaRegistry)
    {
        return false;
    }
    return m_schemaRegistry->isA(omni::fabric::TokenC(sourceTypeName), omni::fabric::TokenC(queryTypeName));
}

inline bool UsdSchemaRegistry::IsTyped(const TfToken& primTypeName)
{
    return IsA(primTypeName, TfToken("UsdTyped"));
}

inline bool UsdSchemaRegistry::IsConcrete(const TfToken& primType) const
{
    return m_schemaRegistry->isConcrete(omni::fabric::TokenC(primType));
}

inline bool UsdSchemaRegistry::IsAppliedAPISchema(const TfToken& apiSchemaType) const
{
    return m_schemaRegistry->isAppliedAPISchema(omni::fabric::TokenC(apiSchemaType));
}

inline bool UsdSchemaRegistry::IsMultipleApplyAPISchema(const TfToken& apiSchemaType) const
{
    return m_schemaRegistry->isMultipleApplyAPISchema(omni::fabric::TokenC(apiSchemaType));
}

inline bool UsdSchemaRegistry::IsUnknown(const TfToken& schemaType) const
{
    return !IsA(schemaType, TfToken("UsdSchemaBase"));
}

inline TfToken UsdSchemaRegistry::GetAliasFromName(const TfToken& name) const
{
    return TfToken(m_schemaRegistry->getAliasFromName(omni::fabric::TokenC(name)));
}

inline UsdSchemaRegistry::operator bool() const
{
    return bool(m_schemaRegistry);
}
}
