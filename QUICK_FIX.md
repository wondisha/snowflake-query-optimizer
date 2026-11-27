# QUICK FIX: Windows AppStore Python Issue

## The Problem
You're using Windows AppStore Python 3.13, which blocks native DLL loading.
Snowflake connector needs native C++ support → Doesn't work with AppStore Python.

## The Solution (3 Steps - 10 minutes)

### Step 1: Install Official Python 3.11
**Option A: Automated (Recommended)**
```powershell
# Run as Administrator
iwr https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe -OutFile python-installer.exe
.\python-installer.exe
```

**Option B: Manual**
1. Visit https://www.python.org/downloads/
2. Download Python 3.11.9 (Windows 64-bit Installer)
3. Run the installer
4. **CRITICAL:** Check "Add Python to PATH"
5. Click "Install Now"
6. Finish and close

### Step 2: Restart PowerShell
Close PowerShell completely, then reopen

### Step 3: Verify & Recreate Environment
```powershell
# Verify new Python installed
python --version
# Should show: Python 3.11.9 (NOT 3.13)

# Go to project directory
cd D:\agent\snowflake_query_optimizer

# Remove old venv
rmdir /s venv

# Create new venv with official Python
python -m venv venv

# Activate it
venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Test
python main.py health-check
```

**Expected output:**
```
[OK] Snowflake connection healthy!
```

## Verification Checklist

- [ ] Python 3.11.9 installed (not AppStore version)
- [ ] "Add Python to PATH" was checked during install
- [ ] PowerShell restarted after install
- [ ] Old venv removed (`rmdir /s venv`)
- [ ] New venv created (`python -m venv venv`)
- [ ] Requirements installed (`pip install -r requirements.txt`)
- [ ] `python --version` shows 3.11.9

## Commands to Run (Copy-Paste)

```powershell
# 1. Download & install official Python
iwr https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe -OutFile python-installer.exe
.\python-installer.exe
# Then restart PowerShell after installer finishes

# 2. After restart, verify
python --version

# 3. Recreate environment
cd D:\agent\snowflake_query_optimizer
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt --upgrade

# 4. Test
python main.py health-check

# 5. Try the application
python main.py analyze
python main.py chat
```

## Still Not Working?

### Issue: "Python still showing 3.13"
**Solution:**
```powershell
# Check which Python is being used
where python
# Should NOT contain "WindowsApps"

# If it does, uninstall AppStore Python:
# Settings > Apps > Installed apps > Python 3.13 > Uninstall
# Then restart PowerShell
```

### Issue: "pip not found"
**Solution:**
```powershell
# Use python -m pip instead
python -m pip install -r requirements.txt
```

### Issue: "Permission denied when installing"
**Solution:**
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell > Run as Administrator
```

### Issue: "Still getting DLL error"
**Solution:**
1. Confirm: `where python` - should NOT show "WindowsApps"
2. Completely uninstall AppStore Python from Settings
3. Restart computer
4. Reinstall official Python
5. Create fresh venv

## Why This Happens

| Python Source | Restriction | Works |
|---|---|---|
| Windows AppStore | Blocks native DLLs | ❌ |
| python.org | None | ✅ |
| Anaconda | None | ✅ |
| WSL | None | ✅ |
| Docker | None | ✅ |

Snowflake connector includes native C++ code that needs unrestricted DLL access.

## Success Indicators

After fixing, you should see:
```
# Health check
$ python main.py health-check
[OK] Snowflake connection healthy!

# Analysis runs
$ python main.py analyze
[ANALYZE] Analyzing your Snowflake database...

# Chat works
$ python main.py chat
[BOT] Running initial database analysis for context...
```

## Need Help?

1. Check INSTALL_PYTHON.md for detailed instructions
2. Verify Python version: `python --version`
3. Verify PATH: `where python`
4. Check installation: `python -c "import snowflake.connector; print('OK')"`

---

**Key Point:** The code is correct. The issue is the Python environment. Official Python = everything works! ✓
