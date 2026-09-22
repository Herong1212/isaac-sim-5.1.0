# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.7.11] - 2025-09-10
- NavMesh API update

## [0.7.10] - 2025-08-26
- Fix the UI hang

## [0.7.9] - 2025-07-28
- Push notification if command file is not saved on simulation start

## [0.7.8] - 2025-07-11
- Removed a redundant branch

## [0.7.7] - 2025-06-12
- fix test settings in extension.toml

## [0.7.6] - 2025-06-05
- Menu items relocated to Tools>Action and Event Data Generation

## [0.7.5] - 2025-05-29
- Internal code change

## [0.7.4] - 2025-05-19
- Ensure consistent extension name and title

## [0.7.3] - 2025-05-16
- upgrade to event system 2.0

## [0.7.2] - 2025-05-12
- Added incident and agent response to the confi file and UI

## [0.7.1] - 2025-04-24
- Use Searchfield for filters and NavMesh Areas
- Re-arrange UI layout
- Add icons
- Replace the save text button with a icon button

## [0.7.0] - 2025-04-22
- Upgrade to Kit 107.3
- Rename Transporter to iw.hub
- Changed character.filters from string to list

## [0.6.1] - 2025-04-07
- Upgrades to Kit 107.2

## [0.6.0] - 2025-04-03
- Prepare for Kit 107.2

## [0.5.14] - 2025-03-01
- Republished due to repo URL change

## [0.5.13] - 2025-01-10
- Version match with core

## [0.5.12] - 2025-01-08
- Fixed loading custom animations from S3

## [0.5.11] - 2024-12-24
- Version match with core

## [0.5.10] - 2024-12-20
- Version match with core

## [0.5.9] - 2024-12-16
- Upgraded NavMesh version

## [0.5.8] - 2024-12-12
- Disable lidar cameras

## [0.5.7] - 2024-12-10
- Fixed a bug that causes Queue to show as character

## [0.5.6] - 2024-12-05
- Version match with core

## [0.5.5] - 2024-12-04
- Fixed the "Save As" button

## [0.5.4] - 2024-11-22
- Version match with core

## [0.5.3] - 2024-11-15
- Fix errors in which windows can't be closed and are out of sync with the menu
- All AgentSDG windows will use one SimManager instance
- Fix the error where previously loaded config file will not be loaded after closing and reopening the window

## [0.5.2] - 2024-11-09
- Fixed a bug in the Replicator Settings panel that causes output directory to be overwritten.

## [0.5.1] - 2024-11-01
- Version match with core

## [0.5.0] - 2024-10-31
- Scene Settings Panel is merged with the Global Settings Panel
- Added color code for invalid input and unsaved changes
- Moved some functionality, including command injection and custom command, to seperate menu windows.
- Improved the Custom Command Randomization Panel
- Replicator Settings Panel is changed to adapt the writers change.
- Code is more modularized.
- Compatibility with Kit 106.4
- Extension renamed to isaacsim.replicator.agent.ui


## [0.4.0] - 2024-08-27
- Use home directory for default writer output
- Merge robot module to ORA and code refactor
- Added a new writer called DHWriter to enable auto-labeling of DH character attributes
- Code change related to the omni.anim.navigation-106.1 update

## [0.3.2] - 2024-08-05
- Version match with core

## [0.3.1] - 2024-07-10
- Improved the robot spawning such that it checks the AABB for the robots to prevent spawning inside the static obstacles
- SDG now runs synchronously by default

## [0.3.0] - 2024-06-28
- Camera and Lidar list input support
- Command Randomizer for Custom Commands

## [0.2.4] - 2024-06-07
- update extension dependency versions

## [0.2.3] - 2024-05-23
- fix simulation length typo
- fix ui typo

## [0.2.2] - 2024-05-17
- add omni.kit.window.section constraint for camera_calibration
- refine warning messages

## [0.2.0] - 2024-05-13
- fix corrupted icon
- bump up version in the default config file

## [0.1.16] - 2024-05-07
- fix version constraint

## [0.1.15] - 2024-05-06
- Matching core version

## [0.1.14] - 2024-04-15
### Changed
- Setup UI features
