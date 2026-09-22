// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/core/IObject.h>

namespace omni {
namespace graph {
namespace core {

//! Declare the INodeCategories interface definition
OMNI_DECLARE_INTERFACE(INodeCategories);


/** Interface to the list of categories that a node type can belong to */
class INodeCategories_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.graph.core.INodeCategories")>
{
protected:
    /**
     * Get the number of categories available
     *
     * @returns Count of fixed category types
     */
    virtual size_t getCategoryCount_abi() noexcept = 0;

    /**
     * Get the list of available categories and their descriptions.
     *
     * The caller is responsible for allocating and destroying buffers large enough to hold "bufferSize" results.
     * If bufferSize > getCategoryCount() then the entries at the ends of the buffers will be filled with nullptr.
     *
     * @param[in] categoryNameBuffer List of category names
     * @param[in] categoryDescriptionBuffer List of category descriptions corresponding to the names
     * @param[in] bufferSize Number of entries to fill in the buffers
     *
     * @return true if the category buffer was successfully filled and the bufferSize matched the category count
     */
    virtual OMNI_ATTR("no_py") bool getCategories_abi(
        OMNI_ATTR("*c_str, out, not_null, count=bufferSize") char const** categoryNameBuffer,
        OMNI_ATTR("*c_str, out, not_null, count=bufferSize") char const** categoryDescriptionBuffer,
        size_t bufferSize
    ) noexcept = 0;

    /**
     * Define a new category
     *
     * @param[in] categoryName Name of the new category
     * @param[in] categoryDescription Description of the category
     *
     * @return false if there was already a category with the given name
     */
    virtual bool defineCategory_abi(
        OMNI_ATTR("c_str, in, not_null") char const* categoryName,
        OMNI_ATTR("c_str, in, not_null") char const* categoryDescription
    ) noexcept = 0;

    /**
     * Remove an existing category, mainly to manage the ones created by a node type for itself
     *
     * @param[in] categoryName Name of the category to remove
     *
     * @return false if there was no category with the given name
     */
    virtual bool removeCategory_abi(
        OMNI_ATTR("c_str, in, not_null") char const* categoryName
    ) noexcept = 0;
};

} // namespace core
} // namespace graph
} // namespace omni

#include "INodeCategories.gen.h"  // generated file
