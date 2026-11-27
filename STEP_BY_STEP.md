# STEP-BY-STEP FIX (Just Follow These Steps)

## Step 1: Uninstall AppStore Python
Right now, you have broken Python. We need to remove it first.

### Method 1: Automatic (Easiest)
1. Right-click `fix_python_auto.bat` in this folder
2. Select "Run as Administrator"
3. Follow the prompts
4. **Close and restart Command Prompt when done**
5. Skip to Step 3

### Method 2: Manual
1. Open **Settings**
2. Go to **Apps** > **Installed apps**
3. Search for **"Python"**
4. Click on **"Python 3.13"** from Microsoft Store
5. Click **Uninstall**
6. Click **Uninstall** again to confirm
7. Wait for it to finish
8. Continue to Step 2

---

## Step 2: Install Official Python
1. Go to https://www.python.org/downloads/
2. Click the big blue button: **"Download Python 3.11.9"**
3. Wait for download to complete
4. **Run the installer** (python-3.11.9-amd64.exe)
5. **IMPORTANT:** Check the box "Add Python to PATH" ✓
6. Click "Install Now"
7. Wait for installation to complete
8. Click "Close"
9. **Close Command Prompt completely**
10. **Open NEW Command Prompt**

---

## Step 3: Verify Installation
Open a **new Command Prompt** and type:
```
python --version
```

**You should see:** `Python 3.11.9`

If you still see 3.13, restart your computer and try again.

---

## Step 4: Fix the Project
In Command Prompt, run these commands one by one:

```cmd
cd D:\agent\snowflake_query_optimizer

rmdir /s /q venv

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt --upgrade
```

Wait for all packages to install (might take 2-3 minutes).

---

## Step 5: Test It Works
```cmd
python main.py health-check
```

**You should see:** `[OK] Snowflake connection healthy!`

If you see that, you're done! ✓

---

## Step 6: Try the Application
Now you can run:
```cmd
python main.py analyze
python main.py chat
python main.py cost-report
```

---

## Troubleshooting

### "Still showing Python 3.13"
- Did you restart Command Prompt? (Close completely, open new one)
- Did you check "Add Python to PATH" during install?
- Try restarting your computer

### "Python not found"
- Make sure installer finished
- Make sure you opened a NEW Command Prompt after installing

### "pip: command not found"
- Try: `python -m pip install -r requirements.txt`

### "venv: command not found"
- Python 3.11 not installed correctly
- Reinstall from https://www.python.org/downloads/

---

## Still Stuck?

Check which Python you have:
```cmd
where python
```

Should show: `C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python311\...`

Should NOT show: `...WindowsApps...`

If it shows WindowsApps path, AppStore Python is still there - uninstall it completely.

---

## Summary
1. ❌ Delete: AppStore Python 3.13
2. ✅ Install: Official Python 3.11 from python.org
3. ✅ Check: "Add Python to PATH"
4. ✅ Recreate: Virtual environment
5. ✅ Done!
