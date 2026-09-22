// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once
#include <omni/core/Omni.h>
#include <omni/core/IObject.h>
namespace omni { using namespace omni::core; }

namespace omni {
namespace inspect {

OMNI_DECLARE_INTERFACE(IInspector);

//! Base class for object inspection requests.
class IInspector_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.inspect.IInspector")>
{
protected:
    /** Set the help information for the current invocation of the inspector. For when behavior == eHelp
     * @param[in] helpString The help information, describing the configuration of the inspector
     */
    virtual void setHelp_abi(OMNI_ATTR("c_str, not_null")const char* helpString) noexcept = 0;

    /** Returns the help information currently available on the inspector. Note that this could change
     * from one invocation to the next so it's important to read it immediately after requesting it.
     * @returns String containing the help information describing the current configuration of the inspector
     */
    virtual OMNI_ATTR("c_str")const char* helpInformation_abi() noexcept = 0;

    /** Returns the common flag used to tell the inspection process to put the help information into the
     * inspector using the setHelp_abi function. Using this approach avoids having every inspector/object
     * combination add an extra ABI function just for retrieving the help information, as well as providing a
     * consistent method for requesting it.
     * @returns String containing the name of the common flag used for help information
     */
    virtual OMNI_ATTR("c_str, not_null")const char* helpFlag_abi() noexcept = 0;

    /** Enable or disable an inspection flag. It's up to the individual inspection operations or the derived
     * inspector interfaces to interpret the flag.
     * @param[in] flagName Name of the flag to set
     * @param[in] flagState New state for the flag
     */
    virtual void setFlag_abi(OMNI_ATTR("c_str, not_null")const char* flagName, bool flagState) noexcept = 0;

    /** Checks whether a particular flag is currently set or not.
     * @param[in] flagName Name of the flag to check
     * @returns True if the named flag is set, false if not
     */
    virtual bool isFlagSet_abi(OMNI_ATTR("c_str, not_null")const char* flagName) noexcept = 0;
};

} // namespace inspect
} // namespace omni

#include "IInspector.gen.h"
