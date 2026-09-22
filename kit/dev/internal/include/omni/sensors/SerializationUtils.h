// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include <cstdint>

namespace omni
{
namespace sensors
{

/**
 * Constant values for indicating the endian
 * @param SER_LIL_ENDIAN Indicates the usage of lil endian
 * @param SER_BIG_ENDIAN Indicates the usage of big endian
 */
static const bool SER_LIL_ENDIAN = false;
static const bool SER_BIG_ENDIAN = true;

/**
 * Function that facilitates serializing primitive types
 * @note
 *      - Function fills the buffer with the serialized bytes
 *      - User is responsible for adequate buffer size (no out of bounds check)
 *      - The input idx will be advanced to after the last used position for ease of consecutive use, example:
 *          -   serPrimitive<std::uint32_t>(buffer, idx, &data->id, SER_BIG_ENDIAN);
 *          -   serPrimitive<std::uint32_t>(buffer, idx, &data->size, SER_BIG_ENDIAN);
 * @param buffer To be serialized buffer
 * @param idx Current position in the buffer
 * @param primitive Primitive
 * @param big_endian Use big endian serialization, if true
 * @result Returns true, if successfull
 */

template <typename T>
bool serPrimitive(uint8_t* buffer, uint32_t* idx, T* primitive, bool isBigEndian)
{
    const int64_t size = sizeof(T);
    if ((size > 64) || (!buffer) || (!idx) || (!primitive))
        return false;

    uint64_t prim_bytes = 0;
    memcpy(&prim_bytes, primitive, size);

    if (isBigEndian)
    {
        // big endian serialization required
        for (int8_t i = static_cast<int8_t>(size - 1); i >= 0; i--)
        {
            buffer[(*idx)++] = (uint8_t)((prim_bytes & (((uint64_t)0xFF) << (i << 3))) >> (i << 3));
        }
    }
    else
    {
        // little endian serialization required
        for (int8_t i = 0; i < size; i++)
        {
            buffer[(*idx)++] = (uint8_t)((prim_bytes & (((uint64_t)0xFF) << (i << 3))) >> (i << 3));
        }
    }

    return true;
}


/**
 * Function that facilitates crc16 calculation (cyclic redundancy check - CRC-16/CCITT-FALSE)
 * @param buffer To be checked raw data buffer
 * @param wLength Length of the raw data chunk
 * @result Returns crc value
 */

static inline uint16_t crc16CcittFalse(uint8_t* buffer, uint16_t wLength)
{
    uint8_t i;
    uint16_t wCrc = 0xffff;

    if (wLength == 0)
        return (~wCrc);

    while (wLength--)
    {
        wCrc ^= *(unsigned char*)buffer++ << 8;
        for (i = 0; i < 8; i++)
            wCrc = wCrc & 0x8000 ? (wCrc << 1) ^ 0x1021 : wCrc << 1;
    }
    return wCrc & 0xffff;
}

} // namespace sensors
} // namespace omni
