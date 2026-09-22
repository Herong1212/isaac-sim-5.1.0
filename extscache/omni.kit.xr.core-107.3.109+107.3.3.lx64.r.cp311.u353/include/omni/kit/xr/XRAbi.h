// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include <omni/container/IReadOnlyArray.h>
#include <omni/container/ReadOnlyArray.h>
#include <omni/kit/xr/IXRError.h>
#include <omni/str/IReadOnlyCString.h>


namespace omni
{
namespace kit
{
namespace xr
{


/////////////////////////////////////////////////////////////
// XRError strings can be found inside a dedicated API in
// the core plugin. This function wraps accessing that plugin
// and simplifies accessing error information.
/////////////////////////////////////////////////////////////

inline const char* getXRErrorString(XRError error)
{
    return carb::getCachedInterface<IXRError>()->getXRErrorString(error);
}

/////////////////////////////////////////////////////////////
// XR functionality throws an XRException on returning an
// error from a function. Most internal functions will throw
// an exception for error handling. Most ABI/API functions will
// return an error code. The class enables the user to retrieve
// the original error code.
/////////////////////////////////////////////////////////////

class XRException : public std::runtime_error
{
public:
    /**
     * @brief Get the string describing the error for which the code
     * is given.
     *
     * @param err    error code
     *
     * @return string with error description
     */
    std::string convertXRErrorToString(XRError err)
    {
        return carb::getCachedInterface<IXRError>()->getXRErrorString(err);
    }

    /**
     * @brief Construct a new XRException object
     *
     * @param err       XRError code
     * @param function  [optional] function that threw the exception
     * @param file      [optional] file in which exception was thrown
     * @param line      [optional] line number at which exception was thrown
     */
    XRException(XRError err, const char* function = nullptr, const char* file = nullptr, uint32_t line = 0)
        : std::runtime_error(convertXRErrorToString(err)), m_err(err), m_function(function), m_file(file), m_line(line)
    {
    }

    /**
     * @brief Construct a new XRException object with a custom error field.
     * NOTE: Not all errors can be described by an XRError code. For example errors from an external API
     * such as OpenXR. In that case we throw a eCustomError and attach an error description to the exception.
     *
     * @param err       XRError string
     * @param function  [optional] function that threw the exception
     * @param file      [optional] file in which exception was thrown
     * @param line      [optional] line number at which exception was thrown
     */
    XRException(const std::string& error, const char* function = nullptr, const char* file = nullptr, uint32_t line = 0)
        : std::runtime_error(error), m_err(XRError::eCustomError), m_function(function), m_file(file), m_line(line)
    {
        m_customError = std::string("XRError: ") + error;
    }


    /**
     * @brief Construct a new XRException object with custom error message
     *
     * @param err       XRError code
     * @param errStr    XRError string
     * @param function  [optional] function that threw the exception
     * @param file      [optional] file in which exception was thrown
     * @param line      [optional] line number at which exception was thrown
     */
    XRException(XRError err,
                const std::string& errStr,
                const char* function = nullptr,
                const char* file = nullptr,
                uint32_t line = 0)
        : std::runtime_error(errStr), m_err(err), m_function(function), m_file(file), m_line(line)
    {
        m_customError = errStr;
    }

    /**
     * @brief Get the XRError code of the exception.
     *
     * @return XRError code
     */
    XRError getXRError() const
    {
        return m_err;
    }

    /**
     * @brief Get the XRError as string that can be used to display to the user.
     * NOTE: In case of a custom error please capture the error into a string object as
     * the pointer provided will have a lifetime of the exception object.
     *
     * @return pointer to string with error
     */
    const char* getXRErrorString() const
    {
        if (!m_customError.empty())
        {
            return m_customError.c_str();
        }

        return carb::getCachedInterface<IXRError>()->getXRErrorString(m_err);
    }

    /**
     * @brief Convenience function so exception can be converted to an
     * XRError code.
     *
     * @return XRError code
     */
    operator XRError() const
    {
        return m_err;
    }

    /**
     * @brief Get the function name in which the exception was thrown.
     *
     * @return function name
     */
    const char* getFunction() const
    {
        return m_function;
    }

    /**
     * @brief Get the file name in which the exception was thrown.
     *
     * @return file name
     */
    const char* getFile() const
    {
        return m_file;
    }

    /**
     * @brief Get the line number in which the exception was thrown.
     *
     * @return line number
     */
    uint32_t getLine() const
    {
        return m_line;
    }

private:
    XRError m_err;
    const char* m_function;
    const char* m_file;
    uint32_t m_line;

    std::string m_customError;
};

/////////////////////////////////////////////////////////////
// Macros for handling throwing XRErrors
/////////////////////////////////////////////////////////////

#define XR_THROW_IF_ERROR(_err_)                                                                                       \
    {                                                                                                                  \
        if (_err_ != omni::kit::xr::XRResult::eSuccess)                                                                \
        {                                                                                                              \
            throw omni::kit::xr::XRException(_err_, __FUNCTION__, __FILE__, __LINE__);                                 \
        }                                                                                                              \
    }

#define THROW_XR_ERROR_AND_CARB_LOG_IT(_err_, _errorMessage_, ...)                                                     \
    {                                                                                                                  \
        CARB_LOG_ERROR(_errorMessage_, ##__VA_ARGS__);                                                                 \
        throw omni::kit::xr::XRException(_err_, _errorMessage_, __FUNCTION__, __FILE__, __LINE__);                     \
    }

#define THROW_XR_ERROR(_err_)                                                                                          \
    {                                                                                                                  \
        throw omni::kit::xr::XRException(_err_, __FUNCTION__, __FILE__, __LINE__);                                     \
    }

#define THROW_CUSTOM_XR_ERROR(_err_, _errStr_)                                                                         \
    {                                                                                                                  \
        throw omni::kit::xr::XRException(_err_, _errStr_, __FUNCTION__, __FILE__, __LINE__);                           \
    }

/////////////////////////////////////////////////////////////
// Macros which return given result if it is not XRResult::eSuccess
/////////////////////////////////////////////////////////////


#define RETURN_XRRESULT_IF_NOT_SUCCESS(_xrResult_, _errorMessage_)                                                     \
    if ((_xrResult_) != XRResult::eSuccess)                                                                            \
    {                                                                                                                  \
        CARB_LOG_ERROR(_errorMessage_);                                                                                \
        return (_xrResult_);                                                                                           \
    }

#define RETURN_OTHER_XRRESULT_IF_NOT_SUCCESS(_xrResultToCheck_, _errorMessage_, __xrResultToReturn__)                  \
    if ((_xrResultToCheck_) != XRResult::eSuccess)                                                                     \
    {                                                                                                                  \
        CARB_LOG_ERROR(_errorMessage_);                                                                                \
        return (__xrResultToReturn__);                                                                                 \
    }

#define THROW_XRERROR_IF_NOT_SUCCESS(_xrResultToCheck_, _errorMessage_, __xrResultToReturn__)                          \
    if ((_xrResultToCheck_) != XRResult::eSuccess)                                                                     \
    {                                                                                                                  \
        CARB_LOG_ERROR(_errorMessage_);                                                                                \
        THROW_XR_ERROR(__xrResultToReturn__);                                                                          \
    }

/////////////////////////////////////////////////////////////
// Macros for at the bottom of a try statement
// NOTE: All the ABI functions have this at the bottom
// to catch any errors (XRExceptions and other exceptions)
// and translate those into an XRError return code.
/////////////////////////////////////////////////////////////

#define XR_NO_OP

#define CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR_WITH_HOOK_ON_ERROR(_hook)                                             \
    catch (omni::kit::xr::XRException & ex)                                                                            \
    {                                                                                                                  \
        if (ex.getXRError() != XRResult::eSkipFrame)                                                                   \
        {                                                                                                              \
            CARB_LOG_ERROR_ONCE(                                                                                       \
                "An XRError occurred (%s, %s, %d): %s", ex.getFunction(), ex.getFile(), ex.getLine(), ex.what());      \
        }                                                                                                              \
        _hook;                                                                                                         \
        return ex.getXRError();                                                                                        \
    }                                                                                                                  \
    catch (std::exception & ex)                                                                                        \
    {                                                                                                                  \
        CARB_LOG_ERROR_ONCE(                                                                                           \
            "Some c++ exception occurred: %s (caught at %s line %d)", ex.what(), __FUNCTION__, __LINE__);              \
        _hook;                                                                                                         \
        return omni::kit::xr::XRError::eInternalError;                                                                 \
    }                                                                                                                  \
    catch (...)                                                                                                        \
    {                                                                                                                  \
        CARB_LOG_ERROR_ONCE("An unknown error occurred");                                                              \
        _hook;                                                                                                         \
        return omni::kit::xr::XRError::eInternalError;                                                                 \
    }

#define CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR() CATCH_AND_RETURN_XREXCEPTIONS_AS_XRERROR_WITH_HOOK_ON_ERROR(XR_NO_OP)

#define CATCH_AND_RETURN_OTHER_EXCEPTIONS_AS_XRERROR_WITH_HOOK_ON_ERROR(_hook)                                         \
    catch (std::exception & ex)                                                                                        \
    {                                                                                                                  \
        CARB_LOG_ERROR_ONCE(                                                                                           \
            "Some c++ exception occurred: %s (caught at %s line %d)", ex.what(), __FUNCTION__, __LINE__);              \
        _hook;                                                                                                         \
        return omni::kit::xr::XRError::eInternalError;                                                                 \
    }                                                                                                                  \
    catch (...)                                                                                                        \
    {                                                                                                                  \
        CARB_LOG_ERROR_ONCE("An unknown error occurred");                                                              \
        _hook;                                                                                                         \
        return omni::kit::xr::XRError::eInternalError;                                                                 \
    }
#define CATCH_AND_RETURN_OTHER_EXCEPTIONS_AS_XRERROR()                                                                 \
    CATCH_AND_RETURN_OTHER_EXCEPTIONS_AS_XRERROR_WITH_HOOK_ON_ERROR(XR_NO_OP)

/////////////////////////////////////////////////////////////
// Version of the macro where no XRError is returned
// NOTE: Most functions on the ABI layer now return error code
// which should be preferred, so the user of the function
// knows whether an exception was intercepted.
/////////////////////////////////////////////////////////////

#define CATCH_XREXCEPTIONS_WITH_HOOK_ON_ERROR(_hook)                                                                   \
    catch (omni::kit::xr::XRException & ex)                                                                            \
    {                                                                                                                  \
        if (ex.getXRError() != XRResult::eSkipFrame)                                                                   \
        {                                                                                                              \
            CARB_LOG_ERROR_ONCE(                                                                                       \
                "An XRError occurred (%s, %s, %d): %s", ex.getFunction(), ex.getFile(), ex.getLine(), ex.what());      \
        }                                                                                                              \
        _hook;                                                                                                         \
    }                                                                                                                  \
    catch (std::exception & ex)                                                                                        \
    {                                                                                                                  \
        CARB_LOG_ERROR_ONCE(                                                                                           \
            "Some c++ exception occurred: %s (caught at %s line %d)", ex.what(), __FUNCTION__, __LINE__);              \
        _hook;                                                                                                         \
    }                                                                                                                  \
    catch (...)                                                                                                        \
    {                                                                                                                  \
        CARB_LOG_ERROR_ONCE("An unknown error occurred");                                                              \
        _hook;                                                                                                         \
    }
#define CATCH_XREXCEPTIONS() CATCH_XREXCEPTIONS_WITH_HOOK_ON_ERROR(XR_NO_OP)

/////////////////////////////////////////////////////////////
// Extensions to the carb ONI system
// In case of containers we add special rules to build API
// functions that return pieces as vectors or sets
// These macros help setup ONI return containers
/////////////////////////////////////////////////////////////


// Output reference string (output type is omni::str::IReadOnlyCString)
#define XR_ONI_ABI_OUT_STD_STRING()                                                                                                             \
    OMNI_ATTR(                                                                                                                                  \
        "output_convert_prefix=std::string(omni::core::steal(,  output_convert_type=std::string,  output_convert_suffix=)->getBuffer()),  out") \
    omni::str::IReadOnlyCString*&

// Return of string (output type is omni::str::IReadOnlyCString)
#define XR_ONI_ABI_RET_STD_STRING()                                                                                                       \
    OMNI_ATTR(                                                                                                                            \
        "output_convert_prefix=std::string(omni::core::steal(,  output_convert_type=std::string,  output_convert_suffix=)->getBuffer())") \
    omni::str::IReadOnlyCString*

// return of vector of given type (output type is omni::container::IReadOnlyArray)
#define XR_ONI_ABI_RET_STD_VECTOR(_array_type)                                                                         \
    OMNI_ATTR("output_convert_prefix=omni::container::convertReadOnlyTypedArray<" #_array_type                         \
              ">(,  output_convert_type=std::vector<" #_array_type ">,   output_convert_suffix=)")                     \
    omni::container::IReadOnlyArray*

// Output reference vector of given type (output type is omni::container::IReadOnlyArray)
#define XR_ONI_ABI_OUT_STD_VECTOR(_array_type)                                                                         \
    OMNI_ATTR("output_convert_prefix=omni::container::convertReadOnlyTypedArray<" #_array_type                         \
              ">(,  output_convert_type=std::vector<" #_array_type ">,   output_convert_suffix=),  out")               \
    omni::container::IReadOnlyArray*&

// return of set of given type (output type is omni::container::IReadOnlyArray)
#define XR_ONI_ABI_RET_STD_SET(_array_type)                                                                            \
    OMNI_ATTR("output_convert_prefix=omni::container::convertReadOnlyTypedArrayToSet<" #_array_type                    \
              ">(,  output_convert_type=std::set<" #_array_type ">,   output_convert_suffix=)")                        \
    omni::container::IReadOnlyArray*

// Output reference set of given type (output type is omni::container::IReadOnlyArray)
#define XR_ONI_ABI_OUT_STD_SET(_array_type)                                                                            \
    OMNI_ATTR("output_convert_prefix=omni::container::convertReadOnlyTypedArrayToSet<" #_array_type                    \
              ">(,  output_convert_type=std::set<" #_array_type ">,   output_convert_suffix=),  out")                  \
    omni::container::IReadOnlyArray*&

// return of vector of strings (output type is omni::container::IReadOnlyArray)
#define XR_ONI_ABI_RET_STD_STRING_VECTOR()                                                                             \
    OMNI_ATTR(                                                                                                         \
        "output_convert_prefix=omni::container::convertReadOnlyStringArray"                                            \
        "(,  output_convert_type=std::vector<std::string>,   output_convert_suffix=)")                                 \
    omni::container::IReadOnlyArray*

// Output reference of vector of strings (output type is omni::container::IReadOnlyArray)
#define XR_ONI_ABI_OUT_STD_STRING_VECTOR()                                                                             \
    OMNI_ATTR(                                                                                                         \
        "output_convert_prefix=omni::container::convertReadOnlyStringArray"                                            \
        "(,  output_convert_type=std::vector<std::string>,   output_convert_suffix=),  out")                           \
    omni::container::IReadOnlyArray*&

// return of vector of IObjects by type (output type is omni::container::IReadOnlyArray)
// NOTE: first parameter is the type in the returned container, second parameter is the smart pointer object
// This will allow capturing pointers and doing the reference counting automatically when return an array of objects
#define XR_ONI_ABI_RET_STD_VECTOR_STEAL_TYPE(_array_type, _new_type)                                                   \
    OMNI_ATTR("output_convert_prefix=omni::container::convertReadOnlyTypedStealObjectArray<" #_array_type              \
              "," #_new_type ">(,  output_convert_type=std::vector<" #_new_type ">,   output_convert_suffix=)")        \
    omni::container::IReadOnlyArray*

// Output reference of vector of IObjects by type (output type is omni::container::IReadOnlyArray)
// NOTE: first parameter is the type in the returned container, second parameter is the smart pointer object
// This will allow capturing pointers and doing the reference counting automatically when return an array of objects
#define XR_ONI_ABI_OUT_STD_VECTOR_STEAL_TYPE(_array_type, _new_type)                                                   \
    OMNI_ATTR("output_convert_prefix=omni::container::convertReadOnlyTypedStealObjectArray<" #_array_type              \
              "," #_new_type ">(,  output_convert_type=std::vector<" #_new_type ">,   output_convert_suffix=),  out")  \
    omni::container::IReadOnlyArray*&

// return of vector of IObjects by type (output type is omni::container::IReadOnlyArray)
// NOTE: first parameter is the type in the returned container, second parameter is the smart pointer object
// This will allow capturing pointers and doing the reference counting automatically when return an array of objects
#define XR_ONI_ABI_RET_STD_VECTOR_BORROW_TYPE(_array_type, _new_type)                                                  \
    OMNI_ATTR("output_convert_prefix=omni::container::convertReadOnlyArrayToObjectArray<" #_array_type "," #_new_type  \
              ">(,  output_convert_type=std::vector<" #_new_type ">,   output_convert_suffix=)")                       \
    omni::container::IReadOnlyArray*

// Output reference of vector of IObjects by type (output type is omni::container::IReadOnlyArray)
// NOTE: first parameter is the type in the returned container, second parameter is the smart pointer object
// This will allow capturing pointers and doing the reference counting automatically when return an array of objects
#define XR_ONI_ABI_OUT_STD_VECTOR_BORROW_TYPE(_array_type, _new_type)                                                  \
    OMNI_ATTR("output_convert_prefix=omni::container::convertReadOnlyArrayToObjectArray<" #_array_type "," #_new_type  \
              ">(,  output_convert_type=std::vector<" #_new_type ">,   output_convert_suffix=),  out")                 \
    omni::container::IReadOnlyArray*&


/////////////////////////////////////////////////////////////
// Helpers defining how an ABI object can be casted
/////////////////////////////////////////////////////////////

#define XR_ONI_ABI_CASTABLE_IMPL(implTypeName)                                                                         \
    enum : omni::core::TypeId                                                                                          \
    {                                                                                                                  \
        kTypeId = OMNI_TYPE_ID(implTypeName),                                                                          \
        kIsCastableImpl = 0                                                                                            \
    };                                                                                                                 \
    virtual void* cast_abi(omni::core::TypeId id) noexcept override                                                    \
    {                                                                                                                  \
        if (id == kTypeId)                                                                                             \
        {                                                                                                              \
            this->acquire();                                                                                           \
            return this;                                                                                               \
        }                                                                                                              \
        return BaseType::cast_abi(id);                                                                                 \
    }

#define XR_ONI_ABI_CASTABLE_NO_PARENT(implTypeName)                                                                    \
    enum : omni::core::TypeId                                                                                          \
    {                                                                                                                  \
        kTypeId = OMNI_TYPE_ID(implTypeName),                                                                          \
        kIsCastableImpl = 0                                                                                            \
    };                                                                                                                 \
    virtual void* cast_abi(omni::core::TypeId id) noexcept override                                                    \
    {                                                                                                                  \
        if (id == kTypeId)                                                                                             \
        {                                                                                                              \
            this->acquire();                                                                                           \
            return this;                                                                                               \
        }                                                                                                              \
        return nullptr;                                                                                                \
    }

} // namespace xr
} // namespace kit
} // namespace omni
