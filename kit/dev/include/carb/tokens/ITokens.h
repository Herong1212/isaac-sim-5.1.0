// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Implementation of `ITokens` interface
#pragma once

#include "../Interface.h"
#include "../cpp/ZStringView.h"
#include "../cpp/StringView.h"
#include "../../omni/String.h"

//! @brief Version of the `ITokens` interface
#define carb_tokens_ITokens_latest CARB_HEXVERSION(1, 1)
//! @brief Default version of the `ITokens` interface
#ifndef carb_tokens_ITokens
#    define carb_tokens_ITokens CARB_HEXVERSION(1, 0)
#endif

namespace carb
{
//! Namespace for `ITokens`.
namespace tokens
{

/**
 * Possible result of resolving tokens.
 */
enum class ResolveResult
{
    eSuccess, //!< Result indicating success.
    eTruncated, //!< Result that indicates success, but the output was truncated.
    eFailure, //!< Result that indicates failure.
};

/**
 * Possible options for ending of the resolved string
 */
enum class StringEndingMode
{
    eNullTerminator, //!< Indicates that the resolved string is NUL-terminated.
    eNoNullTerminator //!< Indicates that the resolved string is not NUL-terminated.
};

/**
 * Flags for token resolution algorithm
 */
using ResolveFlags = uint32_t;
const ResolveFlags kResolveFlagNone = 0; //!< Default token resolution process
const ResolveFlags kResolveFlagLeaveTokenIfNotFound = 1; //!< If cannot resolve token in a string then leave it as is.

/**
 * Interface for storing tokens and resolving strings containing them. Tokens are string pairs {name, value} that can be
 * referenced in a string as `"some text ${token_name} some other text"`, where the token name starts with a sequence
 * `"${"` and end with a first closing `"}"`.
 *
 * If a token with the name \<token_name\> has a defined value, then it will be substituted with its value.
 * If the token does not have a defined value, an empty string will be used for the replacement. This interface will use
 * the ISetting interface, if available, as storage and in such case tokens will be stored under the '/app/tokens' node.
 *
 * Note: The "$" symbol is considered to be special by the tokenizer and should be escaped by doubling it ("$" -> "$$")
 * in order to be processed as just a symbol "$"
 * Ex: "some text with $ sign" -> "some text with $$ sign"
 *
 * Single unescaped "$" signs are considered to be a bad practice to be used for token resolution but they are
 * acceptable and will be resolved into single "$" signs and no warning will be given about it.
 *
 * Ex:
 *   "$" -> "$",
 *   "$$" -> "$",
 *   "$$$" -> "$$"
 *
 * It's better to use the helper function "escapeString" from the "TokensUtils.h" to produce a string
 * that doesn't have any parts that could participate in tokenization. As a token name start with "${" and ends with the
 * first encountered "}" it can contain "$" (same rules about escaping it apply) and "{" characters, however such cases
 * will result in a warning being output to the log.
 * Ex: for the string "${bar$${}" the token resolution process will consider the token name to be "bar${"
 * (note that "$$" is reduced into a single "$") and a warning will be outputted into the log.
 *
 * Tokens are resolved recursively unless an error occurs. For instance, given:
 * ```cpp
 * setValue("a", "${b}");
 * setValue("b", "${c}");
 * setValue("c", "hello ${d}");
 * setValue("d", "world");
 *
 * resolveString(tokens, "${a}"); // will return "hello world"
 * ```
 *
 * Environment variables are automatically available as tokens, if defined. These are specified with the text
 * `${env:<var name>}` where `<var name>` is the name of the environment variable. The `env:` prefix is a reserved name,
 * so any call to \ref ITokens::setValue() or \ref ITokens::setInitialValue() with a name that starts with `env:` will
 * be rejected. The environment variable is read when needed and not cached in any way. An undefined environment
 * variable behaves as an undefined token.
 *
 * @thread_safety the interface's functions are not thread safe. It is responsibility of the user to use all necessary
 * synchronization mechanisms if needed. All data passed into a plugin's function must be valid for the duration of the
 * function call.
 */
struct ITokens
{
    // 1.0 - Initial release
    // 1.1 - added string_view-based functions
    CARB_PLUGIN_INTERFACE_EX("carb::tokens::ITokens", carb_tokens_ITokens_latest, carb_tokens_ITokens)
    // Ensure proper initialization order
    // Members must be declared in the same sequence as initialized

    /**
     * Sets a new value for the specified token, if the token didn't exist it will be created.
     *
     * Note: if the value is null then the token will be removed (see also: "removeToken" function). In this case true
     * is returned if the token was successfully deleted or didn't exist.
     *
     * @param name token name not enclosed in "${" and "}". Passing a null pointer results in an error
     * @param value new value for the token. Passing a null pointer deletes the token
     *
     * @return true if the operation was successful, false if the token name was null or an error occurred during the
     * operation
     */
    bool(CARB_ABI* setValue)(const char* name, const char* value);

    /**
     * Creates a token with the given name and value if it was non-existent. Otherwise does nothing.
     *
     * @param name Name of a token. Passing a null pointer results in an error
     * @param value Value of a token. Passing a null pointer does nothing.
     */
    void setInitialValue(const char* name, const char* value) const;

    /**
     * A function to delete a token.
     *
     * @param name token name not enclosed in "${" and "}". Passing a null pointer results in an error
     *
     * @return true if the operation was successful or token with such name didn't exist, false if the name is null or
     * an error occurred
     */
    bool removeToken(const char* name) const;

    /**
     * Tries to resolve all tokens in the source string buffer and places the result into the destination buffer.
     * If the destBufLen isn't enough to contain the result then the result will be truncated.
     *
     * @param sourceBuf the source string buffer. Passing a null pointer results in an error
     * @param sourceBufLen the length of the source string buffer
     * @param destBuf the destination buffer. Passing a null pointer results in an error
     * @param destBufLen the size of the destination buffer
     * @param endingMode sets if the result will have a null-terminator (in this case passing a zero
     * destBufLen will result in an error) or not
     * @param resolveFlags flags that modify token resolution process
     * @param[out] resolvedSize optional parameter. If the provided buffer were enough for the operation and it
     * succeeded then resolvedSize <= destBufLen and equals to the number of written bytes to the buffer, if the
     * operation were successful but the output were truncated then resolvedSize > destBufLen and equals to the minimum
     * buffer size that can hold the fully resolved string, if the operation failed then the value of the resolvedSize
     * is undetermined
     *
     * @retval ResolveResult::eTruncated if the destination buffer was too small to contain the result (note that if the
     *      StringEndingMode::eNullTerminator was used the result truncated string will end with a null-terminator)
     * @retval ResolveResult::eFailure if an error occurred.
     * @retval ResolveResult::eSuccess will be returned if the function successfully wrote the whole resolve result into
     *      the \p destBuf.
     */
    ResolveResult(CARB_ABI* resolveString)(const char* sourceBuf,
                                           size_t sourceBufLen,
                                           char* destBuf,
                                           size_t destBufLen,
                                           StringEndingMode endingMode,
                                           ResolveFlags resolveFlags,
                                           size_t* resolvedSize);

    /**
     * Calculates the minimum buffer size required to hold the result of resolving of the input string buffer.
     *
     * @param sourceBuf the source string buffer. Passing a null pointer results in an error
     * @param sourceBufLen the length of the source string buffer
     * @param endingMode sets if the result will have a null-terminator or not
     * @param resolveFlags flags that modify token resolution process
     * @param[out] resolveResult optional parameter that will contain the result of the attempted resolution to
     * calculate the necessary size
     *
     * @returns The calculated minimum size. In case of any error the function will return 0.
     */
    size_t(CARB_ABI* calculateDestinationBufferSize)(const char* sourceBuf,
                                                     size_t sourceBufLen,
                                                     StringEndingMode endingMode,
                                                     ResolveFlags resolveFlags,
                                                     ResolveResult* resolveResult);

    /**
     * Check the existence of a token
     *
     * @param tokenName the name of a token that will be checked for existence. Passing a null pointer results in an
     * error
     *
     * @return true if the token with the specified name exists, false is returned if an error occurs or there is no
     * token with such name
     */
    bool(CARB_ABI* exists)(const char* tokenName);

#if CARB_VERSION_ATLEAST(carb_tokens_ITokens, 1, 1)

    // Extended interface functions (v1.1)
    /**
     * Sets a new value for the specified token using string views, if the token didn't exist it will be created.
     *
     * This is a string view variant of setValue() and unlike setValue() it cannot delete a token. Use deleteValueS() to
     * delete a token.
     * @param name token name as a string view, not enclosed in "${" and "}"
     * @param value new value for the token as a string view
     *
     * @return true if the operation was successful, false if an error occurred during the operation
     */
    bool(CARB_ABI* setValueS)(const cpp::zstring_view& name, const cpp::zstring_view& value);

    /**
     * Tries to resolve all tokens in the source string buffer and places the result into the destination string.
     *
     * This is a string view variant of resolveString().
     *
     * @param sourceBuf the source string buffer as a string view
     * @param destBuf the destination string that will be resized to contain the result
     * @param resolveFlags flags that modify token resolution process
     *
     * @retval ResolveResult::eFailure if an error occurred.
     * @retval ResolveResult::eSuccess will be returned if the function successfully resolved all tokens.
     */
    ResolveResult(CARB_ABI* resolveStringS)(const cpp::string_view& sourceBuf,
                                            omni::string& destBuf,
                                            ResolveFlags resolveFlags);

    /**
     * Check the existence of a token using a string view
     *
     * This is a string view variant of exists().
     *
     * @param tokenName the name of a token that will be checked for existence as a string view
     *
     * @return true if the token with the specified name exists, false is returned if there is no token with such name
     */
    bool(CARB_ABI* existsS)(const cpp::zstring_view& tokenName);

    /**
     * A function to delete a token.
     *
     * @param name token name as a string view, not enclosed in "${" and "}"
     *
     * @return true if the operation was successful or token with such name didn't exist, false if an error occurred
     */
    bool(CARB_ABI* deleteValueS)(const cpp::zstring_view& name);

    /**
     * Calculates the minimum buffer size required to hold the result of resolving of the input string buffer.
     *
     * This is a string view variant of calculateDestinationBufferSize().
     *
     * @param sourceBuf the source string buffer as a string view
     * @param endingMode sets if the result will have a null-terminator or not
     * @param resolveFlags flags that modify token resolution process
     * @param[out] resolveResult optional parameter that will contain the result of the attempted resolution to
     * calculate the necessary size
     *
     * @returns The calculated minimum size. In case of any error the function will return 0.
     */
    size_t(CARB_ABI* calculateDestinationBufferSizeS)(const cpp::string_view& sourceBuf,
                                                      StringEndingMode endingMode,
                                                      ResolveFlags resolveFlags,
                                                      ResolveResult* resolveResult);

    /**
     * Creates a token with the given name and value if it was non-existent. Otherwise does nothing.
     *
     * This is a string view variant of setInitialValue().
     *
     * @param name Name of a token as a string view
     * @param value Value of a token as a string view
     */
    void setInitialValueS(cpp::zstring_view name, cpp::zstring_view value) const
    {
        if (!existsS(name))
        {
            setValueS(name, value);
        }
    }

#endif
};

inline void ITokens::setInitialValue(const char* name, const char* value) const
{
    if (!exists(name) && value)
    {
        setValue(name, value);
    }
}

inline bool ITokens::removeToken(const char* name) const
{
    return setValue(name, nullptr);
}

} // namespace tokens
} // namespace carb
