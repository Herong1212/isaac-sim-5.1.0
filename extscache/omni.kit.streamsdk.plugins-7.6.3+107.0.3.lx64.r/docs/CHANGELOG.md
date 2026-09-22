# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [7.6.3] - 2025-03-21
### Changed
- OMPE-40959: Update Support Level from Enterprise to Core.

## [7.6.2] - 2025-03-07
### Changed
- Log all headers received and do case insensitive comparisons

## [7.6.1] - 2025-02-20
### Fixed
- Crash on second connection if `--/app/livestream/allowResize=false`

## [7.6.0] - 2025-02-18
### Changed
- Update to use a newer version of streamsdk (35560324.0_gs_04_72) to fix crash when calling nvstSetRemotePeerIceCandidate.

## [7.5.0] - 2025-02-05
### Changed
- Update to build with the latest Kit 107.0 and ABI=1

## [7.3.3] - 2025-02-03
### Removed
- Unused carb.streamclient plugins.

## [7.3.2] - 2025-01-28
### Fixed
- Disable ice if a public endpoint is specified.

## [7.3.1] - 2025-01-23
### Added
- NVCF-REQID header as an extra field for all carb log messages

## [7.3.0] - 2025-01-21
### Changed
- Update to build with the latest Kit 107.0

## [7.2.1] - 2024-12-17
### Added
- New `/app/livestream/allowDynamicResize` setting (experimental).

## [7.2.0] - 2024-12-13
### Added
- New `/app/livestream/publicEndpointAddress` and `/app/livestream/publicEndpointPort` settings.

### Changed
- Update to use a newer version of streamsdk (35264228.0_gs_04_72).

### Fixed
- The `/app/livestream/disableSdkScaling` setting not being applied on Linux.
- Resize requests greater than the original stream resolution causing a stream disconnect.

## [7.1.0] - 2024-12-10
### Changed
- Update to build with the latest Kit 107.0

### Fixed
- Ensure that StreamSDK uses the initial resolution requested by the client.

## [7.0.4] - 2024-11-29
### Fixed
- Ensure the server resizes to the initial resolution requested by the client.

## [7.0.3] - 2024-11-27
### Added
- Enclose Nucleus server name with quotes.

## [7.0.2] - 2024-11-25
### Added
- New `/app/livestream/maxPushStreamDataAttempts` setting for potential performance improvement.
- Additional profiler zones to help better narrow down potential performance issues.

## [7.0.1] - 2024-11-22
### Added
- New `/app/livestream/skipCudaSync` setting for potential performance improvement.

## [7.0.0] - 2024-11-14
### Changed
- Update to build with Kit 107.0

## [6.1.2] - 2024-11-12
### Added
- New `/app/livestream/disableFrameCopying` setting.

## [6.1.1] - 2024-11-04
### Changed
- Map machine generated StreamSDK logs to carb info logs instead of fatal.
- Remove redundant time stamps from StreamSDK logs.

## [6.1.0] - 2024-10-23
### Changed
- Update to use a newer version of streamsdk (35031330.0_gs_04_69).

## [6.0.0] - 2024-09-25
### Changed
- Update to build with Kit 106.2

## [5.3.0] - 2024-09-24
### Changed
- Update to use a newer version of streamsdk (34885067.0_gs_04_69).
- Update to build with Kit 106.1

## [5.2.3] - 2024-09-04
### Added
- Extract Nucleus-Token from signaling headers.

## [5.2.2] - 2024-08-28
### Changed
- Map debug StreamSDK logs to carb info logs instead of verbose.

## [5.2.1] - 2024-07-16
### Added
- Client connected/disconnected events.
- Checks to ensure the height of the stream is always even.

## [5.2.0] - 2024-05-20
### Added
- API to set STUN credentials.
- New `/app/livestream/disableSdkScaling` setting.

### Changed
- Update to use a newer version of streamsdk (34291689.0_gs_04_66).

## [5.1.0] - 2024-04-15
### Changed
- Update to use a newer version of streamsdk (34145418.0_gs_04_65).

## [5.0.5] - 2024-02-29
### Added
- Support for audio streaming.

## [5.0.4] - 2024-02-28
### Added
- Ability to stream aovs other than ldr color ones.

## [5.0.3] - 2024-02-26
### Fixed
- Viewport streaming at arbitrary resolutions by accounting for pitched destination memory.

## [5.0.2] - 2024-02-21
### Added
- Support for custom resize messages from the streaming client.

### Changed
- Ignore the new skipCapture setting if viewportEnabled is true.

## [5.0.1] - 2024-02-20
### Added
- New /app/livestream/skipCapture setting for performance improvement.

## [5.0.0] - 2024-02-12
### Changed
- Updated to build with Kit 107.0

## [4.2.0] - 2024-02-08
### Changed
- Update to use a newer version of streamsdk (33859876.0_gs_04_63).

## [4.1.1] - 2024-02-06
### Added
- Option to stream multiple viewports over separate connections.

## [4.1.0] - 2024-01-25
### Added
- Option to stream just the viewport instead of the whole app.

## [4.0.0] - 2024-01-02
### Changed
- Updated to build with Kit 106.0

## [3.2.1] - 2023-12-19
### Added
- OMPRW-209: Support for sending and receiving custom messages between the streaming client and server.

## [3.2.0] - 2023-09-28
### Changed
- Remove some unused settings and dependencies.
- Updated to build with the latest repo_* packages.
- Update to use a newer version of streamsdk (33332890.0_gs_04_59).
- OM-79857: Don't define WITH_CONTINUOUS_INPUT_STREAM when building carb.livestream.plugin

## [3.1.0] - 2023-09-18
### Changed
- Updated to build with a newer version of Kit 105.2

## [3.0.7] - 2023-08-29
### Changed
- OM-107252: Link against StreamServerShared instead of StreamServerRtc.

## [3.0.6] - 2023-08-28
### Changed
- OM-106027: Send clipboard contents to the client in response to 'clipboard contents set' events instead of ctrl+c / ctrl+x shortcuts.

## [3.0.5] - 2023-08-24
### Changed
- OM-106843: Exposed setting for streaming server output directory.

## [3.0.4] - 2023-08-16
### Changed
- OM-67525: Don't perform potentially expensive cuda operations unless we're actively streaming.

## [3.0.3] - 2023-08-15
### Added
- OM-96889: Support for copy text from the server to paste in the client using ctrl+x.

## [3.0.2] - 2023-08-08
### Added
- OM-96889: Support for copy/pasting text from the server to the client.

## [3.0.1] - 2023-08-07
### Added
- OM-96889: Support for copy/pasting text from the client to the server.

## [3.0.0] - 2023-07-25
### Changed
- Updated to build with Kit 105.2

## [2.3.0] - 2023-07-24
### Changed
- Updated to build with a newer version of Kit 105.1

## [2.2.5] - 2023-07-12
### Added
- OM-90910: Added structured log output for stream connect/disconnect events, and quality of service updates.

## [2.2.4] - 2023-05-31
### Fixed
- OM-87218: Process `NvstLockKeysEvent`s to fix numpad input.

## [2.2.3] - 2023-05-31
### Changed
- OM-89964: Use `NvstQosStatus::recommendedMode::width / height` instead of `NvstQosStatus::preferredWidth / preferredHeight`.

## [2.2.2] - 2023-05-30
### Changed
- Enable ETLI dump flags for webrtc streaming

## [2.2.1] - 2023-05-23
### Changed
- OM-95623: Exposed qosStatusCallback to Python.
- OM-89964: Support streaming resolution >1080p.

## [2.2.0] - 2023-05-18
### Changed
- OM-92703: Updated to use a newer version of streamsdk (32816806.0_gs_04_55).

## [2.1.3] - 2023-05-15
### Fixed
- Set default values for streaming media port range settings.

## [2.1.2] - 2023-05-15
### Changed
- Expose settings for streaming media port range.

## [2.1.1] - 2023-05-15
### Changed
- Pull in some changes that were made to the original extensions that are still present in kit.

## [2.1.0] - 2023-05-12
### Changed
- Updated to build with Kit 105.1

## [2.0.1] - 2023-05-11
### Fixed
- OM-93598: Judder when livestreaming Composer 2023.1

## [2.0.0] - 2023-05-05
### Added
- Moved from kit into kit-livestream
