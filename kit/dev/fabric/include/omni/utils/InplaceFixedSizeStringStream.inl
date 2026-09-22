// Copyright (c) 2025, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <ostream>

namespace omni
{

// Simple string output stream that uses an fix in place memory buffer for storage
template <std::size_t Size>
class InplaceFixedSizeStringStream : public std::ostream
{
public:
    InplaceFixedSizeStringStream()
    : std::ostream(&m_buf), m_buf()
    {}
    const char* c_str() const
    {
        return m_buf.c_str();
    }
    void reset()
    {
        m_buf.reset();
        clear();
    }

private:
    class FixedSizeBuffer : public std::streambuf
    {
    public:
        FixedSizeBuffer()
        {
            reset();
        }
        const char* c_str() const
        {
            *pptr() = '\0';
            return m_buffer;
        }
        void reset()
        {
            setp(m_buffer, m_buffer + Size - 1);
            m_buffer[0] = '\0';
        }
    protected:
        int_type overflow(int_type ch) override
        {
            // prevent buffer overflow when we reach the size of the buffer
            if (ch != traits_type::eof() && pptr() < epptr())
            {
                *pptr() = ch;
                pbump(1);
                return ch;
            }
            return traits_type::eof();
        }

    private:
        char m_buffer[Size];
    };

    FixedSizeBuffer m_buf;
};

} //namespace omni
