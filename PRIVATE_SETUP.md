# Private Repository Setup

Complete local git repository setup for **Plex Renamer** - ready to go public when you're ready.

> **Status:** ✅ Local private repository
> **When to go public:** Whenever you want (update docs + push)
> **Effort to release:** ~30 minutes when ready

---

## What This Setup Does

✅ **Creates a local git repository**
- Tracks all your code changes
- Full version history
- Can push to GitHub Private whenever ready
- Zero public exposure until you decide

✅ **Keeps all documentation**
- Release guides ready to use
- Distribution recommendations prepared
- One-command deployment when ready

✅ **No external services needed**
- Works completely offline
- GitHub account not required yet
- Can add later with one command

---

## Step 1: Initialize Private Git Repository

Run these commands in PowerShell at `r:/media/tv`:

```powershell
# Navigate to project directory
cd r:/media/tv

# Initialize git repository
git init

# Configure git (one-time setup)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Verify configuration
git config --list
```

### Expected Output
```
user.name=Your Name
user.email=your.email@example.com
core.repositoryformatversion=0
core.filemode=false
core.bare=false
...
```

---

## Step 2: Create Initial Commit

```powershell
# Add all files to git
git add .

# View what will be committed
git status

# Create initial commit
git commit -m "Initial commit: Plex Renamer v1.0.0 - Complete feature set"

# View the commit
git log --oneline
```

### Expected Output
```
f3e2d1c (HEAD -> main) Initial commit: Plex Renamer v1.0.0 - Complete feature set
```

---

## Step 3: Set Up for Future Releases

### Option A: Keep Completely Local (No GitHub)

**Best for:** Personal/private use, company internal tool

```powershell
# You're done! Your git repo is ready.
# All commits are tracked locally.

# View all commits
git log --pretty=format:"%h %s"

# View differences
git diff HEAD~1

# Create backups
# (git is already your backup system)
```

### Option B: Push to GitHub as Private (Later)

When you're ready to go public or share with others:

```powershell
# 1. Create private GitHub repo at https://github.com/new
# 2. Copy the HTTPS URL from GitHub
# 3. Run these commands:

git remote add origin https://github.com/YOUR_USERNAME/plex-renamer.git
git branch -M main
git push -u origin main

# Now you have:
# - Local git history
# - Cloud backup on GitHub (private)
# - Ready to make public with one command
```

---

## 📁 Files Included & Ready

All files are prepared for when you're ready to release:

### **Core Application**
- ✅ `plex_renamer.py` - Production-ready code
- ✅ `run.bat`, `run.ps1` - Windows launchers
- ✅ `plex_renamer.sh` - Original bash version (kept for reference)

### **Documentation (Ready to Use)**
- ✅ `README.md` - User guide (ready to show)
- ✅ `QUICKSTART.md` - Quick start (ready to share)
- ✅ `FEATURES.md` - Feature comparison
- ✅ `DEVELOPMENT.md` - Dev/customization guide
- ✅ `INDEX.md` - Overview document

### **Release Documentation (For Later)**
- ✅ `DISTRIBUTION.md` - What method to use
- ✅ `RELEASE.md` - Full release instructions
- ✅ `GIT_SETUP.md` - GitHub setup guide

### **Configuration (Already Set Up)**
- ✅ `LICENSE` - MIT License
- ✅ `pyproject.toml` - Python package config
- ✅ `setup.py` - Setup script (for pip install)
- ✅ `MANIFEST.in` - Package manifest
- ✅ `.gitignore` - Git rules
- ✅ `CHANGELOG.md` - Version tracking
- ✅ `config.example.json` - Config template

**Everything is ready. Nothing is public yet.**

---

## 🔐 Privacy & Security

### What's Private
✅ **Your local git repo is completely private**
- Only on your computer
- Not accessible to anyone
- Full version control
- Zero online exposure

### When You're Ready to Go Public
- Decide on timing (v1.0, v1.5, v2.0, whenever)
- Update GitHub account info in docs
- Create GitHub repo (private or public)
- Push one command
- Create release when ready

### No Rush
- Keep it private as long as you want
- When ready: ~30 minutes to go public
- All docs already prepared
- Can be private → public → paid → whatever

---

## 📊 Git Workflow (Local Only)

### Making Changes

```powershell
# Make changes to plex_renamer.py

# Check what changed
git status

# View the changes
git diff

# Stage changes
git add plex_renamer.py

# Commit with message
git commit -m "fix: Improve fuzzy matching algorithm"

# View history
git log --oneline
```

### Version Tracking

```powershell
# Create a development version tag (won't be released)
git tag v1.0.0-dev "Development version"

# Create a release tag (when ready to share)
git tag -a v1.0.0 -m "Release version 1.0.0"

# View all tags
git tag -l
```

### Branching (for experimentation)

```powershell
# Create feature branch
git branch feature/new-feature
git checkout feature/new-feature
# ... make changes ...
git commit -m "feature: Add new feature"

# Switch back to main
git checkout main

# Merge when ready
git merge feature/new-feature

# Delete branch
git branch -d feature/new-feature
```

---

## 📋 When You're Ready to Go Public

### Checklist for Release Day

- [ ] Review final code and documentation
- [ ] Create GitHub account (if needed)
- [ ] Create private GitHub repo
- [ ] Update DISTRIBUTION.md with your GitHub username
- [ ] Push to GitHub: `git push -u origin main`
- [ ] Create GitHub release from v1.0.0 tag
- [ ] Share the link!

### Single Command When Ready

```powershell
# After creating GitHub repo, one command to push:
git push -u origin main

# Then on GitHub: Click "Release" and follow the template
```

---

## 🔄 Keeping Code Safe

### Backup Strategy

**Git is your backup:**
```powershell
# All commits are stored locally
git reflog                        # View all changes

# If you mess up, restore
git reset --hard HEAD~1          # Undo last commit
git revert HEAD                  # Undo with new commit
```

### Additional Backups

```powershell
# Copy entire folder as backup
Copy-Item -Path r:/media/tv -Destination r:/media/tv.backup -Recurse

# Or use Windows Backup
# Or use cloud sync (OneDrive, Google Drive, etc.)
```

---

## 📖 Documentation Status

### Ready to Use Now (Share Anytime)
- README.md ✅
- QUICKSTART.md ✅
- FEATURES.md ✅
- DEVELOPMENT.md ✅

### Ready to Use When Going Public
- DISTRIBUTION.md ✅ (update username)
- RELEASE.md ✅ (already complete)
- GIT_SETUP.md ✅ (already complete)

### Configuration Ready
- LICENSE ✅
- pyproject.toml ✅
- setup.py ✅
- CHANGELOG.md ✅

**Nothing needs updating - everything is ready to go.**

---

## 🎯 Timeline Options

### Option 1: Keep Private Indefinitely
```
Now → Private git repo
  ↓
Use locally
  ↓
Never release
  ↓
Personal tool forever
```

### Option 2: Release Soon (Next Month)
```
Now → Private git repo
  ↓
April → Add features, fix bugs
  ↓
May → Go public with v1.0 (GitHub Releases)
  ↓
Community users
```

### Option 3: Release Eventually (Six Months)
```
Now → Private git repo
  ↓
Months → Develop, test, polish
  ↓
Later → Release as v1.0 (GitHub Releases)
  ↓
Large audience
```

**No pressure. No timeline. Release whenever you want.**

---

## 🔧 Useful Git Commands (Local Only)

```powershell
# View history
git log --oneline -10              # Last 10 commits
git log --graph --all --oneline    # Visual history

# Check status
git status                         # What changed?
git diff                          # What are the changes?

# Undo things
git restore plex_renamer.py        # Undo file changes
git reset --soft HEAD~1            # Undo commit, keep changes
git reset --hard HEAD~1            # Undo everything

# Branches
git branch                         # List branches
git branch my-feature              # Create branch
git checkout my-feature            # Switch branch
git merge my-feature               # Merge back

# Tags
git tag v1.0.0                     # Create tag
git tag -l                         # List all tags
git show v1.0.0                    # Show tag info
```

---

## 💡 Tips for Private Development

### Clean Commit Messages
Good:
```
feat: Add fuzzy show matching
fix: Handle multi-episode files correctly
docs: Update README with examples
chore: Update dependencies
```

Bad:
```
stuff
fix
update
asdf
```

### Commit Frequently
- Small commits = easier to review/revert
- Good for tracking changes
- Makes history clearer

### Use Branches for Big Changes
- Main branch = stable
- Feature branches = experimental
- Easy to abandon or merge later

---

## 🚦 When Someone Asks to Use It

### Option A: Share Source Code Directly
```powershell
# Copy entire folder
Copy-Item -Path r:/media/tv -Destination r:/person/tv -Recurse

# They can run:
python plex_renamer.py
```

### Option B: Create a ZIP for Sharing
```powershell
# Create ZIP archive
Compress-Archive -Path r:/media/tv -DestinationPath plex-renamer-v1.0.zip

# Share the ZIP file
# They extract and run
```

### Option C: Push to Private GitHub (Later)
```powershell
# When ready to share with specific people:
git push -u origin main
# Share GitHub link as private repo
```

### Option D: Eventually Make Public
```powershell
# Change GitHub repo from private → public
# Create release
# Share with world
```

---

## ✅ Current Status

| Item | Status | When Needed |
|------|--------|-------------|
| Code | ✅ Production Ready | Now |
| Documentation | ✅ Complete | When releasing |
| Git Setup | ⚙️ Run commands below | Now |
| GitHub | Not started | When going public |
| Release | Not started | When going public |

---

## 🎯 What to Do Now

### Immediate (Takes 5 minutes)

```powershell
# 1. Open PowerShell
# 2. Navigate to project
cd r:/media/tv

# 3. Initialize git
git init
git config user.name "Your Name"
git config user.email "your@email.com"
git add .
git commit -m "Initial commit: Plex Renamer v1.0.0"

# Done! Your private repo exists.
```

### Then (Optional)

```powershell
# View your commits
git log --oneline

# Make changes, create branches, experiment
# Everything is tracked locally
```

### Later (When Going Public)

- Run: `git push -u origin <github-url>`
- Create release on GitHub
- Share link

---

## 📞 What's Ready for Release

When you decide to go public, you already have:

✅ **Application**
- Production-quality code
- Windows launchers
- Complete feature set

✅ **Documentation**
- User guides (README, QUICKSTART)
- Developer guides (DEVELOPMENT)
- Feature documentation (FEATURES)

✅ **Release Infrastructure**
- MIT License
- Proper Python packaging
- Git configuration
- Release guides

✅ **All You Need to Do**
1. Create GitHub account (if needed)
2. Create GitHub repo
3. Run: `git push -u origin main`
4. Create release from tag
5. Share link

**That's it. Everything else is done.**

---

## 🎁 Bottom Line

You now have:

1. **Complete private git repository**
   - All code tracked locally
   - Full version history
   - Zero public exposure
   - Completely yours

2. **Ready-to-go release documentation**
   - All guides prepared
   - No guesswork needed
   - One-command deployment

3. **Professional-quality application**
   - Production code
   - Complete documentation
   - Clean structure

4. **Flexibility**
   - Release now: 30 minutes
   - Release later: Still 30 minutes
   - Never release: Still works great locally

**Take your time. When you're ready, you're ready.**

---

## 🏁 Next Step

```powershell
# Copy these 4 commands:
git init
git config user.name "Your Name"
git config user.email "your@email.com"
git add .
git commit -m "Initial commit: Plex Renamer v1.0.0"

# Paste into PowerShell at r:/media/tv
# You're done!
```

**Your private repository is ready.** 🔐

