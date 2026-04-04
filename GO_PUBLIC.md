# From Private to Public - Release When Ready

One-command guide to go public whenever you decide.

> **Current Status:** Private local git repository
> **When Ready:** Follow this simple 3-step process
> **Time Required:** ~30 minutes
> **Effort Level:** Very Easy

---

## 🎯 Transition Checklist

When you're ready to release, go through this quick list:

### Before Creating Public Release

- [ ] Code is tested and stable
- [ ] Documentation is reviewed
- [ ] You want this public (no backing out!)
- [ ] 30 minutes available

### Then Execute

- [ ] Create GitHub account (skip if you have one)
- [ ] Create GitHub repository
- [ ] Update config with your username
- [ ] Run git push command
- [ ] Create release on GitHub
- [ ] Share the link!

---

## 📋 Step-by-Step: Making It Public

### Step 1: Create GitHub Account (5 minutes)

Go to https://github.com/signup and create an account.

> Already have GitHub? Skip to Step 2

---

### Step 2: Create GitHub Repository (5 minutes)

1. **Go to:** https://github.com/new
2. **Repository name:** `plex-renamer`
3. **Description:** `Professional tool for organizing TV shows in Plex-perfect format`
4. **Public:** Select this (now's when you go public!)
5. **License:** Select "MIT License"
6. **Click:** Create repository

GitHub gives you a URL. Copy it (you'll need it in next step).

Example: `https://github.com/YOUR_USERNAME/plex-renamer.git`

---

### Step 3: Push Your Code (5 minutes)

In PowerShell at `r:/media/tv`:

```powershell
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/plex-renamer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Done! Your code is now on GitHub!**

---

### Step 4: Create Your First Release (10 minutes)

In PowerShell at `r:/media/tv`:

```powershell
# Create a release tag
git tag -a v1.0.0 -m "Release version 1.0.0 - Initial stable release"

# Push the tag to GitHub
git push origin v1.0.0
```

---

### Step 5: Publish Release on GitHub (10 minutes)

1. **Go to:** `https://github.com/YOUR_USERNAME/plex-renamer`
2. **Click:** Releases tab (right side)
3. **Click:** "Create a release" or "Draft a new release"
4. **Select tag:** v1.0.0
5. **Title:** `Plex Renamer v1.0.0 - Initial Release`
6. **Description:** Copy from below ↓

```markdown
## 🎉 Initial Stable Release

Professional tool for organizing TV shows in Plex-perfect format!

## ✨ Features

- **Progress Bars & Rich UI** - Beautiful real-time feedback
- **Undo System** - Complete rename history with restore
- **Auto-Detect Shows** - Fuzzy matching for messy folders
- **Multi-Episode Support** - S01E01-E03 format
- **Plex-Perfect Structure** - Show/Season XX/Episode.mkv

## 🚀 Quick Start

### Windows
```cmd
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
- [FEATURES.md](FEATURES.md) - Feature details

---

**Ready to use! Download the ZIP or clone the repo.**
```

7. **Publish release** button
8. **Done!**

---

## ✅ You're Now Public!

Your project is now live at:
- **Repository:** `https://github.com/YOUR_USERNAME/plex-renamer`
- **Releases:** `https://github.com/YOUR_USERNAME/plex-renamer/releases`
- **Latest Release:** `https://github.com/YOUR_USERNAME/plex-renamer/releases/tag/v1.0.0`

---

## 📊 What Users See

### On GitHub

1. **Repository page** shows:
   - Your README.md
   - Code files
   - Folder structure
   - Clone/download buttons

2. **Releases tab** shows:
   - v1.0.0 with your description
   - Source code (ZIP, TAR)
   - Download button
   - Release notes

### How They Get It

**Option 1: Download ZIP**
- Go to Releases tab
- Click "Source code (zip)"
- Extract and run

**Option 2: Clone**
```bash
git clone https://github.com/username/plex-renamer.git
cd plex-renamer
python plex_renamer.py
```

**Option 3: Download Raw File**
```bash
curl -O https://raw.githubusercontent.com/username/plex-renamer/main/plex_renamer.py
python plex_renamer.py
```

---

## 🎁 Optional: Advanced Releases

### Add Windows Executable (Optional)

After going public, you can add a `.exe` file for Windows users:

```powershell
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile plex_renamer.py

# Creates: dist/plex-renamer.exe
# Upload to GitHub Release as "asset"
```

Then users can:
```
Download plex-renamer-v1.0.0.exe
Double-click to run (no Python needed!)
```

---

### Add to PyPI (Optional)

Later, enable: `pip install plex-renamer`

```powershell
# When ready (v1.1.0+)
pip install build twine
python -m build
twine upload dist/*
```

See [RELEASE.md](RELEASE.md) for full details.

---

## 📈 After Going Public

### Immediate (Day 1-3)
- ✅ Share link on social media
- ✅ Post on r/python, r/homelab
- ✅ Share with friends/colleagues

### Short-term (Week 1-2)
- ✅ Respond to any issues
- ✅ Fix bugs reported
- ✅ Answer questions

### Medium-term (Month 1-3)
- ✅ Consider feature requests
- ✅ Plan v1.1.0
- ✅ Build documentation

### Long-term (Month 3+)
- ✅ Regular updates
- ✅ Community management
- ✅ New features/improvements

---

## 🔄 Making Updates After Release

### Releasing v1.1.0

```powershell
# Make your changes
# Edit plex_renamer.py, etc.

# Update versions:
# - pyproject.toml
# - setup.py
# - CHANGELOG.md

# Commit changes
git add .
git commit -m "feat: Add new features for v1.1.0"

# Create new tag
git tag -a v1.1.0 -m "Release v1.1.0 - New features"

# Push to GitHub
git push origin main v1.1.0

# On GitHub: Create new release from v1.1.0 tag
```

---

## 💡 Tips for Going Public

### Before You Release
- ✅ Test the code works
- ✅ Review README one more time
- ✅ Check LICENSE is correct
- ✅ Verify QUICKSTART.md is clear

### For Release Notes
- ✅ Be clear about features
- ✅ Include requirements
- ✅ Provide quick-start command
- ✅ Link to full documentation

### For Community
- ✅ Respond to issues quickly
- ✅ Be welcoming to contributors
- ✅ Fix reported bugs
- ✅ Consider feature requests

### For Maintenance
- ✅ Keep dependencies updated
- ✅ Update documentation
- ✅ Plan next version
- ✅ Engage with users

---

## 🎯 Alternative: Stay Private

If you change your mind, you can always keep it private:

```powershell
# Create GitHub repo as PRIVATE instead of PUBLIC
# Code is safe in cloud backup
# Only you can access it
# Can make public anytime
```

Or keep it local only:

```powershell
# Don't push to GitHub at all
# Your private git repo on your computer
# Can push anytime in the future
```

**No commitment needed. You control the timeline.**

---

## 📞 Support Resources

When you have questions:

| Question | Answer Location |
|----------|-----------------|
| How do I set up git? | [PRIVATE_SETUP.md](PRIVATE_SETUP.md) |
| How do I release? | [RELEASE.md](RELEASE.md) |
| Which method should I use? | [DISTRIBUTION.md](DISTRIBUTION.md) |
| How do I customize? | [DEVELOPMENT.md](DEVELOPMENT.md) |
| How do I use it? | [QUICKSTART.md](QUICKSTART.md) |

---

## ⏱️ Quick Timeline

```
Now:        Private git repo (local only)
            ↓
Week 3-4:   Decide to release
            ↓
Day 1:      Create GitHub account
            ↓
Day 2:      Create repo, push code
            ↓
Day 3:      Create v1.0.0 release
            ↓
Day 4+:     Share with world!
```

**Total cost: 30 minutes of your time**

---

## 🏁 When You're Ready

You have everything you need. Just:

1. ✅ Open PowerShell at `r:/media/tv`
2. ✅ Follow the 5 steps above
3. ✅ Share the link
4. ✅ Done!

**No guesswork. Everything is documented. You've got this! 🚀**

---

## Ready to Take the Leap?

**When You Decide:** Just open this file, follow the 5 steps, and you're public.

**No Step 6.** That's it. You're done.

**Your private work becomes public work.**

**Your private tool becomes a community tool.**

**And it all starts with one decision: "Today's the day."**

---

**Until then: Enjoy your private repository. Take your time. When you're ready... this guide will be waiting.** 🔐

