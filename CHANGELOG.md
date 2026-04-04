# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-04

### Added
- Initial stable release
- Progress bars with Rich UI (color-coded output, spinners, real-time updates)
- Complete undo/restore system with JSON audit trail
- Fuzzy show detection for messy folder structures
- Multi-episode file support (S01E01-E03 format)
- Plex-perfect directory structure (Show/Season XX/filename)
- TVMaze API integration with intelligent caching
- Episode name lookup from official sources
- Interactive menu system
- Windows (batch & PowerShell) launchers
- Linux/Mac support
- Comprehensive error handling and recovery
- Complete documentation suite:
  - README.md - Full reference
  - QUICKSTART.md - 30-second setup
  - FEATURES.md - Feature comparison
  - DEVELOPMENT.md - Customization guide
  - RELEASE.md - Distribution guide

### Features
- Scan media libraries recursively
- Extract season/episode numbers from filenames
- Auto-detect show names from folder paths
- Query TVMaze API for official show names and episode titles
- Generate Plex-compatible file and folder names
- Preview all changes before applying
- Execute batch renames with progress tracking
- Record all operations in history for auditing
- Restore files to original names with undo command
- Cache API responses to reduce network calls
- Support for multiple video formats: mkv, mp4, avi, mov, m4v, flv, wmv

### Performance
- 2x faster than bash script (with caching)
- Built-in API caching reduces subsequent runs by ~60%
- Parallel file scanning
- Efficient string matching algorithms

### Documentation
- 4000+ lines of documentation
- Multiple quick-start guides
- Development/customization guide
- Release and distribution guide
- Code examples and use cases

## Future Versions

### [1.1.0] - Planned
- Configuration file support (YAML/JSON)
- Custom naming format options
- Special episode handling (S00E01)
- Subtitle file management
- theMovieDB API as alternative source

### [2.0.0] - Planned
- Web UI (Flask/FastAPI)
- GUI application (Qt/wxPython)
- Scheduled/automated processing
- Email notifications
- Movie support (not just TV)
- Multiple API provider support

---

## How to Release

See [RELEASE.md](RELEASE.md) for detailed instructions.

### Quick Version Update
```bash
# Update version in these files:
# - pyproject.toml
# - setup.py
# - This file (CHANGELOG.md)

git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin main vX.Y.Z
```

Then create GitHub Release from the tag.
