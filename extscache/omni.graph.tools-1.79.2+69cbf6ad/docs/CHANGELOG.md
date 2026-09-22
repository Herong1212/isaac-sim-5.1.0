(changelog_omni_graph_tools)=

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.79.2] - 2025-05-01
### Changed
- Prepare for Python-3.12

## [1.79.1] - 2024-09-10
### Fixed
- Fix security issues (OMPE-18747).

## [Unreleased]
## [1.79.0] - 2024-05-20
### Changed
-  Additional fix for OGN node generation build when using kit-kernel

## [1.78.0] - 2024-05-07
### Changed
-  Fix OGN node generation build when using kit-kernel

## [1.77.0] - 2024-02-14
### Added
- Code generate helper methods for pre and post render graph nodes, as part of the node database.

## [1.76.1] - 2024-02-05
### Changed
- Small fix for unit test.

## [1.76.0] - 2024-01-26
### Added
- More detailed database tests for better code coverage of generated code

## [1.75.0] - 2024-01-25
### Added
- Function to nicely format attribute and node type names for the user
- Pedantic mode for the node generator so that smaller details needing attention can emit warnings
### Changed
- Modified docs generator to use the nice formatting when an explicit override does not exist
- Updated the OGN best practices documentation with more information on execution attributes

## [1.74.0] - 2024-01-19
### Added
- Documentation for best practices in naming and documentation in .ogn files.
### Changed
- Modified repo tools to share common code and look in the DriveSim relative locations
- Changed nodes.json generator to call the script directly in the build rather than going through repo tools

## [1.73.0] - 2024-01-15
### Changed
- Moved nodes.json generation to a post build command

## [1.72.0] - 2024-01-12
### Changed
- Ogn scanner now prioritizes package files even with a version mismatch occurs

## [1.71.0] - 2024-01-12
### Added
- extras keyword for specifying the addition of generators not normally running
- Implementation of Python database generation for cpp nodes when it is added as an extra

## [1.70.0] - 2024-01-09
### Added
- Extra code coverage.

## [1.69.2] - 2024-01-02
### Fixed
- Removed an API test that changes state based on whether tests are running or not

## [1.69.1] - 2023-12-28
### Changed
- Avoid generation of unnecessary test code

## [1.69.0] - 2023-12-27
### Changed
- Changed test generation to use separate graphs instead of fresh scenes
- Threading tests now run multiple test cases at once

## [1.68.0] - 2023-12-19
### Added
- OGN_GENERATED_TEST_LIMIT can be used to limit the number of test cases that are run

## [1.68.0] - 2023-12-20
### Added
- Code coverage tests for attribute generation and some utilities

## [1.67.1] - 2023-12-20
### Added
- Extra code coverage.
### Removed
- Miscellaneous dead and/or redundant code-paths.

## [1.67.0] - 2023-12-19
### Added
- Testing for main_docs and generate_type_name_conversions tools
### Changed
- Configuration of the tools to allow for easier testing
### Removed
- Obsolete tool to add node type information to the .toml file - that approach will not be used

## [1.66.0] - 2023-12-15
### Removed
- The unused generated Python databases on C++ nodes

## [1.65.0] - 2023-12-08
### Changed
- Invalid extended types cause ogn parsing to fail

## [1.64.0] - 2023-12-05
### Changed
- Ensured the icon path written as metadata is relative

## [1.63.0] - 2023-12-01
### Changed
- Modified the icon path metadata to point to the build tree

## [1.62.1] - 2023-11-27
### Added
- Handle OSError that may be raised when the test module __init__.py file cannot be locked for writing.

## [1.62.0] - 2023-11-23
### Fixed
- init_instance and release_instance were not passing the instanceID to the user callback

## [1.61.1] - 2023-11-17
### Fixed
- Fixed exception when the number of node definitions to be imported as background tasks is less than the thread count.

## [1.61.0] - 2023-11-17
### Changed
- Deprecated the generated db.internalState and DB::sInternalState functions, in favor of the sharedState and perInstanceState version
- Stack created OGN databsases now have access to (auto)instances
### Added
- Generates the code in the python OGN database that can invoke init_instance and release_instance if implemented by the node writer

## [1.60.0] - 2023-11-09
### Added
- Coverage filtering for generated node types marked as internal:test

## [1.59.0] - 2023-11-09
### Changed
- Made documentation references consistent through use of substitutions

## [1.58.3] - 2023-11-06
### Fixed
- Import the tests synchronously when running the extension tests.

## [1.58.2] - 2023-11-02
### Fixed
- Leaking file handles from configuration files

## [1.58.1] - 2023-10-27
### Fixed
- Numpy type definitions in the conversions data

## [1.58.0] - 2023-10-22
### Changed
- Rearrangement of docs for AutoNode
### Added
- Tool for dumping the set of all available types to a .rst file

## [1.57.1] - 2023-10-18
### Changed
- Removed redundant variables generated in the database files, which cause compilation warnings.

## [1.57.0] - 2023-10-18
### Added
- OGN generator now instrument the database to take into account mapped attribute

## [1.56.1] - 2023-10-17
### Fixed
- Premake file filters were not handling update tag and type name conversion file correctly

## [1.56.0] - 2023-10-13
### Changed
- Renamed put_func to register_function to more accurately reflect what it is doing
### Added
- Methods for deregistering functions

## [1.55.0] - 2023-10-11
### Removed
- Incorrectly identified SDF types for attribute types without an equivalent
### Fixed
- Incorrect references to node types when it meant node type names

## [1.54.1] - 2023-10-06
### Added
- Dependency on omni.kit.test. Needed because we import nodes' test modules even when not running tests and they import omni.kit.test.

## [1.54.0] - 2023-10-06
### Changed
- Moved ogn_types.py to an AutoNode specific location
### Added
- Repo tools command and support for creating file mapping all supported type representations
- Module for providing the above mapping data
### Removed
- Obsolete data_types.py file

## [1.53.0] - 2023-09-29
### Changed
- Reorganized AutoNode documentation to reflect separation of runtime and developer mode
- Hid some deprecated code

## [1.52.0] - 2023-09-28
### Changed
- Access the IAttribute interface from an object instead of from Carbonite where it could fail

## [1.51.0] - 2023-09-21
### Added
- Explicit module for type annotations in the .toml file
### Changed
- Generated compute functions, to simplify the parameters they accept

## [1.50.0] - 2023-09-18
### Added
- Access for the cudaPointers keyword
- Added code generation to get cudaPointer value into the metadata

## [1.49.0] - 2023-09-13
### Changed
- Location processing for AutoNode toml definitions
- Documentation for AutoNode to add information about the setting
- Import location for data type definitions
- AutoNode generator tool argument list
- compute generation for AutoNode definitions
### Added
- Implementation of AutoNode generator calls as part of build
### Fixed
- Syntax of test generated .toml files

## [1.48.0] - 2023-09-08
### Added
- Functionality and test to generate the nodes.json node type definition metadata file programmatically

## [1.47.0] - 2023-08-31
### Added
- Tests for all types with the generator
### Changed
- Modified the generator to recognize all legal OGN type definitions
### Removed
- Support for plain Python types, temporarily

## [1.46.2] - 2023-08-02
### Changed
- Fixed config for generating matrix2d types.
- Adding matrix2d to matrices union configuration.

## [1.46.1] - 2023-08-02
### Changed
- Fix for a small test generation error when reading test file paths.

## [1.46.0] - 2023-07-31
### Removed
- Obsolete autograph support

## [1.45.2] - 2023-07-30
### Removed
- Long deprecated function that has no body

## [1.45.1] - 2023-07-28
### Removed
- Unnecessary Linux file copy for doc index building

## [1.45.0] - 2023-07-26
### Added
- Ability to utilize external test scenes in .ogn "tests" constructs.

## [1.44.0] - 2023-07-25
### Changed
- Revert output and state bundle name space separator to underscore

## [1.43.0] - 2023-07-13
### Removed
- Obsolete documentation special case for tutorial nodes

## [1.42.1] - 2023-07-14
### Added
- Error handling for when a generated test file is unreadable

## [1.42.0] - 2023-07-11
### Changed
- Moved the post build command project to a common area so that it can be shared by downstream repos

## [1.41.1] - 2023-06-28
### Changed
- Small edit to parsing logic for the "pure" scheduling hint.

## [1.41.0] - 2023-06-27
### Changed
- Modified toc specification to point to an extension-local directory
- Changed the ogn file dependencies to not include the table of contents generator files
- Modified generation and parsing of per-extension index files to link to local files instead of the node library
- Modified format of generated node documentation files to correspond to what is found in the node library
### Added
- Extension root parameter to the node documentation index generator
- veryVerbose flag to the node documentation index generator for extra output
- Deprecation support for constant objects
- Ability to specify pre and post documentation files for any node
- Support for CSV table output in restructuredText and readable directory list for argparse arguments

## [1.40.1] - 2023-06-27
### Changed
- OGN node and test generation is multi threaded
- OGN nodes and test modules can be imported in parallel on multiple threads
- Python tests are imported on a separate thread

## [1.40.0] - 2023-06-22
### Added
- Parsing logic for new "pure" scheduling hint.

## [1.39.0] - 2023-05-31
### Fixed
- Adjusted the CRLF settings for the generated .md node table of content files

## [1.38.0] - 2023-05-29
### Fixed
- Regeneration of table of contents with new data
- Algorithm looking for location of the config dir in downstream repos

## [1.37.0] - 2023-05-26
### Added
- Keyword CREATE_ATTRIBUTES for controller.edit() function

## [1.36.2] - 2023-05-23
### Changed
- Small comment change.

## [1.36.1] - 2023-05-11
### Added
- Warning to generated code for input bundle that is invalid but is required for computation

## [1.36.0] - 2023-05-09
### Fixed
- Refactored deprecation decorators to work in more cases
### Added
- Beefed up the deprecation tests

## [1.35.1] - 2023-05-08
### Fixed
- Bug with Python code generator for BundleContents

## [1.35.0] - 2023-05-08
### Deprecated
- Removed deprecated locations of Python modules

## [1.34.0] - 2023-05-02
### Added
- Parsing support for the addition of node type forwarding for a node type in the .ogn file

## [1.33.0] - 2023-05-02
### Changed
- Changed the dynamic attribute accessors getDynamicInputs(), getDynamicOutputs(), getDynamicStates() to return gsl::span.

## [1.32.0] - 2023-04-19
### Deprecated
- Removed all references to ContextHelper and OmniGraphHelper
- Old .ogn test specification format no longer supported

## [1.31.0] - 2023-04-11
### Added
- Generation of the table of contents documentation for nodes
### Changed
-
### Removed
- Obsolete unitTest flag from the node generator command
- Unnecessary import in generated Python tests

## [1.30.0] - 2023-04-07
### Added
- Generate code for OmniGraphDatabase to cache dynamic input, output and state attributes.

## [1.29.0] - 2023-04-06
### Added
- Ability to use allowedTokens as a top level definition for attributes
- Ability to reference an allowedToken by name or value as a default in the .ogn
- Tests for the new functionality
### Fixed
- Stored tokens internally with reference counts to avoid sporadic illegal data accesses

## [1.28.0] - 2023-03-31
### Changed
- target attributes now use relationships with output and state ports

## [1.27.3] - 2023-03-28
### Changed
- Filtered out cpp nodes from using batched reads and writes

## [1.27.2] - 2023-03-24
### Changed
- target python wrapping changed from string to usdrt Sdf.Path

## [1.27.1] - 2023-03-22
### Fixed
- Made all docstrings to publicly visible documentation consistent

## [1.27.0] - 2023-03-21
### Fixed
- Use top level Python module's name instead of ext_id as module name when generating cached node code

## [1.26.0] - 2023-03-17
### Added
- Implementing target attribute type

## [1.25.0] - 2023-03-17
### Added
- Generate an __update__ file indicating that the tools scripts are up to date
- Build support for respect of the __update__ file when deciding whether to regenerate from .ogn files
- Updated category_definitions to use Python 3.10 type syntax, mostly as a test for incremental rebuilds

## [1.24.0] - 2023-03-14
### Changed
- Default of cudaPointers on Python nodes is now CPU instead of CUDA as it was before, mainly for Warp

## [1.23.0] - 2023-03-09
### Added
- Change default index for static version of internal state to return the authoring graph
- Added wrappers for shared and per-instance versions of internal state functions

## [1.22.11] - 2023-02-28
### Fixed
- Rebuild python Database if input bundles are invalid

## [1.22.10] - 2023-02-27
### Added
- Generation of OGN tests on vectorized data

## [1.22.9] - 2023-02-25
### Changed
- Modifed format of Overview to be consistent with the rest of Kit

## [1.22.8] - 2023-02-22
### Added
- Removed debugging print

## [1.22.7] - 2023-02-21
### Added
- ThreadsafetyTestUtils to public API.

## [1.22.6] - 2023-02-19
### Changed
- Added label to the main doc page so that higher level docs can reference the extension

## [1.22.5] - 2023-02-14
### Fixed
- Made test file pattern account for node files not beginning with Ogn

## [1.22.4] - 2023-02-08
### Changed
- Modified lookup of target extension version to account for the modified path names

## [1.22.3] - 2023-02-07
### Fixed
- Removed an unused import

## [1.22.2] - 2023-02-02
### Fixed
- Lint error that appeared when pylint updated

## [1.22.1] - 2023-01-30
### Changed
- Removed the kit-sdk landing page
- Moved all of the documentation into the new omni.graph.docs extension

## [1.22.0] - 2023-01-16
### Changed
- Split functions and added configuration information to make the ogn project builds more flexible

## [1.21.1] - 2023-01-11
### Changed
- Sort the generated Python import statements to ensure a consistent ordering

## [1.21.0] - 2023-01-11
### Changed
- OGN generator for vectorization

## [1.20.1] - 2022-12-14
### Fixed
- Made build level access of config directory account for being inside the SDK as well as in the build

## [1.20.0] - 2022-12-13
### Changed
- Attribute Union Definitions are now loaded from a json configuration file(AttributeUnionConfiguration.json)

## [1.19.0] - 2022-12-02
### Changed
- Modified Python node type code generation process to handle multiple versions on-demand

## [1.18.1] - 2022-11-30
### Fixed
- Output formatting for string and token defaults containing special characters

## [1.18.0] - 2022-10-21
### Added
- Internal utilities for support of testing node type registration

## [1.17.0] - 2022-09-30
### Fixed
- Changed code emission to avoid defining interface that will not be used

## [1.16.3] - 2022-09-14
### Added
- Better documentation for categories
### Removed
- Testing for obsolete transform data type

## [1.16.2] - 2022-08-30
### Fixed
- Linting errors

## [1.16.1] - 2022-08-24
### Fixed
- AttributeManager has_* generated methods for optional extended attributes.

## [1.16.0] - 2022-08-19
### Added
- Support for new setting that turns deprecations into errors
- Tests for deprecation code
- Access to deprecation message logs to use for testing

## [1.15.3] - 2022-08-16
### Changed
- Refactored checking for legal extension name as Python import

## [1.15.2] - 2022-08-09
### Fixed
- Applied formatting to all of the Python files

## [1.15.1] - 2022-08-05
### Fixed
- All of the lint errors reported on the Python files in this extension

## [1.15.0] - 2022-08-01
###
- Change `m_primHandle` to `m_bundleHandle` in `BundleAttributeManager`

## [1.14.1] - 2022-07-25
###
- Added ALLOW_MULTI_INPUTS metadata key

## [1.14.0] - 2022-07-13
###
- Added UI_TYPE metadata key, added class method to MetadataKeys to get all the metadata key strings

## [1.13.0] - 2022-07-08
### Added
- Support for 'deprecation' attribute keyword in .ogn files.

## [1.12.0] - 2022-07-07
### Changed
- Refactored import of non-public API to emit a deprecation warning
- Moved node_generator/ into the _impl section
### Added
- Support for fully defined Python API at the omni.graph.tools level
- Support for fully defined Python API at the omni.graph.tools.ogn level
- Support for public API consistency test

## [1.11.0] - 2022-06-28
### Changed
- Merged to USD and import generated tests and added enhanced generated code coverage

## [1.10.0] - 2022-06-23
### Removed
- Support for the deprecated Autograph functionality, now in omni.graph.core.autonode

## [1.9.1] - 2022-06-17
### Fixed
- Corrected bad API documentation formatting
### Added
- Documentation links for Python API

## [1.9.0] - 2022-06-13
### Added
- Check to see if values are already set before initializing defaults in Python nodes

## [1.8.1] - 2022-06-08
### Fixed
- Add stdint include when constructing node database files.

## [1.8.0] - 2022-06-07
### Added
- Support for generator settings to alter the generated code
- Generator setting for Python output optimization
- Build flag to modify generator settings
- Generator script support for generator settings being passed around

## [1.7.0] - 2022-05-27
### Added
- Ability for the controller to take an attribute description as the first parameter instead of only attributes

## [1.6.2] - 2022-05-17
### Fixed
- Improved node description formatting by using newlines to indicate paragraph breaks

## [1.6.1] - 2022-05-11
### Added
- Category for UI nodes

## [1.6.0] - 2022-05-10
### Added
- Ability to use @deprecated_function with property getters and setters.

## [1.5.4] - 2022-05-06
### Fixed
- Fixed the emission of the CPU to GPU pointer information for output bundles

## [1.5.3] - 2022-04-29
### Fixed
- Fixed incorrect line highlighting in user guide

## [1.5.2] - 2022-04-25
### Fixed
- Stopped generating bundle handle extraction in situations where the handle will not be used

## [1.5.1] - 2022-04-05
### Fixed
- Removed regeneration warning until such time as the regeneration actually happens

## [1.5.0] - 2022-03-24
### Fixed
- Fixed generated contents of tests/__init__.py to be constant
- Refactored generation to use standard import pattern
- ### Added
- Ability to create generated directories on the fly rather than insisting they already exist

## [1.4.0] - 2022-03-14
### Added
- *ensure_nodes_in_toml.py* to add the **[[omnigraph]]** section to the extension.toml file

## [1.3.2] - 2022-03-14
### Added
- examples category

## [1.3.1] - 2022-03-09
### Added
- Added literalOnly to the list of metadata keys
- Added some explanation for the literalOnly metadata key to the OGN reference guide

## [1.3.0] - 2022-03-08
### Changed
- Changed the naming of the generated tests to be shorter for easier use in TestRunner
- Changed the generated USD to use the schema prims
- Changed the generated test scripts to use the schema prims
- Removed unused USD metadata from generated code

## [1.2.4] - 2022-03-08
### Changed
- Modified C++ generated code node registration to match *omni.graph.core 2.23.3*

## [1.2.3] - 2022-02-15
### Added
- script node category

## [1.2.1] - 2022-02-10
### Added
- Unset the useSchemaPrims setting for tests until they are working

## [1.2.0] - 2022-02-09
### Changed
- Moved autograph to omni.graph.core, retained imports for backward compatibility

## [1.1.1] - 2021-08-30

### Breaking Changes
- Type names have changed. `Float32` is now `Float` and `Int32` is now `Int`.

### Improvements and Bugfixes
- *BUGFIX* Fixed type initializers in autograph
- *PERF IMPROVEMENT* Functions using Autofunc now use code generated at read time instead of runtime lookups.
- *UI IMPROVEMENT* Nodes no longer have extra connections with the node name.

## [1.1.0] - 2021-08-19

### Adds Autograph
Added Autograph tools and types

## [1.0.0] - 2021-03-01
### Initial Version
- Started changelog with initial released version of the OmniGraph core
