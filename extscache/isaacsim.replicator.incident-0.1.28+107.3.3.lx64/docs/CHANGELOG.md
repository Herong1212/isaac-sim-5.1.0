# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.28] - 2025-10-06
- fix event panel button when event section is not in config file

## [0.1.27] - 2025-09-10
- NavMesh API update

## [0.1.26] - 2025-08-26
- Internal code change

## [0.1.25] - 2025-07-30
- Internal code change

## [0.1.24] - 2025-07-28
- Internal dependency update

## [0.1.23] - 2025-07-16
- Fix typo

## [0.1.22] - 2025-07-10
- more data validation

## [0.1.21] - 2025-07-08
- Fix scene tagging menu lifetime issues

## [0.1.20] - 2025-07-07
- Add to logging for spill area search

## [0.1.19] - 2025-07-03
- Fix issues of saving config file in UI
- Update the recording condition checking

## [0.1.18] - 2025-07-02
- Update IRI UI elements

## [0.1.17] - 2025-07-01
- lifetime bugfix for IRI scene tagging menu

## [0.1.16] - 2025-06-25
- Update broken UI logic for updating seed

## [0.1.15] - 2025-06-12
- fix test settings in extension.toml

## [0.1.14] - 2025-06-06
- ux improvements

## [0.1.13] - 2025-06-05
- Menu items relocated to Tools>Action and Event Data Generation

## [0.1.12] - 2025-06-03
- Remove broken dependency of IRI on OAP

## [0.1.11] - 2025-05-30
- Update incident->event naming in UI

## [0.1.10] - 2025-05-29
- Rename 'Incident' to 'Events'

## [0.1.9] - 2025-05-29
- Internal code change

## [0.1.8] - 2025-05-23
- Adjust settings for IRI to run standalone in Isaacsim
- adjust fractional cutoff opacity for rendering spills
- include navmesh bundle to get UI for baking navmesh

## [0.1.7] - 2025-05-22
- Give IRI access to the timeline end extender in case the user hasn't set the scene long enough for the events defined.

## [0.1.6] - 2025-05-19
- Ensure consistent extension name and title

## [0.1.5] - 2025-05-09
- Bugfixes relating to IRI config file UI

## [0.1.4]
- Updated scene tagging UI which has now moved to the menu position tools>replicator

## [0.1.3] - 2025-04-22
- Incident parsing is handled by ConfigFile parser from OMU as a section of the IRA config file
- Incidents now accept general triggers defined in IRA config file properties
- Semantic labeling of indicent prims is now dynamic
- Resimulate bug fixes

## [0.1.2] - 2025-04-07
- Supports toppling items with the physx engine, spontaneous fires with omni.flowusd and liquid spills with a custom simulation.
- Integrates with IRA to produce randomized incidents.
- Adds a scene tagging UI to tag incident items in the scene.
- Upgrades to Kit 107.2.

## [0.1.1] - 2025-04-03
- Prepare for Kit 107.2.

## [0.1.0] - 2025-01-09
- Initial version of the isaacsim.replicator.incident extension.
