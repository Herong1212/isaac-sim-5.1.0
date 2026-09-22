# Copyright 2019-2022, Collabora, Ltd.
# Copyright 2019, Benjamin Saunders <ben.e.saunders@gmail.com>
#
# SPDX-License-Identifier: BSL-1.0
#
# Maintained by:
# 2019-2022 Rylie Pavlik <rylie.pavlik@collabora.com> <rylie@ryliepavlik.com>

# Get input from main CMake script
set(MANIFEST_TEMPLATE "/builds/omniverse/xr/xcr/deps/monado/cmake/openxr_manifest.in.json")
set(DESTINATION "")
set(OUT_FILENAME "")
set(CONFIGURE_OUTPUT_FILE "/builds/omniverse/xr/xcr/_build-XCR/mnd/src/xrt/targets/openxr/intermediate_manifest_buildtree_openxr_xcr.json")
set(IS_INSTALL OFF)
set(MANIFEST_DESCRIPTION "OpenXR runtime manifest")
set(TARGET "openxr_xcr")
# Target install dir relative to install prefix
set(RELATIVE_TARGET_DIR "")
# Target so/dll filename
set(TARGET_FILENAME "")
# The relative path from the manifest dir to the library. Optional.
set(TARGET_DIR_RELATIVE_TO_MANIFEST
    "")
# Config option
set(ABSOLUTE_TARGET_PATH "")
if (NOT LIBMONADO)
    set(LIBMONADO "")
endif()

if(TARGET_PATH)
    # This is at build time, not install time
    set(CONFIGURE_OUTPUT_FILE "${OUT_FILE}")
elseif(ABSOLUTE_TARGET_PATH)
    # Absolute path to TARGET
    message(
        STATUS
            "Installing ${MANIFEST_DESCRIPTION} with absolute path to library")
    set(TARGET_PATH "${RELATIVE_TARGET_DIR}/${TARGET_FILENAME}")
    if(NOT IS_ABSOLUTE ${RELATIVE_TARGET_DIR})
        set(TARGET_PATH "${CMAKE_INSTALL_PREFIX}/${TARGET_PATH}")
    endif()
    if(LIBMONADO)
        set(LIBMONADO "${RELATIVE_TARGET_DIR}/${LIBMONADO}")
        if(NOT IS_ABSOLUTE ${RELATIVE_TARGET_DIR})
            set(LIBMONADO "${CMAKE_INSTALL_PREFIX}/${LIBMONADO}")
        endif()
    endif()
elseif(TARGET_DIR_RELATIVE_TO_MANIFEST)
    # Relative path to target.
    message(
        STATUS
            "Installing ${MANIFEST_DESCRIPTION} with JSON-relative path to library"
    )
    set(TARGET_PATH "${TARGET_DIR_RELATIVE_TO_MANIFEST}/${TARGET_FILENAME}")
    if(LIBMONADO)
        get_filename_component(LIBMONADO "${LIBMONADO}" NAME)
        set(LIBMONADO "${TARGET_DIR_RELATIVE_TO_MANIFEST}/${LIBMONADO}")
    endif()
else()
    # Unqualified filename: requires it exist on the system shared library search path.
    message(
        STATUS
            "Installing ${MANIFEST_DESCRIPTION} with unqualified library filename (uses system search path)"
    )
    set(TARGET_PATH "${TARGET_FILENAME}")
    if(LIBMONADO)
        get_filename_component(LIBMONADO "${LIBMONADO}" NAME)
    endif()
endif()

if(LIBMONADO)
    set(extra_fields ",\n        \"MND_libmonado_path\": \"${LIBMONADO}\"")
endif()

if(WIN32)
    # Windows really wants backslashes in the manifest, and they must be escaped.
    string(REPLACE "/" [[\\]] TARGET_PATH ${TARGET_PATH})
endif()

set(target_path "${TARGET_PATH}")
# Create manifest
configure_file("${MANIFEST_TEMPLATE}" "${CONFIGURE_OUTPUT_FILE}")

if(IS_INSTALL)
    # Install it
    file(
        INSTALL
        DESTINATION "${CMAKE_INSTALL_PREFIX}/${DESTINATION}"
        TYPE FILE FILES "${CONFIGURE_OUTPUT_FILE}")
endif()
