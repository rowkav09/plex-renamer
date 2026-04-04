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
import subprocess
import sys
import html
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import difflib

try:
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from rich.syntax import Syntax
except ImportError:
    print("Installing required packages (quiet mode)...")
    install_cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-input",
        "--quiet",
        "requests",
        "rich",
    ]
    install_result = subprocess.run(install_cmd, capture_output=True, text=True)
    if install_result.returncode != 0:
        print("Dependency installation failed.")
        error_text = (install_result.stderr or install_result.stdout).strip()
        if error_text:
            lines = error_text.splitlines()
            print("Details:")
            print("\n".join(lines[-8:]))
        raise SystemExit(1)
    print("Dependencies installed.")
    import requests
    from rich.console import Console
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
    "TVDB_API_BASE": "https://api4.thetvdb.com/v4",
    "PREFERRED_SOURCE": "tvmaze",  # fixed: tvmaze only
    "NAMING_PROFILE": "plex",  # plex | kodi
    "TV_EPISODE_FORMAT": "sxe",  # sxe | x
    "KODI_WRITE_NFO": True,
    "KODI_NFO_SOURCE": "tvdb",  # tvdb | imdb | tvmaze | auto
    "KODI_CLEAN_EPISODE_TITLES": True,
    "SAFE_MODE": True,
    "PROTECT_NON_EMPTY_FOLDERS": True,
    "SUPPORTED_EXTENSIONS": {
        ".mkv", ".mp4", ".avi", ".mov", ".m4v", ".flv", ".wmv",
        ".m2ts", ".mts", ".ts", ".mpeg", ".mpg", ".asf", ".qt", ".iso"
    },
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
    media_type: str
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
        self.preferred_source = "tvmaze"
        self.tvdb_api_key = os.getenv("TVDB_API_KEY", "").strip()
        self.tvdb_pin = os.getenv("TVDB_PIN", "").strip()
        self.tvdb_token: Optional[str] = None

    def set_preferred_source(self, source: str):
        """Set preferred metadata source for this runtime session."""
        self.preferred_source = "tvmaze"

    def _tvdb_headers(self) -> Optional[Dict[str, str]]:
        """Build TVDB auth headers if credentials are available."""
        if not self.tvdb_api_key:
            return None

        if not self.tvdb_token and not self._tvdb_login():
            return None

        return {
            'Authorization': f'Bearer {self.tvdb_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def _tvdb_login(self) -> bool:
        """Authenticate with TVDB v4 API and cache token in memory."""
        if not self.tvdb_api_key:
            return False

        payload = {'apikey': self.tvdb_api_key}
        if self.tvdb_pin:
            payload['pin'] = self.tvdb_pin

        try:
            url = f"{CONFIG['TVDB_API_BASE']}/login"
            response = self.session.post(url, json=payload, timeout=8)
            response.raise_for_status()
            data = response.json()
            token = data.get('data', {}).get('token')
            if token:
                self.tvdb_token = token
                return True
        except Exception as e:
            console.print(f"[yellow]Warning: TVDB login failed: {e}[/yellow]")

        return False

    def _search_show_tvdb(self, query: str) -> Optional[Dict]:
        """Search for a show in TVDB."""
        headers = self._tvdb_headers()
        if not headers:
            return None

        try:
            url = f"{CONFIG['TVDB_API_BASE']}/search"
            params = {'query': query, 'type': 'series'}
            response = self.session.get(url, params=params, headers=headers, timeout=8)
            response.raise_for_status()
            results = response.json().get('data', [])

            if results:
                series = results[0]
                series_id = series.get('tvdb_id') or series.get('id')
                if series_id:
                    return {
                        'id': int(series_id),
                        'name': series.get('name', query),
                        '_source': 'tvdb',
                    }
        except Exception as e:
            console.print(f"[yellow]Warning: TVDB show lookup failed for '{query}': {e}[/yellow]")

        return None

    def _get_episode_tvdb(self, series_id: int, season: int, episode: int) -> Optional[str]:
        """Get episode title from TVDB."""
        headers = self._tvdb_headers()
        if not headers:
            return None

        try:
            url = f"{CONFIG['TVDB_API_BASE']}/series/{series_id}/episodes/default/{season}/{episode}"
            response = self.session.get(url, headers=headers, timeout=8)
            response.raise_for_status()
            data = response.json().get('data', {})
            return data.get('name')
        except Exception:
            # Fall back to season endpoint for broader compatibility with API variants.
            try:
                url = f"{CONFIG['TVDB_API_BASE']}/series/{series_id}/episodes/official"
                params = {'season': season}
                response = self.session.get(url, params=params, headers=headers, timeout=8)
                response.raise_for_status()
                episodes = response.json().get('data', {}).get('episodes', [])
                for ep in episodes:
                    if ep.get('number') == episode:
                        return ep.get('name')
            except Exception as e:
                console.print(f"[yellow]Warning: TVDB episode lookup failed: {e}[/yellow]")

        return None
    
    def search_show(self, query: str) -> Optional[Dict]:
        """Search for a show by name."""
        cached = self.cache.get_show(query)
        if cached:
            return cached

        preferred = "tvmaze"
        ordered_sources = ['tvdb', 'tvmaze'] if preferred == 'tvdb' else ['tvmaze', 'tvdb']

        for source in ordered_sources:
            if source == 'tvmaze':
                try:
                    url = f"{CONFIG['API_SEARCH']}{query}"
                    response = self.session.get(url, timeout=5)
                    response.raise_for_status()

                    data = response.json()
                    if data:
                        show_data = data[0].get('show', {})
                        if show_data.get('id'):
                            show_data['_source'] = 'tvmaze'
                            self.cache.set_show(query, show_data)
                            return show_data
                except Exception as e:
                    console.print(f"[red]API Error searching TVMaze for '{query}': {e}[/red]")

            if source == 'tvdb':
                show_data = self._search_show_tvdb(query)
                if show_data:
                    self.cache.set_show(query, show_data)
                    return show_data
        
        return None
    
    def get_episode(self, show_id: int, season: int, episode: int) -> Optional[str]:
        """Get episode name from show ID."""
        # Try preferred source first, then fallback.
        preferred = "tvmaze"

        if preferred == 'tvdb':
            ep_name = self._get_episode_tvdb(show_id, season, episode)
            if ep_name:
                return ep_name

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

        if preferred != 'tvdb':
            return self._get_episode_tvdb(show_id, season, episode)
        
        return None


# ============================================================================
# SHOW DETECTION & FUZZY MATCHING
# ============================================================================

class ShowDetector:
    """Detects show names from folder names and file patterns, with fuzzy matching."""
    
    def __init__(self, api: TVMazeAPI):
        self.api = api

    def _is_generic_folder_name(self, name: str) -> bool:
        """Return True for folder names that are not reliable show titles."""
        generic_patterns = [
            r'(?i)^season\s*\d+$',
            r'(?i)^s\d+$',
            r'(?i)^specials?$',
            r'(?i)^extras?$',
            r'(?i)^episodes?$',
            r'(?i)^complete\s*series$',
            r'(?i)^disc\s*\d+$',
            r'(?i)^cd\s*\d+$',
        ]
        return any(re.fullmatch(pattern, name.strip()) for pattern in generic_patterns)
    
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

        if self._is_generic_folder_name(cleaned):
            # Use parent folder when current folder is only a season/disc marker.
            parent = os.path.dirname(folder_path)
            if parent and parent != folder_path:
                parent_name = os.path.basename(parent)
                cleaned_parent = self.clean_name(parent_name)
                if cleaned_parent:
                    show = self.api.search_show(cleaned_parent)
                    if show and show.get('id'):
                        return cleaned_parent, show
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

    def guess_show_from_filename(self, filename: str) -> Optional[Tuple[str, Dict]]:
        """Guess show name from filename when folder names are generic."""
        stem = os.path.splitext(filename)[0]

        # Trim everything from the first episode marker onward.
        stem = re.sub(r'(?i)\b[sS]\d{1,2}[eE]\d{1,2}.*$', '', stem)
        stem = re.sub(r'(?i)\b\d{1,2}x\d{1,2}.*$', '', stem)
        stem = re.sub(r'(?i)\bseason[\s._-]*\d+[\s._-]*(?:episode|ep)[\s._-]*\d+.*$', '', stem)

        # Clean trailing separators left behind after trimming.
        stem = re.sub(r'[\s._-]+$', '', stem)
        cleaned = self.clean_name(stem)
        if not cleaned:
            return None

        show = self.api.search_show(cleaned)
        if show and show.get('id'):
            return cleaned, show

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
            # Season 1 Episode 01 or Season_1_Ep_01 variants
            r'[sS]eason[\s._-]*(\d+)[\s._-]*(?:[eE]pisode|[eE]p)[\s._-]*(\d+)(?:-(?:[eE]pisode|[eE]p)?(\d+)|[\s._-]*(?:to|through|thru)[\s._-]*(?:[eE]pisode|[eE]p)?[\s._-]*(\d+))?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                season = int(match.group(1))
                start_ep = int(match.group(2))
                end_raw = next((g for g in match.groups()[2:] if g is not None), None)
                end_ep = int(end_raw) if end_raw else None
                return season, start_ep, end_ep
        
        return None

    @staticmethod
    def extract_episode_title_from_filename(filename: str) -> Optional[str]:
        """Extract a human title from filenames like 'Season 1 Episode 02 - 46 Long'."""
        stem = os.path.splitext(filename)[0]
        patterns = [
            r'(?i)\bseason[\s._-]*\d+[\s._-]*(?:episode|ep)[\s._-]*\d+\s*[-:.]\s*(.+)$',
            r'(?i)\b[s]\d{1,2}[e]\d{1,2}(?:-[e]\d{1,2})?\s*[-:.]\s*(.+)$',
            r'(?i)\b\d{1,2}x\d{1,2}\s*[-:.]\s*(.+)$',
        ]
        for pattern in patterns:
            match = re.search(pattern, stem)
            if match:
                title = match.group(1).strip(" .-_")
                if title:
                    return title
        return None


class FileRenamer:
    """Handles file scanning and rename planning."""
    
    def __init__(
        self,
        api: TVMazeAPI,
        detector: ShowDetector,
        root_path: str,
        tv_episode_format: str = "sxe",
        naming_profile: str = "plex"
    ):
        self.api = api
        self.detector = detector
        self.root_path = root_path
        self.tv_episode_format = tv_episode_format.strip().lower()
        self.naming_profile = naming_profile.strip().lower()
        self._root_dir_names_cache: Optional[List[str]] = None

    def _format_episode_token(self, season: int, start_ep: int, end_ep: Optional[int]) -> str:
        """Format TV episode token based on selected naming convention."""
        # Kodi profile always uses strict SxxEyy style.
        if self.naming_profile == "kodi":
            if end_ep:
                return f"S{season:02d}E{start_ep:02d}E{end_ep:02d}"
            return f"S{season:02d}E{start_ep:02d}"

        if self.tv_episode_format == "x":
            if end_ep:
                return f"{season}x{start_ep:02d}-x{end_ep:02d}"
            return f"{season}x{start_ep:02d}"

        if end_ep:
            return f"s{season:02d}e{start_ep:02d}-e{end_ep:02d}"
        return f"s{season:02d}e{start_ep:02d}"

    @staticmethod
    def _sanitize_path_component(value: str) -> str:
        """Sanitize filename/folder name for cross-platform filesystem safety."""
        sanitized = re.sub(r'[<>:"/\\|?*]', '', value)
        sanitized = sanitized.strip().rstrip('.')
        return sanitized

    @staticmethod
    def _extract_show_year(show_data: Dict) -> Optional[int]:
        """Extract a release year from API show metadata when available."""
        candidates = [
            show_data.get('premiered'),
            show_data.get('firstAired'),
            show_data.get('year'),
        ]
        for value in candidates:
            if value is None:
                continue
            match = re.search(r'\b(19\d{2}|20\d{2})\b', str(value))
            if match:
                return int(match.group(1))
        return None

    @staticmethod
    def _normalize_title_base(value: str) -> str:
        """Normalize a show title for folder-matching (ignores optional year suffix)."""
        base = re.sub(r'\s*\(\d{4}\)\s*$', '', value).strip().lower()
        base = re.sub(r'[^a-z0-9]+', '', base)
        return base

    def _get_root_dir_names(self) -> List[str]:
        """Return top-level directories in root path (cached for one scan session)."""
        if self._root_dir_names_cache is not None:
            return self._root_dir_names_cache

        names: List[str] = []
        try:
            for entry in os.scandir(self.root_path):
                if entry.is_dir():
                    names.append(entry.name)
        except Exception:
            names = []

        self._root_dir_names_cache = names
        return names

    def _resolve_existing_show_folder(self, show_name: str, preferred_folder: str) -> str:
        """Reuse existing folder variants to avoid creating duplicate series folders."""
        existing = self._get_root_dir_names()
        if not existing:
            return preferred_folder

        target_base = self._normalize_title_base(show_name)
        candidates = [name for name in existing if self._normalize_title_base(name) == target_base]

        # If preferred already exists and there are no competing variants, use it directly.
        if preferred_folder in existing and len(candidates) <= 1:
            return preferred_folder

        if not candidates:
            return preferred_folder

        # Prefer year-qualified folders when available, then exact plain title, then first stable candidate.
        year_candidates = sorted([name for name in candidates if re.search(r'\(\d{4}\)\s*$', name)])
        if year_candidates:
            return year_candidates[0]

        plain_title = self._sanitize_path_component(show_name)
        if plain_title in candidates:
            return plain_title

        return sorted(candidates)[0]

    def write_kodi_tvshow_nfo(self, show_folder_path: str, show_data: Dict) -> bool:
        """Write tvshow.nfo with a TVMaze URL to lock Kodi scraper matching."""
        externals = show_data.get('externals') or {}
        imdb_id = externals.get('imdb')
        tvdb_id = externals.get('thetvdb')
        tvmaze_id = show_data.get('id')

        preference = CONFIG.get("KODI_NFO_SOURCE", "auto").strip().lower()
        nfo_url = None

        if preference == "tvdb" and tvdb_id:
            nfo_url = f"https://www.thetvdb.com/series/{tvdb_id}"
        elif preference == "imdb" and imdb_id:
            nfo_url = f"https://www.imdb.com/title/{imdb_id}/"
        elif preference == "tvmaze" and tvmaze_id:
            nfo_url = f"https://www.tvmaze.com/shows/{tvmaze_id}"
        elif preference == "auto":
            if imdb_id:
                nfo_url = f"https://www.imdb.com/title/{imdb_id}/"
            elif tvdb_id:
                nfo_url = f"https://www.thetvdb.com/series/{tvdb_id}"
            elif tvmaze_id:
                nfo_url = f"https://www.tvmaze.com/shows/{tvmaze_id}"

        if not nfo_url:
            # Fallback order if preferred source is unavailable.
            if tvdb_id:
                nfo_url = f"https://www.thetvdb.com/series/{tvdb_id}"
            elif imdb_id:
                nfo_url = f"https://www.imdb.com/title/{imdb_id}/"
            elif tvmaze_id:
                nfo_url = f"https://www.tvmaze.com/shows/{tvmaze_id}"
            else:
                return False

        nfo_path = os.path.join(show_folder_path, "tvshow.nfo")
        nfo_content = f"{nfo_url}\n"

        try:
            os.makedirs(show_folder_path, exist_ok=True)
            if os.path.exists(nfo_path):
                with open(nfo_path, "r", encoding="utf-8") as f:
                    existing = f.read().strip()
                if existing == nfo_content.strip():
                    return True
            with open(nfo_path, "w", encoding="utf-8") as f:
                f.write(nfo_content)
            return True
        except Exception:
            return False

    @staticmethod
    def clean_kodi_episode_title(title: str) -> str:
        """Normalize stylized titles so Kodi display avoids fake media extensions."""
        value = html.unescape((title or "").strip())
        value = re.sub(r'\.(mov|mpeg|mkv|mp4|wmv|avi|flv|m4v)$', '', value, flags=re.I)
        # Remove prefixes like "eps1.0_" so Kodi doesn't show redundant numbering.
        value = re.sub(r'(?i)^eps\d+(?:\.\d+)?[_\s-]*', '', value)
        value = value.replace('_', ' ')
        value = re.sub(r'\s+', ' ', value).strip()
        return value

    @staticmethod
    def write_kodi_episode_nfo(
        media_file_path: str,
        show_name: str,
        season: int,
        episode: int,
        episode_title: str
    ) -> bool:
        """Write sidecar episode NFO next to media file for Kodi episode title override."""
        nfo_path = os.path.splitext(media_file_path)[0] + ".nfo"
        xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<episodedetails>\n'
            f'  <title>{html.escape(episode_title)}</title>\n'
            f'  <showtitle>{html.escape(show_name)}</showtitle>\n'
            f'  <season>{season}</season>\n'
            f'  <episode>{episode}</episode>\n'
            '</episodedetails>\n'
        )

        try:
            if os.path.exists(nfo_path):
                with open(nfo_path, "r", encoding="utf-8") as f:
                    existing = f.read()
                if existing == xml:
                    return True
            with open(nfo_path, "w", encoding="utf-8") as f:
                f.write(xml)
            return True
        except Exception:
            return False
    
    def scan_media_files(self, root_path: str) -> List[str]:
        """Scan for media files."""
        files = []
        for root, dirs, filenames in os.walk(root_path):
            for filename in filenames:
                if any(filename.lower().endswith(ext) for ext in CONFIG['SUPPORTED_EXTENSIONS']):
                    files.append(os.path.join(root, filename))
        return files

    @staticmethod
    def _clean_movie_title(value: str) -> str:
        """Normalize movie title text from folder/file names."""
        value = re.sub(r'\[.*?\]', '', value)
        value = re.sub(r'\(.*?\)$', '', value)
        value = re.sub(r'\b(720p|1080p|2160p|bluray|webrip|x264|x265|h264|h265|dvdrip)\b', '', value, flags=re.I)
        value = value.replace('.', ' ').replace('_', ' ')
        value = re.sub(r'\s+', ' ', value).strip(' -')
        return value

    @staticmethod
    def _extract_movie_title_year(filename: str, folder_path: str) -> Tuple[Optional[str], Optional[int]]:
        """Extract best-effort movie title and optional year from file/folder names."""
        stem = os.path.splitext(os.path.basename(filename))[0]
        folder_name = os.path.basename(folder_path)

        generic_folder_names = {
            "movies", "movie", "films", "film", "videos", "video", "media"
        }

        year = None
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', stem)
        if not year_match:
            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', folder_name)
        if year_match:
            year = int(year_match.group(1))

        # Prefer folder title when it looks specific, otherwise file stem.
        if folder_name.strip().lower() in generic_folder_names:
            base = stem
        else:
            base = folder_name if len(folder_name) >= 4 else stem
        title = re.split(r'\b(19\d{2}|20\d{2})\b', base)[0]
        title = FileRenamer._clean_movie_title(title)
        if not title:
            title = FileRenamer._clean_movie_title(re.split(r'\b(19\d{2}|20\d{2})\b', stem)[0])

        return (title or None), year

    def plan_movie_rename(self, file_path: str) -> Optional[RenameAction]:
        """Plan a movie rename to Plex movie format: Movie Name (Year)/Movie Name (Year).ext"""
        filename = os.path.basename(file_path)
        dir_path = os.path.dirname(file_path)
        ext = os.path.splitext(filename)[1]

        title, year = self._extract_movie_title_year(filename, dir_path)
        if not title:
            return None

        if year:
            movie_base = f"{title} ({year})"
        else:
            movie_base = title

        movie_base = self._sanitize_path_component(movie_base)

        new_filename = f"{movie_base}{ext}"
        new_path = os.path.join(self.root_path, movie_base, new_filename)

        if file_path.lower() == new_path.lower():
            return None

        return RenameAction(
            original_path=file_path,
            new_path=new_path,
            media_type="movies",
            show_name=movie_base,
            season=0,
            episode=0,
            episode_name="Movie"
        )
    
    def plan_tv_rename(self, file_path: str) -> Optional[RenameAction]:
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
            show_match = self.detector.guess_show_from_filename(filename)
        if not show_match:
            return None
        
        query, show_data = show_match
        show_name = show_data.get('name')
        show_id = show_data.get('id')
        
        if not show_name or not show_id:
            return None
        
        # Get episode name
        filename_ep_title = EpisodeExtractor.extract_episode_title_from_filename(filename)
        ep_name = self.api.get_episode(show_id, season, start_ep)
        if ep_name:
            ep_name = html.unescape(ep_name)
        if filename_ep_title:
            # Prefer source filename title when present; these rips are often more accurate for casing/punctuation.
            ep_name = filename_ep_title
        if not ep_name:
            ep_name = f"Episode {start_ep}"
        
        # Build Plex-perfect path
        season_folder = f"Season {season:02d}"
        show_year = self._extract_show_year(show_data)
        if show_year:
            preferred_show_folder = self._sanitize_path_component(f"{show_name} ({show_year})")
        else:
            preferred_show_folder = self._sanitize_path_component(show_name)
        show_folder = self._resolve_existing_show_folder(show_name, preferred_show_folder)
        show_folder_path = os.path.join(self.root_path, show_folder)

        if self.naming_profile == "kodi" and CONFIG.get("KODI_WRITE_NFO", True):
            self.write_kodi_tvshow_nfo(show_folder_path, show_data)
        
        # Format episode string
        ep_str = self._format_episode_token(season, start_ep, end_ep)
        
        if show_year:
            display_show_name = f"{show_name} ({show_year})"
        else:
            display_show_name = show_name

        safe_show_name = self._sanitize_path_component(display_show_name)
        safe_ep_name = self._sanitize_path_component(ep_name)

        if self.naming_profile == "kodi":
            # Kodi strict form: Show Name (Year) - S01E01.ext
            new_filename = f"{safe_show_name} - {ep_str}{ext}"
        else:
            # Plex-friendly form keeps human episode title.
            new_filename = f"{safe_show_name} - {ep_str} - {safe_ep_name}{ext}"
        new_path = os.path.join(show_folder_path, season_folder, new_filename)
        
        # Skip if already correctly named
        if file_path.lower() == new_path.lower():
            return None
        
        return RenameAction(
            original_path=file_path,
            new_path=new_path,
            media_type="tv",
            show_name=show_name,
            season=season,
            episode=start_ep,
            episode_name=ep_name
        )

    def plan_rename(self, file_path: str, media_type: str) -> Optional[RenameAction]:
        """Plan a rename based on the selected media type."""
        normalized = media_type.strip().lower()
        if normalized == "tv":
            return self.plan_tv_rename(file_path)
        if normalized == "movies":
            return self.plan_movie_rename(file_path)
        if normalized == "both":
            tv_action = self.plan_tv_rename(file_path)
            if tv_action:
                return tv_action
            return self.plan_movie_rename(file_path)
        return None


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
            "media_type": action.media_type,
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

    @staticmethod
    def _has_media_files(path: str, max_dirs: int = 200) -> bool:
        """Fast check for at least one supported media file under a path."""
        checked = 0
        for root, _, files in os.walk(path):
            checked += 1
            for name in files:
                if any(name.lower().endswith(ext) for ext in CONFIG['SUPPORTED_EXTENSIONS']):
                    return True
            if checked >= max_dirs:
                break
        return False

    @staticmethod
    def _resolve_root_path(root_path: str, media_type: str = "tv") -> str:
        """Resolve a usable media root across common Windows/Linux path styles."""
        # On Windows, transparently map /r/... style defaults to R:\... paths.
        if os.name == "nt" and root_path.startswith("/r/"):
            mapped_root = f"R:\\{root_path[3:].replace('/', '\\')}"
            if os.path.exists(mapped_root):
                return mapped_root

        if os.path.exists(root_path) and PlexRenamer._has_media_files(root_path):
            return root_path

        if media_type == "movies":
            candidates = [
                r"R:\media\movies",
                r"R:\media\Movies",
                r"/r/media/movies",
                r"/r/media/Movies",
            ]
        elif media_type == "both":
            candidates = [
                r"R:\media",
                r"/r/media",
                r"R:\media\tv",
                r"R:\media\movies",
            ]
        else:
            candidates = [
                r"R:\media\tv",
                r"R:\media\TV",
                r"/r/media/tv",
                r"/r/media/TV",
            ]

        for candidate in candidates:
            if os.path.exists(candidate) and PlexRenamer._has_media_files(candidate):
                return candidate

        if os.path.exists(root_path):
            return root_path

        return root_path
    
    def __init__(
        self,
        root_path: str = CONFIG['ROOT'],
        media_type: str = "tv",
        tv_episode_format: str = CONFIG['TV_EPISODE_FORMAT'],
        naming_profile: str = CONFIG['NAMING_PROFILE'],
        metadata_source: str = CONFIG['PREFERRED_SOURCE']
    ):
        self.media_type = media_type
        self.tv_episode_format = tv_episode_format.strip().lower()
        self.naming_profile = naming_profile.strip().lower()
        self.metadata_source = "tvmaze"
        self.root_path = self._resolve_root_path(root_path, media_type)
        self.backup_dir = os.path.join(self.root_path, ".backups")
        self.cache_file = os.path.join(self.backup_dir, "show_cache.json")
        self.history_file = os.path.join(self.backup_dir, "rename_history.json")

        self.cache = ShowCache(self.cache_file)
        self.api = TVMazeAPI(self.cache)
        self.api.set_preferred_source("tvmaze")
        self.detector = ShowDetector(self.api)
        self.renamer = FileRenamer(
            self.api,
            self.detector,
            self.root_path,
            self.tv_episode_format,
            self.naming_profile
        )
        self.history = RenameHistory(self.history_file)
        self.actions: List[RenameAction] = []

    @staticmethod
    def _is_non_empty_directory(path: str) -> bool:
        """Return True when a directory contains at least one file or child directory."""
        if not os.path.isdir(path):
            return False
        try:
            return any(True for _ in os.scandir(path))
        except Exception:
            return True

    def configure_runtime(
        self,
        root_path: str,
        media_type: str,
        tv_episode_format: Optional[str] = None,
        naming_profile: Optional[str] = None,
        metadata_source: Optional[str] = None
    ):
        """Update runtime target folder and media type from interactive prompts."""
        selected_type = media_type.strip().lower()
        selected_episode_format = (tv_episode_format or self.tv_episode_format).strip().lower()
        selected_naming_profile = (naming_profile or self.naming_profile).strip().lower()
        resolved_root = self._resolve_root_path(root_path, selected_type)

        self.media_type = selected_type
        self.tv_episode_format = selected_episode_format
        self.naming_profile = selected_naming_profile
        self.metadata_source = "tvmaze"
        self.root_path = resolved_root
        self.backup_dir = os.path.join(self.root_path, ".backups")
        self.cache_file = os.path.join(self.backup_dir, "show_cache.json")
        self.history_file = os.path.join(self.backup_dir, "rename_history.json")

        self.cache = ShowCache(self.cache_file)
        self.api = TVMazeAPI(self.cache)
        self.api.set_preferred_source("tvmaze")
        self.detector = ShowDetector(self.api)
        self.renamer = FileRenamer(
            self.api,
            self.detector,
            self.root_path,
            self.tv_episode_format,
            self.naming_profile
        )
        self.history = RenameHistory(self.history_file)
        self.actions = []
    
    def display_banner(self):
        """Display welcome banner."""
        console.print(Panel(
            "[bold cyan]Plex Media Renamer[/bold cyan]\n"
            "Organize TV shows and movies in Plex format",
            style="cyan"
        ))
    
    def display_plan(self):
        """Display rename plan in a table."""
        if not self.actions:
            console.print("[yellow]No changes needed![/yellow]")
            return
        
        table = Table(title=f"Rename Plan ({len(self.actions)} files)")
        table.add_column("Type", style="yellow")
        table.add_column("Title", style="cyan")
        table.add_column("Info", style="magenta")
        table.add_column("Status", style="green")
        
        for action in self.actions:
            ep_name = action.episode_name[:30] + "..." if len(action.episode_name) > 30 else action.episode_name
            if action.media_type == "tv":
                info = f"S{action.season:02d}E{action.episode:02d}"
            else:
                info = "Movie"
            table.add_row(
                action.media_type,
                action.show_name,
                info,
                ep_name
            )
        
        console.print(table)

    def _discover_folder_layout_fixes(self) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
        """Plan top-level TV folder rename fixes and blocked conflicts.

        Returns:
        - fixes: (old_path, new_path, reason)
        - blocked: (old_path, desired_path, reason)
        """
        fixes: List[Tuple[str, str, str]] = []
        blocked: List[Tuple[str, str, str]] = []
        if not os.path.exists(self.root_path):
            return fixes, blocked

        try:
            entries = [e for e in os.scandir(self.root_path) if e.is_dir()]
        except Exception:
            return fixes, blocked

        existing_names = {e.name.lower(): e.name for e in entries}

        for entry in entries:
            current_name = entry.name
            if current_name.startswith('.'):
                continue

            cleaned = self.detector.clean_name(current_name)
            if not cleaned:
                continue

            base_query = re.sub(r'\s*\(\d{4}\)\s*$', '', cleaned).strip()
            if not base_query:
                continue

            show_data = self.api.search_show(base_query)
            if not show_data or not show_data.get('name'):
                continue

            show_name = show_data.get('name')
            show_year = self.renamer._extract_show_year(show_data)
            if show_year:
                desired_name = self.renamer._sanitize_path_component(f"{show_name} ({show_year})")
            else:
                desired_name = self.renamer._sanitize_path_component(show_name)

            if current_name.lower() == desired_name.lower():
                continue

            target_exists = desired_name.lower() in existing_names and existing_names[desired_name.lower()] != current_name
            if target_exists:
                old_path = os.path.join(self.root_path, current_name)
                desired_path = os.path.join(self.root_path, desired_name)
                blocked.append((old_path, desired_path, "target already exists"))
                continue

            old_path = os.path.join(self.root_path, current_name)
            new_path = os.path.join(self.root_path, desired_name)
            fixes.append((old_path, new_path, f"{current_name} -> {desired_name}"))

        return fixes, blocked

    def fix_folder_layout(self):
        """Rename top-level show folders in place to normalized names without moving individual files."""
        if self.media_type not in ("tv", "both"):
            console.print("[yellow]Folder layout fix currently applies to TV show roots only.[/yellow]")
            return

        fixes, blocked = self._discover_folder_layout_fixes()
        if not fixes and not blocked:
            console.print("[yellow]No folder layout fixes needed.[/yellow]")
            return

        if fixes:
            table = Table(title=f"Folder Layout Fixes ({len(fixes)})")
            table.add_column("Current Folder", style="cyan")
            table.add_column("New Folder", style="green")
            for old_path, new_path, _ in fixes[:30]:
                table.add_row(os.path.basename(old_path), os.path.basename(new_path))
            console.print(table)

        if blocked:
            blocked_table = Table(title=f"Blocked Folder Fixes ({len(blocked)})")
            blocked_table.add_column("Current Folder", style="yellow")
            blocked_table.add_column("Desired Folder", style="magenta")
            blocked_table.add_column("Reason", style="red")
            for old_path, desired_path, reason in blocked[:30]:
                blocked_table.add_row(os.path.basename(old_path), os.path.basename(desired_path), reason)
            console.print(blocked_table)

        if fixes and not Confirm.ask("Apply direct folder rename fixes?", default=True):
            return

        renamed = 0
        skipped = 0
        protected_non_empty = 0
        allow_non_empty = not CONFIG.get("PROTECT_NON_EMPTY_FOLDERS", True)

        if not allow_non_empty:
            allow_non_empty = Confirm.ask(
                "Allow renaming non-empty folders? (recommended: no)",
                default=False
            )

        if fixes:
            for old_path, new_path, _ in fixes:
                try:
                    if os.path.exists(new_path):
                        skipped += 1
                        continue

                    if self._is_non_empty_directory(old_path) and not allow_non_empty:
                        protected_non_empty += 1
                        continue

                    os.rename(old_path, new_path)
                    renamed += 1
                except Exception as e:
                    skipped += 1
                    console.print(f"[red]Folder rename error: {old_path} -> {e}[/red]")

        # Optional fallback: still rename blocked folders, but with a suffix, never moving contents.
        if blocked and Confirm.ask("Rename blocked folders with suffix ' - unmerged' (still rename-only)?", default=False):
            for old_path, desired_path, _ in blocked:
                desired_name = os.path.basename(desired_path)
                parent = os.path.dirname(desired_path)

                if self._is_non_empty_directory(old_path) and not allow_non_empty:
                    protected_non_empty += 1
                    continue

                candidate = f"{desired_name} - unmerged"
                index = 2
                while os.path.exists(os.path.join(parent, candidate)):
                    candidate = f"{desired_name} - unmerged {index}"
                    index += 1

                fallback_path = os.path.join(parent, candidate)
                try:
                    os.rename(old_path, fallback_path)
                    renamed += 1
                except Exception as e:
                    skipped += 1
                    console.print(f"[red]Folder rename error: {old_path} -> {e}[/red]")

        if skipped or protected_non_empty:
            console.print(
                f"[yellow]Folder layout fix complete: renamed {renamed}, skipped {skipped}, protected non-empty {protected_non_empty}.[/yellow]"
            )
        else:
            console.print(f"[green]Folder layout fix complete: renamed {renamed}.[/green]")

    def generate_kodi_nfo_for_all_shows(self):
        """Generate/update tvshow.nfo for all top-level TV show folders without renaming files."""
        if self.media_type not in ("tv", "both"):
            console.print("[yellow]NFO generation currently applies to TV show roots only.[/yellow]")
            return

        if not os.path.exists(self.root_path):
            console.print("[yellow]TV root path does not exist.[/yellow]")
            return

        show_dirs = []
        for entry in os.scandir(self.root_path):
            if entry.is_dir() and not entry.name.startswith('.'):
                show_dirs.append(entry)

        if not show_dirs:
            console.print("[yellow]No show folders found.[/yellow]")
            return

        written = 0
        skipped = 0
        failed = 0

        for entry in sorted(show_dirs, key=lambda e: e.name.lower()):
            cleaned = self.detector.clean_name(entry.name)
            query = re.sub(r'\s*\(\d{4}\)\s*$', '', cleaned).strip()
            if not query:
                skipped += 1
                continue

            show_data = self.api.search_show(query)
            if not show_data or not show_data.get('id'):
                skipped += 1
                continue

            if self.renamer.write_kodi_tvshow_nfo(entry.path, show_data):
                written += 1
            else:
                failed += 1

        if failed:
            console.print(f"[yellow]NFO generation complete: written {written}, skipped {skipped}, failed {failed}.[/yellow]")
        else:
            console.print(f"[green]NFO generation complete: written {written}, skipped {skipped}.[/green]")

    def generate_kodi_episode_nfo_for_all_shows(self):
        """Generate/update per-episode NFO sidecars to control Kodi episode titles."""
        if self.media_type not in ("tv", "both"):
            console.print("[yellow]Episode NFO generation currently applies to TV show roots only.[/yellow]")
            return

        if not os.path.exists(self.root_path):
            console.print("[yellow]TV root path does not exist.[/yellow]")
            return

        written = 0
        skipped = 0
        failed = 0

        show_dirs = [e for e in os.scandir(self.root_path) if e.is_dir() and not e.name.startswith('.')]
        for show_dir in sorted(show_dirs, key=lambda e: e.name.lower()):
            show_query = re.sub(r'\s*\(\d{4}\)\s*$', '', self.detector.clean_name(show_dir.name)).strip()
            if not show_query:
                continue

            show_data = self.api.search_show(show_query)
            if not show_data or not show_data.get('id'):
                continue

            show_id = show_data.get('id')
            show_name = show_data.get('name') or show_query

            for root, _, files in os.walk(show_dir.path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    if not any(filename.lower().endswith(ext) for ext in CONFIG['SUPPORTED_EXTENSIONS']):
                        continue

                    ep_info = EpisodeExtractor.extract_episodes(filename)
                    if not ep_info:
                        skipped += 1
                        continue

                    season, start_ep, _ = ep_info
                    ep_name = self.api.get_episode(show_id, season, start_ep)
                    if not ep_name:
                        ep_name = EpisodeExtractor.extract_episode_title_from_filename(filename)
                    if not ep_name:
                        ep_name = f"Episode {start_ep}"

                    if CONFIG.get("KODI_CLEAN_EPISODE_TITLES", True):
                        ep_name = self.renamer.clean_kodi_episode_title(ep_name)

                    ok = self.renamer.write_kodi_episode_nfo(file_path, show_name, season, start_ep, ep_name)
                    if ok:
                        written += 1
                    else:
                        failed += 1

        if failed:
            console.print(f"[yellow]Episode NFO generation complete: written {written}, skipped {skipped}, failed {failed}.[/yellow]")
        else:
            console.print(f"[green]Episode NFO generation complete: written {written}, skipped {skipped}.[/green]")
    
    def scan_and_plan(self):
        """Scan files and plan renames."""
        console.print(f"\n[bold]Scanning[/bold] {self.root_path}...")
        
        files = self.renamer.scan_media_files(self.root_path)
        console.print(f"Found [cyan]{len(files)}[/cyan] media files")
        
        self.actions = []

        if not files:
            console.print("[yellow]No media files found.[/yellow]")
            return

        status_step = max(1, len(files) // 50)
        console.print("[cyan]Planning renames...[/cyan]")

        for idx, file_path in enumerate(files, start=1):
            action = self.renamer.plan_rename(file_path, self.media_type)
            if action:
                self.actions.append(action)

            if idx % status_step == 0 or idx == len(files):
                print(f"\r  Processed {idx}/{len(files)} files", end="", flush=True)

        print()
        
        console.print(f"\nPlanned [cyan]{len(self.actions)}[/cyan] rename operations")
    
    def commit_changes(self):
        """Apply all rename operations."""
        if not self.actions:
            return
        
        console.print(f"\n[bold]Applying {len(self.actions)} changes...[/bold]\n")

        total = len(self.actions)
        status_step = max(1, total // 50)
        success_count = 0
        failure_count = 0
        skipped_count = 0

        for idx, action in enumerate(self.actions, start=1):
            try:
                if not os.path.exists(action.original_path):
                    skipped_count += 1
                    print()
                    console.print(f"[yellow]Skipped missing source: {action.original_path}[/yellow]")
                    continue

                if os.path.exists(action.new_path):
                    skipped_count += 1
                    print()
                    console.print(f"[yellow]Skipped existing destination: {action.new_path}[/yellow]")
                    continue

                # Create parent directories
                os.makedirs(os.path.dirname(action.new_path), exist_ok=True)
                
                # Move file
                shutil.move(action.original_path, action.new_path)
                
                # Record in history
                self.history.record_rename(action)
                success_count += 1
                
            except Exception as e:
                failure_count += 1
                print()
                console.print(f"[red]Error: {action.original_path} -> {e}[/red]")

            if idx % status_step == 0 or idx == total:
                print(f"\r  Applied {idx}/{total} changes", end="", flush=True)

        print()
        
        if failure_count or skipped_count:
            console.print(
                f"\n[yellow]Applied {success_count}/{total} changes with {failure_count} error(s) and {skipped_count} skipped.[/yellow]"
            )
        else:
            console.print("\n[green]✓ All changes applied successfully![/green]")
    
    def show_recent_history(self, count: int = 10):
        """Display recent rename history."""
        recent = self.history.get_recent(count)
        if not recent:
            console.print("[yellow]No rename history[/yellow]")
            return
        
        table = Table(title=f"Recent Renames (last {len(recent)})")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Title", style="magenta")
        table.add_column("Info", style="green")
        
        for record in recent[-10:]:
            timestamp = record['timestamp'][:19]
            media_type = record.get('media_type', 'tv')
            if media_type == 'tv':
                info = f"S{record.get('season', 0):02d}E{record.get('episode', 0):02d}"
            else:
                info = 'Movie'
            table.add_row(
                timestamp,
                media_type,
                record['show'],
                info
            )
        
        console.print(table)
    
    def interactive_menu(self):
        """Interactive menu."""
        self.display_banner()

        entered_root = Prompt.ask("Media folder path", default=self.root_path).strip()
        media_type = Prompt.ask("Media type", choices=["tv", "movies", "both"], default=self.media_type)
        naming_profile = Prompt.ask("Naming profile", choices=["plex", "kodi"], default=self.naming_profile)
        episode_format = Prompt.ask(
            "TV episode naming",
            choices=["sxe", "x"],
            default=self.tv_episode_format
        )
        self.configure_runtime(entered_root, media_type, episode_format, naming_profile)
        console.print(f"Using folder: [cyan]{self.root_path}[/cyan]")
        console.print(f"Media type: [cyan]{self.media_type}[/cyan]")
        console.print(f"Profile: [cyan]{self.naming_profile}[/cyan]")
        console.print(f"TV naming: [cyan]{self.tv_episode_format}[/cyan]")
        console.print("Metadata DB: [cyan]tvmaze[/cyan]")
        
        while True:
            console.print("\n[bold cyan]Options:[/bold cyan]")
            console.print("1. Scan and plan renames")
            console.print("2. Show rename plan")
            console.print("3. Apply changes")
            console.print("4. View recent history")
            console.print("5. Undo last rename")
            console.print("6. Fix folder layout (rename folders only)")
            console.print("7. Generate Kodi tvshow.nfo files")
            console.print("8. Generate Kodi episode .nfo files")
            console.print("9. Exit")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])
            
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
                self.fix_folder_layout()
            elif choice == "7":
                self.generate_kodi_nfo_for_all_shows()
            elif choice == "8":
                self.generate_kodi_episode_nfo_for_all_shows()
            elif choice == "9":
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
