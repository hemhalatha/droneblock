# Changelog

All notable changes to the **DroneBlock** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-01

### Added
- **Core API**: Top-level exports in `__init__.py` for clean imports (`from droneblock import Drone`).
- **Type Hints**: Full PEP 484 type coverage across all modules.
- **Safety Manager**: Priority-based rule engine for deterministic safety constraints.
- **Replay System**: `Recorder` and `Player` for creating and replaying high-resolution flight traces.
- **Packaging**: `setup.py` and `requirements.txt` for standard installation.

### Changed
- **Refactor**: Complete overhaul of `MissionExecutor` for better sequential logic handling.
- **Refactor**: `PymavlinkConnector` now uses keyword arguments (`p1=val`) for safer command dispatch.
- **Documentation**: All docstrings updated to Google Python Style.
- **Logging**: Replaced `print()` with structured logging (INFO, WARN, ERROR, TRACE).

### Fixed
- **Timeouts**: `Action` classes now strictly enforce execution time limits.
- **Consistency**: Unified `BaseConnector` interface across potential backends.
