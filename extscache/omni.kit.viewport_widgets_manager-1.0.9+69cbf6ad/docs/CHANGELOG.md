# Changelog

## [1.0.9] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [1.0.8] - 2022-10-25
### Changed 
- Import of omni.kit.viewport.utility.tests.setup_viewport_test_window

## [1.0.7] - 2022-08-31
### Changed 
- Fix issue to calculate widget pos caused by world transform update delay.
- Put some delay to improve widgets refresh performance.

## [1.0.6] - 2022-06-02
### Changed 
- Remove usage of RTX for test in favor of Storm.
- Update image threshold for differencce in title-bar when running with Viewport Next.

## [1.0.5] - 2022-05-23
### Changed 
- Add dependency on omni.kit.viewport.utility
### Fixes
- Fix widget positioning for Viewport Legacy and Next

## [1.0.4] - 2021-12-20
### Fixes
- Fix widget positioning issue if stage units are meters.
- Fix empty Sdf.Path comparison issue.

## [1.0.3] - 2021-08-21
### Fixes
- Fix perf issue to query duplicate prim path, and add trace for usd notice.

## [1.0.0] - 2021-03-09
### Changed 
- Initial extension.
