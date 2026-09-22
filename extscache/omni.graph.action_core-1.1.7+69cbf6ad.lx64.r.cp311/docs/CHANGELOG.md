(changelog_omni_graph_action_core)=

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.7] - 2024-07-16
### Changed
- Reduce scope of mutex lock to prevent dead-lock

## [1.1.6] - 2024-02-27
### Changed
- Removed usd dependency

## [1.1.5] - 2024-01-30
### Fixed
- bug canceling action latent node

## [1.1.4] - 2023-12-20
### Changed
- Modify ActionContainerGraphDef's executor to use the SafeDispatch scheduling strategy.

## [1.1.3] - 2023-11-29
### Fixed
- Added validity checks to ensure node type is still active when scheduling

## [1.1.2] - 2023-11-01
### Fixed
- Potential crash using dependency folding

## [1.1.1] - 2023-10-18
### Changed
- Using the added 'canEvaluate' ABI from core

## [1.1.0] - 2023-09-28
### Add IActionGraphNodes

## [1.0.0] - 2023-08-10
### Move IActionGraph from omni.graph.action
