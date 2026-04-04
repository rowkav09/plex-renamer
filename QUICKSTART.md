# Quick Start Guide - Plex TV Show Renamer

## 30-Second Setup

### 1. Install Python (if needed)
Download from https://www.python.org/downloads/ and install (check "Add Python to PATH")

### 2. Run the Tool
**Windows (Command Prompt):**
```cmd
run.bat
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1
```

**Linux/Mac:**
```bash
python3 plex_renamer.py
```

## First Run

The tool will:
1. ✓ Auto-install dependencies (requests, rich)
2. ✓ Show interactive menu
3. ✓ Scan your TV library (no changes yet - safe to try!)

## Basic Workflow

### Option 1: One-Command Run
```
1. Scan and plan renames
   → Shows preview of all changes
2. Apply changes
   → Makes all the renames
3. Done!
```

### Option 2: Review Before Committing
```
1. Scan and plan renames
2. Show rename plan
   → Review the table carefully
3. Apply changes
   → Confirms before applying
```

### Option 3: Undo a Mistake
```
4. View recent history
   → See what was renamed
5. Undo last rename
   → Restores previous name
```

## Example Session

```
========================================
   Plex TV Show Renamer
========================================

Options:
1. Scan and plan renames
2. Show rename plan
3. Apply changes
4. View recent history
5. Undo last rename
6. Exit

Select option [1-6]: 1

Scanning /r/media/tv...
Found 237 media files
Processing files... ████████████████████ 100%

Planned 45 rename operations

┌────────────────────────────────────────┐
│ Rename Plan (45 files)                 │
├──────────────┬──────────┬──────────────┤
│ Show         │ Episode  │ Status       │
├──────────────┼──────────┼──────────────┤
│ Breaking Bad │ S01E01   │ Pilot        │
│ Breaking Bad │ S01E02   │ Cat's in...  │
│ The Office   │ S01E01   │ Pilot        │
│ The Office   │ S01E02   │ Diversity... │
└──────────────┴──────────┴──────────────┘

Select option [1-6]: 3

Apply all planned changes? [Y/n]: y

Applying 45 changes...

Renaming files... ████████████████████ 100%

✓ All changes applied successfully!
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python not found" | Install Python from python.org |
| "Show not found" | Rename folder to remove special characters |
| "No changes needed" | Files already named correctly |
| "Only partial shows renamed" | Some shows not in TVMaze database |

## File Locations

After first run, these folders are created:

```
/r/media/tv/
├── .backups/
│   ├── rename_history.json    ← Your undo history
│   └── show_cache.json        ← API cache (speeds up subsequent runs)
├── Show Name 1/
│   ├── Season 01/
│   └── Season 02/
└── Show Name 2/
    └── Season 01/
```

## Next Steps

1. **Review the output** - Check renamed files in Explorer
2. **Run again** - Tool handles partial renames gracefully
3. **Check history** - Option 4 shows what was changed
4. **Undo if needed** - Option 5 reverses last operation

## Tips

- ✓ Safe to run multiple times - won't re-rename correctly named files
- ✓ First run slowest (API lookups) - subsequent runs faster (cached)
- ✓ Can cancel anytime before "Apply changes"
- ✓ Always review plan before applying
- ✓ Keep history for audit trail

## Common Issues

### "Connection timeout"
- Check internet connection
- TVMaze API may be down temporarily
- Try again in a few minutes

### "Show name not recognized"
- Show may not be on TVMaze
- Try renaming folder with clearer name
- Check spelling

### "Episode names wrong"
- Episode name comes from TVMaze database
- Verify on https://www.tvmaze.com manually
- Manual rename as fallback

## Need Help?

1. Check full README.md for advanced options
2. See console error messages for specific issues  
3. Use history to understand what went wrong
4. Undo to restore previous state

---

**Pro Tip:** Run once with -dry-run (future feature) to preview without changes!
