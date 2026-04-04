# Git Repository Setup & Release Strategy

> ⏸️ **For Later:** This guide is for when you're ready to make your project public.
> For setting up your private repository now, see [QUICK_START_PRIVATE.md](QUICK_START_PRIVATE.md) or [PRIVATE_SETUP.md](PRIVATE_SETUP.md)

Complete guide for bundling Plex Renamer as a GitHub repository with recommended distribution strategy.

## Current Status

✅ **Ready for GitHub Release**

Your project has everything needed for distribution:
- ✅ Production-ready code
- ✅ Comprehensive documentation
- ✅ License (MIT)
- ✅ Setup files (pyproject.toml, setup.py)
- ✅ .gitignore configured
- ✅ CHANGELOG.md
- ✅ Release guide (RELEASE.md)

---

## Step 1: Initialize Git Repository

Run these commands in PowerShell at `r:/media/tv`:

```powershell
# Navigate to project
cd r:/media/tv

# Initialize git repo
git init

# Configure git (first time only)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Plex Renamer v1.0.0"

# View commit log
git log --oneline
```

### Expected Output
```
* a1b2c3d (HEAD -> main) Initial commit: Plex Renamer v1.0.0
```

---

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. **Repository name:** `plex-renamer`
3. **Description:** "Professional tool for organizing TV shows in Plex-perfect format"
4. **Public** (recommended - for open source projects)
5. **DO NOT** initialize with README (you already have one)
6. **DO NOT** add .gitignore (you already have one)
7. **License:** MIT (select from dropdown)
8. Click **Create repository**

---

## Step 3: Connect Local Repo to GitHub

GitHub will show you commands. Use one of these:

### Using HTTPS (Easier for beginners)
```powershell
git remote add origin https://github.com/YOUR_USERNAME/plex-renamer.git
git branch -M main
git push -u origin main
```

### Using SSH (If you have SSH keys set up)
```bash
git remote add origin git@github.com:YOUR_USERNAME/plex-renamer.git
git branch -M main
git push -u origin main
```

### Verify Connection
```powershell
git remote -v
# Should show:
# origin https://github.com/YOUR_USERNAME/plex-renamer.git (fetch)
# origin https://github.com/YOUR_USERNAME/plex-renamer.git (push)
```

---

## Recommended Release Strategy: GitHub Releases

### Why GitHub Releases?

**Best for your project because:**
- ✅ Simple - No complicated tooling
- ✅ Free - GitHub hosts everything
- ✅ Discoverable - Shows up in "Releases" tab
- ✅ User-friendly - Easy download as ZIP
- ✅ Flexible - Can host multiple file formats
- ✅ Social - Shows release history/activity
- ✅ Open source friendly - Standard for public projects

---

## Create Your First Release

### Step 1: Tag the Version

```powershell
# Create annotated git tag
git tag -a v1.0.0 -m "Release version 1.0.0 - Initial stable release with all core features"

# Push tag to GitHub
git push origin v1.0.0

# Verify tag was created
git tag -l
```

### Step 2: Create GitHub Release

1. Go to your repository: `https://github.com/YOUR_USERNAME/plex-renamer`
2. Click **Releases** tab (right side)
3. Click **Draft a new release**
4. Select tag: **v1.0.0**
5. Title: **Plex Renamer v1.0.0 - Initial Release**
6. Description (copy/paste):

```markdown
## 🎉 Initial Stable Release

Professional tool for organizing TV shows in Plex-perfect format.

## ✨ Features

- **Progress Bars & Rich UI** - Real-time feedback with beautiful colors
- **Undo System** - Complete rename history, restore previous names anytime
- **Auto-Detect Shows** - Fuzzy matching handles messy folder names
- **Multi-Episode Support** - S01E01-E03 format for grouped episodes
- **Plex-Perfect Structure** - Creates ideal: Show/Season XX/Episode.mkv

## 🚀 Quick Start

### Windows
```cmd
download and extract ZIP, then:
python plex_renamer.py
# or
run.bat
```

### Linux/Mac
```bash
git clone https://github.com/YOUR_USERNAME/plex-renamer.git
cd plex-renamer
python3 plex_renamer.py
```

## 📋 Requirements
- Python 3.7+
- Internet connection (for TVMaze API)

## 📚 Documentation
- [README.md](README.md) - Complete reference
- [QUICKSTART.md](QUICKSTART.md) - 30-second setup
- [FEATURES.md](FEATURES.md) - What's new vs bash script
- [RELEASE.md](RELEASE.md) - How to release updates

## 🔗 Links
- [Full Documentation](https://github.com/YOUR_USERNAME/plex-renamer#readme)
- [Issues](https://github.com/YOUR_USERNAME/plex-renamer/issues)
- [License](LICENSE)

**Ready to use! No installation needed - just download and run.**
```

7. (Optional) Check **This is a pre-release** if you want
8. Click **Publish release**

✅ **Done!** Your release is now live.

---

## How Users Get Your Code

### Option 1: Download from GitHub
- Go to Releases page
- Download "Source code (zip)"
- Extract and run

### Option 2: Clone from Git
```bash
git clone https://github.com/username/plex-renamer.git
cd plex-renamer
python plex_renamer.py
```

### Option 3: Raw File Download
```bash
curl -O https://raw.githubusercontent.com/username/plex-renamer/main/plex_renamer.py
python plex_renamer.py
```

---

## For Future Releases

### When You Make Updates

```powershell
# 1. Make your changes and test locally

# 2. Update version numbers in:
#    - pyproject.toml
#    - setup.py
#    - Update CHANGELOG.md with changes

# 3. Commit changes
git add .
git commit -m "feat: Add new feature or 'fix: Bug fix'"

# 4. Create new version tag
git tag -a v1.1.0 -m "Release v1.1.0 - New features and improvements"
git push origin main v1.1.0

# 5. Go to GitHub Releases and click "Draft a new release"
#    - Select tag v1.1.0
#    - Add description
#    - Publish
```

---

## Advanced: Building Standalone Executable

To create a `.exe` for Windows users (no Python required):

```powershell
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --name plex-renamer plex_renamer.py

# Output: dist/plex-renamer.exe

# Upload to GitHub Releases as asset
```

Users can then:
1. Download `plex-renamer.exe`
2. Double-click to run
3. No Python installation needed!

---

## Optional: Publish to PyPI

Later, if you want users to install via pip:

```bash
pip install plex-renamer
plex-renamer
```

See [RELEASE.md](RELEASE.md) for detailed PyPI instructions.

---

## Project Structure for GitHub

```
plex-renamer/
├── plex_renamer.py          # Main application
├── run.bat                  # Windows launcher
├── run.ps1                  # PowerShell launcher
├── README.md                # Main documentation
├── QUICKSTART.md            # Quick start guide
├── FEATURES.md              # Feature comparison
├── DEVELOPMENT.md           # Dev customization guide
├── RELEASE.md               # Release strategy guide
├── CHANGELOG.md             # Version history
├── LICENSE                  # MIT License
├── .gitignore               # Git ignore rules
├── pyproject.toml           # Modern Python package config
├── setup.py                 # Setup script (for pip)
├── MANIFEST.in              # Package manifest
└── config.example.json      # Configuration template
```

---

## GitHub Best Practices

### 1. Write Good Commit Messages
```bash
git commit -m "feat: Add fuzzy show matching"  # Good
git commit -m "stuff"                         # Bad
```

### 2. Use Releases for Version Tags
- Every release = git tag + GitHub Release
- Helps users track versions
- Clear history of changes

### 3. Keep README Updated
- Keep it current with latest features
- Include installation and usage
- Add badges for visibility

### 4. Update CHANGELOG
- Document every release
- What's new
- What's fixed
- Breaking changes

### 5. Respond to Issues
- Be friendly and helpful
- Consider feature requests
- Document workarounds

---

## Visibility & Discovery

### Make Your Project Discoverable

1. **Add to Awesome Lists**
   - https://github.com/sindresorhus/awesome
   - Search for relevant category (media, tools, python)

2. **GitHub Topics** (on repository page)
   - Add: `plex`, `media`, `python`, `tv-shows`, `renamer`

3. **Social Media**
   - Tweet with #python #plex #opensource
   - Post on Reddit r/python, r/homelab
   - Dev.to article about the project

4. **GitHub README Badges**
   ```markdown
   [![GitHub license](https://img.shields.io/github/license/username/plex-renamer)](LICENSE)
   [![GitHub release](https://img.shields.io/github/release/username/plex-renamer)](https://github.com/username/plex-renamer/releases)
   [![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue)](https://www.python.org/)
   ```

---

## Summary: Complete Setup

### Checklist

- [ ] Initialize git: `git init && git add . && git commit -m "..."`
- [ ] Create GitHub repository
- [ ] Connect local to GitHub: `git remote add origin ...`
- [ ] Push to GitHub: `git push -u origin main`
- [ ] Create git tag: `git tag -a v1.0.0 -m "..."`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] Create GitHub Release from tag
- [ ] Add release description/notes
- [ ] Publish release
- [ ] Share the link!

### Links After Setup

- **Repository:** https://github.com/YOUR_USERNAME/plex-renamer
- **Releases:** https://github.com/YOUR_USERNAME/plex-renamer/releases
- **Raw File:** https://raw.githubusercontent.com/YOUR_USERNAME/plex-renamer/main/plex_renamer.py

---

## Need Help?

See detailed guides:
- [RELEASE.md](RELEASE.md) - Full release strategy docs
- [GitHub Docs](https://docs.github.com/repositories/releasing-projects-on-github) - Official GitHub help
- [Semantic Versioning](https://semver.org/) - How to version your project

---

## Timeline

- **Now:** Git repo + releases
- **Soon:** GitHub Actions for CI/CD
- **Later:** PyPI package for `pip install`
- **Future:** Standalone .exe builder

All documented for when you're ready!

---

**You're ready to share your project with the world! 🚀**

Next step: Run the git commands above to create your repository.
