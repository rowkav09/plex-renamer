# ⚡ Quick Private Setup (5 Minutes)

Complete your private git repository setup in under 5 minutes.

---

## Copy & Paste These Commands

Open **PowerShell** and paste these commands one by one:

```powershell
cd r:/media/tv
```

```powershell
git init
```

```powershell
git config user.name "Your Name"
```

```powershell
git config user.email "your@email.com"
```

```powershell
git add .
```

```powershell
git commit -m "Initial commit: Plex Renamer v1.0.0"
```

```powershell
git log --oneline
```

---

## Done!

You now have a complete private git repository with version history.

**That's it. You're done setting up.**

---

## Next Steps (Whenever You Want)

### Option A: Keep it Private (Forever)
- Your code is safe
- Full version control
- No public exposure
- Runs locally

### Option B: Make it Public (30 minutes)
- Follow [GO_PUBLIC.md](GO_PUBLIC.md)
- Create GitHub account
- Push to GitHub
- Create release
- Share with world

### Option C: Share with Someone Now
```powershell
# Copy entire folder
Copy-Item -Path r:/media/tv -Destination C:/destination -Recurse

# Or create ZIP
Compress-Archive -Path r:/media/tv -DestinationPath r:/plex-renamer-v1.0.zip
```

---

## 📚 Documentation Guide

| File | For | When |
|------|-----|------|
| [PRIVATE_SETUP.md](PRIVATE_SETUP.md) | Detailed private setup | If those 6 commands don't work |
| [GO_PUBLIC.md](GO_PUBLIC.md) | Making it public later | When you decide to release |
| [README.md](README.md) | Using the tool | Now or anytime |
| [QUICKSTART.md](QUICKSTART.md) | Quick usage | Now or anytime |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Customizing the tool | If you want to change things |

---

## ✅ Your Repository is Now Private & Safe

```
r:/media/tv/
├── .git/                    (Your version history)
├── plex_renamer.py         (Production code)
├── README.md               (Documentation)
├── LICENSE                 (License)
└── ... (all other files)
```

**Everything is tracked. Nothing is public.**

---

## Commands You'll Use

```powershell
# See what changed
git status

# See the changes
git diff

# Make a new commit
git add .
git commit -m "Your message here"

# See your history
git log --oneline

# When ready to go public
git push -u origin main
```

---

## That's All You Need

**Right now:** Those 6 copy-paste commands ✅

**Later:** [GO_PUBLIC.md](GO_PUBLIC.md) when you're ready

**Never:** If you decide to keep it private forever

---

## 🚀 You're Ready

Go run those 6 commands. You're done with setup!

**Then read whichever guide applies:**
- Private forever → You're already done
- Go public later → Read [GO_PUBLIC.md](GO_PUBLIC.md) when ready
- Use the tool now → Read [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md)

