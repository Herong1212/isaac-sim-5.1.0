// Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#ifdef __cplusplus
#include "XRGpuToolsConvertParams.h"
#endif

#define PI 3.1415926535897932384626433832795

inline float lanczosFcn(float x, float a)
{
    if (abs(x) < 1e-3)
    {
        return 1.0f;
    }

    return a * sin(PI * x) * sin(PI * x / a) / (PI * PI * x * x);
}

inline float lanczos2D(float2 x, float a)
{
    return lanczosFcn(x.x, a) * lanczosFcn(x.y, a);
}

#define LANCZOS_SAMPLE_DATATYPE(datatype)                                                                    \
    inline datatype lanczosSample(Texture2D<datatype> tex, uint2 texSize, float2 loc, int lanczos_order = 1) \
    {                                                                                                        \
        loc = loc * texSize - 0.5f;                                                                          \
        int2 floor_loc = floor(loc);                                                                         \
        datatype result = 0.0f;                                                                              \
        float weight = 0.0f;                                                                                 \
                                                                                                             \
        for (int y = floor_loc.y - lanczos_order + 1; y < floor_loc.y + lanczos_order + 1; y++)              \
        {                                                                                                    \
            for (int x = floor_loc.x - lanczos_order + 1; x < floor_loc.x + lanczos_order + 1; x++)          \
            {                                                                                                \
                int2 coord = int2(x, y);                                                                     \
                if (coord.x < 0 || coord.y < 0 || coord.x >= texSize.x || coord.y >= texSize.y)              \
                {                                                                                            \
                    continue;                                                                                \
                }                                                                                            \
                float w = lanczos2D(loc - float2(x, y), lanczos_order);                                      \
                result += w * tex[uint2(x, y)];                                                              \
                weight += w;                                                                                 \
            }                                                                                                \
        }                                                                                                    \
                                                                                                             \
        return weight == 0 ? 0.0f : result / weight;                                                         \
    }

LANCZOS_SAMPLE_DATATYPE(float)
LANCZOS_SAMPLE_DATATYPE(float2)
LANCZOS_SAMPLE_DATATYPE(float3)
LANCZOS_SAMPLE_DATATYPE(float4)
