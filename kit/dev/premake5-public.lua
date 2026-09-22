------------------------------------------------------------------------------------------------------------------------
------------------                                 Overview                                           ------------------
------------------------------------------------------------------------------------------------------------------------

-- This file defines common variables, functions, project templates to be used both inside Kit SDK projects and outside.
-- External repos can include that file, redefine some variables and use common functions.
-- To enable redefining global variables "x = x or something" pattern used everywhere. Thus defining a variable before
-- including that file will override them.


------------------------------------------------------------------------------------------------------------------------
------------------                              premake Options                                       ------------------
------------------------------------------------------------------------------------------------------------------------

newoption {
    trigger     = "generate-ext-projects",
    description = "(Optional) Generate utility VS project for each extension. They are not used for compilation, but only contain python, configs, docs files for convenience."
}

newoption {
    trigger     = "platform-host",
    description = "(Optional) Specify host platform for cross-compilation"
}

newoption {
    trigger     = "platform-target",
    description = "(Optional) Specify target platform for cross-compilation"
}

------------------------------------------------------------------------------------------------------------------------
------------------                              omni.repo.build                                       ------------------
------------------------------------------------------------------------------------------------------------------------

-- Shared build scripts from repo_build package, explicit path:
repo_build = repo_build or require("_repo/deps/repo_build/lua/omni/repo/build")

-- Enable /sourcelink flag for VS
repo_build.enable_vstudio_sourcelink()

-- Remove /JMC parameter for visual studio
repo_build.remove_vstudio_jmc()


------------------------------------------------------------------------------------------------------------------------
------------------                              Common Variables                                      ------------------
------------------------------------------------------------------------------------------------------------------------

-- C++17 is the minimum standard Carbonite supports
CPP_DIALECT = CPP_DIALECT or "C++17"

-- This will likely change when the msvc version changes
-- It must match the directroy `VC/Tools/MSVC` in the msvc package in host-deps.packman.xml
MSVC_VERSION = MSVC_VERSION or "14.29.30133"

-- Version of MSBuild in use
MSBUILD_VERSION = MSBUILD_VERSION or "15.0"

-- Version of the Windows SDK in use
WINSDK_VERSION = WINSDK_VERSION or "10.0.19041.0"

local current_file_dir = repo_build.get_abs_path(".")

-- Repo root
root = root or current_file_dir

-- Target platform name, e.g. windows-x86_64
platform = platform or "%{cfg.system}-%{cfg.platform}"

-- Host and target platform name, e.g. windows-x86_64
platform_host = platform_host or _OPTIONS["platform-host"] or platform;
platform_target = platform_target or _OPTIONS["platform-target"] or platform;

-- Target config, e.g. debug, release
config = config or "%{cfg.buildcfg}"

-- Constant with all configurations we build
ALL_CONFIGS = ALL_CONFIGS or { "debug", "release" }

-- Folder to store solution in. _ACTION is compilation target, e.g.: vs2017, make etc.
workspace_dir = workspace_dir or "%{root}/_compiler/".._ACTION

-- Various commonly used repo paths:
build_dir = build_dir or "%{root}/_build"
target_deps = target_deps or build_dir.."/target-deps"
host_deps = host_deps or build_dir.."/host-deps"
bin_dir = bin_dir or build_dir.."/%{platform}/%{config}"
exts_dir = exts_dir or bin_dir.."/exts"
extscache_dir = extscache_dir or bin_dir.."/extscache"

-- Kit SDK config
kit_sdk_config = kit_sdk_config or "%{config}"

-- Former way of locating Kit build files, including the gsl/ package. Replaced with kit_dev_dir. Normally the variable
-- is defined here. This warning catches any cases where apps have redefined it. It can be deleted in Kit 106.
if kit_target_deps then
    premake.warn("kit_target_deps is no longer supported in the Kit build. Use kit_dev_dir instead.")
end

-- If this file is consumed from kit-sdk package fs structure is a bit different. Folders like ${root}/include, moved to
-- ${root}/_build/$platform/$config/dev/include . And ${root}/_build/$platform/$config is package root. We autodetect it by
-- looking at parent folder name for user convenience.
is_packaged_sdk = path.getname(current_file_dir) == "dev"
if is_packaged_sdk then
    -- Kit SDK folder. For external repo they need to specify where they linked kit in. We provide recommended default.
    kit_sdk = kit_sdk or "%{root}/_build/%{platform}/%{config}/kit"

    -- "dev" folder is where current file is. Root for local build and "dev" folder Kit SDK package. It is used for
    -- build-time paths, like `include`, `deps` folders etc.
    kit_dev_dir = kit_dev_dir or kit_sdk.."/dev"

    -- Bin folder is where kit executable is. For external repo it is kit sdk root.
    kit_sdk_bin_dir = kit_sdk_bin_dir or kit_sdk

    -- OGN helpers are in the Kit package
    ogn_helper_path = ogn_helper_path or kit_dev_dir.."/ogn/ogn_helpers.lua"

    -- There are no extensions in kit-kernel package, just check for one well known in /exts
    is_packaged_kernel = not os.isdir(current_file_dir.."/../exts/omni.graph.tools")

    -- premake templates exist parallel to this file
    usd_module = require("premake5-usd")
else
    -- Kit SDK folder. For local build it is root.
    kit_sdk = kit_sdk or root

    -- "dev" folder is where current file is. Root for local build and "dev" folder Kit SDK package. It is used for
    -- build-time paths, like `include`, `deps` folders etc.
    kit_dev_dir = kit_dev_dir or "%{root}/_build/%{platform}/"..kit_sdk_config.."/dev"

    -- Bin folder is where kit executable is. For local build it is in platform/config specific subfolders.
    kit_sdk_bin_dir = kit_sdk_bin_dir or build_dir.."/%{platform}/"..kit_sdk_config

    -- OGN helpers are pulled from the source tree so that they can be used by every extension's premake file
    ogn_helper_path = ogn_helper_path or current_file_dir.."/source/extensions/omni.graph.tools/ogn_helpers.lua"

    is_packaged_kernel = false

    -- premake templates are pulled from usd directory (copied into dev for distribution)
    usd_module = require(current_file_dir.."/../usd/premake/premake5-usd")
end

if is_packaged_kernel then
    extsbuild_dir = extsbuild_dir or bin_dir.."/extsbuild"
else
    extsbuild_dir = extsbuild_dir or kit_sdk_bin_dir.."/exts"
end

-- Location of the omni.bind tool
omni_bind_path = omni_bind_path or "_build/target-deps/carb_sdk_plugins/tools/omni.bind/omni.bind.lua"

-- Define the canonical way to call the Kit version of Python
if os.target() == "windows" then
    -- Windows custom build tools merge everything together into one script so the Python batch file
    -- has to be "called" or it will only run the first one.
    pythonScriptPath = "call "..kit_dev_dir.."/tools/packman/python.bat"
else
    -- path.getabsolute gives the realpath rather than the symbolic path in linux
    pythonScriptPath = kit_dev_dir.."/tools/packman/python.sh"
end

-- By default include licenses from root into each extension. Can be overriden and controlled per extension too.
PROJECT_EXT_INCLUDE_ROOT_LICENSES_DEFAULT = true

-- Backward compatibility switch, to be removed
PROJECT_EXT_AUTOLINK_EXTENSIONS_TARGET_FOLDER = true

-- Template Used to generate all the kit.bat, test.bat and other batch/shell files
-- format are: bin_relative, executable, config_path, extra_args
KIT_RUNNER_SHELL_TEMPLATE = KIT_RUNNER_SHELL_TEMPLATE or {
    ["windows"] = [[
@echo off
setlocal
call "%%~dp0%s\%s" %s %s %%*
]],
    ["linux"] = [[
#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
if [ ! -z "$OMNI_KIT_LD_PRELOAD" ]; then
    export LD_PRELOAD="$OMNI_KIT_LD_PRELOAD:$LD_PRELOAD"
fi
if [ "$_MR_BUILD_WITH_ASAN" == "true" ]; then
    export LIB_ASAN_PATH=$SCRIPT_DIR/libasan.so.6
    export ASAN_OPTIONS="protect_shadow_gap=0:halt_on_error=0:detect_leaks=1"
    export LSAN_OPTIONS="exitcode=0"
    if [ "$LD_PRELOAD" != *"libasan.so"* ]; then
        export LD_PRELOAD="${LIB_ASAN_PATH}${LD_PRELOAD:+:$LD_PRELOAD}"
    fi
    echo "ASAN_OPTIONS=${ASAN_OPTIONS}"
    echo "LSAN_OPTIONS=${LSAN_OPTIONS}"
    echo "LIB_ASAN_PATH=${LIB_ASAN_PATH}"
    echo "LD_PRELOAD=${LD_PRELOAD}"
fi
${EXEC:-exec} "$SCRIPT_DIR/%s/%s" %s %s "$@"
]],
    ["macosx"] = [[
#!/bin/bash
set -e
SCRIPT_DIR=$(dirname ${BASH_SOURCE})
exec "$SCRIPT_DIR/%s/%s" %s %s "$@"
]],
}

-- Test suite name to use by default when generating projects like `tests-[suite]-omni.foo`
EXT_TEST_TEST_SUITE_DEFAULT = "python"

------------------------------------------------------------------------------------------------------------------------
------------------                           Common Helper Functions                                  ------------------
------------------------------------------------------------------------------------------------------------------------

-- Returns absolute path to folder where currently executed premake lua file is located.
function get_current_lua_file_dir()
    return path.getabsolute(".")
end

-- Returns folder name where currently executed premake lua file is located.
function get_current_dir_name()
    return path.getname(get_current_lua_file_dir())
end

-- Based on current folder return a tuple: (ext_name, ext_tag). E.g. "omni.renderer-ui" -> ("omni.renderer", "ui")
function get_current_extension_name_and_tag()
    local folder = get_current_dir_name()
    if string.match(folder, "-") then
        return table.unpack(repo_build.split(folder, "-"))
    else
        return folder, ""
    end
end

-- Build extension id out of name and tag
function get_extension_id(ext_name, ext_tag)
    local ext_id = ext_name
    if ext_tag ~= "" then
        ext_id = ext_id.."-"..ext_tag
    end
    return ext_id
end

-- Get a table of default paths and info (id, name, tag etc.) for current extension.
function get_current_extension_info()
    local ext = {}

    -- Basics
    ext.name, ext.tag = get_current_extension_name_and_tag()
    ext.id = get_extension_id(ext.name, ext.tag)

    -- Target directory where extension is built into
    ext.target_dir = exts_dir.."/"..ext.id

    -- Typical folder where binaries of extension go into
    ext.bin_dir = ext.target_dir.."/bin"

    -- Project group (for VS)
    ext.group = "extensions"

    return ext
end

-- Get table value by key or default
function get_value_or_default(table, key, default)
    if table[key] ~= nil then
        return table[key]
    end
    return default
end

-- Merge table2 into table1
function merge_tables(table1, table2)
    for k,v in pairs(table2) do table1[k] = v end
    return table1
end

-- Concat array1 + array2
function concat_arrays(array1, array2)
    for _, v in pairs(array2) do table.insert(array1, v) end
    return array1
end

-- String formatting with interpolation, e.g.: string_fmt_vars("${a}+%{b}", {a=2, b=3}) => "2+3"
-- both ${} and %{} syntax support
function string_fmt_vars(str, vars)
    return (str:gsub('([$%%]%b{})', function(w) return vars[w:sub(3, -2)] or w end))
end

-- String formatting with interpolation multiple times for recursive subsituition,
-- e.g.: string_fmt_vars_recursive("${a}", {a="${b}", b=3}) => "3"
function string_fmt_vars_recursive(str, vars)
    local s0 = str
    for i=1,16 do
        local s1 = string_fmt_vars(s0, vars)
        if s0 == s1 then break end
        s0 = s1
    end
    return s0
end

function is_string_empty(s)
    return s == nil or s == ''
end

function link_boost_for_windows(libs)
    defines { "BOOST_ALL_NO_LIB", "BOOST_ALL_DYN_LINK" }

    filter { "system:windows", "configurations:debug" }
        for _, l in ipairs(libs) do
            links { l.."-vc142-mt-gd-x64-1_82"}
        end

    filter { "system:windows", "configurations:release" }
        for _, l in ipairs(libs) do
            links { l.."-vc142-mt-x64-1_82"}
        end

    filter {}
end

-- Pull in omni.bind code generator
if os.isfile(omni_bind_path) then
    dofile(omni_bind_path)
end

-- Pull in OGN code generator
if os.isfile(ogn_helper_path) then
    dofile(ogn_helper_path)
end

-- Write experience running .bat/.sh file, like _build\windows-x86_64\release\example.helloext.app.bat
function create_experience_runner(name, config_path, config, kit_sdk_config, extra_args, executable)
    local os_target = os.target()
    if os_target == "windows" then
        local executable = executable or "kit.exe"
        local bat_file_dir = root.."/_build/windows-x86_64/"..config
        local bat_file_path = bat_file_dir.."/"..name..".bat"
        local kit_bin_abs = string_fmt_vars_recursive(kit_sdk_bin_dir, {
            root=root, config=config, kit_sdk=kit_sdk, kit_sdk_config=kit_sdk_config, platform="windows-x86_64"
        })
        local kit_bin_relative = path.normalize(path.getrelative(bat_file_dir, kit_bin_abs)):gsub("/", "\\")
        local config_path = (is_string_empty(config_path) and "") or "\"%%~dp0"..config_path.."\""
        local f = io.open(bat_file_path, 'w')
        f:write(string.format(KIT_RUNNER_SHELL_TEMPLATE[os_target], kit_bin_relative, executable, config_path, extra_args))
        f:close()
    else
        local exe = "kit"
        if _OPTIONS["enable-gcov"] then
            exe = "kit-gcov"
        end
        local executable = executable or exe

        -- platform-target is preferred, but repo_build doesn't always pass this.
        -- use platform-host as a fallback
        local platform = _OPTIONS["platform-target"] or platform_host or _OPTIONS["platform-host"]
        if platform == nil then
            error("--platform-target, --platform-host or platform_host must be specified")
        end

        local sh_file_dir = root.."/_build/"..platform.."/"..config
        local sh_file_path = sh_file_dir.."/"..name..".sh"
        local kit_bin_abs = string_fmt_vars_recursive(kit_sdk_bin_dir, {
            root=root, config=config, kit_sdk=kit_sdk, kit_sdk_config=kit_sdk_config, platform=platform
        })
        local kit_bin_relative = path.normalize(path.getrelative(sh_file_dir, kit_bin_abs))
        local config_path = (is_string_empty(config_path) and "") or "\"$SCRIPT_DIR/"..config_path.."\""
        local f = io.open(sh_file_path, 'w')
        f:write(string.format(KIT_RUNNER_SHELL_TEMPLATE[os_target], kit_bin_relative, executable, config_path, extra_args))
        f:close()
        os.chmod(sh_file_path, 755)
    end
end

-- Define Kit experience. Different ways to run kit with particular config
function define_experience(name, args)
    local args = args or {}
    local experience = args.experience or name..".json"
    local config_path = get_value_or_default(args, "config_path", "experiences/"..experience)
    local extra_args = args.extra_args or ""
    local define_project = get_value_or_default(args, "define_project", true)

    -- Create a VS project on windows to make debugging and running from VS easier:
    if os.target() == "windows" and define_project then
        group "apps"
        project(name)
            kind "Utility"
            location ("%{root}/_compiler/".._ACTION.."/%{prj.name}")
            debugcommand ("%{kit_sdk_bin_dir}/kit.exe")
            debugdir ("%{bin_dir}")
            if config_path == "" then
                debugargs (extra_args)
            else
                local config_abs_path = bin_dir.."/"..config_path
                debugargs ("\""..config_abs_path.."\" "..extra_args)
                files { config_abs_path }
            end
            vpaths { [""] = "**.json" }
        dependson { "kit" }
    end

    -- Write bat and sh files as another way to run them:
    for _, config in ipairs(ALL_CONFIGS) do
        local kit_sdk_config = get_value_or_default(args, "kit_sdk_config", kit_sdk_config)
        if kit_sdk_config == "%{config}" then
            kit_sdk_config = config
        end
        create_experience_runner(name, config_path, config, kit_sdk_config, extra_args)
    end
end

-- Define Kit app. Run kit with particular .kit file.
function define_app(kitfile, args)
    local args = args or {}
    local subfolder = args.subfolder or "apps"
    args.config_path = subfolder .. "/" .. kitfile
    if path.getextension(args.config_path) ~= ".kit" then
        args.config_path = args.config_path..".kit"
    end
    define_experience(kitfile, args)

    local define_test = get_value_or_default(args, "define_test", true)
    local test_args = get_value_or_default(args, "test_args", {})

    -- Generate test-[ext_name].bat/sh file to run single extension test.
    if define_test then
        define_ext_test_experience(kitfile, test_args)
    end

    local add_profile_startup_script = get_value_or_default(args, "add_profile_startup_script", false)
    if add_profile_startup_script then
        create_app_profile_startup_script(kitfile..".profile_startup", args)
    end
end


-- Define experience to test one particular extension.
-- @ext_name: Extension name.
-- @python_module: Python module name, if different from extension name. (optional)
function define_ext_test_experience(ext_name, args)
    local args = args or {}

    local python_module = get_value_or_default(args, "python_module", ext_name)

    local script_dir_token = (os.target() == "windows") and "%~dp0" or "$SCRIPT_DIR"

    local test_args = {
        "--enable omni.kit.test", -- We always need omni.kit.test extension as testing framework
        "--enable omni.kit.loop-default", -- Ensure we use our default runloop for test runner (for kit-kernel case)
        "--/app/enableStdoutOutput=0", -- Do not print startup/shutdown messages for test runner itself (less noise).
        "--/exts/omni.kit.test/testExts/0='"..ext_name.."'", -- Only include tests from the python module
        "--ext-folder \""..script_dir_token.."/exts\" ", -- Auto add "exts" folder near batch files. For external repos.
        "--ext-folder \""..script_dir_token.."/extscache\" ", -- Auto add "extscache" folder near batch files. For external repos.
        "--ext-folder \""..script_dir_token.."/apps\" ", -- Auto add "apps" folder near batch files. For external repos.
        "--/exts/omni.kit.test/testExtOutputPath=\""..script_dir_token.."/../../../_testoutput\" ",
        "--portable-root \""..script_dir_token.."/\" ", -- Run tests always in portable mode
        "--/telemetry/mode=test",
        "--/crashreporter/data/testName=\"ext-test-"..ext_name.."\"",
    }

    -- Allow passing additional args
    local extra_test_args = get_value_or_default(args, "extra_test_args", {})
    test_args = concat_arrays(test_args, extra_test_args)

    local suite = get_value_or_default(args, "suite", EXT_TEST_TEST_SUITE_DEFAULT)

    local exp_args = {
        config_path = "",
        extra_args = table.concat(test_args, " "),
        define_project = false
    }
    exp_args = merge_tables(exp_args, args)

    local test_name = suite and string.format("tests-%s-%s", suite, ext_name) or ("tests-"..ext_name)
    define_experience(test_name, exp_args)
end


-- Create script (batch file) to profile app startup.
function create_app_profile_startup_script(name, args)
    local is_window = os.target() == "windows"
    local extra_args = args.extra_args or ""

    -- Write bat and sh files
    local executable = is_window and "profile_startup.bat" or "profile_startup.sh"
    for _, config in ipairs(ALL_CONFIGS) do
        local kit_sdk_config = get_value_or_default(args, "kit_sdk_config", kit_sdk_config)
        if kit_sdk_config == "%{config}" then
            kit_sdk_config = config
        end
        create_experience_runner(name, args.config_path, config, kit_sdk_config, extra_args, executable)
    end
end


-- Add folder with source files to solution under specified vpath/ virtual group (helper)
-- @vpath: Virtual folder in VS project
-- @dir: Directory with files
-- @pattern: Wildcard pattern to search for files with. By default **. Can be just a file name.
function add_files(vpath, dir, pattern)
    local pattern = pattern or "**"
    files { dir.."/"..pattern }
    vpaths {
        [vpath.."/*"] = dir.."/*"
    }
end

-- Setup all msvc and winsdk paths. That later can be moved to actual msvc and sdk packages
function setup_msvc_toolchain()
    systemversion (WINSDK_VERSION)

    -- system include dirs:
    local msvcInclude = host_deps.."/msvc/VC/Tools/MSVC/"..MSVC_VERSION.."/include"
    local sdkInclude = {
        host_deps.."/winsdk/include/winrt",
        host_deps.."/winsdk/include/um",
        host_deps.."/winsdk/include/ucrt",
        host_deps.."/winsdk/include/shared"
    }
    externalincludedirs { msvcInclude, sdkInclude }

    -- system lib dirs:
    local msvcLibs = host_deps.."/msvc/VC/Tools/MSVC/"..MSVC_VERSION.."/lib/onecore/x64"
    local sdkLibs = { host_deps.."/winsdk/lib/ucrt/x64", host_deps.."/winsdk/lib/um/x64" }
    syslibdirs { msvcLibs, sdkLibs }

    -- system binary dirs:
    bindirs {
        host_deps.."/msvc/VC/Tools/MSVC/"..MSVC_VERSION.."/bin/HostX64/x64",
        host_deps.."/msvc/MSBuild/"..MSBUILD_VERSION.."/bin", host_deps.."/winsdk/bin/x64"
    }

    -- silence warnings from "/external:W" on some VS2019 toolchains.
    buildoptions { "/experimental:external" }

    -- defines to silence MSVC deprecation warnings
    defines {
        "_SILENCE_EXPERIMENTAL_FILESYSTEM_DEPRECATION_WARNING"
    }
end

-- Setup build settings for handling deprecated
function setup_deprecated()
    if _OPTIONS["deprecated"] == "warning" then
        filter { "system:linux" }
            disablewarnings { "error=deprecated-declarations" }
        filter {}
        if os.target() == "windows" then
            print("Windows' compiler cl.exe cannot demote individual warnings when using warnings-as-errors (/WX)")
            print("Please use \"disable\" if you wish to build with deprecated code")
            os.exit(1)
        end
    end
    if _OPTIONS["deprecated"] == "disable" then
        filter { "system:linux" }
            disablewarnings { "deprecated-declarations" }
        filter { "system:windows" }
            disablewarnings { "4996" } -- unfortunately /WX doesn't allow demotion, only disable, revisit with clang
        filter {}
    end
end

-- This setup will update global state, but by default doesn't change anything unless you specify an option, so no harm
setup_deprecated()

------------------------------------------------------------------------------------------------------------------------
------------------                             OpenUSD Build Support                                     ------------------
------------------------------------------------------------------------------------------------------------------------

-- Begin OpenUSD inclusion
USD_ROOT = root.."/_build/target-deps/usd/"

usd_common_libs = {
    "ar",
    "arch",
    "gf",
    "plug",
    "sdf",
    "tf",
    "usd",
    "vt"
}

usd_options = {
    usd_root = USD_ROOT.."%{cfg.buildcfg}",
    python_root = root.."/_build/target-deps/python",
    usd_suppress_warnings = true,
    no_set_cxx11_flag = true
}

function merge_usd_libs(common_libs, additional_libs)
    -- Merges the list of common USD libraries and any
    -- additional ones required by a specific plugin into
    -- a single table
    if additional_libs == nil then
        return common_libs
    end

    local result = {}
    for i=1,#common_libs do
        result[i] = common_libs[i]
    end
    for i=1,#additional_libs do
        result[#result + 1] = additional_libs[i]
    end

    return result
end

function add_python()
    -- Adds the Python dependency that OpenUSD is dependent on
    -- Calling add_usd() will also add Python underneath
    -- Use this method when python support is needed, but USD is not
    usd_module.use_python(usd_options)
end

function add_usd(additional_usd_libs)
    -- Adds OpenUSD dependencies
    usd_libs = merge_usd_libs(usd_common_libs, additional_usd_libs)
    usd_module.use_usd(usd_options, usd_libs)

    -- Adds pthread support for workers so that each
    -- project doesn't explicitly have to
    filter { "system:linux or macosx" }
        buildoptions { "-pthread" }
        links { "dl", "pthread" }
    filter { "system:linux", "configurations:debug" }
      links { "tbb_debug" }
    filter { "system:linux", "configurations:release" }
      links { "tbb" }
    filter {}

    defines { "TBB_SUPPRESS_DEPRECATED_MESSAGES=1" }
end

-- Python version we are bulding with
python_version = usd_module.get_python_version(usd_options)

-- if the python version is 3.10 or greater, build all extensions, otherwise build a subset
python_cutoff_version = tonumber("39")
python_version_value = python_version:gsub("%.", "")
python_version_value = tonumber(python_version_value)
if python_version_value > python_cutoff_version then
    is_python_version_latest = true
else
    is_python_version_latest = false
end

-- End OpenUSD inclusion

------------------------------------------------------------------------------------------------------------------------
------------------                              Project Templates                                     ------------------
------------------------------------------------------------------------------------------------------------------------

function commonProjectSetup(args)
    -- Nothing to do here currently. We used to set the CXX11 ABI flag
    -- here for Linux, but now we use the default of =1.
end

function project_common(project_name)
    project (project_name)

    -- Set minimum C++ standard for all projects
    cppdialect(CPP_DIALECT)

    -- Ensures __cplusplus macro is correctly reflecting the current c++ version when using Visual Studio.
    filter { "system:windows" }
        buildoptions { "/Zc:__cplusplus" } -- actual values of __cplusplus (https://learn.microsoft.com/en-us/cpp/build/reference/zc-cplusplus?view=msvc-170)
    filter { "system:linux" }
        links { "rt" } -- needed by carb::RString
    filter {}
end

-- Wrapper over premake project() function to avoid specifying location() all the time too.
function project_with_location(project_name)
    project_common (project_name)
    location ("%{root}/_compiler/".._ACTION.."/%{prj.name}")

    -- OM-77249: /Brepro linker flag on Windows helps making deterministic builds
    filter { "system:windows" }
        linkoptions { "/Brepro" }
    filter {}

    defines { "OMNI_COMPILE_AS_MODULE", "carb_eventdispatcher_IEventDispatcher=CARB_HEXVERSION(1,4)" }
end

-- Generic utility project for extension. It doesn't build, only makes scripts, docs, lua files etc. available in VS project.
-- It also automatically creates few folder links ("config", "scripts"), copies and links licenses. Follow the code for details.
-- @ext: table from get_current_extension_info() function
function project_ext(ext, args)
    local args = args or {}
    local include_root_licenses = get_value_or_default(args, "include_root_licenses", PROJECT_EXT_INCLUDE_ROOT_LICENSES_DEFAULT)
    local root_licenses_path = args.root_licenses_path or "${root}/_build/PACKAGE-LICENSES"
    local copy_nvidia_ext_licence = get_value_or_default(args, "copy_nvidia_ext_licence", true)
    local define_test = get_value_or_default(args, "define_test", true)
    local generate_ext_project = get_value_or_default(args, "generate_ext_project", _OPTIONS["generate-ext-projects"])
    local ext_projext_name = get_value_or_default(args, "ext_projext_name", ext.id)
    local test_args = get_value_or_default(args, "test_args", {})
    test_args["suite"] = get_value_or_default(args, "test_suite", EXT_TEST_TEST_SUITE_DEFAULT)

    group (ext.group.."/"..ext.id)

    -- Generate test-[ext_name].bat/sh file to run single extension test.
    if define_test then
        define_ext_test_experience(ext.id, test_args)
    end

    -- Optionally generate utility project for each extension
    if generate_ext_project then
        project_with_location (ext_projext_name)
            kind "Utility"
            vpaths { ["*"] = "." }
            files { ".".."/**.py" }
            files { ".".."/**.toml" }
            files { ".".."/**.lua" }
            files { ".".."/**.rst" }
    end

    -- Automatically link "target" folder into [extension root] is deprecated. Remove if empty, produce warning otherwise:
    local target_dir_path = get_current_lua_file_dir().."/target"
    if os.isdir(target_dir_path) then
        if next(os.match(target_dir_path.."/*")) == nil then
            os.rmdir(target_dir_path)
        end
        premake.warn("Automatic folder link of extension 'target' folder is deprecated. Remove: '"..target_dir_path.."' and reorganize your extension to explicitly folder link required folder with 'repo_build.prebuild_link {}'.")
    end
    if os.isdir(target_dir_path) and PROJECT_EXT_AUTOLINK_EXTENSIONS_TARGET_FOLDER then
        repo_build.prebuild_link { "target", ext.target_dir }
    else
        -- Following links and copies are only supported when whole "target" folder was not linked (they will conflict).

        -- Automatically link "config" folder into [extension root]/config if it exists
        if os.isdir(get_current_lua_file_dir().."/config") then
            repo_build.prebuild_link { "config", ext.target_dir.."/config" }
        end

        -- Automatically link "scripts" folder into [extension root]/scripts if it exists
        if os.isdir(get_current_lua_file_dir().."/scripts") then
            repo_build.prebuild_link { "scripts", ext.target_dir.."/scripts" }
        end

        -- Automaitcally link root licenses folder and copy nvidia license template (unless disabled)
        if include_root_licenses then
            repo_build.prebuild_link { root_licenses_path, ext.target_dir.."/PACKAGE-LICENSES/dependencies" }
        end
        if copy_nvidia_ext_licence then
            repo_build.prebuild_copy { kit_dev_dir.."/tools/license-templates/ext-LICENSE-TEMPLATE.md", ext.target_dir.."/PACKAGE-LICENSES/"..ext.id.."-LICENSE.md" }
        end
    end
end

-- Common extension plugin settings.
-- @ext: table from get_current_extension_info() function
function project_ext_plugin(ext, project_name)
    project_with_location(project_name)
    kind "SharedLib"
    staticruntime "Off"
    targetdir (ext.bin_dir)

    includedirs {
        "%{kit_dev_dir}/include",
    }

    filter { "system:linux" }
        links { "rt" } -- needed by carb::RString
    filter { "system:macosx" }
        -- allow any plugin to weakly link against 'libcarb.dylib'.  This is typically the only
        -- symbol that is needed externally from a plugin.  Note that on MacOS, weakly linking
        -- against something requires an explicit linker option to specify the name of the symbol
        -- to be weak linked against.  Simply marking it as a weak symbol in the code is not
        -- enough.
        linkoptions { "-Wl,-U,_carbReallocate" }
        linkoptions { "-Wl,-U,_omniWeakObjectGetOrCreateControlBlock" }
        linkoptions { "-Wl,-U,_omniWeakObjectControlBlockOp" }
    filter {}
end


-- Common python bindings settings
-- Arguments passed as a table (to allow named and optional arguments):
-- @ext: table from get_current_extension_info() function
-- @project_name: Name of the project.
-- @module: Python module name. It is recommened to start it with underscore.
-- @target_subdir: Subdirectory in extension's target folder where to build bindings.
-- @src: Source directory (optional).
function project_ext_bindings(args)
    local ext = args.ext
    local project_name = args.project_name
    local module = args.module
    local bindings_target_dir = ext.target_dir.."/"..args.target_subdir
    local src = args.src or nil
    local iface_project = args.iface_project or nil
    local config = args.config or nil

    project_with_location(project_name)
    targetdir (bindings_target_dir)

    if type(src) == "string" then
        add_files("src", src)
        repo_build.prebuild_copy { src.."/*.py", bindings_target_dir }
    end

    if iface_project ~= nil then
        dependson { iface_project }
    end

    links { "carb" }
    includedirs { "%{target_deps}/pybind11/include" }
    filter { "system:linux" }
        if not is_python_version_latest then
            disablewarnings { "undef", "deprecated-declarations" } -- for old pybind11; remove when we upgrade to pybind 2.7+
        end
        links { "rt" } -- needed by carb::RString
    filter { "system:macosx" }
        -- update the search path for libpython to be in the same directory as our plugin
        -- CC-952: investigate whether we can do this as part of the link line
        -- TODO: this would need to be updated for dynamic python versions but currently macos is not supported completely
        local py_rpath = "@rpath/libpython"..python_version..".dylib"
        postbuildcommands{"install_name_tool -change \"$$(otool -L %{cfg.linktarget.abspath} | grep libpython | head -n 1 | sed 's/(.*)$$//' | awk '{$$1=$$1};1')\" \""..py_rpath.."\" \"%{cfg.linktarget.abspath}\""}
        linkoptions { "-Wl,-U,_carbReallocate" }
        linkoptions { "-Wl,-U,_omniWeakObjectGetOrCreateControlBlock" }
        linkoptions { "-Wl,-U,_omniWeakObjectControlBlockOp" }

        if _OPTIONS["silence-warnings"] == nil then
            -- "delete-abstract-non-virtual-dtor" occurs every time an Omni Interface is used in
            --     a python binding.  The std::unique_ptr that pybind11 uses to wrap the object
            --     tries to delete it, but no virtual destructor is ever defined in those interfaces.
            -- "deprecated-declarations" occurs every time a deprecated member function exists in a
            --     Carbonite Interface and that interface is used in a python binding.
            disablewarnings { "error=delete-abstract-non-virtual-dtor", "error=deprecated-declarations" }
        else
            disablewarnings { "delete-abstract-non-virtual-dtor", "deprecated-declarations" }
        end
    filter {}

    local python_folder = "%{kit_sdk_bin_dir}/python"
    repo_build.define_bindings_python(module, python_folder, python_version, config)
end

-- Common extension library with c++ tests (doctest) settings.
-- @ext: table from get_current_extension_info() function
function project_ext_tests(ext, project_name)
    project_with_location(project_name)
    kind "SharedLib"
    defines { "OMNI_COMPILE_AS_MODULE" }
    staticruntime "Off"
    exceptionhandling "On"
    targetdir (ext.bin_dir)

    -- the doctest implementation is provided in omni.kit.test.
    -- this tells the test DLL we're building to dllimport
    -- doctest symbols
    defines { "DOCTEST_CONFIG_IMPLEMENTATION_IN_DLL" }

    includedirs {
        "%{kit_dev_dir}/include",
    }
    libdirs {
        extsbuild_dir.."/omni.kit.test/bin",
    }
    links { "carb", "omni.kit.test.plugin" }
end


function project_ext_omnibind(ext, project_name)
    project_with_location(project_name)
    kind "StaticLib"
    targetdir (ext.bin_dir)

    includedirs {
        "%{kit_dev_dir}/include",
        --"%{root}/source/plugins/common",
    }
end

function setup_project_assertions()
    local assertsEnabled = _OPTIONS["assert"]
    if assertsEnabled ~= nil then
        print("*** CARB_ASSERT_ENABLED ***")
        filter  { "configurations:release" }
            defines { "CARB_ASSERT_ENABLED", "_CONTAINER_DEBUG_LEVEL=1" } --_CONTAINER_DEBUG_LEVEL is vc140+ ABI stable STL accessor assertion
        filter {}
    end
end

function setup_project_checks()
    local checksEnabled = _OPTIONS["no-check"]
    if checksEnabled ~= nil then
        print("*** CARB_CHECK_ENABLED=0 ***")
        defines { "CARB_CHECK_ENABLED=0" }
    end
end
------------------------------------------------------------------------------------------------------------------------
------------------                             CUDA Build Support                                     ------------------
------------------------------------------------------------------------------------------------------------------------

-- ----------------------------------------------------------------------
-- Support function for the CUDA build. Has to be external as it is called at resolution time, when the cuda() object
-- is no longer available.
-- Take a list of include directories and return a string representing the compiler parameters that include them all
-- {"include/", "include2/"} -> "-I include -I include2"
function _include_files_to_string(includes)
    -- Sort the include list for consistent command line generation, otherwise the string will be in random order and
    -- the build commands will think they have changed and always trigger a rebuild.
    local sortedIncludes = {}
    for key, includePath in ipairs(includes) do
        sortedIncludes[key] = "-I "..tostring(includePath)
    end
    table.sort(sortedIncludes, function (k1, k2) return k1:lower() < k2:lower() end)
    return table.concat(sortedIncludes, " ")
end

-- Object that will contain all of the support for being able to compile CUDA files.
--
-- Be sure that all of your CUDA files are included in your project (shown here as a separate directory though
-- they can anywhere so long as they are added to your project)
--
--    add_files("cuda", "myCudaDirectory")
--
-- To enable this feature add this line to your plugin project:
--
--    add_cuda_build_support()
--
-- @args: Optional table that can override the default configuration:
--    driver (false): Link to the CUDA driver library (libcuda)
--    no_runtime (false): Do not link to the CUDA runtime library (libcudart)
--    use_static_rt (false): Use static linking for the CUDA runtime, else use a .dll/.so
--    cuda_package_path (target_deps/cuda): Location of the CUDA package
--    host_compiler_vs (host_deps/msvc/VC): Location of the C++ host compiler
--    carb_sdk_include (target_deps/carb_sdk_plugins/include): Location of the Carbonite SDK include directory
--    extra_nvcc_args (): Extra arguments to pass to the nvcc compiler, as a single string
--    extra_host_compiler_args (): Extra arguments to pass to the host compiler, as a single string
--    is_ptx (): If true, compile the files as a PTX files, and generate .h files with the ptx code as an array
--    include_files (): Additional include files that should trigger .cu files recompilation
--
function add_cuda_build_support(args)
    local cuda = {}
    local args = args or {}
    cuda.driver = args.driver or false
    cuda.no_runtime = args.no_runtime or false
    cuda.use_static_rt = args.use_static_rt or false
    cuda.cuda_package_path = args.cuda_package_path or target_deps.."/cuda"
    cuda.nvcc_path = path.getabsolute(cuda.cuda_package_path.."/bin/nvcc"..(os.host() == "windows" and ".exe" or ""))
    cuda.host_compiler_vs = args.host_compiler_vs or path.getabsolute("%{root}/_build/host-deps/msvc/VC")
    cuda.carb_sdk_include = args.carb_sdk_include or path.getabsolute("%{root}/_build/target-deps/carb_sdk_plugins/include")
    cuda.extra_nvcc_args = args.extra_nvcc_args or ""
    cuda.extra_host_compiler_args = args.extra_host_compiler_args or ""
    cuda.is_ptx = args.is_ptx or false
    cuda.include_files = args.include_files or {}
    cuda.bin2c_path = path.getabsolute(cuda.cuda_package_path.."/bin/bin2c"..(os.host() == "windows" and ".exe" or ""))


    -- ----------------------------------------------------------------------
    -- Take in a list of command-line "-FOO" options and return the list of them as a string separated by commas
    -- {"-Wall", "-D"} -> "-Wall,-D"
    function cuda._separate_options_with_commas(options)
        local result = "";
        local sep = "";
        for option in string.gmatch(options, "-%w+") do
            result = result..sep..tostring(option)
            sep = ","
        end
        return result;
    end

    -- ----------------------------------------------------------------------
    -- Helper function to implement a build step that preprocesses .cu files (CUDA code) for compilation on Windows
    -- @nvcc_host_compiler_flags: Flags to pass on to the host compiler
    -- @nvcc_flags: Flags to pass on to the CUDA compiler
    function cuda._make_nvcc_command_windows(nvcc_host_compiler_flags, nvcc_flags)
        ext = ".obj"
        if cuda.is_ptx then
            ext = ".ptx"
            nvcc_flags = nvcc_flags.." -ptx -dc "
        end
        local buildString = "\""..cuda.nvcc_path.."\""..
                            " "..nvcc_flags.." "..cuda.extra_nvcc_args..
                            " --compiler-bindir "..cuda.host_compiler_vs..
                            " -Xcompiler="..nvcc_host_compiler_flags..",/Zc:__cplusplus "..
                            " --std c++17"..
                            cuda.extra_host_compiler_args..
                            " -c -I "..cuda.carb_sdk_include..
                            " %{_include_files_to_string(cfg.includedirs)}"..
                            " -o %{cfg.objdir}/%{file.basename}"..ext..
                            " %{file.abspath}"
        buildmessage ("%{file.basename}%{file.extension}")
        buildcommands { buildString }

        buildinputs { "%{file.abspath}", cuda.include_files }
        if cuda.is_ptx then
            buildcommands { "{MKDIR} %{cfg.objdir} ", cuda.bin2c_path.." -st -c -p 0 ".."%{cfg.objdir}/%{file.basename}.ptx > %{cfg.objdir}/%{file.basename}.ptx.h"}
            buildoutputs { "%{cfg.objdir}/%{file.basename}.ptx.h" }
        else
            buildoutputs { "%{cfg.objdir}/%{file.basename}"..ext }
        end
    end

    -- ----------------------------------------------------------------------
    -- Helper function to implement a build step that preprocesses .cu files (CUDA code) for compilation on Linux
    -- @nvcc_host_compiler_flags: Flags to pass on to the host compiler
    -- @nvcc_flags: Flags to pass on to the CUDA compiler
    function cuda._make_nvcc_command_linux(nvcc_host_compiler_flags, nvcc_flags)
        ext = ".o"
        if cuda.is_ptx then
            ext = ".ptx"
            nvcc_flags = nvcc_flags.." -ptx -dc "
        end
        local allHostArgs = nvcc_host_compiler_flags.." "..cuda.extra_host_compiler_args
        local buildString = "\""..cuda.nvcc_path.."\""..
                            " -std=c++17"..
                            " "..nvcc_flags.." "..cuda.extra_nvcc_args..
                            " -Xcompiler="..cuda._separate_options_with_commas(allHostArgs)..
                            " --std c++17"..
                            " -c -I "..cuda.carb_sdk_include..
                            " %{_include_files_to_string(cfg.includedirs)}"..
                            " -MF \"$(@:%.o=%.d)\" -MD -MP"..
                            " -o %{cfg.objdir}/%{file.basename}"..ext..
                            " %{file.abspath}"
        buildmessage ("%{file.basename}%{file.extension}")
        buildcommands { "{MKDIR} %{cfg.objdir} ", buildString }

        buildinputs { "%{file.abspath}", cuda.include_files }
        if cuda.is_ptx then
            buildcommands { "{MKDIR} %{cfg.objdir} ", cuda.bin2c_path.." -st -c -p 0 ".."%{cfg.objdir}/%{file.basename}.ptx > %{cfg.objdir}/%{file.basename}.ptx.h"}
            buildoutputs { "%{cfg.objdir}/%{file.basename}.ptx.h" }
        else
            buildoutputs { "%{cfg.objdir}/%{file.basename}"..ext }
        end
    end

    -- ----------------------------------------------------------------------
    -- Create pre-compiled SASS for all architectures that are supported by CUDA 11.5 (Maxwell to Ampere)
    function cuda._get_sass_parameters()
        local sass = "-gencode=arch=compute_52,code=sm_52 ".. -- Maxwell
                     "-gencode=arch=compute_53,code=sm_53 "..
                     "-gencode=arch=compute_60,code=sm_60 ".. -- Pascal
                     "-gencode=arch=compute_61,code=sm_61 "..
                     "-gencode=arch=compute_62,code=sm_62 "..
                     "-gencode=arch=compute_70,code=sm_70 ".. -- Volta
                     "-gencode=arch=compute_72,code=sm_72 "..
                     "-gencode=arch=compute_75,code=sm_75 ".. -- Turing
                     "-gencode=arch=compute_80,code=sm_80 ".. -- Ampere
                     "-gencode=arch=compute_86,code=sm_86 "..
                     "-gencode=arch=compute_87,code=sm_87 "..
                     "-gencode=arch=compute_89,code=sm_89 ".. -- Ada
                     "-gencode=arch=compute_90,code=sm_90 "   -- Hopper
        -- For forward compatibility with future architectures we also include a Hopper-based PTX
        -- that can be JIT compiled at runtime
        local ptx = "-gencode=arch=compute_90,code=compute_90 "

        if cuda.is_ptx then
            return " "
        end

        return sass..ptx
    end

    -- ----------------------------------------------------------------------
    -- Build rules for CUDA files
    function cuda._add_cuda_files()
        local sass = cuda._get_sass_parameters()
        local winFlags = "/MD"
        if cuda.use_static_rt then
            winFlags = "/MT"
        end

        if cuda.is_ptx then
            -- quirk for Windows builds:
            -- VC resource compiler may try to compile/link something, complaining about missing
            -- entry point. But we're not building an obj, just generating a ptx header from .cu
            filter { "system:windows" }
                kind "StaticLib"
                removefiles { "%{root}/_build/omniverse-kit-details.rc" }
            filter {}
        end

        filter { "files:**.cu", "system:windows", "configurations:debug" }
            cuda._make_nvcc_command_windows(winFlags.."d", sass.." -g")
        filter { "files:**.cu", "system:windows", "configurations:release" }
            cuda._make_nvcc_command_windows(winFlags, sass)
        filter { "files:**.cu", "system:linux", "configurations:debug" }
            cuda._make_nvcc_command_linux("-fPIC -g", sass.." -g")
        filter { "files:**.cu", "system:linux", "configurations:release" }
            cuda._make_nvcc_command_linux("-fPIC", sass)
        filter {}
    end

    -- ----------------------------------------------------------------------
    -- Add build dependencies on libraries and include paths used when accessing CUDA driver code
    function cuda._add_cuda_driver_headers_libs()
        -- Add in the library directory or stubs
        filter { "system:linux"  }
            libdirs { cuda.cuda_package_path.."/lib64/stubs" }
            disablewarnings { "error=overflow", "error=switch", "error=reorder", "error=unused-function" }
            links { "cuda" }
        filter { "system:windows" }
            libdirs { cuda.cuda_package_path.."/lib/x64" }
            links { "cuda" }
        filter {}
        includedirs { cuda.cuda_package_path.."/include" }
    end

    -- ----------------------------------------------------------------------
    -- Add build dependencies on libraries and include paths used when accessing CUDA runtime code
    function cuda._add_cuda_runtime_headers_libs()
        -- Add in the library directories
        filter { "system:linux"  }
            libdirs { cuda.cuda_package_path.."/lib64" }
            -- linking to cudart_static requires libpthread, libdl, and librt
            -- https://gitlab.kitware.com/cmake/cmake/-/issues/20249
            buildoptions { "-pthread" }
            links { "cudart_static", "dl", "pthread", "rt" }
        filter { "system:windows" }
            libdirs { cuda.cuda_package_path.."/lib/x64" }
            links { "cudart_static" }
        filter {}
        includedirs { cuda.cuda_package_path.."/include" }
    end

    -- Do the actual work to configure the build to handle CUDA files
    cuda._add_cuda_files()
    if cuda.driver then
        cuda._add_cuda_driver_headers_libs()
    end
    if not cuda.no_runtime then
        cuda._add_cuda_runtime_headers_libs()
    end
end

-- Even though `ccache` theoretically supports precompiled headers, it's safer
-- to just not mix PCH + ccache. So, if ccache is enabled, typically via setting
-- the CARB_CCACHE envvar or via `repo build --ccache`, we will not remove the NoPCH
-- flag.
function remove_nopch_flag()
    if repo_build.ccache_path() == nil then
        removeflags { "NoPCH" }
    end
end

-- USD-adjacent plugins typically reference this massive USD PCH.
-- Define the header + source only when `ccache` is not in user due to reasons defined
-- in `remove_nopch_flag()`.
function enable_usd_pch()
    if repo_build.ccache_path() == nil then
        remove_nopch_flag()
        pchheader "UsdPCH.h"
        pchsource "%{root}/source/pch/UsdPCH.cpp"
        files { "%{root}/source/pch/UsdPCH.cpp" }
    else
        -- When ccache is enabled, add this file to the "Forced Includes" section of the project
        buildoptions { "/FI\"%{root}/source/pch/UsdPCH.h\"" }
    end
end
