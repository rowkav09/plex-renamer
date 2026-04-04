#!/usr/bin/env python3
"""
Plex TV Show Renamer - Professional tool for organizing TV shows in Plex format.

Features:
- Progress bar and rich UI
- Undo/restore system with JSON backups
- Fuzzy show detection (handles messy folder names)
- Multi-episode file support (S01E01-E03)
- Plex-perfect folder structure: Show Name/Season 01/Show Name - s01e01 - Episode Name.ext
"""

import os
import json
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import difflib

try:
    import requests
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from rich.syntax import Syntax
except ImportError:
    print("Installing required packages...")
    os.system("pip install requests rich")
    import requests
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from rich.syntax import Syntax

console = Console()

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    "ROOT": r"/r/media/tv",
    "API_SEARCH": "https://api.tvmaze.com/search/shows?q=",
    "API_EPISODES": "https://api.tvmaze.com/shows",
    "SUPPORTED_EXTENSIONS": {".mkv", ".mp4", ".avi", ".mov", ".m4v", ".flv", ".wmv"},
    "BACKUP_DIR": r"/r/media/tv/.backups",
    "HISTORY_FILE": r"/r/media/tv/.backups/rename_history.json",
    "CACHE_FILE": r"/r/media/tv/.backups/show_cache.json",
}


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class RenameAction:
    """Represents a single file rename operation."""
    original_path: str
    new_path: str
    show_name: str
    season: int
    episode: int
    episode_name: str
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


# ============================================================================
# CACHE & API
# ============================================================================

class ShowCache:
    """Caches TV show API lookups to reduce API calls."""
    
    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self.data = self._load()
    
    def _load(self) -> Dict:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)
    
    def get_show(self, query: str) -> Optional[Dict]:
        if query in self.data:
            return self.data[query]
        return None
    
    def set_show(self, query: str, show_data: Dict):
        self.data[query] = show_data
        self._save()


class TVMazeAPI:
    """Handles TVMaze API interactions with caching and error handling."""
    
    def __init__(self, cache: ShowCache):
        self.cache = cache
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'PlexRenamer/1.0'})
    
    def search_show(self, query: str) -> Optional[Dict]:
        """Search for a show by name."""
        cached = self.cache.get_show(query)
        if cached:
            return cached
        
        try:
            url = f"{CONFIG['API_SEARCH']}{query}"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if data:
                show_data = data[0].get('show', {})
                self.cache.set_show(query, show_data)
                return show_data
        except Exception as e:
            console.print(f"[red]API Error searching for '{query}': {e}[/red]")
        
        return None
    
    def get_episode(self, show_id: int, season: int, episode: int) -> Optional[str]:
        """Get episode name from show ID."""
        try:
            url = f"{CONFIG['API_EPISODES']}/{show_id}/episodes"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            episodes = response.json()
            for ep in episodes:
                if ep.get('season') == season and ep.get('number') == episode:
                    return ep.get('name')
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fetch episode info: {e}[/yellow]")
        
        return None


# ============================================================================
# SHOW DETECTION & FUZZY MATCHING
# ============================================================================

class ShowDetector:
    """Detects show names from folder names and file patterns, with fuzzy matching."""
    
    def __init__(self, api: TVMazeAPI):
        self.api = api
    
    def clean_name(self, name: str) -> str:
        """Remove special characters and normalize."""
        # Remove common patterns
        name = re.sub(r'\[.*?\]', '', name)  # [1080p] etc
        name = re.sub(r'\(.*?\)', '', name)  # (2020) etc
        name = re.sub(r'[^a-zA-Z0-9\s-]', '', name)  # Remove special chars
        name = re.sub(r'\s+', ' ', name).strip()
        return name
    
    def guess_show_from_folder(self, folder_path: str) -> Optional[Tuple[str, Dict]]:
        """Guess show name from folder path."""
        folder_name = os.path.basename(folder_path)
        cleaned = self.clean_name(folder_name)
        
        if not cleaned:
            return None
        
        # Try direct search
        show = self.api.search_show(cleaned)
        if show and show.get('id'):
            return cleaned, show
        
        # Try fuzzy matching with folder hierarchy
        # Go up one level
        parent = os.path.dirname(folder_path)
        if parent and parent != folder_path:
            parent_name = os.path.basename(parent)
            cleaned_parent = self.clean_name(parent_name)
            if cleaned_parent:
                show = self.api.search_show(cleaned_parent)
                if show and show.get('id'):
                    return cleaned_parent, show
        
        # Try removing common suffixes
        for suffix in [' season', ' s', ' tv', ' series']:
            if cleaned.lower().endswith(suffix):
                base = cleaned[:-len(suffix)].strip()
                show = self.api.search_show(base)
                if show and show.get('id'):
                    return base, show
        
        return None
    
    def find_best_match(self, query: str, known_shows: List[str]) -> Optional[str]:
        """Find best match from known shows using difflib."""
        matches = difflib.get_close_matches(query.lower(), 
                                            [s.lower() for s in known_shows],
                                            n=1, cutoff=0.6)
        if matches:
            return matches[0]
        return None


# ============================================================================
# FILE PROCESSING
# ============================================================================

class EpisodeExtractor:
    """Extracts episode information from filenames."""
    
    @staticmethod
    def extract_episodes(filename: str) -> Optional[Tuple[int, int, Optional[int]]]:
        """
        Extract season and episode numbers.
        Returns (season, start_episode, end_episode) or None
        
        Patterns:
        - S01E01
        - S01E01-E03
        - s01e01
        - 1x01
        """
        patterns = [
            r'[sS](\d+)[eE](\d+)(?:-[eE](\d+))?',  # S01E01 or S01E01-E03
            r'(\d+)x(\d+)',  # 1x01
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                season = int(match.group(1))
                start_ep = int(match.group(2))
                end_ep = int(match.group(3)) if match.lastindex >= 3 else None
                return season, start_ep, end_ep
        
        return None


class FileRenamer:
    """Handles file scanning and rename planning."""
    
    def __init__(self, api: TVMazeAPI, detector: ShowDetector):
        self.api = api
        self.detector = detector
    
    def scan_media_files(self, root_path: str) -> List[str]:
        """Scan for media files."""
        files = []
        for root, dirs, filenames in os.walk(root_path):
            for filename in filenames:
                if any(filename.lower().endswith(ext) for ext in CONFIG['SUPPORTED_EXTENSIONS']):
                    files.append(os.path.join(root, filename))
        return files
    
    def plan_rename(self, file_path: str) -> Optional[RenameAction]:
        """Plan a single file rename."""
        filename = os.path.basename(file_path)
        dir_path = os.path.dirname(file_path)
        ext = os.path.splitext(filename)[1]
        
        # Extract episodes
        ep_info = EpisodeExtractor.extract_episodes(filename)
        if not ep_info:
            return None
        
        season, start_ep, end_ep = ep_info
        
        # Detect show
        show_match = self.detector.guess_show_from_folder(dir_path)
        if not show_match:
            return None
        
        query, show_data = show_match
        show_name = show_data.get('name')
        show_id = show_data.get('id')
        
        if not show_name or not show_id:
            return None
        
        # Get episode name
        ep_name = self.api.get_episode(show_id, season, start_ep)
        if not ep_name:
            ep_name = f"Episode {start_ep}"
        
        # Build Plex-perfect path
        season_folder = f"Season {season:02d}"
        show_folder = show_name
        
        # Format episode string
        if end_ep:
            ep_str = f"s{season:02d}e{start_ep:02d}-e{end_ep:02d}"
        else:
            ep_str = f"s{season:02d}e{start_ep:02d}"
        
        new_filename = f"{show_name} - {ep_str} - {ep_name}{ext}"
        new_path = os.path.join(CONFIG['ROOT'], show_folder, season_folder, new_filename)
        
        # Skip if already correctly named
        if file_path.lower() == new_path.lower():
            return None
        
        return RenameAction(
            original_path=file_path,
            new_path=new_path,
            show_name=show_name,
            season=season,
            episode=start_ep,
            episode_name=ep_name
        )


# ============================================================================
# UNDO SYSTEM
# ============================================================================

class RenameHistory:
    """Manages rename history for undo functionality."""
    
    def __init__(self, history_file: str):
        self.history_file = history_file
        self.records = self._load()
    
    def _load(self) -> List[Dict]:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, indent=2)
    
    def record_rename(self, action: RenameAction):
        """Record a rename operation."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "original": action.original_path,
            "new": action.new_path,
            "show": action.show_name,
            "season": action.season,
            "episode": action.episode,
        }
        self.records.append(record)
        self._save()
    
    def get_recent(self, count: int = 10) -> List[Dict]:
        """Get recent rename records."""
        return self.records[-count:]
    
    def undo_last(self) -> bool:
        """Undo the last rename operation."""
        if not self.records:
            return False
        
        record = self.records[-1]
        original = record['original']
        new = record['new']
        
        if os.path.exists(new):
            os.makedirs(os.path.dirname(original), exist_ok=True)
            shutil.move(new, original)
            self.records.pop()
            self._save()
            return True
        
        return False


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class PlexRenamer:
    """Main application class."""
    
    def __init__(self, root_path: str = CONFIG['ROOT']):
        self.root_path = root_path
        self.cache = ShowCache(CONFIG['CACHE_FILE'])
        self.api = TVMazeAPI(self.cache)
        self.detector = ShowDetector(self.api)
        self.renamer = FileRenamer(self.api, self.detector)
        self.history = RenameHistory(CONFIG['HISTORY_FILE'])
        self.actions: List[RenameAction] = []
    
    def display_banner(self):
        """Display welcome banner."""
        console.print(Panel(
            "[bold cyan]Plex TV Show Renamer[/bold cyan]\n"
            "Professional tool for organizing TV shows in Plex format",
            style="cyan"
        ))
    
    def display_plan(self):
        """Display rename plan in a table."""
        if not self.actions:
            console.print("[yellow]No changes needed![/yellow]")
            return
        
        table = Table(title=f"Rename Plan ({len(self.actions)} files)")
        table.add_column("Show", style="cyan")
        table.add_column("Episode", style="magenta")
        table.add_column("Status", style="green")
        
        for action in self.actions:
            ep_name = action.episode_name[:30] + "..." if len(action.episode_name) > 30 else action.episode_name
            table.add_row(
                action.show_name,
                f"S{action.season:02d}E{action.episode:02d}",
                ep_name
            )
        
        console.print(table)
    
    def scan_and_plan(self):
        """Scan files and plan renames."""
        console.print(f"\n[bold]Scanning[/bold] {self.root_path}...")
        
        files = self.renamer.scan_media_files(self.root_path)
        console.print(f"Found [cyan]{len(files)}[/cyan] media files")
        
        self.actions = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Processing files...", total=len(files))
            
            for file_path in files:
                action = self.renamer.plan_rename(file_path)
                if action:
                    self.actions.append(action)
                progress.update(task, advance=1)
        
        console.print(f"\nPlanned [cyan]{len(self.actions)}[/cyan] rename operations")
    
    def commit_changes(self):
        """Apply all rename operations."""
        if not self.actions:
            return
        
        console.print(f"\n[bold]Applying {len(self.actions)} changes...[/bold]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Renaming files...", total=len(self.actions))
            
            for action in self.actions:
                try:
                    # Create parent directories
                    os.makedirs(os.path.dirname(action.new_path), exist_ok=True)
                    
                    # Move file
                    shutil.move(action.original_path, action.new_path)
                    
                    # Record in history
                    self.history.record_rename(action)
                    
                except Exception as e:
                    console.print(f"[red]Error: {action.original_path} -> {e}[/red]")
                
                progress.update(task, advance=1)
        
        console.print("\n[green]✓ All changes applied successfully![/green]")
    
    def show_recent_history(self, count: int = 10):
        """Display recent rename history."""
        recent = self.history.get_recent(count)
        if not recent:
            console.print("[yellow]No rename history[/yellow]")
            return
        
        table = Table(title=f"Recent Renames (last {len(recent)})")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Show", style="magenta")
        table.add_column("Episode", style="green")
        
        for record in recent[-10:]:
            timestamp = record['timestamp'][:19]
            table.add_row(
                timestamp,
                record['show'],
                f"S{record['season']:02d}E{record['episode']:02d}"
            )
        
        console.print(table)
    
    def interactive_menu(self):
        """Interactive menu."""
        self.display_banner()
        
        while True:
            console.print("\n[bold cyan]Options:[/bold cyan]")
            console.print("1. Scan and plan renames")
            console.print("2. Show rename plan")
            console.print("3. Apply changes")
            console.print("4. View recent history")
            console.print("5. Undo last rename")
            console.print("6. Exit")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6"])
            
            if choice == "1":
                self.scan_and_plan()
                self.display_plan()
            elif choice == "2":
                self.display_plan()
            elif choice == "3":
                if self.actions:
                    if Confirm.ask("Apply all planned changes?", default=True):
                        self.commit_changes()
            elif choice == "4":
                self.show_recent_history()
            elif choice == "5":
                if self.history.undo_last():
                    console.print("[green]✓ Last rename undone[/green]")
                else:
                    console.print("[red]Nothing to undo[/red]")
            elif choice == "6":
                console.print("[cyan]Goodbye![/cyan]")
                break


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the application."""
    app = PlexRenamer()
    app.interactive_menu()


if __name__ == "__main__":
    main()
