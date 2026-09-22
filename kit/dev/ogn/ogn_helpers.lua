------------------------------------------------------------------------------------------------------------------------
-- Support for .ogn file build processing. See the Kit documentation for setting up a build using these functions.
--[[
begin-documentation
The ogn project configuration information is kept in a table, much the same as how the extension configuration
information is kept in a table. You start with the extension information as your base:

.. code-block:: lua

    local ext = get_current_extension_info()

Then you can either populate all of the ogn project information in one step

.. code-block:: lua

    local ogn = get_ogn_project_information(ext, "omni/my/extension")

or you can customize your project name and plugin include path by splitting the population into two steps

.. code-block:: lua

    local ogn = create_ogn_project_information(ext, "omni/my/extension")
    ogn.project_path = my_custom_project_name
    ogn.plugin_path = "plugin/include"
    add_ogn_project_dependencies(ogn)

Both `get_ogn_project_information` and `create_ogn_project_information` take an optional third parameter that points
to a file containing type definitions described in :ref:`ogn_type_definition_overrides`. In order to use your own
custom configuration file you would add in a call to the function that will install it into the build for you:

.. code-block:: lua

    install_ogn_configuration_file("my_configs/MyTypeConfiguration.json")

Once the configuration is set up in this manner you can use the contents of the table to point your C++ or Python
project definitions to the standard locations used by ogn, and then define the project that will generate the code
and documentation from your .ogn file definitions

.. code-block:: lua

    project_ext_ogn(ext, ogn, settings)

The `settings` parameter is an optional table that can be used to further configure the project definition. If the
table entry *no_group* is present (i.e. settings["no_group"] is not nil) then the standard build grouping is not
defined for this project. Any other non-nil table entries will be treated as being a value to pass to the generator
as a Carbonite setting of the form */persistent/omnigraph/generator/SETTING*.

Within your project definition you will want to add the common ogn dependencies as determined by the *ogn* table.
The easiest way to do this is in one step with the single call

.. code-block:: lua

    add_ogn_dependencies(ogn, python_node_directories)
    -- e.g. add_ogn_dependencies(ogn, {"python/nodes"})

where *python_node_directories* is a table of directories in which Python nodes live. You do not have to include the
directories for C++ nodes in this list. This function does three things, which you can also call separately if you
are using different build flags or wish to structure your build file differently.

.. code-block:: lua

    -- Define the standard directory and extension dependencies
    set_up_ogn_dependencies(ogn)
    -- Define the C++-specific flags and link libraries
    set_ogn_cpp_flags(ogn)
    -- Tell the project where to find the implementation of Python .ogn nodes
    link_ogn_python_directories(ogn, python_node_directories)

You can also generate some documentation index files that list all of the nodes in your repo both by category and
by extension. Once they are generated they end up in _build/ogn/docs/ where you can include them in some toctree.

.. code-block:: lua

    project_ogn_docs_index()

.. code-block:: md

    .. toctree::
    :maxdepth: 1
    :glob:

    ../../../../../_build/ogn/docs/*

end-documentation
--]]
------------------------------------------------------------------------------------------------------------------------

-- ----------------------------------------------------------------------
-- Returns either the given directory if absolute, or the directory relative to the root
function ogn_abs_or_relative(path_to_check, default_root)
    if path.isabsolute(path_to_check) then
        return path_to_check
    end
    return default_root.."/"..path_to_check
end

-- ----------------------------------------------------------------------
-- Utility to find the directory the OGN shipped directory lives in, as it is not available directly through variables
function ogn_build_path()
    -- If using the Kit SDK then look in the installed link to the SDK tree
    if is_packaged_sdk then
        return path.getrelative(".", kit_sdk.."/dev/ogn")
    end

    -- Otherwise the Kit build location is the right place
    return path.getrelative(".", "%{root}/_build/ogn")
 end

-- ----------------------------------------------------------------------
-- Utility to find the directory the OGN config directory lives in, as it is not available directly through variables
function ogn_config_path()
    return ogn_build_path().."/config"
 end

-- ----------------------------------------------------------------------
-- Find and return a location of omni.graph.tools extension
function ogn_tools_ext_path()
    -- If using the kit-kernel package then look in a dir for a build-time installed extensions:
    if is_packaged_kernel then
        return path.getrelative(".", extsbuild_dir.."/omni.graph.tools")
    end

    -- In all other cases it should be included (either in SDK package or local build)
    return path.getrelative(".", kit_sdk_bin_dir.."/exts/omni.graph.tools")
 end

-- ----------------------------------------------------------------------
-- Lua has no easy sorting function so this function provides an iterator ordered by key name
-- @tableToIterate: Table to be iterated
-- @sortFunction: Alternate sort function, use lexical ordering if not specified
-- @return: Function that iterates over a sorted version of the table
function pairsSortedByKeys (tableToIterate, sortFunction)
    local sortedTable = {}
    for index in pairs(tableToIterate) do
        table.insert(sortedTable, index)
    end
    table.sort(sortedTable, sortFunction)
    local i = 0
    local iter = function ()   -- iterator function
        i = i + 1
        if sortedTable[i] == nil then
            return nil
        else
            return sortedTable[i], tableToIterate[sortedTable[i]]
        end
    end
    return iter
end

-- ----------------------------------------------------------------------
-- Helper function to print a string representation of a table
-- @tableToPrint: Table whose contents are to be sorted and printed
-- @indentLevel: sets the initial level of indentation.
function printTable (tableToPrint, indentLevel)
    if not indentLevel then
        indentLevel = 0
    end

    for key, value in pairsSortedByKeys(tableToPrint) do
        formatting = string.rep("    ", indentLevel) .. key .. ": "
        if type(value) == "table" then
            print(formatting)
            printTable(value, indentLevel + 1)
        elseif type(value) == 'boolean' then
            print(formatting .. tostring(value))
        else
            print(formatting .. value)
        end
    end
end

-- ----------------------------------------------------------------------
-- @return: True if the the environment variable to show debugging information is enabled
function debuggingOGN ()
    return os.getenv("OGN_DEBUG") ~= nil
end

function pedanticOGN ()
    return os.getenv("OGN_PEDANTIC") ~= nil
end

-- ----------------------------------------------------------------------
-- Get a table of standard paths and project names for an OGN project
-- @ext: table from the get_current_extension_info() function
-- @import_path: Python import path the project would use (e.g. omni/graph/tools for this project)
-- @type_definitions: Optional path to file containing alternative generated code type definitions (mostly for C++)
-- Returns a table containing the ogn project definition information
--
-- If you set the environment variable OGN_DEBUG you can see the resulting parameters.
-- This assumes that your project is laid out in a manner consistent with what is described in OGN documentation:
--    PROJECT/
--        bindings/
--        docs/
--        nodes/
--        plugin/
--        python/
--            tests/
-- These are the generated table contents:
--    Source Paths
--      bindings_path : Subdirectory containing the C++ implementing Python bindings
--      toml_path     : Subdirectory containing the extension.toml file with the configuration
--      docs_path     : Subdirectory containing the documentation to publish
--      nodes_path    : Subdirectory containing the C++ OmniGraph nodes
--      plugin_path   : Subdirectory containing the C++ implementing the plugin
--      python_path   : Subdirectory containing the Python code
--    Target Paths
--      icon_target_path         : Path to the installed node icons
--      python_root_path         : Path to the directory to include in the python path to find the below modules
--      python_target_path       : Path to the Python import directory of the extension
--      python_tests_target_path : Path to the Python tests import directory of the extension
--      bindings_module          : Name of the Python bindings module for the extension
--      bindings_target_path     : Pyton bindings module import path, relative to root of the extension's Python tree
--      intermediate_target_path : Path to the directory containing intermediate build information
--    Project Information
--      import_path          : Subdirectory for both Python and C++ import/include
--      module               : Prefix for project names (import_path with "/" replace by ".")
--      plugin_project       : Name of the project that builds the C++ code
--      ogn_project          : Name of the project that processes the .ogn files
--      python_project       : Name of the project that processes the Python code
--      type_definition_path : Path to the configuration file that modifies generated type defnitions
--
function create_ogn_project_information(ext, import_path, type_definition_path)
    -- First do a sanity check so that a meaningful message will be printed if there is something amiss in the setup
    if not ext then
        premake.error("OGN project requires extension information received from get_current_extension_info() call")
    end
    if not ext.target_dir then
        premake.error("OGN project requires extension information contain a valid target_dir")
    end
    if not import_path then
        premake.error("OGN project cannot run without valid import_path")
    end
    if import_path:sub(-1) == "/" then
        premake.warning("Trailing '/' in the import_path is being ignored. Remove it.")
        import_path = string.sub(import_path, 1, -2)
    end
    if not target_deps then
        premake.error("OGN project cannot run without valid global variable target_deps")
    end
    if not kit_dev_dir then
        -- Previously the target_deps directory was the source of gsl/ and Fabric. It's been deprecated, with this
        -- check installed for backward compatibility. It can be removed completely in Kit 106.
        if not kit_target_deps then
            premake.error("OGN project requires kit_dev_dir to be defined for proper building")
        else
            premake.warning("OGN project requires kit_dev_dir to be defined for proper building")
            kit_dev_dir = kit_target_deps
        end
    end

    local ogn = {}

    -- Define the project variables
    ogn.import_path = import_path
    ogn.module = string.gsub(import_path, "/", ".")
    ogn.plugin_project = ogn.module..".plugin"
    ogn.ogn_project = ogn.module..".ogn"
    ogn.python_project = ogn.module..".python"
    ogn.type_definition_path = type_definition_path
    ogn.enable_autonode = false

    -- Set paths for the source directories
    ogn.bindings_path = "bindings"
    ogn.docs_path = "docs"
    ogn.nodes_path = "nodes"
    ogn.plugin_path = "plugins"
    ogn.python_path = "python"
    ogn.toml_path = "config"

    -- Set up target locations
    ogn.python_root_path = ext.target_dir
    ogn.extension_toml_path = ext.target_dir.."/config/extension.toml"
    ogn.icon_target_path = ext.target_dir.."/ogn/icons"
    ogn.docs_target_path = ext.target_dir.."/ogn/docs"
    ogn.node_description_path = ext.target_dir.."/ogn/nodes.json"
    ogn.python_target_path = ogn.python_root_path.."/"..import_path
    ogn.python_tests_target_path = ogn.python_target_path.."/tests"
    ogn.bindings_module = "_"..string.gsub(import_path, "/", "_")
    ogn.bindings_target_path = import_path.."/bindings"
    ogn.intermediate_target_path = "%{cfg.objdir}".."/tags"
    ogn.toc = nil

    -- If debugging is turned on then output all of the defined variables
    if debuggingOGN() then
        print("OGN: Project Import ", import_path)
        printTable(ogn, 1)
    end

    return ogn
end

-- ----------------------------------------------------------------------
-- Add the definition of standard include directories and extension dependencies to the ogn project information
-- @ogn: table from the create_ogn_project_information() function
function add_ogn_project_dependencies(ogn)
    -- Create a table with the expected include dependencies in it
    ogn.includedirs = {
        "%{build_dir}/ogn/include",      -- Generated OGN header files
        kit_dev_dir.."/gsl/include",     -- Support for std::span for tuple and array types
        ogn.plugin_path,                 -- This project's plugin header files, if any
        kit_dev_dir.."/fabric/include",  -- Fabric
    }

    -- Create a table with minimal project dependencies in it.
    ogn.dependson = { "omni.graph.core.plugin", "omni.graph.tools", ogn.ogn_project }
end

-- ----------------------------------------------------------------------
-- Get a table of standard paths and project names for an OGN project and then set build dependencies
-- @ext: table from get_current_extension_info() function
-- @import_path: Python import path the project would use (e.g. omni/graph/tools for this project)
-- @type_definitions: Optional path to file containing alternative generated code type definitions (mostly for C++)
-- Returns a table containing the ogn project definition information
-- See the description of create_ogn_project_information() to see what information is added to the table
-- See the description of add_ogn_project_dependencies() to see what build dependencies are added
--
function get_ogn_project_information(ext, import_path, type_definition_path)
    local ogn = create_ogn_project_information(ext, import_path, type_definition_path)
    add_ogn_project_dependencies(ogn)
    return ogn
end

-- ----------------------------------------------------------------------
-- Define the standard build, include, and library dependencies for an OGN-aware project
-- @ogn: table from get_ogn_project_information() function
--
function set_up_ogn_dependencies(ogn)

    -- moved from add_usd method to individual plugins
    -- use dynamically linked runtime
    staticruntime("Off")
    filter { "configurations:debug" }
        runtime "Debug"
    filter  { "configurations:release" }
        runtime "Release"
    filter {}

    -- begin OpenUSD
    extra_usd_libs = {
        "usdUtils"
    }

    add_usd(extra_usd_libs)
    -- end OpenUSD

    -- Enact the dependencies extracted from the OGN configuration
    includedirs { ogn.includedirs }
    libdirs { ogn.libdirs }
    dependson { ogn.dependson }

    -- The API has some concurrent containers in use so tbb is needed
    filter { "system:linux" }
        disablewarnings { "undef", "deprecated-declarations" } -- must have for tbb :(
    filter { "configurations:debug" }
        links { "tbb_debug" }
    filter { "configurations:release" }
        links { "tbb" }
    filter {}

    if debuggingOGN() then
        print("OGN: Add Dependencies")
        print("     includedirs")
        printTable(ogn.includedirs, 2)
        print("     libdirs")
        printTable(ogn.libdirs, 2)
        print("     dependson")
        printTable(ogn.dependson, 2)
    end
end

-- ----------------------------------------------------------------------
-- Tell the OGN-aware project where the definitions of Python nodes can be found
-- @ogn: table from get_ogn_project_information() function
-- @python_node_directories: Optional list of directories containing Python nodes (to link, providing hot-loading)
--
function link_ogn_python_directories(ogn, python_node_directories)
    -- Walk the list of extra arguments and link them to the generated ogn/ Python directory
    if python_node_directories ~= nil then
        for _,directory in ipairs(python_node_directories) do
            if debuggingOGN() then
                print("OGN: Adding link to Python node directory "..directory)
            end
            repo_build.prebuild_link {
                { directory, ogn.python_target_path.."/ogn/"..directory},
            }
        end
    elseif debuggingOGN() then
        print("OGN: Python node directories are nil in project "..ogn.import_path)
    end
end

-- ----------------------------------------------------------------------
-- Common settings for projects that are set up for OGN file usage
-- @ogn: table from get_ogn_project_information() function
function set_ogn_cpp_flags(ogn)
    -- Access the USD data types used by tuples, and the carb framework used to acquire the omni.graph.core interfaces
    links { "carb" }

    -- Standard way of building in Omniverse
    exceptionhandling "On"
    rtti "On"
    language "C++"

    -- Linux finds problems in the omni.graph.core wrapper includes so filter those errors
    filter { "system:linux" }
        removeflags { "FatalCompileWarnings", "UndefinedIdentifiers" }
    filter{}

    -- Work around https://github.com/intel/tbb/issues/154 which can randomly show up in generated code
    -- This can be removed once the TBB bug is fixed
    if kit_sdk_config == "debug" then
        defines { "TBB_USE_DEBUG=1" }
    elseif kit_sdk_config == "release" then
        defines { "TBB_USE_DEBUG=0" }
    else
        -- Fallback to filters
        filter { "configurations:debug" }
            defines { "TBB_USE_DEBUG=1" }
        filter  { "configurations:release" }
            defines { "TBB_USE_DEBUG=0" }
        filter {}
    end
end

-- ----------------------------------------------------------------------
-- Add in standard dependencies and build flags for OGN projects
-- @ogn: table from get_ogn_project_information() function
-- @python_node_directories: Optional table of directories containing Python nodes (to link, providing hot-loading)
-- @kit_sdk_config: Optional allows the env to override the config Debug/Release of kit
--
function add_ogn_dependencies(ogn, python_node_directories)
    set_up_ogn_dependencies(ogn)
    set_ogn_cpp_flags(ogn)
    link_ogn_python_directories(ogn, python_node_directories)
end

-- ----------------------------------------------------------------------
-- Common settings for projects that want to make use of .ogn files.
-- @ext: table from get_current_extension_info() function
-- @ogn: table from get_ogn_project_information() function
-- @settings: table of settings to refine the project configuration
--            no_group (bool): Do not add the project to the default group, let the caller do it
--            toc (str): If specified, generate a table of contents in the 'toc' directory (absolute or relative)
--            [anything else]: Pass on to the make_node_generator_command to define generator settings
function project_ext_ogn(ext, ogn, settings)

    -- Handle any special settings and then remove them from what is passed on to the node generator
    if settings ~= nil then
        if settings.no_group ~= nil then
            group (ext.group.."/"..ext.id)
            settings.no_group = nil
        end

        if settings.toc ~= nil then
            if path.isabsolute(settings.toc) then
                ogn.toc = settings.toc
            else
                ogn.toc = debug.getinfo(2).source:match("@?(.*/)").."/"..settings.toc
            end
            settings.toc = nil
        end
    end

    project_with_location (ogn.ogn_project)
    kind "Utility"

    -- The tools scripts have to be in place before they can generate .ogn files
    dependson { "omni.graph.tools" }

    -- Pre-generate AutoNode node ogn definitions
    if ogn.enable_autonode then
        generate_autonode_type_definitions(ogn, ext.name)
    end

    local ogn_files = os.matchfiles("**.ogn")

    -- If debugging is turned on then output all of the defined variables
    if debuggingOGN() then
        print("OGN: Defining OGN project")
        printTable(ogn_files, 1)
    end

    make_node_generator_command(
        ogn,
        ext.name,
        ogn_files,
        settings
    )

    -- Add the post-build command that generates the nodes.json summary file containing cached node metadata
    local shell_ext=".sh"
    if os.target() == "windows" then
        shell_ext=".bat"
    end
    local calling_directory = debug.getinfo(2).source:match("@?(.*[\\/])")
    local omnigraph_metadata_path = ogn_tools_ext_path().."/omni/graph/tools/_impl/repo_tools/generate_node_metadata.py"

    if not pythonScriptPath then
        premake.error("OGN node metadata generator requires the global variable 'pythonScriptPath' point to a path to run Python")
    end

    local build_nodes_json_command = table.concat{ pythonScriptPath,
        " "..omnigraph_metadata_path,
        " --extension-root \""..calling_directory.."\"",
        " --destination \""..ogn.node_description_path.."\"",
    }

    if debuggingOGN() then
        print("OGN: Building nodes.json for "..ext.name)
        build_nodes_json_command = build_nodes_json_command.." --log-level DEBUG"
        print(build_nodes_json_command)
    end

    buildmessage("Building nodes.json for "..ext.name)
    postbuildcommands { build_nodes_json_command }
end

-- ----------------------------------------------------------------------
-- Function to pre-process OmniGraph AutoNode nodes defined in code files.
-- Used to run the decorator node type generator commands.
-- @ext_name: Extension name
-- @ogn: Table from get_ogn_project_information() function
function generate_autonode_type_definitions(ogn, ext_name)

    local python_ogn_path = ogn.python_target_path.."/ogn"
    if not ext_name then
        premake.error("OGN AutoNode node type generator requires an extension name")
    end

    -- local inline_autogenerated_path
    local shell_ext=".sh"
    if os.target() == "windows" then
        shell_ext=".bat"
    end
    local build_autonode_command = table.concat{ root.."/repo"..shell_ext,
        " omnigraph_autonode",
        " --module-root \""..ogn.python_root_path.."\"",
        " --toml-file \""..ogn.extension_toml_path.."\"",
        " --ogn-folder \""..python_ogn_path.."/__autonode\" ",
        " --node-type-folder \""..python_ogn_path.."\" "
    }

    if debuggingOGN() then
        print("OGN: scanning for AutoNode definitions in "..ext_name)
        build_autonode_command = build_autonode_command.." --log-level DEBUG"
        print(build_autonode_command)
    end

    buildmessage("Building autonode for "..ext_name)
    prebuildcommands { build_autonode_command }
end

-- ----------------------------------------------------------------------
-- This is the custom rule that must be called on the .ogn description file to generate the node interface files
-- @ogn = The OGN project information
-- @extension_name = The name of the extension for which the files are being generated
-- @ogn_file_list = The list of the .ogn files to process
-- @settings: Table of settings to pass to the node generator command
-- For each X.ogn file passed into this function it will create these files in the _build/ogn directory:
--     include/X_ogn.h     : Generated C++ interface classes on which the node algorithm can be built
-- these files in the extension build directory (e.g. _build/windowsx86_64/debug/exts/my.extension)
--     ogn/docs/X_ogn.rst   : Generated documentation of the node and its attributes
-- and these files in the python_path directory (e.g. _build/windowsx86_64/debug/exts/my.extension/my/extension)
--     ogn/X_ogn.py    : Wrapper class that provides Pythonic property-based access to the node's attribute data
--     tests/TestXOgn.py : Test script that exercises the basic node functionality
--     tests/usd/X_ogn.usda  : USD template instantiating a node with the defined attributes and defaults
function make_node_generator_command(ogn, extension_name, ogn_file_list, settings)
    ext_header = ".h"
    ext_docs = ".rst"
    ext_python = ".py"
    ext_test = ".py"
    ext_usd = ".usda"

    -- Extract information from the project definitions
    local project_name = ogn.module
    local icon_target_path = ogn.icon_target_path
    local docs_target_path = ogn.docs_target_path
    local python_path = ogn.python_target_path

    -- First do a sanity check so that a meaningful message will be printed if there is something amiss in the setup
    if not project_name then
        premake.error("OGN node generator requires a project name")
    end
    if not python_path then
        premake.error("OGN node generator requires a Python path")
    end
    if not extension_name then
        premake.error("OGN node generator requires an extension name")
    end
    if not ogn_file_list then
        premake.error("OGN node generator requires a list of .ogn files")
    end
    if not kit_sdk_bin_dir then
        premake.error("OGN node generator requires the global variable 'kit_sdk_bin_dir' point to the platform-specific build root")
    end
    if not pythonScriptPath then
        premake.error("OGN node generator requires the global variable 'pythonScriptPath' point to a path to run Python")
    end
    if not os.isdir(root) then
        premake.error("OGN node generator requires the global variable 'root' point to the directory where the Kit _build/ directory can be found")
    end

    -- Map out the locations for all of the generated files. Not set up initially since it relies on build time variables
    local ogn_path = path.getrelative(".", "%{root}/_build/ogn")
    local intermediate_path = path.getrelative(".", "%{cfg.objdir}".."/tags")
    local config_path = ogn_config_path()
    local docs_path = path.getrelative(".", docs_target_path)
    local include_path = ogn_path.."/include"
    local python_ogn_path = python_path.."/ogn"
    local python_tests_path = python_path.."/ogn/tests"
    local usd_path = python_tests_path.."/usd"
    local icon_path = path.getrelative(".", icon_target_path)
    local tools_ext_path = ogn_tools_ext_path()
    local tools_path = tools_ext_path.."/omni/graph/tools"
    local generate_node_path = tools_path.."/generate_node.py"
    local tools_tag_path = tools_ext_path.."/__updated__"
    local repo_man_path = path.getrelative(".", "%{root}/_repo/deps/repo_man")

    -- If debugging is turned on then output all of the defined variables
    if debuggingOGN() then
        print("OGN: Node generator information")
        print("     config_path              = ", config_path)
        print("     docs_path                = ", docs_path)
        print("     generate_node_path       = ", generate_node_path)
        print("     icon_path                = ", icon_path)
        print("     include_path             = ", include_path)
        print("     intermediate_path        = ", intermediate_path)
        print("     ogn_path                 = ", ogn_path)
        print("     python_ogn_path          = ", python_ogn_path)
        print("     python_tests_path        = ", python_tests_path)
        print("     settings                 = ", settings)
        print("     tools_path               = ", tools_path)
        print("     type_definition_path     = ", ogn.type_definition_path)
        print("     unwritable_ogn_directory = ", python_ogn_path)
        print("     usd_path                 = ", usd_path)
    end

    -- Set up the common build flags.
    -- The node generator command will generate files into the same directory for all generated files.
    -- Details within the node description file will determine whether those files are actually generated or not.
    -- Quote all of the paths just in case they contain spaces.
    local ogn_command = table.concat { pythonScriptPath,
        " \""..generate_node_path.."\"",
        " --configDir \""..config_path.."\"",
        " --cpp \""..include_path.."\"",
        " --docs \""..docs_path.."\"",
        " --extension \""..extension_name.."\"",
        " --icons \""..icon_path.."\"",
        " --intermediate \""..intermediate_path.."\"",
        " --module \""..project_name.."\"",
        " --python \""..python_ogn_path.."\"",
        " --tests \""..python_tests_path.."\"",
        " --usdPath \""..usd_path.."\"",
        " --unwritable \""..python_ogn_path.."\""
    }

    if ogn.type_definition_path ~= nil then
        ogn_command = ogn_command.." --typeDefinitions \""..ogn.type_definition_path.."\""
    end

    -- Although the command will accept the -toc command for backward compatibility it does not do anything at the
    -- moment. There is anticipation that at some point in the future when documentation generation moves out of
    -- kit_repo_docs.py then it might be needed again so for not it will be accepted and ignored to minimize future
    -- compatibility problems.
    -- if ogn.toc ~= nil then
    --     ogn_command = ogn_command.." -toc \""..ogn.toc.."\""
    -- end

    -- If there are any custom settings to pass construct that portion of the command line here
    if settings ~= nil then
        for _, setting in pairs(settings) do
            -- Some settings may have been processed already and "removed" by having entries set to nil - ignore those
            if setting ~= nil then
                ogn_command = ogn_command.." --setting \""..setting.."\""
            end
        end
    end

    if debuggingOGN() then
        ogn_command = ogn_command.." --verbose"
    end

    if pedanticOGN() then
        ogn_command = ogn_command.." --pedantic"
    end

    for _, file in pairs(ogn_file_list) do
        -- Confirm that the file type is correct
        if string.endswith(file, ".ogn") then
            add_files("ogn", ".", file)
            filter ("files:"..file)
                if debuggingOGN() then
                    buildmessage( "Running node generator on "..file )
                else
                    buildmessage( "%{file.basename}%{file.extension}" )
                end
                buildcommands { ogn_command.." --nodeFile \"%{file.abspath}\"" }
                buildinputs { "%{file.abspath}", tools_tag_path }
                buildoutputs { intermediate_path.."/%{file.basename}.ogn.built" }
            filter {}
        end
    end
end

-- ----------------------------------------------------------------------
-- Support for installing a node generator configuration file into a known common location.
-- @configuration_file: File to be installed
function install_ogn_configuration_file(configuration_file)
    repo_build.prebuild_copy {
        { configuration_file, ogn_config_path() },
    }
end

-- ----------------------------------------------------------------------
-- Create a project that will create index files for node documentation in this app. This can be called from any
-- premake file but it should only be called from one, otherwise the projects will be trying to write the same files.
-- @settings: table of settings to refine the project configuration
--            extra_roots (list[str]): If specified, the list of extra directories with extensions containing
--                                     node documentation files that should be included. BUILD/exts/ will always
--                                     be checked as that is where extensions usually live in the build tree.
--            verbose (bool): Add basic debugging information to the output
--            veryVerbose (bool): Add detailed debugging information to the output
function project_ogn_docs_index(settings)

    -- Work around the bug in "kind 'Utility'" on Linux to ensure the postbuildcommands run
    -- Utility projects don't work in Makefiles so create a dummy static lib project
    filter { "system:linux"  }
        kind "StaticLib"
        files { ogn_build_path().."/__LinuxStaticLibWorkaround.cpp" }
    filter {}
    filter { "system:windows"  }
        kind "Utility"
    filter {}

    local verbosity = ""
    local roots = " --extensionRoot \"%{root}/_build/%{platform}/%{config}/exts\""

    -- If there are any custom settings to pass construct that portion of the command line here
    if settings ~= nil then
        if settings.verbose ~= nil then
            verbosity = " --verbose"
            settings.verbose = nil
        end

        if settings.veryVerbose ~= nil then
            verbosity = " --veryVerbose"
            settings.veryVerbose = nil
        end

        if settings.extra_roots ~= nil then
            if type(settings.extra_roots) ~= "table" then
                print("extra_roots entry in project_ogn_docs_index settings must be an array, got"..type(settings.extra_roots))
            else
                for _, extra_root in pairs(settings.extra_roots) do
                    roots = roots.."  --extensionRoot \""..extra_root.."\""
                end
            end
            settings.extra_roots = nil
        end
    end

    -- Respect environment variable overrides to add debugging output to the index creation
    if os.getenv("OGN_DEBUG") ~= nil then
        verbosity = " --veryVerbose"
    elseif os.getenv("OGN_DOCS_DEBUG") ~= nil then
        verbosity = " --verbose"
    end

    -- After the build is done, assemble a table of contents in the ogn-generated documentation directory
    local docs_path = path.getrelative(".", "%{root}/_build/ogn").."/docs"
    local assembleTocCommand = table.concat { pythonScriptPath,
        " \""..extsbuild_dir.."/omni.graph.tools/omni/graph/tools/make_docs_toc.py\"",
        " --ognDirectory \""..docs_path.."\"", verbosity, roots
    }

    if verbosity ~= "" then
        print("OGN Index Command = "..assembleTocCommand)
    end

    postbuildcommands { assembleTocCommand }
end
