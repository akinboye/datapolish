# DataPolish 🧹✨

**AI-Powered Data Cleaning Library for Python**

DataPolish is a comprehensive data cleaning and preprocessing library that combines powerful automation with AI-driven insights to help you prepare your data for analysis and machine learning.

[![PyPI version](https://badge.fury.io/py/datapolish.svg)](https://badge.fury.io/py/datapolish)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

### 🤖 AI-Powered Intelligence
- **Smart Data Descriptions** - Get instant rule-based insights about your dataset
- **Intelligent Recommendations** - Receive personalized cleaning suggestions
- **Automated Explanations** - Understand what cleaning operations did to your data

### 🧹 Comprehensive Cleaning
- **Missing Values** - 5 strategies (drop, mean, median, mode, forward fill)
- **Outlier Detection** - IQR and Z-score methods with flexible actions
- **Duplicate Removal** - Smart duplicate detection and removal
- **Column Management** - Drop columns by name or index

### 📊 Advanced Analysis
- **Correlation Analysis** - Detailed correlation reports with interpretations
- **Data Profiling** - Comprehensive quality scoring and statistics
- **Quality Metrics** - Automated data quality assessment

### 📈 Professional Visualizations
- Overview dashboards
- Missing value heatmaps
- Distribution plots
- Correlation matrices
- Outlier visualizations
- Categorical analysis
- **Export DataFrame as images** - Perfect for reports and presentations

### 💾 Flexible I/O
- Support for CSV, Excel, JSON formats
- Smart auto-save functionality
- Multiple export options
- Preserves original data

---

## 🚀 Quick Start

### Installation

```bash
pip install datapolish
```

### Basic Usage

```python
from datapolish import DataCleaner

# Load your data
cleaner = DataCleaner("your_data.csv")

# Get AI-powered description
print(cleaner.describe_data(detail_level=0))

# Get intelligent recommendations
print(cleaner.get_recommendations())

# Clean your data
config = {
    'missing': {'strategy': 'median'},
    'outliers': {'method': 'iqr', 'action': 'cap'},
    'duplicates': {'drop': True}
}
cleaner.clean(config)

# Get explanation of what was done
print(cleaner.explain_cleaning('detailed'))

# Save cleaned data
cleaner.save()  # Auto-saves to ./datapolish_output/
```

---

## 📚 Comprehensive Example

```python
from datapolish import DataCleaner

# Initialize
cleaner = DataCleaner("sales_data.csv")

# 1. Drop unnecessary columns
cleaner.drop_columns('ID', 'Internal_Code', 0)  # By name or index

# 2. Analyze correlations
result = cleaner.analyze_correlation('Price', 'Sales')
print(result['interpretation'])

# 3. View data as professional image
cleaner.view_as_image(rows=10, save_path='preview.png')
cleaner.view_as_image(rows=-10, save_path='tail.png')  # Last 10 rows

# 4. Profile your data
profile = cleaner.profile()
print(f"Quality Score: {profile['quality_score']}/100")

# 5. Visualize data quality
cleaner.visualize('overview', save_path='dashboard.png')
cleaner.visualize('missing', save_path='missing_values.png')

# 6. Clean with smart configuration
config = {
    'missing': {'strategy': 'median'},
    'outliers': {'method': 'iqr', 'action': 'cap', 'threshold': 1.5},
    'duplicates': {'drop': True, 'keep': 'first'}
}
cleaner.clean(config)

# 7. Verify results
cleaner.view_as_image(rows=10, save_path='cleaned_preview.png')

# 8. Save cleaned data
cleaner.save("cleaned_sales_data.csv")
```

---

## 🎯 Key Features in Detail

### 1. Drop Columns (New!)

Drop columns by name, index, or both:

```python
# By name
cleaner.drop_columns('Age', 'Gender')

# By index (0-based)
cleaner.drop_columns(0, 2, 5)

# Mix both!
cleaner.drop_columns('Name', 0, 'Email', 3)
```

### 2. Correlation Analysis (New!)

Get detailed correlation analysis with AI interpretation:

```python
# Analyze specific pair
result = cleaner.analyze_correlation('Height', 'Weight')
print(result['interpretation'])  # Plain English explanation

# Find all significant correlations
result = cleaner.analyze_correlation(threshold=0.5)
for corr in result['all_correlations']:
    print(f"{corr['col1']} ↔ {corr['col2']}: {corr['correlation']:.3f}")
```

### 3. View as Image (New!)

Export DataFrame as professional table images:

```python
# First 10 rows
cleaner.view_as_image(rows=10, save_path='preview.png')

# Last 10 rows (using negative index!)
cleaner.view_as_image(rows=-10, save_path='tail.png')

# Full table
cleaner.view_as_image(save_path='full_data.png')

# Custom styling
cleaner.view_as_image(
    rows=20,
    save_path='styled.png',
    title='My Dataset',
    show_dtypes=True
)
```

### 4. AI-Powered Descriptions

```python
# Brief description
print(cleaner.describe_data(0))

# Detailed description
print(cleaner.describe_data(1))
```

### 5. Smart Recommendations

```python
recommendations = cleaner.get_recommendations()
print(recommendations)
```

### 6. Professional Visualizations

```python
# Overview dashboard
cleaner.visualize('overview', save_path='dashboard.png')

# Missing values heatmap
cleaner.visualize('missing', save_path='missing.png')

# Distribution plots
cleaner.visualize('distribution', 
                 columns=['Age', 'Salary', 'Score'],
                 save_path='distributions.png')

# Correlation matrix
cleaner.visualize('correlation', save_path='correlations.png')
```

---

## 🎓 Documentation

### Core Methods

#### `DataCleaner(file_path)`
Initialize the cleaner with your data file.

**Parameters:**
- `file_path` (str): Path to CSV, Excel, or JSON file

---

#### `drop_columns(*columns)`
Remove columns by name or index.

**Parameters:**
- `*columns`: Column names (str) or indices (int, 0-based)

**Returns:** List of dropped column names

**Example:**
```python
cleaner.drop_columns('ID', 0, 'Email', 3)
```

---

#### `analyze_correlation(col1=None, col2=None, threshold=0.3, method='pearson')`
Analyze correlations with detailed interpretations.

**Parameters:**
- `col1` (str): First column (for specific pair analysis)
- `col2` (str): Second column (for specific pair analysis)
- `threshold` (float): Minimum correlation to report (for all-pairs)
- `method` (str): 'pearson', 'spearman', or 'kendall'

**Returns:** Dictionary with correlation analysis

**Example:**
```python
# Specific pair
result = cleaner.analyze_correlation('X', 'Y')

# All pairs
result = cleaner.analyze_correlation(threshold=0.5)
```

---

#### `view_as_image(rows=None, save_path=None, **kwargs)`
Export DataFrame as professional table image.

**Parameters:**
- `rows` (int/None): Number of rows (positive=first N, negative=last N, None=all)
- `save_path` (str): Where to save the image
- `title` (str): Custom title
- `show_dtypes` (bool): Show data types in headers
- `figsize` (tuple): Figure size

**Example:**
```python
cleaner.view_as_image(rows=10, save_path='preview.png')
cleaner.view_as_image(rows=-10, save_path='tail.png')
```

---

#### `profile()`
Get comprehensive data profile.

**Returns:** Dictionary with statistics and quality metrics

---

#### `describe_data(detail_level=0)`
Get AI-generated data description.

**Parameters:**
- `detail_level` (int): 0=brief, 1=detailed

**Returns:** String description

---

#### `get_recommendations()`
Get AI-generated cleaning recommendations.

**Returns:** String with recommendations

---

#### `visualize(plot_type='overview', **kwargs)`
Create professional visualizations.

**Parameters:**
- `plot_type` (str): 'overview', 'missing', 'distribution', 'correlation', 'outliers', 'categorical'
- `save_path` (str): Where to save the plot
- `columns` (list): Specific columns (for some plot types)

---

#### `clean(config)`
Execute cleaning operations.

**Parameters:**
- `config` (dict): Cleaning configuration

**Example:**
```python
config = {
    'missing': {'strategy': 'median'},
    'outliers': {'method': 'iqr', 'action': 'cap'},
    'duplicates': {'drop': True}
}
cleaner.clean(config)
```

---

#### `explain_cleaning(detail_level='summary')`
Get explanation of cleaning operations.

**Parameters:**
- `detail_level` (str): 'summary' or 'detailed'

**Returns:** String explanation

---

#### `save(filename=None, format='csv')`
Save cleaned data.

**Parameters:**
- `filename` (str): Output filename (optional)
- `format` (str): 'csv', 'excel', or 'json'

**Returns:** Path to saved file

---

## 📊 Cleaning Configuration

### Missing Values

```python
config = {
    'missing': {
        'strategy': 'median',  # 'drop', 'mean', 'median', 'mode', 'ffill'
        'columns': ['Age', 'Salary']  # Optional: specific columns
    }
}
```

### Outliers

```python
config = {
    'outliers': {
        'method': 'iqr',        # 'iqr' or 'zscore'
        'action': 'cap',         # 'cap', 'remove', or 'flag'
        'threshold': 1.5,        # IQR multiplier (default 1.5)
        'columns': ['Price']     # Optional: specific columns
    }
}
```

### Duplicates

```python
config = {
    'duplicates': {
        'drop': True,
        'keep': 'first',  # 'first', 'last', or False
        'subset': None    # Optional: columns to check
    }
}
```

### Complete Configuration

```python
config = {
    'missing': {'strategy': 'median'},
    'outliers': {'method': 'iqr', 'action': 'cap'},
    'duplicates': {'drop': True}
}
cleaner.clean(config)
```

---

## 💡 Use Cases

### Data Science Projects
- Clean datasets before analysis
- Generate quality reports
- Create visualization dashboards

### Machine Learning Pipelines
- Preprocess training data
- Handle missing values intelligently
- Detect and handle outliers

### Business Analytics
- Prepare data for reporting
- Ensure data quality
- Create professional visualizations

### Data Quality Audits
- Assess data quality scores
- Identify data issues
- Generate comprehensive reports

---

## 🔧 Requirements

- Python 3.7 or higher
- pandas >= 1.3.0
- numpy >= 1.20.0
- scipy >= 1.7.0
- matplotlib >= 3.3.0
- seaborn >= 0.11.0
- openpyxl >= 3.0.0

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Contact

- **Author:** Akinboye Yusuff
- **Email:** mailakinboye@gmail.com
- **GitHub:** https://github.com/akinboye/datapolish

---

## 🙏 Acknowledgments

DataPolish was created to make data cleaning accessible, intelligent, and efficient for everyone from beginners to data science professionals.

---

## ⭐ Star us on GitHub!

If you find DataPolish helpful, please star the repository!

---

**Happy Data Cleaning!** 🧹✨📊
