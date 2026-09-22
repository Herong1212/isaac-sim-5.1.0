
# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.0.32] - 2025-09-04
- Moved IRC assets into the nucleus server

## [0.0.31] - 2025-07-30
- Asset path update

## [0.0.30] - 2025-07-15
- Fixed a bug where output path's value was being overwritten by the config file

## [0.0.29] - 2025-06-12
- fix test settings in extension.toml

## [0.0.28] - 2025-06-09
- Exposed output path which is an IRC parameter through a textbox in the UI panel

## [0.0.27] - 2025-06-06
- Fixed an issue with IRC's integration with IRO for IsaacSim

## [0.0.26] - 2025-06-06
- Menu items relocated to Tools>Action and Event Data Generation

## [0.0.25] - 2025-06-05
* Fixes a UI issue where the text input widget for IRC's stage wasn't showing up

## [0.0.24] - 2025-06-04
* Fixed a bug with incorrectly trying to fetch prim from USD path

## [0.0.23] - 2025-06-03
* Now handles API calls more gracefully if the NIM endpoint is incorrect or a timeout occurs

## [0.0.22] - 2025-06-02
* Suppress confusing warning messages about prim not being found
* addressed an issue relating to a confusing folder creation message appearing when a folder clearly is created
* Changed the model to use meta/llama3-8b-instruct instead

## [0.0.21] - 2025-05-29
- State of the caption results is cleared every time the user hits the Gen Captions button
- Files are updated only when a caption is generated
- If both the NIM_API_KEY and key are missing only then do we produce a warning message

## [0.0.20] - 2025-05-29
- Internal code change

## [0.0.19] - 2025-05-28
- Now properly picks up the NIM key when IRC is called through a writer
- Fixed some issues with the writers
- Added IRO and IRA config files with IRC writers as samples

## [0.0.18] - 2025-05-22
- Updated the model to use llama3-70b-instruct
- Also removed the Q&A widget from the Captions Result panel


## [0.0.17] - 2025-05-19
- Ensure consistent extension name and title

## [0.0.16] - 2025-05-20
- Changed USD asset references from nucleus to S3 staging

## [0.0.15] - 2025-05-12
- Enable LLM service use to external users

## [0.0.14] - 2025-04-23
- Changed the UI to make camera prim path selection be a combobox that's automatically populated once a stage is loaded
- Hooked up UI to file picker widget to select a USD stage asset to load
- Made the caption widget contents copyable for where the caption is written and presented to the user.
- Now accepts caption related inputs from the IRC UI

## [0.0.13] - 2025-04-22
- Added the capability to pick up caption and semantic_label from the prim, itself, if available, if it's not in the MONGODB
- Removed the DB UI from the IRC panel

## [0.0.12] - 2025-04-07
- Added patch for empty segmentation or no segmentation required in IRO
- Give early warning about mongodb_uri missing
- Added a DB UI to construct a DB URI. Passes the handler to the object caption reader.
- Added an LLM endpoint UI.
- Abstracted DB functionality to make way for other DBs to pull object captions from.
- Upgrades to Kit 107.2.

## [0.0.11] - 2025-03-01
- Republished due to repo URL change

## [0.0.10] - 2025-01-13
- 1. now support azure OpenAI API key in general, on both Linux and Win
- 2. make IRA configs and output names consistant with IRO output
- 3. Fixed some typos and improved printout logs

## [0.0.9] - 2024-12-19
- Allow passing configs by config file to IRC. Default config file added.
- Improved spatial computing method in support decision
- Reorganized IRC UI and output format
- Added docstrings

## [0.0.8] - 2024-12-10
- Add IRObjectCaptionWriter for Isaacsim.replicator.object, dynamic import only
- Enabled multi-camera output for IRO when it uses IRC writers
- Add e2e test at CI/CD

## [0.0.7] - 2024-11-21
- Add CombinedIROSceneGraphWriter for Isaacsim.replicator.object, dynamic import only
- Reorganized IRO writers for cleaner codes
- Added image export for IROSceneGraphWriter

## [0.0.6] - 2024-11-20
- Add IROSceneGraphWriter for Isaacsim.replicator.object, dynamic import only

## [0.0.5] - 2024-11-19
- Use dynamic install of OpenAI dependency to avoid conflict with omni.ai.langchain.core

## [0.0.4] - 2024-11-18
- SceneGraphWriter bug fix
- Simplify warning printouts

## [0.0.3] - 2024-11-12
- Update extension name from omni to isaacsim
- Move writer from IRA to IRO

## [0.0.2] - 2024-10-31
- Bug fix

## [0.0.1] - 2024-10-09
### Added
- Initial commit
