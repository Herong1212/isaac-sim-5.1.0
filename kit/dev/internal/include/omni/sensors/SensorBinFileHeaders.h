// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include <omni/String.h>

#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>

namespace omni
{
namespace sensors
{


constexpr int32_t DW_MAJOR_VERSION = 5;
constexpr int32_t DW_MINOR_VERSION = 10;
constexpr int32_t DW_PATCH_VERSION = 9878;

#pragma pack(push, 1)

struct PcapHeader
{
    uint32_t magic_number;
    uint16_t version_major;
    uint16_t version_minor;
    int32_t thiszone;
    uint32_t sigfigs;
    uint32_t snaplen;
    uint32_t network;
};

struct DWFileHeader
{
    uint32_t fileMagicNumber;
    int32_t fileVersion;
    int32_t driveworksMajor;
    int32_t driveworksMinor;
    int32_t driveworksPatch;

    char driveworksHash[12]; // not used -- can be zero
    // 32 bytes total
};

struct BeamAngles
{
    float elevation[256];
    size_t numElevations{ 0 }; // TODO: correct place?
    size_t sizeHintEle{ 0 }; // not used;
    float azimuth[256];
    size_t numAzimuths{ 0 }; // TODO: correct place?
    size_t sizeHintAzi{ 0 }; // not used;
};

struct LidarBinFileHeader
{
    DWFileHeader common;
    unsigned char parameterString[256];
    BeamAngles beamAngles;
    unsigned char additionalParam[2048];
    size_t lengthAdditional{ 0 };
};

struct USSBinFileHeader
{
    DWFileHeader common;
    uint8_t unused[2056];
};

struct UbloxBinFileHeader
{
    DWFileHeader common;
};
struct RadarBinFileHeader
{
    DWFileHeader common;
    unsigned char parameterString[512];
};

struct EthernetHeader
{
    uint8_t dst[6];
    uint8_t src[6];
    uint16_t type;
};

struct IPHeader
{
    uint8_t verHeaderLength;
    uint8_t diff;
    uint8_t length[2];
    uint16_t id;
    uint16_t flags;
    uint8_t ttl;
    uint8_t protocol;
    uint16_t checksum;
    uint8_t srcDst[8];
};

struct UDPHeader
{
    uint16_t srcPort;
    uint16_t dstPort;
    uint8_t length[2];
    uint16_t checksum;
};

struct PcapPacketHeader
{
    uint32_t ts_sec;
    uint32_t ts_usec;
    uint32_t incl_len;
    uint32_t orig_len;
    EthernetHeader ethernet;
    IPHeader ip;
    UDPHeader udp;
};

struct DWBinPacketHeader
{
    uint32_t packetSize;
    int64_t packetTimeUs;
};

struct DWUBloxPacketHeader
{
    int64_t packetTimeUs;
    uint16_t packetSize;
    uint16_t nbytes1 = 0x91BA;
    uint32_t nbytes2 = 0x0000007F;
};

struct DWMinimalBinHeader
{
    int64_t timestamp; ///< Packet timestamp in microseconds.
};

struct DWCanMessageHeader
{
    int64_t timestamp; ///< Packet timestamp in microseconds.
    uint32_t id; ///< CAN message ID.
    int16_t size; ///< Payload size in bytes.
};

struct DWCanMessageV1
{
    DWCanMessageHeader header;
    uint8_t data[8]; ///< Fixed size payload (padded with zeros).
};

struct DWCanMessageV2
{
    DWCanMessageHeader header;
    uint8_t data[64]; ///< Fixed size payload (padded with zeros).
};

struct DWDataPacketHeader
{
    uint64_t size; ///< size of the data message payload (in DW: size_t)
    int64_t hostTimestamp; ///< timestamp at which the message was recorder (in DW: dwTime_t)
};

struct GenericBinHeader // Dummy header for writing raw/generic sensor output
{
};

#pragma pack(pop)

template <class Header>
class DWBinFileWriter
{
public:
    DWBinFileWriter() = default;
    DWBinFileWriter(const DWBinFileWriter&) = default;
    DWBinFileWriter(DWBinFileWriter&&) = default;
    DWBinFileWriter& operator=(const DWBinFileWriter&) = default;
    DWBinFileWriter& operator=(DWBinFileWriter&&) = default;

    // No header
    DWBinFileWriter(const omni::string& fileName)
        : m_file(std::ofstream(fileName.c_str(), std::ios::binary | std::ios::out | std::ios::trunc))
    {
    }

    DWBinFileWriter(const omni::string& fileName, const Header& header) : DWBinFileWriter(fileName)
    {
        m_header = header;
        m_file.write((char*)&header, sizeof(Header));
    }

    ~DWBinFileWriter()
    {
        close();
    }

    void close()
    {
        if (m_file.is_open())
        {
            m_file.flush();
            m_file.close();
        }
    }

    void dumpPacket(const PcapPacketHeader& header, const void* packetData)
    {
        m_file.write((char*)&header, sizeof(PcapPacketHeader));
        auto headerLength =
            sizeof(omni::sensors::EthernetHeader) + sizeof(omni::sensors::IPHeader) + sizeof(omni::sensors::UDPHeader);
        m_file.write((char*)packetData, header.incl_len - headerLength);
    }

    void dumpPacket(const DWBinPacketHeader& header, const void* packetData)
    {
        m_file.write((char*)&header, sizeof(DWBinPacketHeader));
        m_file.write((char*)packetData, header.packetSize);
    }

    void dumpPacket(const DWUBloxPacketHeader& header, const void* packetData)
    {
        m_file.write((char*)&header, sizeof(DWUBloxPacketHeader));
        m_file.write((char*)packetData, header.packetSize);
    }

    void dumpPacket(const DWCanMessageHeader& header, const void* packetData)
    {
        char payload[64] = {};
        memcpy((void*)payload, packetData, header.size);

        m_file.write((char*)&header, sizeof(DWCanMessageHeader));
        m_file.write((char*)payload, 64);
    }

    void dumpPacket(const void* packetData, const size_t dataSize)
    {
        m_file.write((char*)packetData, dataSize);
    }

    const Header& getFileHeader() const
    {
        return m_header;
    }

private:
    std::ofstream m_file;
    Header m_header;
};

} // namespace sensors
} // namespace omni
