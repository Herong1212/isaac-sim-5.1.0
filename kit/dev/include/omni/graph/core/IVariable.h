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
#include <omni/core/TypeId.h>
#include <omni/graph/core/Type.h>

namespace omni
{
namespace graph
{
namespace core
{

/**
 * Scope in which the variable has been made available
 */
enum class eVariableScope
{
    /** Variable is accessible only to its graph */
    ePrivate   = 0,
    /** Variable can be read by other graphs */
    eReadOnly  = 1,
    /** Variable can be read/written by other graphs */
    ePublic    = 2,
};

//! Declare the IVariable interface definition
OMNI_DECLARE_INTERFACE(IVariable);

//! Data type to use for a reference to an IVariable interface definition
using IVariablePtr = omni::core::ObjectPtr<IVariable>;

/**
 * Object that contains a value that is local to a graph, available from anywhere in the graph
 */
class IVariable_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.graph.core.IVariable")>
{
protected:

   /**
    * Returns the name of the variable object. The name is derived by
    * removing any variable specific prefixes from the underlying attribute.
    *
    * @return The name of the variable.
    */
    virtual const char* getName_abi() noexcept = 0;

   /**
    *  Returns the full path to the variables underlying attribute
    *
    *  @return The full usd path of the variable
    */
    virtual const char* getSourcePath_abi() noexcept = 0;

   /**
    * Returns the type of the variable
    *
    * @return The type of the variable
    */
    virtual OMNI_ATTR("no_py") Type getType_abi() noexcept = 0;

    /**
     * Returns the category of the variable
     *
     * @return The category of the variable, or an empty string if it is not set.
     */
    virtual const char* getCategory_abi() noexcept = 0;

    /**
     * Sets the category of the variable
     *
     * @param[in] category A string representing the variable category
     */
    virtual void setCategory_abi(OMNI_ATTR("c_str, in, not_null") const char* category) noexcept = 0;

    /**
     * Gets the display name of the variable. By default the display name is the same
     * as the variable name.
     *
     * @return The display name of the variable, or an empty string if it is not set.
     */
    virtual const char* getDisplayName_abi() noexcept = 0;

    /**
     * Set the display name of the variable.
     *
     * @param[in] displayName A string to set the display name to
     */
    virtual void setDisplayName_abi(OMNI_ATTR("c_str, in, not_null") const char* displayName) noexcept = 0;

    /**
     * Get the tooltip used for the variable.
     *
     * @return The tooltip of the variable, or an emtpy string if none is set.
     */
    virtual const char* getTooltip_abi() noexcept = 0;

    /**
     * Set the tooltip used for the variable
     *
     * @param[in] toolTip A description used as a tooltip.
     */
    virtual void setTooltip_abi(OMNI_ATTR("c_str, in, not_null") const char* toolTip) noexcept = 0;

    /**
     * Get the scope of the variable. The scope determines which graphs can read and write the value.
     *
     * @return The scope of the variable.
     */
    virtual eVariableScope getScope_abi() noexcept = 0;

    /**
     * Sets the scope of the variable.
     *
     * @param[in] scope The scope to set on the variable.
     */
    virtual void setScope_abi(eVariableScope scope) noexcept = 0;

    /**
     * Returns whether this variable is valid
     *
     * @return True if the variable is valid, false otherwise
     */
    virtual bool isValid_abi() noexcept = 0;
};

} // namespace core
} // namespace graph
} // namespace omni

#include "IVariable.gen.h"

//! @cond Doxygen_Suppress
//!
//! API part of the variable interface
//! @copydoc omni::graph::core::IVariable_abi
OMNI_DEFINE_INTERFACE_API(omni::graph::core::IVariable)
//! @endcond
{
public:
    /**
     * Changes the type of the variable.
     *
     * @param[in] type The type to change the variable to
     * @returns True if the type was successfully changed, False otherwise. Setting the type
     *          can fail if the backing USD change is on a layer with a weaker opinion.
     */
    inline bool setType(omni::graph::core::Type type) noexcept;

    /**
     * Returns whether the variable has an USD representation on the stage.
     *
     * @return True if the variable is backed by USD, false otherwise
     */
    inline bool isBackedByUsd() noexcept;
};
