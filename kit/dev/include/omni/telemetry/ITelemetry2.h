// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
/// @file
/// @brief Provides a helper interface to allow access to some common telemetry operations.
#pragma once

#include "ITelemetry.h"


namespace omni
{
/** Namespace for telemetry related interfaces and functionality. */
namespace telemetry
{

/** Forward declaration of the ITelemetry2 interface implementation class. */
class ITelemetry2;

/** Names for the current Run environment used for telemetry.
 *
 *  Identifiers used to outline what kind of environment this process is currently running
 *  in.  This may be individual (OVI), cloud (OVC), or enterprise (OVE).
 */
enum class OMNI_ATTR("prefix=e") RunEnvironment
{
    /** The run environment has not been determined yet.
     *
     *  This indicates that the required startup events have not occurred yet or the run
     *  environment could not be determined yet.  An attempt to retrieve the run environment
     *  should be made again at a later time.
     */
    eUndetermined,

    /** Omniverse individual (OVI) desktop session.
     *
     *  This is typically installed and run through the Omniverse desktop launcher app.
     *  Telemetry is enabled through this environment using the public Kratos authenticated
     *  endpoint.
     */
    eIndividual,

    /** Omniverse Cloud (OVC) session.
     *
     *  This type of session is launched through the OVC services portal and the visual output
     *  streamed over the network.  Telemetry is enabled through this environment using a Kratos
     *  authenticated endpoint specific to cloud deployments.
     */
    eCloud,

    /** Omniverse Enterprise (OVE) session.
     *
     *  This type of session is typically installed and run through the Omniverse enterprise
     *  launcher app.  Telemetry is enabled through this environment using the Kratos open
     *  endpoint for enterprise.
     */
    eEnterprise,
};

/** Retrieves the name of a run environment enum value.
 *
 *  @param[in] env  The run environment value to retrieve the name for.
 *  @returns The name of the requested enum if valid.  If an invalid enum value is passed in,
 *           a placeholder string will be returned instead.
 */
inline const char* getRunEnvironmentName(RunEnvironment env)
{
#define GETNAME(name, prefix)   case name: return &(#name)[sizeof(#prefix) - 1]
    switch (env)
    {
        GETNAME(RunEnvironment::eUndetermined, RunEnvironment::e);
        GETNAME(RunEnvironment::eIndividual, RunEnvironment::e);
        GETNAME(RunEnvironment::eCloud, RunEnvironment::e);
        GETNAME(RunEnvironment::eEnterprise, RunEnvironment::e);
        default:
            return "<unknown_run_environment>";
    }
#undef GETNAME
}

/** Interface to handle performing telemetry related tasks.
 *
 *  This provides an abstraction over the lower level telemetry and structured logging systems
 *  and allows control over some common features of it.
 */
class ITelemetry2_abi : public omni::core::Inherits<omni::telemetry::ITelemetry, OMNI_TYPE_ID("omni.kit.telemetry.ITelemetry2")>
{
protected:
    /** Tests whether this session is running as a cloud session.
     *
     *  @returns `true` if this current session is detected as running on a cloud architecture.
     *           Returns `false` if this current session is running outside of a cloud system.
     *
     *  @remarks A cloud session is one that runs on a cloud service provider's system and streams
     *           to a user's machine.  The session runs on behalf of the given user using that
     *           user's privacy information.  When running on a cloud system, the user does not
     *           have direct access to the hardware.  Telemetry handling also differs since the
     *           telemetry transmitter process will not send data anywhere, but simply write to
     *           a log file that can be scraped when the session ends (or in parts during the
     *           session).
     */
    virtual bool isCloudSession_abi() noexcept = 0;

    /** Retrieves the cloud session ID if running as a cloud session.
     *
     *  @returns A string representing the cloud session ID if running as a cloud session.
     *           Returns `nullptr` otherwise.  This will always return `nullptr` if the current
     *           run environment is anything other than @ref RunEnvironment::eCloud.
     *
     *  @remarks The cloud session ID will be a UUID style string that can be used to uniquely
     *           identify one session from another.  When not running as a cloud session, no
     *           string will be returned.  The caller must be able to properly and gracefully
     *           handle this potential failure case.
     */
    virtual const char* getCloudSessionId_abi() noexcept = 0;

    /** Retrieves the current run environment.
     *
     *  @returns The current run environment if it has been detected yet.  If the run environment
     *           could not be determined yet, @ref RunEnvironment::eUndetermined will be returned
     *           instead.  Once a value other than @ref RunEnvironment::eUndetermined is returned,
     *           the run environment will not change for the remainder of the session and can be
     *           safely cached for quicker lookups later.
     */
    virtual RunEnvironment getRunEnvironment_abi() noexcept = 0;

    /** Retrieves the customer ID for enterprise sessions.
     *
     *  @returns The loaded customer ID value if found.  This will be the same value that is
     *           listed as 'org-name' for a given customer on the NVIDIA Licensing Portal web
     *           page.  Returns `nullptr` if the customer ID value was either not found or this
     *           is not an enterprise session.
     */
    virtual const char* getCustomerId_abi() noexcept = 0;
};

} // namespace telemetry
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "ITelemetry2.gen.h"

/** @copydoc omni::telemetry::ITelemetry2_abi */
class omni::telemetry::ITelemetry2
    : public omni::core::Generated<omni::telemetry::ITelemetry2_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "ITelemetry2.gen.h"
