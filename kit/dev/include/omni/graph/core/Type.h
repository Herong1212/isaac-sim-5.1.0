// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/IdTypes.h>
#include <omni/fabric/Type.h>

#include <sstream>
#include <string>
// Alias fabric types into omnigraph for backwards compatibility.
// Use omni/fabric/Type.h outside of the omnigraph project
namespace omni
{
namespace graph
{
namespace core
{
//! OmniGraph Type is just an alias for the Fabric Type
using Type = omni::fabric::Type;
//! OmniGraph BaseDataType is just an alias for the Fabric BaseDataType
using BaseDataType = omni::fabric::BaseDataType;
//! OmniGraph AttributeRole is just an alias for the Fabric AttributeRole
using AttributeRole = omni::fabric::AttributeRole;

using BucketId = omni::fabric::BucketId;

// ======================================================================
/**
 * @brief Get a string that describes the type role in OGN format
 *
 * The role name is slightly different here than @ref omni::fabric::getAttributeRoleName for historical reasons
 *
 * @param r Role whose name is to be returned
 * @return std::string OGN-style name of the given role
 */
inline std::string getOgnRoleName(AttributeRole r)
{
    static const std::string ognRoleNames[] = { "none",
                                                "vector",
                                                "normal",
                                                "point",
                                                "color",
                                                "texcoord",
                                                "quat",
                                                "transform",
                                                "frame",
                                                "timecode",
                                                "text",
                                                "appliedSchema",
                                                "primTypeName",
                                                "execution",
                                                "matrix",
                                                "objectId",
                                                "bundle",
                                                "path",
                                                "instancedAttribute",
                                                "ancestorPrimTypeName",
                                                "target",
                                                "unknown" };

    if (r <= AttributeRole::eUnknown)
    {
        return ognRoleNames[uint8_t(r)];
    }
    return std::string();
}

// ======================================================================
/**
 * @brief Get a string that describes the type in OGN format
 *
 * OGN formats the type names slightly differently than @ref omni::fabric::getTypeName
 *   - the tuples are indexed "float[3]" instead of "float3"
 *   - the roles replace the actual name "colord[3]" instead of "double3 (color)"
 *
 * @param t Type definition whose name is to be returned
 * @return std::string OGN-style name of the type
 */
inline std::string getOgnTypeName(Type t)
{
    std::ostringstream typeName;
    if (t.role == AttributeRole::eText)
    {
        typeName << "string";
        return typeName.str();
    }
    if (t.role == AttributeRole::ePath)
    {
        typeName << "path";
        return typeName.str();
    }
    if (t.role != AttributeRole::eNone)
    {
        typeName << getOgnRoleName(t.role);
        // For roles with explicit types, add that to the role name
        if ((t.role != AttributeRole::eTimeCode) && (t.role != AttributeRole::eTransform) &&
            (t.role != AttributeRole::eFrame) && (t.role != AttributeRole::eObjectId) &&
            (t.role != AttributeRole::eBundle) && (t.role != AttributeRole::eExecution) &&
            (t.role != AttributeRole::eTarget))
        {
            switch (t.baseType)
            {
            case BaseDataType::eHalf:
                typeName << "h";
                break;
            case BaseDataType::eFloat:
                typeName << "f";
                break;
            case BaseDataType::eDouble:
                typeName << "d";
                break;
            default:
                typeName << t.baseType;
                break;
            }
        }
    }
    else
    {
        typeName << t.baseType;
    }

    if (t.componentCount > 1)
    {
        typeName << "[" << uint32_t(t.dimension()) << "]";
    }

    if (t.arrayDepth == 1)
        typeName << "[]";
    else if (t.arrayDepth == 2)
        typeName << "[][]";

    return typeName.str();
}

} // namespace core
} // namespace graph
} // namespace omni
