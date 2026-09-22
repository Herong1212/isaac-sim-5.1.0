(changelog_omni_graph_exec)=

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.6] - 2025-01-08
### Fixed
- cppcheck was complaining about some dangling return values.

## [0.9.5] - 2025-01-03
### Fixed
- Buffer overrun in SmallStack::_allocExternalAndCopyInternal().

## [0.9.4] - 2024-02-02
### Changed
- Fix a deadlock that can occur during combined parallel-recursive on-demand execution that's invoked via
  ExecutionController::executeDefinition.
- Fixed some comment formatting.

## [0.9.3] - 2024-01-31
### Added
- An IScheduleFunction interface implementation to the ScheduleFunction.h header to help reduce
  code duplication (the interface was being implemented in multiple different spots using the
  same code).
### Changed
- Inlined IExecutor method to use the new ScheduleFunction implementation.

## [0.9.2] - 2024-01-17
### Changed
- Logging level for TestProfiling to reduce the amount of unnecessary console output when
  running the unit tests.

## [0.9.1] - 2023-12-08
### Added
- Disambiguation logic for accessing the getUseCount method from objects that implement
  multiple different interfaces that derive from omni::graph::exec::unstable::IBase.
- Unit test to validate that the method is now accessible for such objects.

## [0.9.0] - 2023-11-30
### Added
- Extra code coverage for EF.
### Changed
- Miscellaneous refactorings and clean-up in the EF core.

## [0.8.1] - 2023-11-15
### Changed
- ExecutionContext::applyOnEach can now be applied to the top-level execution graph's NodeGraphDef.

## [0.8.0] - 2023-11-09
### Changed
- ExecutionContext now returns an eSuccess status if executeNode is called on a node without an
  associated definition.
- The templated Executor implementation of IExecutor that comes with EF will return early with an
  eSuccess status if the root task that's being processed in the top-level/"main" execute() method
  has no children.
### Added
- A specialized ExecutorSingleNode that's used exclusively by ExecutionContext::executeNode to
  ensure that the temporary executor doesn't needlessly continue traversing the graph, scheduling
  work, etc. once the targeted node has been evaluated.
- Unit tests to validate the aforementioned changes.

## [0.7.1] - 2023-10-16
### Changed
- Updated documentation for ExecutionContext::isExecutingThread.

## [0.7.0] - 2023-10-09
### Changed
- Modified ExecutionContext to store an unordered_map of context-kickstarting thread IDs rather than
  just a single thread ID. This helps allow for multiple threads to kickstart execution from a single
  context.
- Added new unit tests for ExecutionContext.

## [0.6.0] - 2023-09-27
### Changed
- Exposed the unique id for pass objects in the public, ABI-safe
  PassTypeRegistryEntry struct, which allows passes registered in
  one .dll to be de-registered from an entirely different .dll.
- Small documentation updates (mostly grammatical).
- Updates to the GraphUtils to better handle duplicate node names
  and to provide an option for creating simplified+deterministic
  versions of GraphViz files for use in automated unit tests.

## [0.5.0] - 2023-08-17
### Added
- Added constructor for ExecutionPath taking a span of nodes.

## [0.4.0] - 2023-07-21
### Updated
- Renamed Node::createForDef to Node::create.
### Removed
- Duplicate code patterns for Node::create methods; API refactoring.

## [0.3.0] - 2023-07-17
### Updated
- Renamed IPassPipeline::execute_abi to IPassPipeline::run_abi.

## [0.2.8] - 2023-07-17
### Fixed
- Replaced nonexistant FallbackExecutor documentation references to the correct ExecutorFallback.

## [0.2.7] - 2023-04-17
### Updated
- Split graph traversal documentation into 2 separate sections; basic traversal code examples are now in the "Guides"
section, while the more expansive background information, definitions, animations, advanced code examples, etc. remain
in the original "Advanced" article.

## [0.2.6] - 2023-04-11
### Updated
- Revisions for graph traversal documentation (with new images, animations, examples, edited sections, etc.).

## [0.2.5] - 2023-04-03
### Added
- Graph traversal documentation (minus a couple WIP images).

## [0.2.4] - 2023-03-26
### Updated
- A new `disconnect` method for removing edges between EF nodes.
### Changed
- `remove` method to not perform any automatic reconnections between nodes after removing the target node from the IR.

## [0.2.3] - 2023-03-23
### Added
- Support for single-node cycles.
### Updated
- A couple unit tests to exercise single-node cyclical behavior.

## [0.2.2] - 2023-03-22
### Fixed
- Small alterations to Tarjan's algorithm implementation + VisitLast + VisitAll strategies to work correctly in cyclical graphs where the children of the root node(s) are members of siad cycles.
### Added
- A few new unit tests to exercise EF in situations where children nodes of roots are involved in cycles.
### Changed
- Some refactoring of a couple already-existing unit tests/unit test utilities.

## [0.2.1] - 2023-02-22
### Changed
- Renamed omni.kit.exec references to omni.kit.exec.core

## [0.2.0] - 2023-02-10

- **Breaking**: Pass registration methods now use `ConstName` rather than a hash when specifying the name of nodes/defs
  to match.

## [0.1.1] - 2023-01-30

- Added link at the top of the changelog for docs

## [0.1.0] - 2022-11-14

Initial version
