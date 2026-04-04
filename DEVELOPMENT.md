# Development Guide

This guide helps you understand, customize, or extend the Plex Renamer tool.

## Project Structure

```
plex_renamer/
├── plex_renamer.py          # Main application (all-in-one)
├── run.bat                  # Windows Command Prompt launcher
├── run.ps1                  # Windows PowerShell launcher
├── README.md                # Full documentation
├── QUICKSTART.md            # Get started in 30 seconds
├── FEATURES.md              # Feature comparison with old bash script
├── config.example.json      # Configuration template
├── DEVELOPMENT.md           # This file
└── .backups/                # Created at runtime
    ├── rename_history.json  # Audit trail
    └── show_cache.json      # API response cache
```

## Architecture

### Class Hierarchy

```
PlexRenamer (main app)
├── ShowCache
│   └── Manages TV show API cache
├── TVMazeAPI
│   └── Handles API interactions
├── ShowDetector
│   ├── clean_name()
│   ├── guess_show_from_folder()
│   └── find_best_match()
├── FileRenamer
│   ├── scan_media_files()
│   └── plan_rename()
├── EpisodeExtractor
│   └── extract_episodes()
└── RenameHistory
    ├── record_rename()
    ├── undo_last()
    └── get_recent()
```

### Data Flow

```
1. Scan              → Find all media files
                        ↓
2. Extract Episodes  → Parse S01E01 from filename
                        ↓
3. Detect Show       → Extract show name from folder
                        ↓
4. Query API         → Get show ID and episode name
                        ↓
5. Plan Action       → Create RenameAction object
                        ↓
6. Display Plan      → Show user interactive preview
                        ↓
7. Confirm           → User approves
                        ↓
8. Apply Changes     → Move files
                        ↓
9. Record History    → Save to JSON for undo
```

## Core Components

### 1. ShowCache
**Purpose:** Cache API responses to reduce network calls

```python
cache = ShowCache("/path/to/cache.json")
# First call: hits API
show = cache.get_show("Breaking Bad")  # None
api.search_show("Breaking Bad")
cache.set_show("Breaking Bad", show_data)

# Second call: returns cached
show = cache.get_show("Breaking Bad")  # Returns cached data
```

### 2. TVMazeAPI
**Purpose:** Interact with TVMaze API with error handling

```python
api = TVMazeAPI(cache)

# Search for show
show = api.search_show("Breaking Bad")
# Returns: {"id": 1, "name": "Breaking Bad", ...}

# Get episode name
episode = api.get_episode(show_id=1, season=1, episode=1)
# Returns: "Pilot"
```

### 3. ShowDetector
**Purpose:** Intelligently detect show names from messy folder structures

```python
detector = ShowDetector(api)

# Clean up folder names
detector.clean_name("[Breaking Bad] (2008) [1080p]")
# Returns: "Breaking Bad 2008 1080p"

# Try to find show
result = detector.guess_show_from_folder("/media/break.bad.1x01/")
# Returns: ("Breaking Bad", {show_data})
```

### 4. EpisodeExtractor
**Purpose:** Parse episode numbers from filenames

```python
# S01E01
EpisodeExtractor.extract_episodes("Show.S01E01.mkv")
# Returns: (1, 1, None)

# S01E01-E03 (multi-episode)
EpisodeExtractor.extract_episodes("Show.S01E01-E03.mkv")
# Returns: (1, 1, 3)

# 1x01
EpisodeExtractor.extract_episodes("show.1x01.mkv")
# Returns: (1, 1, None)
```

### 5. RenameHistory
**Purpose:** Track all operations for undo functionality

```python
history = RenameHistory("history.json")

# Record an operation
action = RenameAction(...)
history.record_rename(action)

# Get recent operations
recent = history.get_recent(10)

# Undo last operation
if history.undo_last():
    print("Restored previous name")
```

### 6. FileRenamer
**Purpose:** Orchestrate file scanning and rename planning

```python
renamer = FileRenamer(api, detector)

# Scan library
files = renamer.scan_media_files("/media/tv")

# Plan single rename
action = renamer.plan_rename("/media/tv/show/1x01.mkv")
# Returns: RenameAction or None
```

## Customization Guide

### 1. Change Root Directory
```python
# In CONFIG dict at top of file
CONFIG = {
    "ROOT": "/my/custom/path",  # Change this
    ...
}
```

### 2. Add New Supported File Types
```python
CONFIG = {
    "SUPPORTED_EXTENSIONS": {
        ".mkv", ".mp4", ".avi", ".mov",
        ".webm",  # Add custom types
        ".opus",
    },
    ...
}
```

### 3. Customize Naming Format
```python
# In FileRenamer.plan_rename() method
# Change line:
new_filename = f"{show_name} - {ep_str} - {ep_name}{ext}"

# To:
new_filename = f"[{show_name}] {ep_str} {ep_name}{ext}"
```

### 4. Customize Folder Structure
```python
# In FileRenamer.plan_rename() method
# Change line:
season_folder = f"Season {season:02d}"

# To:
season_folder = f"S{season:02d}"  # Compact format
```

### 5. Use Different API
```python
# Extend the TVMazeAPI class for TMDB or OMDB
class TheMovieDbAPI(TVMazeAPI):
    def search_show(self, query: str) -> Optional[Dict]:
        # Implementation using TheMovieDB API
        pass
    
    def get_episode(self, show_id: int, season: int, episode: int) -> Optional[str]:
        # Implementation using TheMovieDB API
        pass

# Use in main:
api = TheMovieDbAPI(cache, api_key="your_key")
```

### 6. Add New Menu Option
```python
# In PlexRenamer.interactive_menu() method
# Add option:
elif choice == "7":
    self.custom_feature()

# Implement feature:
def custom_feature(self):
    console.print("Doing custom thing...")
    # Your code here
```

### 7. Custom Episode Name Handling
```python
# In FileRenamer.plan_rename() method, after getting ep_name:
if not ep_name:
    # Custom fallback
    ep_name = f"{season}x{ep_num} - [Episode]"  # Instead of "Episode X"
```

## Adding Features

### Example: Add Logging

```python
import logging

# Add to imports
logger = logging.getLogger("PlexRenamer")
handler = logging.FileHandler("rename.log")
logger.addHandler(handler)

# In commit_changes():
logger.info(f"Renamed: {action.original_path} -> {action.new_path}")
```

### Example: Add Dry-Run Mode

```python
# Add flag to PlexRenamer
class PlexRenamer:
    def __init__(self, root_path: str = CONFIG['ROOT'], dry_run: bool = False):
        self.dry_run = dry_run
        ...

# In commit_changes():
def commit_changes(self):
    if self.dry_run:
        console.print("[yellow]DRY RUN: No changes will be made[/yellow]")
        return
    
    # ... existing code ...
```

### Example: Add Notification System

```python
import smtplib
from email.mime.text import MIMEText

def send_notification(self, summary: str):
    """Send email notification of changes"""
    msg = MIMEText(summary)
    msg['Subject'] = "Plex Renamer Completed"
    
    # Configure SMTP
    # Send email
    pass

# In commit_changes():
self.send_notification(f"Processed {len(self.actions)} files")
```

## Testing

### Manual Testing
```bash
# Create test structure
mkdir -p /tmp/test_tv/Breaking\ Bad
touch "/tmp/test_tv/Breaking Bad/1x01.mkv"

# Run with test config
CONFIG["ROOT"] = "/tmp/test_tv"
python plex_renamer.py

# Verify results
ls -R /tmp/test_tv/
```

### Unit Testing (Future)
```python
# tests/test_episode_extractor.py
import unittest
from plex_renamer import EpisodeExtractor

class TestEpisodeExtractor(unittest.TestCase):
    def test_s01e01(self):
        result = EpisodeExtractor.extract_episodes("Show.S01E01.mkv")
        self.assertEqual(result, (1, 1, None))
    
    def test_multi_episode(self):
        result = EpisodeExtractor.extract_episodes("Show.S01E01-E03.mkv")
        self.assertEqual(result, (1, 1, 3))
```

## Performance Optimization

### 1. Parallel API Calls
```python
from concurrent.futures import ThreadPoolExecutor

# In scan_and_plan:
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(self.renamer.plan_rename, f) for f in files]
    for future in futures:
        self.actions.append(future.result())
```

### 2. Batch API Requests
```python
# Get multiple episodes in one call instead of one-by-one
def get_all_episodes(self, show_id: int):
    url = f"{CONFIG['API_EPISODES']}/{show_id}/episodes"
    return self.session.get(url).json()
```

### 3. Index Shows for Fuzzy Search
```python
# Cache all known shows locally
self.show_index = {}
for show in self.api.fetch_all_shows():
    self.show_index[show['name'].lower()] = show
```

## Debugging

### Enable Debug Output
```python
# Add to top of script
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Use:
logger.debug(f"Processing: {file_path}")
```

### Inspect History
```bash
# View JSON history
cat .backups/rename_history.json | python -m json.tool

# View cached shows
cat .backups/show_cache.json | python -m json.tool
```

### Test API Connection
```bash
curl "https://api.tvmaze.com/search/shows?q=breaking+bad" | python -m json.tool
```

## Contributing

1. Fork the project
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and test
4. Update docstrings and comments
5. Submit pull request

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings to classes and methods
- Keep functions focused and small
- Add comments for complex logic

### Before Submitting
- Test with multiple show names
- Verify undo/restore works
- Check error handling
- Update documentation

## License

MIT License - See LICENSE file

---

**Questions?** Check the code comments or README.md for more details.
