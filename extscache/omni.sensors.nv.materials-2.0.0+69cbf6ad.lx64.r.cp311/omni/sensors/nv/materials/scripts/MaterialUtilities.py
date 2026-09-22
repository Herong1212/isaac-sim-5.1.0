# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import numpy as np
import omni.sensors.nv.common._common as common
import omni.sensors.nv.materials._materials as materials


def get_material(wavelength, bandwidth, materialfilename, coatingfilename=None, paintfilename=None):
    profilefactory = materials.acquire_material_profile_reader_interface()
    reader = profilefactory.createInstance()
    reader.initialize()
    num_paints = 0
    with open(materialfilename, "r") as file:
        data = file.read()
        reader.parseJson(data)
    if coatingfilename is not None:
        with open(coatingfilename, "r") as file:
            data = file.read()
            reader.parseCoatingVariantJson(data)
    if paintfilename is not None:
        with open(paintfilename, "r") as file:
            data = file.read()
            reader.parsePaintVariantJson(data)
            num_paints = reader.getNumPaintVariantProperties(wavelength, bandwidth)
    return reader, num_paints


def wrap_angle(angle, lo, hi):
    domain = hi - lo
    if angle < lo:
        return angle + domain
    elif angle > hi:
        return angle - domain
    return angle


def get_bsdf(paints, num_paints=0):
    bsdffactory = materials.acquire_material_util_bsdf_interface()
    bsdf = bsdffactory.createInstance()
    bsdf.initialize(num_paints)
    bsdf.initializePaintVariants(paints)
    return bsdf


def get_material_props(wavelength, bandwidth, reader):
    bkprops = materials.BulkProperties()
    spprops = materials.SpectralProperties()
    wave_type = materials.WaveType.WAVE_ELECTROMAGNETIC
    reader.readMaterialProperties(bkprops, spprops, wavelength, bandwidth, wave_type)
    return bkprops, spprops


def get_variant_props(wavelength, bandwidth, coatings, paints, reader):
    wave_type = materials.WaveType.WAVE_ELECTROMAGNETIC
    reader.readVariantProperties(coatings, paints, wavelength, bandwidth, wave_type)


def compute_area_spot_size_at_range(distance, beam_profile):
    rr_horz = beam_profile.beamWaistHorM / beam_profile.divHorRad
    rr_vert = beam_profile.beamWaistVertM / beam_profile.divVertRad
    rratio_horz = abs(distance - beam_profile.focusDistM) / rr_horz
    rratio_vert = abs(distance - beam_profile.focusDistM) / rr_vert
    wz_sq = (
        beam_profile.Msquared
        * beam_profile.beamWaistHorM
        * beam_profile.beamWaistVertM
        * np.sqrt((1 + rratio_horz * rratio_horz) * (1 + rratio_vert * rratio_vert))
    )
    return np.pi * wz_sq


def get_mat_input():
    return materials.NvMatInput()


def get_mat_output():
    return materials.NvMatOutput()


def get_mat_props():
    return materials.NvPolarizedRayProps()


def get_mat_coatings():
    return materials.CoatingVariantProperties()


def get_mat_paints():
    return materials.PaintVariantProperties()


def get_mat_spectral_properties():
    return materials.SpectralProperties()


def get_mat_bulk_properties():
    return materials.BulkProperties()


def get_mat_solid_angles(initial_spectral_props, current_spectral_props, input_mat):
    return materials.calcSolidAngleForMat(initial_spectral_props, current_spectral_props, input_mat)


def convert_vec_array_to_float2(vec_array):
    if vec_array.size == 2:
        return common.float2.make_float2(vec_array[0], vec_array[1])
    else:
        print("could not convert array to float2")
    return common.float2.make_float2(0, 0)


def convert_vec_array_to_float3(vec_array):
    if vec_array.size == 3:
        return common.float3.make_float3(vec_array[0], vec_array[1], vec_array[2])
    else:
        print("could not convert array to float3")
    return common.float3.make_float3(0, 0, 0)


def convert_vec_array_to_float4(vec_array):
    if vec_array.size == 4:
        return common.float4.make_float4(vec_array[0], vec_array[1], vec_array[2], vec_array[3])
    else:
        print("could not convert array to float4")
    return common.float4.make_float4(0, 0, 0, 0)
