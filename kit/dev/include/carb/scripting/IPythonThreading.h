// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Interface definition for python threading utilities provided by the Carbonite Framework.
#pragma once

#include "../Interface.h"
#include "../InterfaceUtils.h"

namespace carb
{
//! Namespace for scripting utilities and interfaces.
namespace scripting
{

//! State returned by \ref carb::scripting::IPythonThreading::checkLoaded().
enum class PythonThreadingState
{
    eNotLoaded, //!< Python does not appear to be loaded into the process.
    eLoaded, //!< Python is loaded into the process, but is not initialized.
    eInitialized, //!< Python is loaded into the process and is initialized.
};

/**
 * Allows limited control over Python threading aspects without causing Python to be loaded in the process or requiring
 * direct knowledge of Python.
 *
 * If Python is loaded into the project, this interface must be told by calling \ref IPythonThreading::checkLoaded().
 * Carbonite will automatically call this function when *carb.scripting-python.plugin* is started, or when a Python
 * binding is loaded into Python, and when the Framework is started. If Python is loaded into the process through
 * different means, this function must be called.
 *
 * @note This interface is built-in to the Carbonite Framework, so it should be available as long as the Framework
 * has been started.
 *
 * @see AcquirePythonGil ReleasePythonGil
 */
class IPythonThreading
{
public:
    CARB_PLUGIN_INTERFACE("carb::scripting::IPythonThreading", 1, 0);

    /**
     * Checks whether Python is loaded into the process and returns the state value.
     *
     * Typically this function does not need to be manually called as it is automatically called by the Framework when
     * Python bindings (or an owner, like *carb.scripting-python.plugin*) are loaded. It would need to be called if
     * Python was loaded through other means and use of \ref AcquirePythonGil and \ref ReleasePythonGil was desired.
     * @note This function can be expensive to call since modules loaded into the process are enumerated and Python
     *   calls can be made.
     * @returns A \ref PythonThreadingState value indicating the status of python.
     */
    virtual PythonThreadingState checkLoaded() = 0;

    /**
     * Checks whether the calling thread currently owns the Global Interpreter Lock (GIL).
     * @note If \ref checkLoaded() returns anything other than \ref PythonThreadingState::eInitialized, this function
     * will return \c false.
     * @returns \c true if the calling thread owns the GIL; \c false otherwise.
     */
    virtual bool ownsGil() const = 0;

private:
    // Use AcquirePythonGil instead
    friend class AcquirePythonGil;
    virtual void* acquireGil() = 0;
    virtual void releaseGil(void*) = 0;

    // Use ReleasePythonGil instead
    friend class ReleasePythonGil;
    virtual void* saveState() = 0;
    virtual void restoreState(void*) = 0;

public:
};

/**
 * A scoped object that attempts to acquire the Python Global Interpreter Lock (GIL) upon construction, and releases the
 * GIL upon destruction.
 *
 * If Python is not loaded into the process and initialized, this object has no effect. This is safe to call on a thread
 * that already holds the GIL.
 */
class [[nodiscard]] AcquirePythonGil
{
    IPythonThreading* m_threading;
    void* m_state;

public:
    //! Constructor: Attempts to acquire the Python Global Interpreter Lock (GIL).
    AcquirePythonGil() : m_threading(carb::getCachedInterface<IPythonThreading>()), m_state(nullptr)
    {
        if (m_threading)
        {
            m_state = m_threading->acquireGil();
        }
    }
    //! Destructor: Releases the Python Global Interpreter Lock (GIL) if previously acquired.
    ~AcquirePythonGil()
    {
        if (m_threading)
        {
            m_threading->releaseGil(m_state);
        }
    }
};

/**
 * A scoped object that attempts to completely release the Python Global Interpreter Lock (GIL) if held by the current
 * thread, allowing other threads to make progress in the Python interpreter. This is akin to the current Python thread
 * yielding as a co-routine would. Upon destruction of this object, the Python thread resumes and re-acquires the GIL.
 *
 * If Python is not loaded into the process and initialized, this object has no effect. This is also safe to call on a
 * thread that does not hold the GIL.
 */
class [[nodiscard]] ReleasePythonGil
{
    IPythonThreading* m_threading;
    void* m_state;

public:
    //! Constructor: Causes the current Python thread (if running in Python) to yield and release the GIL.
    ReleasePythonGil() : m_threading(carb::getCachedInterface<IPythonThreading>()), m_state(nullptr)
    {
        if (m_threading)
        {
            m_state = m_threading->saveState();
        }
    }
    //! Destructor: Resumes the current Python thread (if previously yielded) and re-acquires the GIL.
    ~ReleasePythonGil()
    {
        if (m_threading && m_state)
        {
            m_threading->restoreState(m_state);
        }
    }
};

} // namespace scripting
} // namespace carb
