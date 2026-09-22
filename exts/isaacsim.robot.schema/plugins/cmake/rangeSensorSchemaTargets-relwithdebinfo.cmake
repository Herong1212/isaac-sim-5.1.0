#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "rangesensorschema::rangeSensorSchema" for configuration "RelWithDebInfo"
set_property(TARGET rangesensorschema::rangeSensorSchema APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(rangesensorschema::rangeSensorSchema PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/librangeSensorSchema.so"
  IMPORTED_SONAME_RELWITHDEBINFO "librangeSensorSchema.so"
  )

list(APPEND _cmake_import_check_targets rangesensorschema::rangeSensorSchema )
list(APPEND _cmake_import_check_files_for_rangesensorschema::rangeSensorSchema "${_IMPORT_PREFIX}/lib/librangeSensorSchema.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
