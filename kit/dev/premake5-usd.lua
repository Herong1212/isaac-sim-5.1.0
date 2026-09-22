-- SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
-- SPDX-License-Identifier: Apache-2.0
--

-- main module table
local m = {}

-- Detects the version of python that is being used
-- in python_root.
-- Arguments: A dictionary of options:
--   python_root: (Required) The path to the root of the python installation.
--                If python_lib_path and python_lib_name are not specified (the default
--                case) the root of the Python installation will be used to auto detect
--                the version of python being used.
--   python_version: (Optional) The specific version of python being used.  Callers
--                   can pass this if they'd like to bypass the auto detect system
--                   in place to detect the version.
--   python_lib_path: (Optional) The specific path to the python library directory.
--                    This can be used for custom python packages that don't conform
--                    to using 'lib' (Windows) or 'libs' (Linux).
--   python_lib_name: (Optional) The name of the library for a python installation that
--                    will be linked against.  This can be used to specify the exact
--                    python library version rather than having this method auto detect
--                    the version present.  This is the library name without the suffix.
--
-- Returns: The version of the python library that will be used to link against.
--          If no version could be auto-deduced, an error will be thrown.
--
function m.get_python_version(options)
    if options["python_root"] == nil then
        error("Must pass root path to python installation!")
    end

    local python_root = options["python_root"]
    local python_lib_path = options["python_lib_path"]
    local python_lib_name = options["python_lib_name"]
    local python_version = options["python_version"]

    -- if the caller already passed the version, return that
    if python_version ~= nil then
        return python_version
    end

    -- if the caller gave us the lib name, deduce the version
    -- from the library
    if python_lib_name ~= nil then
        _, end_index = python_lib_name:find("python")
        return python_lib_name:sub(end_index + 1)
    end

    -- otherwise, attempt to find the python library
    -- in the python path and deduce the version from that
    -- on Windows, the python libraries are in the 'libs' directory
    -- on Linux, it's 'lib'
    if python_lib_path == nil then
    	if os.host() ~= "windows" then
            python_lib_path = python_root.."/lib"
        else
            python_lib_path = python_root.."/libs"
        end
    end

    if os.host() ~= "windows" then
        local python_libs = os.matchfiles(python_lib_path.."/*python*.so")
        if #python_libs > 0 then
            -- linux python has two .so files, one for libpython3 and
            -- one for the specific version of python (e.g., libpython3.10)
            -- we want the latter, so we will sort first based on longest
            -- otherwise we would have to rely on the order that the OS 
            -- returns the files in, which is non-deterministic
            table.sort(python_libs, function(a, b) return #a>#b end)
            python_lib_name = path.getbasename(python_libs[1])
            -- we also picked up the lib part, which we don't want
            python_lib_name = python_lib_name:sub(4, python_lib_name:len())
            if python_version == nil then
                _, end_index = python_lib_name:find("python")
                python_version = python_lib_name:sub(end_index + 1)
            end
        end
    else
        local python_libs = os.matchfiles(python_lib_path.."/python*.lib")
        if #python_libs > 0 then
            -- windows python has two .lib files, one for python3 and
            -- one for the specific version of python (e.g., python310)
            -- we want the latter, so we will sort first based on longest
            -- otherwise we would rely on the order that the OS returns the
            -- files in, which is non-deterministic
            table.sort(python_libs, function(a, b) return #a>#b end)
            python_major_version_lib_name = path.getbasename(python_libs[#python_libs])
            _, end_index = python_major_version_lib_name:find("python")
            python_major_version = python_major_version_lib_name:sub(end_index + 1)
            python_lib_name = path.getbasename(python_libs[1])
            if python_version == nil then
                _, end_index = python_lib_name:find("python")
                python_version = python_lib_name:sub(end_index + 1)
                _, end_index = python_version:find(python_major_version)
                python_minor_version = python_version:sub(end_index + 1)
                python_version = python_major_version.."."..python_minor_version
            end
        end
    end

    -- if we didn't auto deduce a version, let the caller know
    if python_version == nil then
        error("Could not automatically deduce python version!")
    end

    return python_version
end

-- Includes the use of python in the current scope.
-- Arguments:
--   options: A dictionary of options:
--     python_root: (Required) The path to the root of the python installation
--     python_version: (Optional) A string indicating the version of the python installation referenced
--                     Defaults to "3.10" if not specified.
--     python_include_path: (Optional) The path to the include directory for a python installation
--     python_lib_path: (Optional) The path the library directory for a python installation
--     python_lib_name: (Optional) The name of the library for a python installation that will be linked against
--
-- Returns: The python version detected.
--
-- Remarks: This method embeds python includes via `externalincludedirs` rather than `includedirs`
--          In this way we optimize checks on if the python files have changed with the caveat
--          that if you are working via packman and update the version you must make sure you
--          rebuild the scope rather than expecting it to pick up those changes to force a standard
--          build.
--
--          The optional python_* arguments can be set to help determine particular components of a python
--          installation. These are typically used for python installations that might not have standard naming
--          or path conventions.
--
function m.use_python(options)
    if options["python_root"] == nil then
        error("'python_root' option not found!  Must pass root path to python installation!")
    end

    local python_root = options["python_root"]
    local python_version = options["python_version"]
    local python_include_path = options["python_include_path"]
    local python_lib_path = options["python_lib_path"]
    local python_lib_name = options["python_lib_name"]

    local replaced_path = python_root:gsub("%%{cfg.buildcfg}", "release")
    if python_include_path == nil then
        if os.host() ~= "windows" then
            local python_include_paths = os.matchdirs(replaced_path.."/include/python*")
            if #python_include_paths > 0 then
                python_include_path = python_include_paths[1]

                -- strip off the part of the path we knew about so
                -- we can replace it with the original python_root
                start_index, end_index = python_include_path:find("/include/python")
                found_suffix = python_include_path:sub(start_index)
                python_include_path = python_root..found_suffix
            end
        else
            python_include_path = python_root.."/include"
        end
    end

    if python_lib_path == nil then
    	if os.host() ~= "windows" then
            python_lib_path = python_root.."/lib"
        else
            python_lib_path = python_root.."/libs"
        end
    end

    if python_lib_name == nil then
    	if os.host() ~= "windows" then
            local python_libs = os.matchfiles(python_lib_path.."/*python*.so")
            if #python_libs > 0 then
                -- linux python has two .so files, one for libpython3 and
                -- one for the specific version of python (e.g., libpython3.10)
                -- we want the latter, so we will sort first based on longest
                -- otherwise we rely on the order that the OS returns the
                -- files in, which is non-deterministic
                table.sort(python_libs, function(a, b) return #a>#b end)
                python_lib_name = path.getbasename(python_libs[1])
                -- we also picked up the lib part, which we don't want
                python_lib_name = python_lib_name:sub(4, python_lib_name:len())
                if python_version == nil then
                    _, end_index = python_lib_name:find("python")
                    python_version = python_lib_name:sub(end_index + 1)
                end
            end
        else
            local python_libs = os.matchfiles(python_lib_path.."/python*.lib")
            if #python_libs > 0 then
                -- windows python has two .lib files, one for python3 and
                -- one for the specific version of python (e.g., python310)
                -- we want the latter, so we will sort first based on longest
                -- otherwise we rely on the order that the OS returns the
                -- files in, which is non-deterministic
                table.sort(python_libs, function(a, b) return #a>#b end)
                python_lib_name = path.getbasename(python_libs[1])
                if python_version == nil then
                    _, end_index = python_lib_name:find("python")
                    python_version = python_lib_name:sub(end_index + 1)
                end
            end
    	end
    end

    filter { "system:windows" }
        externalincludedirs { python_include_path }
        syslibdirs { python_lib_path }
        links { python_lib_name }
    filter { "system:linux or macosx" }
        externalincludedirs { python_include_path }
        libdirs { python_lib_path }
        linkoptions { "-Wl,-rpath="..python_lib_path }
        links { python_lib_name }
    filter {}

    return python_version
end

-- Retrieves the resolved usd lib names given a non-empty prefix.
--
-- Args:
--   lib_prefix: A string (possibly empty) that specified the
--                   prefix to add onto the base name of each usd library
--                   in the usd_libs table.
--   usd_libs: A table of base names (e.g. tf, arch, etc.) of USD libraries
--             the plugin is dependent on.
--
function m.resolve_usd_lib_names(lib_prefix, usd_libs)
    local out = {}
    for i,x in ipairs(usd_libs) do
        out[i] = lib_prefix..x
    end

    return out
end

-- Retrieves the USD library prefix being used in a USD build, if any.
--
-- Args:
--  usd_lib_path: The path to the USD library directory.
--  base_library_name: The name of the library that will be used to locate the prefix.
--
-- Returns:
--   The USD library prefix being used in the USD build, or nil if the base library
--   was not found.  An empty string will be returned if the library is found, but no
--   prefix is detected.
--
function m._get_usd_lib_prefix(usd_lib_path, base_library_name)
    if usd_lib_path == nil or base_library_name == nil then
        error("Must supply a valid path and base_library_name!")
    end

    usd_lib_prefix = nil
    usd_libraries = os.matchfiles(usd_lib_path.."/*"..base_library_name..".*")
    if #usd_libraries > 0 then
        -- sort the results by length
        -- and use the first one
        table.sort(usd_libraries)
        usd_library = path.getbasename(usd_libraries[1])
        usd_lib_prefix = usd_library:sub(1, usd_library:len() - base_library_name:len())
        if os.host() ~= "windows" then
            -- we also picked up the lib part, which we don't want
            usd_lib_prefix = usd_lib_prefix:sub(4, usd_lib_prefix:len())
        end
    end

    return usd_lib_prefix
end

-- Retrieves information about the USD build being used.
--
-- Args:
--   usd_root: (Required) The path to the root of the USD build.  This path
--             may include the %{cfg.buildcfg} token to generalize among configurations.
--
-- Returns: A tuple containing the following:
--   A boolean indicating whether the USD build being used provides the monolithic library or not
--   The USD library prefix being used (if any, e.g., `usd_`)
--
function m._get_usd_library_info(usd_root)
    if usd_root == nil then
        error("The root path to the USD build must be supplied in `usd_root`!")
    end

    usd_lib_prefix = nil
    is_monolithic = false
    if usd_root:find("%%{cfg.buildcfg}") ~= nil then
        -- generalized configuration, could be looking at either a release
        -- or debug dependency
        replaced_path = usd_root:gsub("%%{cfg.buildcfg}", "release")
        
        -- try to find out what the USD prefix is by looking for a known
        -- non-monolithic USD library name with a longer name
        -- if we don't find one, try the monolithic case
        -- if we still don't find one, attempt to do the same thing
        -- in the debug dependency
        usd_lib_prefix = m._get_usd_lib_prefix(replaced_path.."/lib", "usdGeom")
        if usd_lib_prefix == nil then
            usd_lib_prefix = m._get_usd_lib_prefix(replaced_path.."/lib", "usd_ms")
            if usd_lib_prefix == nil then
                replaced_path = usd_root:gsub("%%{cfg.buildcfg}", "debug")
                usd_lib_prefix = m._get_usd_lib_prefix(replaced_path.."/lib", "usdGeom")
                if usd_lib_prefix == nil then
                    usd_lib_prefix = m._get_usd_lib_prefix(replaced_path.."/lib", "usd_ms")
                    if usd_lib_prefix ~= nil then
                        is_monolithic = true
                    end
                end
            else
                is_monolithic = true
            end
        end
    else
        usd_lib_prefix = m._get_usd_lib_prefix(usd_root.."/lib", "usdGeom")
        if usd_lib_prefix == nil then
            usd_lib_prefix = m._get_usd_lib_prefix(usd_root.."/lib", "usd_ms")
            if usd_lib_prefix ~= nil then
                is_monolithic = true
            end
        end
    end

    if usd_lib_prefix == nil then
        usd_lib_prefix = ""
    end

    return is_monolithic, usd_lib_prefix
end

-- Tries to find the monolithic library of USD given a root path to a USD installation
--
-- Args:
--   options: A dictionary of options
--      usd_root: (Required) The path to the root of the USD installation.  This path
--              may include the %{cfg.buildcfg} token to generaize among configuration
--              flavors.
--
-- Returns: A tuple containing the sanitized monolithic library name and any additional prefix, in that order
--
-- Remarks:
--    By "sanitized" the returned monolithic library name will not contain a platform-specific prefix (i.e libusd_ms)
--    or additional USD library prefix (i.e usd_usd_ms). For example:
--          (Linux) libusd_ms.so would result in "usd_ms", ""
--          (Linux) libusd_usd_ms.so would result in "usd_ms", "usd_"
--          (Windows) usd_ms.lib would result in "usd_ms", ""
--          (Windows) usd_usd_ms.lib would result in "usd_ms", "usd_"
function m.find_usd_monolithic(options)
    -- gather options
    if options["usd_root"] == nil then
        error("'usd_root' option not found!  Must pass root path to USD configuration!")
    end

    local usd_root = options["usd_root"]
    local library_name = nil
    local library_prefix = ""

    -- first try looking for the release build
    replaced_path = usd_root:gsub("%%{cfg.buildcfg}", "release")
    monolithic_libraries = os.matchfiles(replaced_path.."/lib/*usd_ms.*")
    if #monolithic_libraries > 0 then
        -- sort the results by length
        -- and use the first one
        table.sort(monolithic_libraries)
        library_name = path.getbasename(monolithic_libraries[1])
    else
        -- try debug
        replaced_path = usd_root:gsub("%%{cfg.buildcfg}", "debug")
        monolithic_libraries = os.matchfiles(replaced_path.."/lib/*usd_ms.*")
        if #monolithic_libraries > 0 then
            table.sort(monolithic_libraries)
            library_name = path.getbasename(monolithic_libraries[1])
        end
    end

    if os.host() ~= "windows" and library_name ~= nil then
        -- We picked up the library prefix from the file name (i.e libusd_ms.so)
        library_name = library_name:sub(4, library_name:len())
    end

    if library_name ~= nil then
        -- Sadly, there is no rfind in lua
        local start_index, _ = string.find(library_name, "usd_ms")
        if start_index > 1 then
            library_prefix = library_name:sub(1, start_index - 1)
        end
    end

    return library_name, library_prefix
end

-- Parses the build_info.json file and returns the build information.
--
-- Args:
--   build_info_file: The path to the build_info.json file.
--
-- Returns: A table containing the build information.
function m.get_usd_build_info(usd_root)
    if usd_root == nil then
        error("'usd_root' not provided!  Must pass root path to USD configuration!")
    end

    -- read the content of the file into a string
    -- then create a table from it using premake's json support
    replaced_path = usd_root:gsub("%%{cfg.buildcfg}", "release")
    build_info_file = os.matchfiles(replaced_path.."/BUILD_INFO/build_info.json")
    if #build_info_file > 0 then

        content = io.readfile(build_info_file[1])
        build_info_content, err = json.decode(content)
        if err == nil then
            return build_info_content
        end
    end

    -- didn't get it from the release build_info.json file
    -- try the debug build_info.json file
    replaced_path = usd_root:gsub("%%{cfg.buildcfg}", "debug")
    build_info_file = os.matchfiles(replaced_path.."/BUILD_INFO/build_info.json")
    if #build_info_file > 0 then

        content = io.readfile(build_info_file[1])
        build_info_content, err = json.decode(content)
        if err == nil then
            return build_info_content
        end
    end

    return nil
end

-- Determines the flavor of the USD build being used.
-- The flavor is a string identifier used to distinguish
-- between multiple vendors (e.g., "stock", "nv-usd", etc.).
--
-- To determine the flavor, we check to see if it's a
-- NVIDIA package, and if so, read the build_info.json
-- file to determine the flavor.
--
-- Returns: A string denoting the flavor if found or
--          nil if a flavor could not be determined.
function m.get_usd_flavor(usd_root)
    if usd_root == nil then
        error("'usd_root' not provided!  Must pass root path to USD configuration!")
    end

    -- attempt to find the build_info.json file
    local build_flavor = nil
    json_content = m.get_usd_build_info(usd_root)
    if json_content ~= nil and json_content["build_variant"] ~= nil and json_content["build_variant"]["name"] ~= nil then
        build_flavor = json_content["build_variant"]["name"]
    end

    -- map the build flavor "usdview" or "stock" to "usd" for stock builds
    -- to match command line selection
    if build_flavor == "usdview" or build_flavor == "stock" or build_flavor == "nousdview" then
        build_flavor = "usd"
    end

    return build_flavor
end

-- Determines the version of the USD build being used.
-- The version is a string identifier in the form x.y.
--
-- To determine the version, we check to see if it's a
-- NVIDIA package, and if so, read the build_info.json
-- file to determine the version.  Otherwise it will
-- attempt to read the pxr.h file to extract that information.
--
-- Args:
--  usd_root: The path to the root of the OpenUSD build being used.
--
-- Returns: A string denoting the version in the form x.y.
function m.get_usd_version(usd_root)
    if usd_root == nil then
        error("'usd_root' not provided!  Must pass root path to USD configuration!")
    end

    -- attempt to find the build_info.json file
    local version = nil
    json_content = m.get_usd_build_info(usd_root)
    if json_content ~= nil and json_content["usd_ver"] ~= nil then
        version = json_content["usd_ver"]

        -- strip off the 0. major
        return version:sub(3, version:len())
    end

    -- couldn't find a build_info.json file at all
    -- try via the release pxr.h file
    replaced_path = usd_root:gsub("%%{cfg.buildcfg}", "release")
    pxr_h_file = os.matchfiles(replaced_path.."/include/pxr/pxr.h")
    if #pxr_h_file > 0 then
        content = io.readfile(pxr_h_file[1])

        -- try to find the minor and patch version
        minor_first, minor_last = content:find("PXR_MINOR_VERSION")
        patch_first, patch_last = content:find("PXR_PATCH_VERSION")
        if minor_first ~= nil and patch_first ~= nil then
            minor_version = content:sub(minor_last + 1, 2)
            patch_version = content:sub(patch_last + 1, 2)
            patch_version = patch_version:gsub("[\n\r]", "")
            patch_value = to_number(patch_version)
            if patch_value ~= nil then
                if patch_value < 10 then
                    patch_version = "0"..patch_version
                end

                return minor_version.."."..patch_version
            end
        end
    end

    -- try via the debug pxr.h file
    replaced_path = usd_root:gsub("%%{cfg.buildcfg}", "debug")
    pxr_h_file = os.matchfiles(replaced_path.."/include/pxr/pxr.h")
    if #pxr_h_file > 0 then
        content = io.readfile(pxr_h_file[1])

        -- try to find the minor and patch version
        minor_first, minor_last = content:find("PXR_MINOR_VERSION")
        patch_first, patch_last = content:find("PXR_PATCH_VERSION")
        if minor_first ~= nil and patch_first ~= nil then
            minor_version = content:sub(minor_last + 1, 2)
            patch_version = content:sub(patch_last + 1, 2)
            patch_version = patch_version:gsub("[\n\r]", "")
            patch_value = to_number(patch_version)
            if patch_value ~= nil then
                if patch_value < 10 then
                    patch_version = "0"..patch_version
                end

                return minor_version.."."..patch_version
            end
        end
    end

    -- couldn't detect the version, just return nil
    return version
end

-- Includes the use of USD in the current scope.
--
-- We make a few assumptions about the USD structure provided:
-- 1. There are only debug and release configurations
-- 2. The debug and release configurations have the same structure beneath them.
--
-- Different users may have their directories structured differently for their USD
-- builds.  There are two primary ways we have to consider here:
-- 1. The configuration directory serves as part of the root itself - that is
--    the path to the USD structure is x/debug and x/release with the sub-structure
--    underneath the structure we need.
-- 2. The configuration directory is higher level than the USD sub-structure - that is
--    the path to the USD structure is debug/x and release/x with the sub-structure
--    underneath x the structure we need.
--
-- In both of these cases, the user can specify the usd root using the %{cfg.buildcfg}
-- premake token, meaning we only need one variable to capture the usd root.  We do
-- not support any structure that does not follow this convention, i.e., if the debug
-- and release directories are completely separated on disk with no way to specify
-- them in common - for those whatever directory is passed in usd_root will be used
-- no matter the configuration set for the project.
--
-- Note that if you use USD, you must also use python because of boost::python compilation
-- in the USD headers.  For this reason, you must include the required options to
-- the use_python method in addition to those specifically required by this method.
-- 
-- Arguments:
-- options: A dictionary of options:
--   usd_root: (Required) The path to the root of the USD installation.  This path
--             may include the %{cfg.buildcfg} token to generaize among configuration
--             flavors.
--   usd_lib_prefix: (Optional) The prefix to use on all linked usd libraries.
--             e.g., "usd_".  If not specified, the system will attempt to determine
--             the prefix automatically.
--   usd_suppress_warnings: (Optional) A boolean denoting whether or not to suppress warnings
--             when compiling USD headers.  If this is true, it will suppress the warnings
--             for all "external" includes, which we define USD as.
--   boost_include_path: (Optional) The path to the boost headers to use during compilation.
--             If this is not provided, this method will default to attempting to locate
--             the appropriate boost include folder in the usd_root path provided.
--   boost_python_prefix: (Optional) The prefix that will be used to search for the boost_python library name
--             If this is provided, boost_python will be explicitly linked by searching for the boost_python
--             library name. When found, the library name will be used.
--
--             Note that if you have both release and debug boost_python libraries within the same
--             folder, you can set boost_python_prefix to a table that contains different prefixes
--             eg. boost_python_prefix = { release = "boost_python", debug = "boost_python_debug" }
--   python_root: (Optional) The path to the root of the python installation
--             If this is not provided, we assume that USD is built without Python support
--             and Python, or boost_python, will not be included or linked
--   python_version: (Optional) A string indicating the version of the python installation referenced
--             Defaults to "3.10" if not specified.
--   no_set_cxx11_flag: (Optional) A boolean denoting whether the templates will set the flag to enable
--              the cxx11 ABI or not.
--
-- usd_libs: (Required) The list of USD libraries your project needs to link to.
--             These are unprefixed names (e.g., tf, work, usd, etc.)
-- 
-- Remarks: This method embeds USD includes via `externalincludedirs` rather than `includedirs`
--          In this way we optimize checks on if the USd files have changed with the caveat
--          that if you are working via packman and update the version you must make sure you
--          rebuild the scope rather than expecting it to pick up those changes to force a standard
--          build.
--
--          Ordering of library dependencies is important on Linux.  This method will order the
--          links statement in the following way:
--             - USD libraries
--             - boost_python (if python is being used)
--             - python (if python is being used)
--          
--          Note that there may be some dependency ordering in the libraries passed in usd_libs.
--          It is up to the caller to order these appropriately.
--
function m.use_usd(options, usd_libs)

    -- gather options
    if options["usd_root"] == nil then
        error("'usd_root' option not found!  Must pass root path to USD configuration!")
    end

    if usd_libs == nil then
        error("'usd_libs' options not found!  Must pass list of USD libs to link (without prefix)!")
    end

    local usd_root = options["usd_root"]
    local usd_ver = m.get_usd_version(usd_root)
    local usd_suppress_warnings = false
    if options["usd_suppress_warnings"] ~= nil then
        usd_suppress_warnings = options["usd_suppress_warnings"]
    end

    if options["no_set_cxx11_flag"] ~= nil then
        usd_no_set_cxx11_flag = options["no_set_cxx11_flag"]
    end

    -- do we have an explicitly defined USD prefix?
    -- if so, use that - if not, attempt to dynamically determine
    -- what it is
    is_monolithic, usd_lib_prefix = m._get_usd_library_info(usd_root)
    if options["usd_lib_prefix"] ~= nil then
        usd_lib_prefix = options["usd_lib_prefix"]
    end

    -- do we have the boost include folder explicitly or do we need to
    -- try and determine it automatically?  If we have to figure it out
    -- dynamically (the majority of cases), we have to replace any
    -- %{cfg.buildcfg} tokens provided in the usd_root option
    if options["boost_include_path"] == nil then
        -- since we assume each configuration is a mirrored
        -- sub-structure, we can use the release path to acquire
        -- the boost include dir
        replaced_path = usd_root:gsub("%%{cfg.buildcfg}", "release")
        boost_include_paths = os.matchdirs(replaced_path.."/include/boost*")
        if #boost_include_paths > 0 then
            boost_include_path = boost_include_paths[1]
            boost_include_path = boost_include_path:gsub("release", "%%{cfg.buildcfg}")
        else
            -- try debug
            replaced_path = usd_root:gsub("%%{cfg.buildcfg}", "debug")
            boost_include_paths = os.matchdirs(replaced_path.."/include/boost*")
            if #boost_include_paths > 0 then
                boost_include_path = boost_include_paths[1]
                boost_include_path = boost_include_path:gsub("debug", "%%{cfg.buildcfg}")
            end
        end

        -- if we still don't have a boost_include_path (i.e Houdini where it's hboost/...)
        -- we'll set it to the usd root include path. Otherwise, subsequent checks would need to be made
        -- or run into errors with boost_include_path being nil
        boost_include_path = boost_include_path or usd_root.."/include"
    else
        boost_include_path = options["boost_include_path"]
    end

    -- common options
    -- RTTI and exceptionhandling must be on to use USD
    rtti("On")
    exceptionhandling("On")

    -- USD and boost includes are brought in as "externalincludes"
    -- this is to suppress the warnings if the user desires
    externalincludedirs { usd_root.."/include" }
    if usd_ver < "24.11" then
        externalincludedirs { boost_include_path }
    end

    -- USD library directory
    libdirs { usd_root.."/lib" }

    filter { "system:windows" }
        -- preprocessor defines
        defines { "NOMINMAX" }
        if m.get_usd_version(usd_root) < "24.11" then
            defines { "BOOST_ALL_DYN_LINK" }
        end
    filter {}

    -- if it's an nv-usd flavor, define NV_USD
    usd_flavor = m.get_usd_flavor(usd_root)
    if usd_flavor == "nv-usd" then
        defines { "NV_USD" }
    end

    local usd_ver = m.get_usd_version(usd_root)
    if usd_ver == "24.05" then
        defines { "NV_HYDRA" }
    else
        print("Skip definition of NV_HYDRA for OpenUSD version "..usd_ver)
    end

    -- if we have a build_info.json file, we might be to determine
    -- if USD was built with C++11 ABI compatibility
    usd_build_info = m.get_usd_build_info(usd_root)
    if usd_build_info ~= nil  and usd_no_set_cxx11_flag then
        -- the build of USD is coming from usd-ci, which means we might have
        -- more information if USD was built with the new C++11 ABI. The use_cxx11_abi
        -- arg was added to build_info.json fairly late so there could be lots of builds
        -- that don't have this information. For these older builds we assume the old C++11 ABI
        -- on x86_64 and the new C++11 ABI on aarch64
        if usd_build_info["build_variant"] ~= nil then 
            if usd_build_info["build_variant"]["use_cxx11_abi"] ~= nil then
                use_cxx11_abi = usd_build_info["build_variant"]["use_cxx11_abi"]

                filter { "system:linux" }
                    defines { "_GLIBCXX_USE_CXX11_ABI="..tostring(use_cxx11_abi and 1 or 0) }
                filter {}
            else
                filter { "system:linux" }
                    filter {"platforms:x86_64"}
                        defines { "_GLIBCXX_USE_CXX11_ABI=0" }
                    filter {"platforms:aarch64"}
                        defines { "_GLIBCXX_USE_CXX11_ABI=1" }
                    filter {}
                filter {}
            end
        end
    end

    if options["python_root"] ~= nil then
        -- deduce the version of python we are using
        local python_version = m.get_python_version(options)

        if usd_ver < "24.11" then
            -- do we have a boost_python prefix that we need to look for to link?
            -- Most of the time, linking boost_python should be as simple as
            -- links {"boost_python"..python_version } (Linux) or defines {"BOOST_ALL_DYN_LINK"} (Windows)
            -- But there are some situations where linking boost_python is not that straight-forward.
            -- For example, Houdini prefixes all compiled boost libraries with "hboost" or boost_python was
            -- compiled with an older msvc toolset (e.g vc141) and includes that metadata in the library name
            -- So in these situations we'll try to find the boost_python library name from a supplied prefix
            local boost_python_prefix = options["boost_python_prefix"]
            if boost_python_prefix ~= nil then

                local boost_python_release_prefix = boost_python_prefix
                local boost_python_debug_prefix = boost_python_prefix
                if type(boost_python_prefix) == "table" then
                    boost_python_release_prefix = boost_python_prefix["release"]
                    boost_python_debug_prefix = boost_python_prefix["debug"]
                end

                -- Look for the release boost_python library
                replaced_path = usd_root:gsub("%%{cfg.buildcfg}", "release")
                boost_python_lib_paths = os.matchfiles(replaced_path.."/lib/"..boost_python_release_prefix.."*")
                if #boost_python_lib_paths > 0 then
                    table.sort(boost_python_lib_paths)
                    local boost_python_lib_name = path.getbasename(boost_python_lib_paths[1])
                    if os.host() ~= "windows" then
                        -- we picked up the platform-specific prefix which we don't want
                        boost_python_lib_name = boost_python_lib_name:sub(4, boost_python_lib_name:len())
                    end
                    filter { "system:windows" }
                        -- avoid automatically linking boost_python as this will issue errors
                        defines { "BOOST_PYTHON_NO_LIB" }
                    filter { "configurations:release" }
                        links { boost_python_lib_name }
                    filter {}
                end

                -- Also look for the debug boost_python library as the library names can be
                -- different between configurations (Windows)
                replaced_path = usd_root:gsub("%%{cfg.buildcfg}", "debug")
                boost_python_lib_paths = os.matchfiles(replaced_path.."/lib/"..boost_python_debug_prefix.."*")
                if #boost_python_lib_paths > 0 then
                    table.sort(boost_python_lib_paths)
                    local boost_python_lib_name = path.getbasename(boost_python_lib_paths[1])
                    if os.host() ~= "windows" then
                        -- we picked up the platform-specific prefix which we don't want
                        boost_python_lib_name = boost_python_lib_name:sub(4, boost_python_lib_name:len())
                    end
                    filter { "system:windows" }
                        -- avoid automatically linking boost_python as this will issue errors
                        defines { "BOOST_PYTHON_NO_LIB" }
                    filter { "configurations:debug" }
                        links { boost_python_lib_name }
                    filter {}
                end
            else
                -- Use the default behavior for linking boost_python
                -- Windows will automatically link based on build configuration metadata
                -- Linux is simply linked by concatenating the python_version
                filter { "system:linux or macosx" }
                    links { "boost_python"..python_version:gsub("%.", "") }
                filter {}
            end
        else
            links(m.resolve_usd_lib_names(usd_lib_prefix, { "python" }))
        end

        -- add the Python includes / libs
        m.use_python(options)
    end

    -- Work around https://github.com/intel/tbb/issues/154
    filter { "system:windows", "configurations:debug" }
        defines {"TBB_USE_DEBUG=1"}
    filter { "system:windows", "configurations:release" }
        defines {"TBB_USE_DEBUG=0"}
    filter {}

    -- link usd libs
    if is_monolithic then
        links(usd_lib_prefix.."usd_ms")
    else
        local resolved_usd_libs = m.resolve_usd_lib_names(usd_lib_prefix, usd_libs)
        links(resolved_usd_libs)
    end

    -- handle warning suppression
    if usd_suppress_warnings then
        filter { "system:windows" }
            -- this works for VS2022 and up, premake does not support this on VS2019
            -- even though it is supported as of 16.10
            externalwarnings("Off")

            -- for VS2019 and below, we also set the /external:I flag
            buildoptions {
                "/external:W0",
                "/external:I"..usd_root.."/include",
            }
            if usd_ver < "24.11" then
                buildoptions {
                    "/external:I"..boost_include_path
                }
            end
            -- Warnings when including nearly any USD header
            -- disablewarnings {
            --     "4003", -- (warning C4003: not enough arguments for function-like macro re: boost)
            --     "4100", -- unreferenced formal parameter
            --     "4005", -- Hide hundreds of warnings about NOMINMAX redfinition
            --     "4127", -- conditional expression is constant
            --     "4201", -- nonstandard extension used: nameless struct/union
            --     "4305", -- (warning C4305: truncation from 'double' to 'float')
            --     "4244", -- (warning C4244: conversion from 'double' to 'float')
            --     "4267", -- (warning C4267: 'return': conversion from 'size_t' to 'int')
            --     "4996", -- (warning C4996: deprecated symbols)
            -- }
        filter {}
    end

    -- The v142 toolset (and later) strips out the "arch_ctor_<name>"
    -- symbols with /Zc:inline, so all USD based tools need to build with
    -- /Zc:inline- if they deal with arch or tf
    -- this is controlled by the premake option removeunreferencedcodedata
    -- which defaults to on (/Zc:inline) if not set
    filter { "toolset:msc-v142" }
        removeunreferencedcodedata("off")
    filter {}
end

-- Enables the preprocessor defines in the current scope necessary to build USD-plugin python modules.
--
-- Args:
--   name: The name of the USD plug-in.
--   module_name: The name of the python module that will be compiled for the USD plug-in.
--
function m.use_usd_python_modules(name, module_name)

    if name == nil then
        error("Must provide a library name for the USD plug-in to build python modules!")
    end

    if module_name == nil then
        error("Must provide a python module name for the USD plug-in to build python modules!")
    end

    defines {
        "PXR_PYTHON_ENABLED=1",
        "PXR_PYTHON_MODULES_ENABLED=1",
        "MFB_PACKAGE_NAME="..name,
        "MFB_ALT_PACKAGE_NAME="..name,
        "MFB_PACKAGE_MODULE="..module_name
    }
end

return m
