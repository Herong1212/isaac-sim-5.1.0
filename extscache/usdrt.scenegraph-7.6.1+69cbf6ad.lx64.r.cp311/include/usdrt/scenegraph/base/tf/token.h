// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
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

#include <omni/fabric/IToken.h>

#include <string>

namespace usdrt
{

//! @class TfToken
//! Token for efficient comparison, assignment, and hashing of known strings.
//!
//! A TfToken is a handle for a registered string, and can be compared,
//! assigned, and hashed in constant time.
//!
//! This implementation fairly simply wraps @ref omni::fabric::Token.
class TfToken
{
public:
    //! Create the empty token containing omni::fabric::kUninitializedToken.
    TfToken();
    //! Copy constructor
    TfToken(const omni::fabric::Token& token);
    //! Move constructor
    explicit TfToken(omni::fabric::Token&& token) noexcept;
    //! Aquire a token for the given string.
    //! @param token String representation of token
    TfToken(const std::string& token);
    //! Acquire a token for the given string.
    //! @param token C-string representation of token
    TfToken(const char* token);

    //! Get the string that this token represents
    //! @returns String representation of the token.
    const std::string GetString() const;

    //! Get the text that this token represents.
    //! @returns Return the C-string value that this token represents.
    //! @note The returned pointer value is not valid after this TfToken
    //! object has been destroyed.
    const char* GetText() const;

    //! Get the size of the string that this token represents.
    //! @returns Return the size of the string that this token represents.
    size_t size() const;

    //! Update this token with a value from python.
    //! @param fromPython Value extracted from python in the TfToken custom python converter.
    //!
    //! This is used in the python bindings for TfToken to convert from python strings.
    //! @code
    //! // where source is the source PyObject* from python and
    //! // value is the result TfToken
    //! PyObject* tmp = PyObject_Str(source);
    //! value.pyUpdate(PyUnicode_AsUTF8(tmp));
    //! @endcode
    //!
    //! See bindings/common.h [TODO link to this when documented]
    void pyUpdate(const char* fromPython);

    // TODO: other TfToken APIs

    //! Check if this token is empty.
    //! @returns Return true if this token contains omni::fabric::kUninitializedToken, and false otherwise.
    bool IsEmpty() const;

    //! Equality operator [TODO more fabric info?]
    bool operator==(const TfToken& other) const;
    //! Inequality operator
    bool operator!=(const TfToken& other) const;
    //! Less-than operator that compares tokenized strings lexicographically.
    bool operator<(const TfToken& other) const;
    //! Explicit conversion operator for omni::fabric::TokenC,
    //! an integer key that identify paths to C-ABI interfaces
    //! @returns Return omni::fabric::TokenC representation of this token.
    explicit operator omni::fabric::TokenC() const;
    //! Explicit operator for std::move.
    explicit operator omni::fabric::Token() && noexcept;

    friend struct std::hash<usdrt::TfToken>;

private:
    omni::fabric::Token m_token;
};

inline TfToken::TfToken()
{
    // m_token constructs uninitialized by default
}

inline TfToken::TfToken(const omni::fabric::Token& token) : m_token(token)
{
}

inline TfToken::TfToken(omni::fabric::Token&& token) noexcept : m_token(std::move(token))
{
}

inline TfToken::TfToken(const std::string& token) : m_token(token.c_str())
{
}

inline TfToken::TfToken(const char* token) : m_token(token)
{
}

inline bool TfToken::operator==(const TfToken& other) const
{
    return m_token == other.m_token;
}

inline bool TfToken::operator!=(const TfToken& other) const
{
    return !(m_token == other.m_token);
}

inline bool TfToken::operator<(const TfToken& other) const
{
    return m_token < other.m_token;
}

inline TfToken::operator omni::fabric::TokenC() const
{
    return omni::fabric::TokenC(m_token);
}

inline TfToken::operator omni::fabric::Token() && noexcept
{
    return std::move(m_token);
}

inline const std::string TfToken::GetString() const
{
    return m_token.getString();
}

inline const char* TfToken::GetText() const
{
    return m_token.getText();
}

inline size_t TfToken::size() const
{
    return m_token.size();
}

inline void TfToken::pyUpdate(const char* fromPython)
{
    m_token = omni::fabric::Token(fromPython);
}

inline bool TfToken::IsEmpty() const
{
    return m_token == omni::fabric::kUninitializedToken;
}

//! Convenience type for vector of tokens
typedef std::vector<TfToken> TfTokenVector;

} // namespace usdrt

namespace std
{

template <>
struct hash<usdrt::TfToken>
{
    std::size_t operator()(const usdrt::TfToken& key) const
    {
        return hash<omni::fabric::Token>()(key.m_token);
    }
};

} // namespace std
