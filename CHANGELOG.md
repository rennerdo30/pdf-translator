# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- GitHub Actions workflows for CI and releases
- Dependabot configuration for dependencies and workflow updates
- GitHub issue templates and pull request template
- Project governance docs: contributing, code of conduct, security policy
- Automated tests for config parsing, CLI validation, and translator helpers

### Changed

- Hardened GUI thread-safety around Tkinter updates
- Improved translation fallback behavior with chunked translation paths
- Added safer handling for empty or structured model response payloads
- Added output path checks to prevent writing over input files
- Updated project metadata and repository URLs

## [0.1.0] - 2024-12-11

### Added

- Initial release with CLI and Tkinter GUI
- Vision model translation and OCR fallback support
- Side-by-side and overlay output modes
- Proportional text scaling for varying page sizes
