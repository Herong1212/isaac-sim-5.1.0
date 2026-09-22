# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.0.3] - 2025-06-02
### Fixed
- Changes to the async engine's `run` monkey-patch implementation to handle situations where an exception is thrown
inside a separate `asyncio.run` call that's made inside the "top-level" `run` invocation.

## [0.0.2] - 2025-04-07
### Fixed
- OMPE-28324: Removed an unused argument in a lambda function to avoid creating extra Python objects that just need to be garbage collected later.

## [0.0.1] - 2024-07-09
### Changed
- Updated documentation with AI agent.
