# DataPolish - Quick Start Guide

## ⚡ 5-Minute Quick Start

### 1. Install

```bash
pip install -e .
```

### 2. Basic Usage

```python
from datapolish import DataCleaner

# Load data
cleaner = DataCleaner("medical_patient_data.csv")

# Get AI description
print(cleaner.describe_data(0))

# Clean
config = {
    'missing': {'strategy': 'median'},
    'outliers': {'method': 'iqr', 'action': 'cap'},
    'duplicates': {'drop': True}
}
cleaner.clean(config)

# Save
cleaner.save()
```

### 3. Run Demo

```bash
python demo.py
```

---

## 🎯 New Features

### Drop Columns
```python
cleaner.drop_columns('ID', 'Email', 0)  # By name or index
```

### Correlation Analysis
```python
result = cleaner.analyze_correlation('X', 'Y')
print(result['interpretation'])
```

### View as Image
```python
cleaner.view_as_image(rows=10, save_path='preview.png')
cleaner.view_as_image(rows=-10, save_path='tail.png')  # Last 10!
```

---

## 📦 Upload to PyPI

```bash
# Clean
rm -rf dist/ build/ *.egg-info

# Build
python -m build

# Upload
twine upload dist/*
```

---

## ✅ Complete Workflow

```python
from datapolish import DataCleaner

# 1. Load
cleaner = DataCleaner("data.csv")

# 2. Explore
print(cleaner.describe_data(0))
profile = cleaner.profile()

# 3. Drop columns
cleaner.drop_columns('ID', 0)

# 4. Analyze
result = cleaner.analyze_correlation(threshold=0.5)

# 5. Visualize
cleaner.view_as_image(rows=10, save_path='preview.png')
cleaner.visualize('overview', save_path='dashboard.png')

# 6. Clean
config = {
    'missing': {'strategy': 'median'},
    'outliers': {'method': 'iqr', 'action': 'cap'},
    'duplicates': {'drop': True}
}
cleaner.clean(config)

# 7. Save
cleaner.save()
```

---

**That's it!** You're ready to use DataPolish! 🎉
