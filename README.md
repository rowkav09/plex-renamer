# Plex TV Show Renamer

Professional tool for organizing TV shows in Plex-perfect format with advanced features.

## Features

### ✨ Core Features
- **Progress Bars & Rich UI** - Beautiful terminal interface with real-time progress tracking
- **Undo/Restore System** - Complete rename history with ability to undo operations
- **Fuzzy Show Detection** - Automatically finds shows even with messy folder names
- **Multi-Episode Support** - Handles multi-episode files (S01E01-E03)
- **Plex-Perfect Structure** - Creates ideal Plex directory layout:
  ```
  Show Name/
  ├── Season 01/
  │   ├── Show Name - s01e01 - Episode Name.mkv
  │   ├── Show Name - s01e02 - Episode Name.mkv
  │   └── ...
  └── Season 02/
  ```

### 🔧 Advanced Features
- **Show Caching** - Reduces API calls with intelligent caching
- **Episode Name Lookup** - Fetches official episode names from TVMaze
- **Error Recovery** - Graceful handling of missing/incomplete data
- **Batch Operations** - Process entire library in one session
- **History Tracking** - Complete audit trail of all operations

## Installation

### Requirements
- Python 3.7+
- Internet connection (for TVMaze API)
- Optional: TVDB API key for TVDB fallback/lookups

### Setup
```bash
# Install the tool
python plex_renamer.py

# Dependencies will auto-install on first run:
# - requests (API calls)
# - rich (beautiful terminal UI)
```

## Usage

### Interactive Mode (Recommended)
```bash
python plex_renamer.py
```

Then follow the menu:
```
Media folder path (...):
Media type [tv/movies/both] (...):

Options:
1. Scan and plan renames
2. Show rename plan
3. Apply changes
4. View recent history
5. Undo last rename
6. Exit
```

### Examples

#### 1. Rename a messy TV folder
```
Before:
/r/media/tv/
├── Breaking.Bad.S01.1080p/
│   ├── 1x01.mkv
│   ├── 1x02.mkv
│   └── 1x03.mkv

After:
/r/media/tv/
├── Breaking Bad/
│   └── Season 01/
│       ├── Breaking Bad - s01e01 - Pilot.mkv
│       ├── Breaking Bad - s01e02 - Cat's in the Bag.mkv
│       └── Breaking Bad - s01e03 - And the Bag's in the River.mkv
```

#### 2. Handle multi-episode files
```
Input: MyShow.S01E01-E03.mkv
Output: My Show - s01e01-e03 - Episode Name.mkv
```

#### 3. Undo a rename operation
```
Options → 5 (Undo last rename)
```

## Configuration

No external config file is required.

At startup, the script asks for:
- Media folder path
- Media type: `tv`, `movies`, or `both`

Core defaults and API settings are kept directly inside `plex_renamer.py` in the `CONFIG` dictionary:

```python
CONFIG = {
    "ROOT": r"/r/media/tv",                        # Root TV library path
    "API_SEARCH": "https://api.tvmaze.com/...",   # TVMaze API endpoint
  "TVDB_API_BASE": "https://api4.thetvdb.com/v4",  # TVDB v4 API endpoint
  "PREFERRED_SOURCE": "tvmaze",                   # tvmaze or tvdb
    "SUPPORTED_EXTENSIONS": {                       # Video file types
        ".mkv", ".mp4", ".avi", ".mov", ".m4v", ".flv", ".wmv"
    },
}
```

### TVDB Setup (Optional)

Set environment variables before running if you want TVDB support:

```bash
# Linux/macOS
export TVDB_API_KEY="your_api_key"
export TVDB_PIN="your_pin_if_required"

# Windows PowerShell
$env:TVDB_API_KEY="your_api_key"
$env:TVDB_PIN="your_pin_if_required"
```

Then set `PREFERRED_SOURCE` to `"tvdb"` in `plex_renamer.py`.

## How It Works

### 1. Scanning
- Recursively scans the entire TV library
- Identifies all video files
- Extracts season/episode numbers

### 2. Show Detection
- Parses folder names for show title
- Falls back to parsing the show title from filename when folder names are generic
- Removes common patterns: [1080p], (2020), special characters
- Performs fuzzy matching if direct search fails
- Queries TVMaze API for official show info

### 3. Episode Lookup
- Fetches official episode names from TVMaze
- Handles missing episodes gracefully
- Caches results to minimize API calls

### 4. Planning
- Shows preview of all changes in interactive table
- No operations performed until confirmed
- Safe to review before applying

### 5. Applying
- Creates proper directory structure
- Moves files to correct locations
- Records all operations in history

### 6. Undo System
- Stores complete history in JSON
- Can restore files to original locations
- One-click undo for recent operations

## Data Storage

The tool creates a `.backups` folder with:

```
.backups/
├── rename_history.json    # Complete audit trail of all renames
├── show_cache.json        # TVMaze API response cache
└── backups/               # (future) File backups before rename
```

## Supported File Patterns

The tool recognizes these episode patterns:

| Pattern | Example | Result |
|---------|---------|--------|
| S01E01 | `Show.S01E01.mkv` | s01e01 |
| s01e01 | `show.s01e01.mkv` | s01e01 |
| 1x01 | `show.1x01.mkv` | s01e01 |
| Season 1 Episode 01 | `Show Season 1 Episode 01 - Pilot.mkv` | s01e01 |
| S01E01-E03 | `Show.S01E01-E03.mkv` | s01e01-e03 |

## API

The tool uses **TVMaze** API by default (free, no key required):
- Show search: Finds show ID and official name
- Episode lookup: Fetches episode names and info
- Caching built-in: Reduces API load

Optional **TVDB v4** support is available if you provide `TVDB_API_KEY` (and `TVDB_PIN` when required).

## Troubleshooting

### Show Not Found
- Check spelling of folder name
- Try searching TVMaze manually: https://www.tvmaze.com
- Use parent folder name if current is ambiguous

### Episodes Not Found
- Ensure internet connection
- Check show exists on TVMaze
- Verify season/episode numbers are correct

### Permission Errors
- Ensure write permissions to TV library
- Close any files open in media players

### Undo Not Working
- History file may be corrupted
- Ensure `.backups` folder has write permissions
- Manually restore from backup files if needed

## Advanced Usage

### Dry Run (Show Plan Without Applying)
1. Select "Scan and plan renames"
2. Review in "Show rename plan"
3. Select "Exit" without applying
4. Changes are safe - nothing was modified

### Batch Process Multiple Shows
1. Scan and plan (processes entire library)
2. Review complete plan
3. Apply all at once
4. All operations recorded in history

### Manual History Review
```bash
cat .backups/rename_history.json | python -m json.tool
```

## Limitations

- Requires TVMaze API availability
- Manual episode names take precedence over defaults
- Doesn't handle special case episodes (specials, pilots)
- No support for subtitle/secondary files

## Future Enhancements

- [ ] GUIs (tkinter/PyQt)
- [ ] Themoviedb.org API support
- [ ] Imdb integration
- [ ] Web interface
- [ ] Scheduled auto-rename
- [ ] Special episode support (S00E01)
- [ ] Multiple subtitle file handling
- [ ] Backup before rename option

## License

MIT License - Use freely

## Support

For issues:
1. Check `.backups/rename_history.json` for details
2. Review console output messages
3. Try undo operation
4. Manual rename as fallback

---

**Last Updated:** 2026-04-04
