# Fix: Windows AppStore Python DLL Error

## Problem
```
ImportError: DLL load failed while importing sf_core_python: 
An Application Control policy has blocked this file.
```

**Cause:** Windows AppStore Python restricts native DLL loading (sandboxing). The Snowflake connector needs native C++ extensions that AppStore Python blocks.

## Solution 1: Use Python from python.org (Recommended)

### Step 1: Uninstall AppStore Python
```powershell
# Open Windows Settings
# Go to: Settings > Apps > Installed apps
# Search for "Python"
# Remove any "Python 3.13" from Microsoft Store
```

### Step 2: Install Official Python
1. Go to https://www.python.org/downloads/
2. Download "Python 3.11" or "3.12" (Windows Installer)
3. Run the installer
4. **IMPORTANT:** Check "Add Python to PATH"
5. Click "Install Now"

### Step 3: Verify Installation
```powershell
python --version
# Should show: Python 3.11.x or 3.12.x
# NOT: 3.13 (which may still be AppStore version)
```

### Step 4: Recreate Virtual Environment
```bash
cd d:\agent\snowflake_query_optimizer

# Remove old venv
rmdir /s venv

# Create new venv with official Python
python -m venv venv

# Activate venv
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 5: Run Commands
```bash
python main.py health-check
python main.py analyze
python main.py chat
```

---

## Solution 2: Use Windows Terminal with Regular Python

If you have Python installed via other means (Windows Store but not Python app, or Anaconda):

```powershell
# Check if you have other Python installations
where python
# Try python3
python3 --version

# Use it directly
python3 main.py health-check
```

---

## Solution 3: Use Docker (If Available)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "main.py", "analyze"]
```

Build and run:
```bash
docker build -t snowflake-optimizer .
docker run -e SNOWFLAKE_ACCOUNT=your_account snowflake-optimizer
```

---

## Solution 4: Use WSL (Windows Subsystem for Linux)

If you have WSL2 installed:

```bash
# In WSL terminal
cd /mnt/d/agent/snowflake_query_optimizer
python3 main.py health-check
```

---

## Quick Fix Checklist

- [ ] Uninstall AppStore Python
- [ ] Install Python from python.org  
- [ ] Verify: `python --version` shows non-AppStore version
- [ ] Delete old venv: `rmdir /s venv`
- [ ] Create new venv: `python -m venv venv`
- [ ] Activate: `venv\Scripts\activate`
- [ ] Install: `pip install -r requirements.txt`
- [ ] Test: `python main.py health-check`

---

## Why This Happens

| Python Version | Sandbox | DLL Support | Works |
|---|---|---|---|
| AppStore Python | Yes (restricted) | Blocked | ❌ |
| python.org | No | Full | ✅ |
| Anaconda | No | Full | ✅ |
| WSL Python | No | Full | ✅ |
| Docker | No | Full | ✅ |

---

## Verification

After reinstalling Python, verify Snowflake connector works:

```python
# test_import.py
import snowflake.connector
print("SUCCESS: Snowflake connector loaded!")
```

Run it:
```bash
python test_import.py
# Should print: SUCCESS: Snowflake connector loaded!
```

---

## Still Having Issues?

1. **Check Python path:**
   ```bash
   where python
   # Should NOT show: ...WindowsApps...
   ```

2. **Completely remove AppStore Python:**
   - Settings > Apps > Installed apps
   - Search "Python"
   - Uninstall all Python apps from Microsoft Store

3. **Clear pip cache:**
   ```bash
   pip cache purge
   pip install -r requirements.txt --force-reinstall
   ```

4. **Use Python 3.11 instead of 3.13:**
   - Download Python 3.11 from python.org
   - Older versions have more stable support

---

**After fixing this, run:** `python main.py health-check`

You should see: `[OK] Snowflake connection healthy!`
