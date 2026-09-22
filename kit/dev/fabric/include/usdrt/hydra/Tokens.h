// Copyright (c) 2024-2025, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#define USDRT_HYDRA_SCENEDELEGATE_OMNI_NUREC_VOLUME_PRIM_NAMES \
    (INGPFieldAsset) \
    (OmniNuRecVolume) \
    (OmniNuRecFieldAsset)

#define USDRT_HYDRA_SCENEDELEGATE_OMNI_SENSOR_PRIM_NAMES \
    (OmniSensor) \
    (OmniRadar) \
    (OmniLidar) \
    (OmniUltrasonic) \
    (OmniGeneralSensor)

#define USDRT_HYDRA_SCENEDELEGATE_SENSOR_ATTRIBUTE_NAMES \
    ((omniSensorAttributes, "omni:sensor:__attributes__"))

// clang-format off
#define USDRT_HYDRA_SCENEDELEGATE_OMNI_LENS_DISTORTION_ATTRIBUTE_NAMES \
    ((omniLensDistortionAttributes, "omni:lensdistortion:__attributes__")) \
    ((omniLensdistortionModel, "omni:lensdistortion:model")) \
    (ftheta) \
    (kannalaBrandtK3) \
    (radTanThinPrism) \
    (opencvFisheye) \
    (opencvPinhole) \
    ((omniLensdistortionFthetaNominalWidth, "omni:lensdistortion:ftheta:nominalWidth")) \
    ((omniLensdistortionFthetaNominalHeight, "omni:lensdistortion:ftheta:nominalHeight")) \
    ((omniLensdistortionFthetaMaxFov, "omni:lensdistortion:ftheta:maxFov")) \
    ((omniLensdistortionFthetaK0, "omni:lensdistortion:ftheta:k0")) \
    ((omniLensdistortionFthetaK1, "omni:lensdistortion:ftheta:k1")) \
    ((omniLensdistortionFthetaK2, "omni:lensdistortion:ftheta:k2")) \
    ((omniLensdistortionFthetaK3, "omni:lensdistortion:ftheta:k3")) \
    ((omniLensdistortionFthetaK4, "omni:lensdistortion:ftheta:k4")) \
    ((omniLensdistortionFthetaK5, "omni:lensdistortion:ftheta:k5")) \
    ((omniLensdistortionFthetaOpticalCenter, "omni:lensdistortion:ftheta:opticalCenter")) \
    ((omniLensdistortionKannalaBrandtK3NominalWidth, "omni:lensdistortion:kannalaBrandtK3:nominalWidth")) \
    ((omniLensdistortionKannalaBrandtK3NominalHeight, "omni:lensdistortion:kannalaBrandtK3:nominalHeight")) \
    ((omniLensdistortionKannalaBrandtK3MaxFov, "omni:lensdistortion:kannalaBrandtK3:maxFov")) \
    ((omniLensdistortionKannalaBrandtK3K0, "omni:lensdistortion:kannalaBrandtK3:k0")) \
    ((omniLensdistortionKannalaBrandtK3K1, "omni:lensdistortion:kannalaBrandtK3:k1")) \
    ((omniLensdistortionKannalaBrandtK3K2, "omni:lensdistortion:kannalaBrandtK3:k2")) \
    ((omniLensdistortionKannalaBrandtK3K3, "omni:lensdistortion:kannalaBrandtK3:k3")) \
    ((omniLensdistortionKannalaBrandtK3OpticalCenter, "omni:lensdistortion:kannalaBrandtK3:opticalCenter")) \
    ((omniLensdistortionRadTanThinPrismNominalWidth, "omni:lensdistortion:radTanThinPrism:nominalWidth")) \
    ((omniLensdistortionRadTanThinPrismNominalHeight, "omni:lensdistortion:radTanThinPrism:nominalHeight")) \
    ((omniLensdistortionRadTanThinPrismMaxFov, "omni:lensdistortion:radTanThinPrism:maxFov")) \
    ((omniLensdistortionRadTanThinPrismK0, "omni:lensdistortion:radTanThinPrism:k0")) \
    ((omniLensdistortionRadTanThinPrismK1, "omni:lensdistortion:radTanThinPrism:k1")) \
    ((omniLensdistortionRadTanThinPrismK2, "omni:lensdistortion:radTanThinPrism:k2")) \
    ((omniLensdistortionRadTanThinPrismK3, "omni:lensdistortion:radTanThinPrism:k3")) \
    ((omniLensdistortionRadTanThinPrismK4, "omni:lensdistortion:radTanThinPrism:k4")) \
    ((omniLensdistortionRadTanThinPrismK5, "omni:lensdistortion:radTanThinPrism:k5")) \
    ((omniLensdistortionRadTanThinPrismOpticalCenter, "omni:lensdistortion:radTanThinPrism:opticalCenter")) \
    ((omniLensdistortionRadTanThinPrismP0, "omni:lensdistortion:radTanThinPrism:p0")) \
    ((omniLensdistortionRadTanThinPrismP1, "omni:lensdistortion:radTanThinPrism:p1")) \
    ((omniLensdistortionRadTanThinPrismS0, "omni:lensdistortion:radTanThinPrism:s0")) \
    ((omniLensdistortionRadTanThinPrismS1, "omni:lensdistortion:radTanThinPrism:s1")) \
    ((omniLensdistortionRadTanThinPrismS2, "omni:lensdistortion:radTanThinPrism:s2")) \
    ((omniLensdistortionRadTanThinPrismS3, "omni:lensdistortion:radTanThinPrism:s3")) \
    ((omniLensdistortionOpencvFisheyeImageSize, "omni:lensdistortion:opencvFisheye:imageSize")) \
    ((omniLensdistortionOpencvFisheyeCx, "omni:lensdistortion:opencvFisheye:cx")) \
    ((omniLensdistortionOpencvFisheyeCy, "omni:lensdistortion:opencvFisheye:cy")) \
    ((omniLensdistortionOpencvFisheyeK1, "omni:lensdistortion:opencvFisheye:k1")) \
    ((omniLensdistortionOpencvFisheyeK2, "omni:lensdistortion:opencvFisheye:k2")) \
    ((omniLensdistortionOpencvFisheyeK3, "omni:lensdistortion:opencvFisheye:k3")) \
    ((omniLensdistortionOpencvFisheyeK4, "omni:lensdistortion:opencvFisheye:k4")) \
    ((omniLensdistortionOpencvFisheyeFx, "omni:lensdistortion:opencvFisheye:fx")) \
    ((omniLensdistortionOpencvFisheyeFy, "omni:lensdistortion:opencvFisheye:fy")) \
    ((omniLensdistortionOpencvPinholeImageSize, "omni:lensdistortion:opencvPinhole:imageSize")) \
    ((omniLensdistortionOpencvPinholeCx, "omni:lensdistortion:opencvPinhole:cx")) \
    ((omniLensdistortionOpencvPinholeCy, "omni:lensdistortion:opencvPinhole:cy")) \
    ((omniLensdistortionOpencvPinholeFx, "omni:lensdistortion:opencvPinhole:fx")) \
    ((omniLensdistortionOpencvPinholeFy, "omni:lensdistortion:opencvPinhole:fy")) \
    ((omniLensdistortionOpencvPinholeK1, "omni:lensdistortion:opencvPinhole:k1")) \
    ((omniLensdistortionOpencvPinholeK2, "omni:lensdistortion:opencvPinhole:k2")) \
    ((omniLensdistortionOpencvPinholeK3, "omni:lensdistortion:opencvPinhole:k3")) \
    ((omniLensdistortionOpencvPinholeK4, "omni:lensdistortion:opencvPinhole:k4")) \
    ((omniLensdistortionOpencvPinholeK5, "omni:lensdistortion:opencvPinhole:k5")) \
    ((omniLensdistortionOpencvPinholeK6, "omni:lensdistortion:opencvPinhole:k6")) \
    ((omniLensdistortionOpencvPinholeP1, "omni:lensdistortion:opencvPinhole:p1")) \
    ((omniLensdistortionOpencvPinholeP2, "omni:lensdistortion:opencvPinhole:p2")) \
    ((omniLensdistortionOpencvPinholeS1, "omni:lensdistortion:opencvPinhole:s1")) \
    ((omniLensdistortionOpencvPinholeS2, "omni:lensdistortion:opencvPinhole:s2")) \
    ((omniLensdistortionOpencvPinholeS3, "omni:lensdistortion:opencvPinhole:s3")) \
    ((omniLensdistortionOpencvPinholeS4, "omni:lensdistortion:opencvPinhole:s4"))
    // TODO omni:lensdistortion:lut

// clang-format on
