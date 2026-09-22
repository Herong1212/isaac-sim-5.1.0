# CHANGELOG

This project adheres to `Semantic Versioning <https://semver.org/>`_.

## [2.3.5] - 2025-07-07
- OMPE-29928: Fix img test with kit 108.

## [2.3.4] - 2025-05-29
- Fix "SyntaxWarning: invalid escape sequence" for python 3.12 used in kit 108

## [2.3.3] - 2025-02-25
- OMPE-37601: Fix profiler cpu not initialized error.

## [2.3.2] - 2025-02-10
- Remove extraneous test dependencies

## [2.3.1] - 2024-12-10
- OMPE-27610: Add ui update rate settings to control ui update.

## [2.3.0] - 2024-10-31
- OMPE-26534: Refactor profiler window with omni.ui.

## [2.2.4] - 2024-10-23
- OMPE-25770: Use omni.kit.menu.utils and delay the window construction to improve startup time.

## [2.2.3] - 2024-07-03
- OMPE-9458: Remove unnecessary warning

## [2.2.2] - 2024-05-27
- OMPE-8119: An option to disable Memory Stats.

## [2.2.1] - 2023-04-22
- OM-106442: Fixed test for kit master

## [2.2.0] - 2023-11-01
- OM-113720: Remove unused profiler nvdf doc types

## [2.1.3] - 2023-10-09
- OMFP-1986: Cease use of pip-install

## [2.1.2] - 2023-04-03
- Disabled menu_legacy as its will always be off in kit-sdk

## [2.1.1] - 2023-03-10
- Fix the profiler window to work when the cpu profiler is running under the multiplexer profiler.

## [2.1.0] - 2023-03-01
- Added average wall time per span name.

## [2.0.6] - 2023-02-20
- Fix Profiler initialization on Python 3.10

## [2.0.5] - 2023-01-06
- Display only available perfsdk node keys
- Add an option to adjust perfsdk's sampling interval in ms.

## [2.0.4] - 2022-11-08
- Fix column size for perfsdk report generator checkbox.

## [2.0.3] - 2022-10-11
- Added a menu for perfsdk report generator and realtime perfsdk metrics.

## [2.0.2] - 2022-08-23
- Fix for NVDF HTTP request for upload too large (do in batches)

## [2.0.1] - 2022-08-23
- Get tests passing on Kit SDK 104 and above.

## [2.0.0] - 2022-07-08
- Add new extension dependencies to run without legacy Viewport.

## [1.7.0] - 2022-06-29

- Added ChromeTrace class for extracting info from profiler json output and turning into metrics
- Added NVDataflow export of profiler metrics

## [1.4.4] - 2022-04-06

- Delay profiler startup to not disable profiling during startup until it opened or enabled with a hotkey

## [1.4.3] - 2022-04-01

- Added `get_instance()` function
- Added `get_window()` function

## [1.4.2] - 2022-03-30

- Delay profiler startup to not disable profiling during startup (WAR for startup profiling)

## [1.4.1] - 2022-03-29

- Fix startup profile crash report disable
- Add a setting to not show startup profile

## [1.4.0] - 2022-03-28

- Add startup profile (menu entry)

## [1.3.5] - 2022-01-05

- Fix profiler window to be compatible with kit-103.1 (legacy_viewport)

## [1.3.2] - 2020-11-23

- Fix profiler window to be compatible with latest kit sdk because omni.kit.settings removal

## [1.3.1] - 2020-08-02

- Fix profiler to be enabled only during capture

## [1.3.0] - 2020-07-28

- Add F5/Menu for fast capture
- Automatic tracy enable
- Remove buttons in capture browser
- A lot of small improvements on UI / bugfixes

## [1.2.5] - 2020-07-08

- fix UI clipping

## [1.2.4] - 2020-07-08

- reorg UI a bit

## [1.2.3] - 2020-07-06

- added optional Tracy convenience functions into GUI

## [1.2.2] - 2020-07-02

- add cProfile stats dump
- fix stop capture bug
- disable snakeviz in public build

## [1.2.1] - 2020-06-30

- allow only one python profiler selected at once

## [1.2.0] - 2020-06-29

- add cProfile and snakeviz

## [1.1.0] - 2020-06-25

- add capture browser
- add python profiling enable
- make viewport optional
- prepare for publishing

## [1.0.0] - 2020-11-09

### Added

- Ported from extension 1.0 to extension 2.0.
