#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "isaacsensorschema::isaacSensorSchema" for configuration "RelWithDebInfo"
set_property(TARGET isaacsensorschema::isaacSensorSchema APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(isaacsensorschema::isaacSensorSchema PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libisaacSensorSchema.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libisaacSensorSchema.so"
  )

list(APPEND _cmake_import_check_targets isaacsensorschema::isaacSensorSchema )
list(APPEND _cmake_import_check_files_for_isaacsensorschema::isaacSensorSchema "${_IMPORT_PREFIX}/lib/libisaacSensorSchema.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
