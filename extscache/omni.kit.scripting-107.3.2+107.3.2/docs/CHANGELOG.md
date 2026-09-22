# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [107.3.2] - 2025-07-16
- Update to use kit-sdk 107.3.2

## [107.3.1] - 2025-06-22
- Update to use kit-sdk 107.3.1

## [107.3.0] - 2025-05-14
- Update to use kit-sdk 107.3.0

## [107.0.8] - 2025-04-15
- Update to use kit-sdk 107.2.0
- Enable arm packages

## [107.0.7] - 2024-12-18
- Removes legacy viewport extension dependency
- Fix to ensure security check does not load and execute scripts
- Updated to use kit sdk 107.0.3

## [107.0.6] - 2024-12-11
- Fix a regression in script_manager.py for invalid addition on_destroy/on_init on stage chanages

## [107.0.5] - 2024-12-05
- Updated to kit-sdk 107.0.2

## [106.5.5] - 2025-04-14
- Fix to ensure script load immediately after assigned to prim

## [106.5.4] - 2025-02-25
- Clean up extensions to not use _omniclient member of omni.client

## [106.5.3] - 2025-02-11
- Removes legacy viewport extension dependency
- Fix to ensure security check does not load and execute scripts
- Updated to use kit sdk 106.5.2

## [106.5.2] - 2024-12-11
- Fix a regression in script_manager.py for invalid addition on_destroy/on_init on stage chanages

## [106.5.1] - 2024-12-05
- Fixes script not loading properly and on changes to scripts assigned
- Changes to not depend directly on numpy with python.pipapi

## [106.5.0] - 2024-12-04
- Updated to use kit sdk 106.5.0

## [106.4.0] - 2024-12-03
- Updated to use kit sdk 106.4.0
- Fixes Warning when adding Python Scripting on a prim
- Fixes Script instance not removed when prim is removed
- Fixes hot-reload when loaded script is saved

## [106.3.1] - 2024-10-24
- Fix build ui error when performing certain operations from on_init

## [106.3.0] - 2024-09-25
- Updated to use kit sdk 106.3

## [106.2.0] - 2024-09-24
- Updated to use kit sdk 106.2

## [106.1.1] - 2024-08-20
- Fixes for USD Schema warnings

## [106.1.0] - 2024-08-07
- Updated to use kit sdk 106.1

## [106.0.0] - 2024-03-16
- Updates to use kit sdk 106.0
- Fixes hang from omni.client.stat

## [105.2.3] - 2024-02-09
- Fixes to correct the return type for BehaviorScript.message_bus_event_stream

## [105.2.2] - 2023-10-13
- Changes `BehaviorScript.on_update` to be executed from stage_update events instead of app tick events.

## [105.2.1] - 2023-09-28
- Adds support to pass template file to ScriptEditor.create_script_file

## [105.2.0] - 2023-09-27
- Update to use Kit SDK 105.2

## [105.1.2] - 2023-09-12
- Fixes usd notice listener sync performance issue.

## [105.1.1] - 2023-07-06
- Fixes warning from [python.pipapi] that was missing args use_online_index = true

## [105.1.0] - 2023-07-05
- Fixes traversal perf on large stages by moving to usdrt and some other traversal changes.

## [105.0.9] - 2023-05-10
- Fixed a bug where it would always error if you tried to save a script to a nucleus location via the edit button

## [105.0.8] - 2023-04-28
- parameter ui script edit button shows an error message and aborts when it fails to create a file

## [105.0.7] - 2023-04-27
- changed timeline event order to 1000000 so script events always get executed last
- added an edit button for python scripts in the parameter ui
- added a feature for copying python scripts to a location on your machine if they're http paths, and remapping paths in the scene

## [105.0.6] - 2023-02-02
- Fixes python path resolving for kit-sdk fast path resolver changes in kit-kernal

## [105.0.5] - 2023-02-02
- Fixes for higher fidelity for on_update that is not linkined to stage updates.
- Fixes Create script menus not showing up.

## [105.0.4] - 2023-01-31
- Fixes for not being able to attach local BehaviorScript when the stage usd is on an omni server.

## [105.0.3] - 2022-12-22
- Fixes for break in omni.client library api breaking changes.

## [105.0.2] - 2022-12-22
- Do not show edit/new python scripts option in read-only context.

## [105.0.1] - 2022-11-23
- Fixes warning message dialog on remote USD files.

## [105.0.0] - 2022-11-22
- Update kit-sdk 105.0

## [104.1.2] - 2022-11-22
- Fixes regression with invalid reload on stop when AnimationGraph attached.
- Fixes for remote script subfolder load.
- Fixes support for relative from .. imports back to root assigned scripts folder.

## [104.1.1] - 2022-11-18
- Fixes for remote script dependencies

## [104.1.0] - 2022-11-04
- Adds new BehaviorScript overrides for on_play, on_pause, on_stop
- Adds new BehaviorScript helper properties.
- Fixes reload on local dependencies script changes.

## [104.0.19] - 2022-11-03
- Fixes recovery from on_init and on_update script errors

## [104.0.18] - 2022-11-01
- Fix to windows dont require closing to open new script files.

## [104.0.17] - 2022-10-26
- Fix to ensure scripting omnicache/pycache does not lock up extension on startup.

## [104.0.16] - 2022-10-21
- Fix to increase the error trace stack to ensure line numbers are included.

## [104.0.15] - 2022-10-21
- Fixes for improved script error handling and ensure scripts are reloaded when fixed and saved.

## [104.0.14] - 2022-10-20
- Fixes for imported scripts used in BehaviorScript classes.

## [104.0.13] - 2022-10-19
- Fixes related to multiple scripts applied to one or more prims.

## [104.0.12] - 2022-10-18
- Fixes handling remote file deletes and updates to sync to local pycache.

## [104.0.11] - 2022-10-07
- Fixes scripts not loading on linux.

## [104.0.10] - 2022-10-03
- Adds remote debugging support in vscode.
- Adds catches for user Python Scripting errors and handle with log_error.
- Fixes for extension reloading.

## [104.0.9] - 2022-09-27
- Safely convert script filenames with '-' to pep8 compliant Script class

## [104.0.8] - 2022-09-22
- Adds local debugging support in vscode.
- Adds scripting events

## [104.0.7] - 2022-09-02
- Fixes in base BehaviorScript class for auto code complete for usd and timeline properties.

## [104.0.6] - 2022-08-30
- Changes script edits in vscode are always in a new window.

## [104.0.5] - 2022-08-29
- Fixes context menu item order for new and edit scripts.

## [104.0.4] - 2022-08-24
- Minor cleanup to base BehaviorScript class

## [104.0.3] - 2022-08-23
- Minor cleanup to UI

## [104.0.2] - 2022-08-19
- Added security warning to stage loading.
- Renamed to BehaviorScript

## [104.0.1] - 2022-08-18
- Improvements to base BehaviorScript class.

## [104.0.0] - 2022-08-17
- Initial revision.
