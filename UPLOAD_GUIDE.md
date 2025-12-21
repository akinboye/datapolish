# DataPolish - Complete Upload Guide

## 🎯 Package Information

**Package Name:** `datapolish`  
**Version:** 1.0.0  
**Import Name:** `datapolish`  
**Install Command:** `pip install datapolish`

---

## 🚀 Quick Upload Process

### Step 1: Verify Configuration

Both `setup.py` and `pyproject.toml` have:
- ✅ `name = "datapolish"`
- ✅ `version = "1.0.0"`

**Update Your Information:**

1. Open `setup.py` in editor
2. Change line 8: `author="Your Name"` → Your actual name
3. Change line 9: `author_email="your.email@example.com"` → Your email

4. Open `pyproject.toml` in editor  
5. Change line 12: Same updates

---

### Step 2: Clean Previous Builds

```bash
# macOS/Linux
rm -rf dist/ build/ *.egg-info

# Windows (PowerShell)
Remove-Item -Recurse -Force dist, build, *.egg-info
```

---

### Step 3: Build Package

```bash
python -m build
```

**Expected Output:**
```
Successfully built datapolish-1.0.0.tar.gz and datapolish-1.0.0-py3-none-any.whl
```

**Verify:**
```bash
ls dist/
```

Should show:
```
datapolish-1.0.0.tar.gz
datapolish-1.0.0-py3-none-any.whl
```

---

### Step 4: Check Package Quality

```bash
twine check dist/*
```

**Expected Output:**
```
Checking dist/datapolish-1.0.0.tar.gz: PASSED
Checking dist/datapolish-1.0.0-py3-none-any.whl: PASSED
```

---

### Step 5: Get PyPI API Token

1. Go to: https://pypi.org/manage/account/
2. Scroll to "API tokens"
3. Click "Add API token"
4. Name: `datapolish-upload`
5. Scope: **"Entire account"**
6. Click "Add token"
7. **COPY THE TOKEN!** (starts with `pypi-`)

---

### Step 6: Upload to PyPI

```bash
twine upload dist/*
```

**When prompted:**
```
Enter your username: __token__
Enter your password: [paste your PyPI token]
```

**Expected Output:**
```
Uploading datapolish-1.0.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploading datapolish-1.0.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View at:
https://pypi.org/project/datapolish/1.0.0/
```

---

### Step 7: Verify Installation

```bash
pip install datapolish

python -c "from datapolish import DataCleaner; print('✓ DataPolish installed successfully!')"
```

---

## 🎉 Success!

Your package is now live on PyPI!

Anyone can install it:
```bash
pip install datapolish
```

And use it:
```python
from datapolish import DataCleaner

cleaner = DataCleaner("data.csv")
cleaner.clean({'missing': {'strategy': 'median'}})
cleaner.save()
```

---

## 📋 Complete Commands (Copy & Paste)

```bash
# 1. Clean
rm -rf dist/ build/ *.egg-info

# 2. Build
python -m build

# 3. Check
twine check dist/*

# 4. Upload
twine upload dist/*
```

---

## ✅ Pre-Upload Checklist

- [ ] Updated `author` in setup.py
- [ ] Updated `author_email` in setup.py
- [ ] Updated same in pyproject.toml
- [ ] Both files have `name = "datapolish"`
- [ ] Both files have `version = "1.0.0"`
- [ ] Cleaned old builds
- [ ] Built package successfully
- [ ] `twine check` shows PASSED
- [ ] Have PyPI API token
- [ ] Ready to upload!

---

## 🔧 Troubleshooting

### "Package name already exists"
- Check: https://pypi.org/project/datapolish/
- If taken, choose different name in setup.py and pyproject.toml

### "Invalid authentication"
- Username must be: `__token__`
- Password is your full token (starts with `pypi-`)

### "File already exists"
- Can't upload same version twice
- Increment version to 1.0.1

---

## 📖 After Upload

1. Check package page: https://pypi.org/project/datapolish/
2. Test installation: `pip install datapolish`
3. Share with others!

---

**Package Name:** datapolish  
**Ready to Upload!** 🚀
