"""
AI-Powered Cleaning Explainer for PureData

This module provides detailed explanations of data cleaning processes using
lightweight, free, and open-source AI approaches.
"""

import json
from typing import Dict, List, Optional, Any


class CleaningExplainer:
    """
    Provides AI-powered explanations for data cleaning processes.
    Uses rule-based and template-based approaches (lightweight and free).
    """
    
    def __init__(self):
        """Initialize the CleaningExplainer."""
        self.explanation_templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load explanation templates for different cleaning operations."""
        return {
            'missing_values': {
                'drop': {
                    'short': "Rows with missing values were removed from the dataset.",
                    'detailed': """
**Missing Value Removal - Drop Strategy**

**What happened:**
Rows containing missing (null/NaN) values were completely removed from your dataset.

**Why this matters:**
- Missing values can cause errors in analysis and machine learning models
- Dropping is the simplest approach but may lose valuable data
- This is best when you have plenty of data and few missing values

**Technical details:**
- Method: Row-wise deletion (listwise deletion)
- Any row with at least one missing value in the specified columns was removed
- The remaining data is complete with no null values

**Impact:**
- Data size reduced (rows removed)
- Statistical integrity maintained for remaining data
- Potential information loss if many rows were dropped

**When to use:**
- Missing values are <5% of total data
- Missing data is random (MCAR - Missing Completely At Random)
- You have sufficient data after removal
                    """
                },
                'mean': {
                    'short': "Missing values were filled with the average (mean) of each column.",
                    'detailed': """
**Missing Value Imputation - Mean Strategy**

**What happened:**
Missing values in numeric columns were replaced with the arithmetic mean (average) of non-missing values in that column.

**Why this matters:**
- Preserves all rows in your dataset (no data loss)
- Maintains the overall average of the column
- Common statistical approach for numeric data

**Technical details:**
- Calculation: mean = sum(all values) / count(values)
- Applied only to numeric columns
- Each column uses its own mean value
- Missing values are replaced in-place

**Advantages:**
✓ No rows lost
✓ Simple and interpretable
✓ Works well when data is normally distributed

**Limitations:**
✗ Reduces variance in the data
✗ Not suitable for skewed distributions
✗ May not capture relationships between variables

**Example:**
Column 'Age': [25, 30, NaN, 40, 35]
Mean = (25 + 30 + 40 + 35) / 4 = 32.5
Result: [25, 30, 32.5, 40, 35]
                    """
                },
                'median': {
                    'short': "Missing values were filled with the middle value (median) of each column.",
                    'detailed': """
**Missing Value Imputation - Median Strategy**

**What happened:**
Missing values in numeric columns were replaced with the median (middle value) of non-missing values in that column.

**Why this matters:**
- More robust than mean for skewed data
- Not affected by extreme outliers
- Preserves all rows in dataset

**Technical details:**
- Median is the middle value when data is sorted
- For even-length data: average of two middle values
- Applied only to numeric columns
- Each column uses its own median

**Advantages:**
✓ No rows lost
✓ Resistant to outliers
✓ Better for skewed distributions
✓ Maintains data robustness

**When to use:**
- Data has outliers
- Distribution is skewed (not normal)
- Want conservative imputation

**Example:**
Column 'Salary': [30k, 35k, NaN, 150k, 40k]
Sorted: [30k, 35k, 40k, 150k]
Median = 37.5k (not affected by 150k outlier)
Result: [30k, 35k, 37.5k, 150k, 40k]
                    """
                },
                'mode': {
                    'short': "Missing values were filled with the most frequent value in each column.",
                    'detailed': """
**Missing Value Imputation - Mode Strategy**

**What happened:**
Missing values were replaced with the mode (most frequently occurring value) in each column.

**Why this matters:**
- Works for both numeric and categorical data
- Preserves the most common pattern
- Useful for categorical variables

**Technical details:**
- Mode = value that appears most frequently
- If multiple modes exist, first one is used
- Applied to all data types
- Each column uses its own mode

**Advantages:**
✓ Works for categorical data
✓ Preserves common patterns
✓ No rows lost
✓ Intuitive for non-numeric data

**Best for:**
- Categorical variables
- Discrete numeric data
- When most frequent value is meaningful

**Example:**
Column 'Department': ['Sales', 'IT', NaN, 'Sales', 'HR', 'Sales']
Mode = 'Sales' (appears 3 times)
Result: ['Sales', 'IT', 'Sales', 'Sales', 'HR', 'Sales']
                    """
                },
                'constant': {
                    'short': "Missing values were filled with a specified constant value.",
                    'detailed': """
**Missing Value Imputation - Constant Strategy**

**What happened:**
Missing values were replaced with a user-specified constant value.

**Why this matters:**
- Full control over replacement value
- Can indicate "unknown" or "missing" explicitly
- Useful for categorical data

**Technical details:**
- All missing values replaced with same constant
- User defines the replacement value
- Can be any data type
- Preserves all rows

**Common use cases:**
- Fill with 0 for numeric data
- Fill with 'Unknown' for categories
- Fill with 'N/A' to mark missing data
- Domain-specific defaults

**Advantages:**
✓ Full control over imputation
✓ Clear indication of imputed values
✓ Works for all data types
✓ Domain knowledge can be applied

**Example:**
Column 'Category': ['A', NaN, 'B', NaN, 'C']
Constant = 'Unknown'
Result: ['A', 'Unknown', 'B', 'Unknown', 'C']
                    """
                }
            },
            'outliers': {
                'iqr': {
                    'short': "Outliers were detected using the Interquartile Range (IQR) method.",
                    'detailed': """
**Outlier Detection - IQR (Interquartile Range) Method**

**What happened:**
Statistical outliers were identified using the IQR method, which detects values that fall far from the central 50% of your data.

**How it works:**
1. Calculate Q1 (25th percentile) and Q3 (75th percentile)
2. Calculate IQR = Q3 - Q1
3. Define boundaries:
   - Lower bound = Q1 - (multiplier × IQR)
   - Upper bound = Q3 + (multiplier × IQR)
4. Values outside these bounds are outliers

**Default multiplier: 1.5**
- Standard value used in statistics
- Identifies moderate to extreme outliers
- Based on box plot methodology

**Why this matters:**
- Outliers can skew statistical analyses
- May indicate data entry errors or special cases
- Can dramatically affect averages and correlations

**Advantages:**
✓ Not affected by extreme values
✓ Based on data distribution
✓ Well-established statistical method
✓ Works for any distribution shape

**Visual representation (Box Plot):**
```
    |----[====|====]----| 
    ↑    ↑    ↑    ↑    ↑
   Min   Q1  Med  Q3  Max
   
   Outliers: < Q1-1.5×IQR  or  > Q3+1.5×IQR
```

**Example:**
Data: [10, 12, 13, 14, 15, 16, 17, 100]
Q1 = 12.5, Q3 = 16.5, IQR = 4
Lower = 12.5 - 1.5×4 = 6.5
Upper = 16.5 + 1.5×4 = 22.5
Outlier: 100 (> 22.5)
                    """
                },
                'zscore': {
                    'short': "Outliers were detected using the Z-score method (standard deviations from mean).",
                    'detailed': """
**Outlier Detection - Z-Score Method**

**What happened:**
Outliers were identified by measuring how many standard deviations each value is from the mean.

**How it works:**
1. Calculate mean (μ) and standard deviation (σ)
2. For each value: z-score = (value - μ) / σ
3. If |z-score| > threshold, it's an outlier

**Default threshold: 3.0**
- Values > 3 standard deviations from mean
- Captures ~99.7% of data in normal distribution
- Common statistical threshold

**Why this matters:**
- Z-score tells you how "unusual" a value is
- Based on normal distribution assumptions
- Higher threshold = fewer outliers detected

**Advantages:**
✓ Uses all data for detection
✓ Mathematically rigorous
✓ Works well for normally distributed data
✓ Intuitive interpretation

**Limitations:**
✗ Assumes normal distribution
✗ Sensitive to extreme outliers
✗ May not work well for skewed data

**Z-Score interpretation:**
- |z| < 1.0: Within 1 std dev (68% of data)
- |z| < 2.0: Within 2 std dev (95% of data)
- |z| < 3.0: Within 3 std dev (99.7% of data)
- |z| > 3.0: Outlier (0.3% of data)

**Example:**
Data: [10, 12, 14, 16, 18, 50]
Mean = 20, Std = 14.14
Z-score for 50: (50-20)/14.14 = 2.12
Z-score for 10: (10-20)/14.14 = -0.71
At threshold 3.0: No outliers
At threshold 2.0: 50 is an outlier
                    """
                }
            },
            'duplicates': {
                'short': "Duplicate rows were identified and removed from the dataset.",
                'detailed': """
**Duplicate Row Removal**

**What happened:**
Rows that were exact duplicates (all columns identical) were identified and removed, keeping only the first occurrence.

**How it works:**
1. Compare each row to all other rows
2. If all column values match → duplicate
3. Keep first occurrence, remove subsequent ones
4. Can optionally check only specific columns

**Why this matters:**
- Duplicates can skew statistical analyses
- Inflate counts and percentages
- May indicate data collection errors
- Can bias machine learning models

**Detection methods:**
- **Full row**: All columns must match
- **Subset**: Only specified columns checked
- **Case sensitivity**: Exact string matching

**What's kept:**
✓ First occurrence of each unique row
✓ All rows with at least one different value

**What's removed:**
✗ Subsequent identical rows
✗ Rows matching on specified subset

**Common causes of duplicates:**
- Data entry errors
- Multiple data sources
- System glitches
- Repeated measurements
- Data merging issues

**Example:**
Original data:
```
ID  Name   Age
1   Alice  25
2   Bob    30
1   Alice  25  ← Duplicate
3   Carol  28
```

After removal:
```
ID  Name   Age
1   Alice  25  ← Kept (first)
2   Bob    30
3   Carol  28
```

**Impact:**
- Reduced dataset size
- Improved data quality
- More accurate statistics
- Better model performance
                """
            },
            'standardization': {
                'short': "Column names were standardized to a consistent format.",
                'detailed': """
**Column Name Standardization**

**What happened:**
All column names were transformed to a clean, consistent, and code-friendly format.

**Transformations applied:**
1. **Lowercase**: All letters converted to lowercase
2. **Whitespace**: Spaces replaced with underscores
3. **Special characters**: Removed or replaced with underscores
4. **Trimming**: Leading/trailing spaces removed

**Before → After examples:**
- "Customer Name" → "customer_name"
- "Total Price ($)" → "total_price"
- "  Order-ID  " → "order_id"
- "2023 Sales" → "2023_sales"

**Why this matters:**
- Consistent naming improves code readability
- Avoids syntax errors in some tools
- Makes columns easier to reference
- Follows Python naming conventions

**Benefits:**
✓ No spaces in names (easier to type)
✓ All lowercase (prevents case issues)
✓ Valid Python identifiers
✓ Works across all platforms
✓ Improves code portability

**Best practices followed:**
- PEP 8 style guide compliance
- Database-friendly naming
- Cross-platform compatibility
- No reserved keywords

**Technical details:**
- Regex pattern: r'[^\\w\\s]' → '_'
- Multiple spaces → single underscore
- Preserves readability
- Reversible if needed (documented)
                """
            }
        }
    
    def explain(self, 
                operation: str, 
                method: Optional[str] = None, 
                detail_level: str = 'detailed',
                context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate an explanation for a cleaning operation.
        
        Parameters:
        -----------
        operation : str
            Type of operation ('missing_values', 'outliers', 'duplicates', 'standardization')
        method : str, optional
            Specific method used (e.g., 'mean', 'iqr', 'drop')
        detail_level : str, default='detailed'
            Level of explanation: 'short' or 'detailed'
        context : dict, optional
            Additional context about the operation (e.g., parameters, results)
        
        Returns:
        --------
        str : Explanation text
        """
        if operation not in self.explanation_templates:
            return f"No explanation available for operation: {operation}"
        
        if method and method in self.explanation_templates[operation]:
            template = self.explanation_templates[operation][method]
        else:
            # Return general explanation for the operation
            template = self.explanation_templates[operation]
            if isinstance(template, dict) and 'short' not in template:
                # If no specific method, return first available
                method_key = list(template.keys())[0]
                template = template[method_key]
        
        explanation = template.get(detail_level, template.get('detailed', ''))
        
        # Add context if provided
        if context:
            explanation += self._add_context(context)
        
        return explanation
    
    def _add_context(self, context: Dict[str, Any]) -> str:
        """Add contextual information to the explanation."""
        context_text = "\n\n**Your Results:**\n"
        
        if 'rows_affected' in context:
            context_text += f"- Rows affected: {context['rows_affected']}\n"
        
        if 'columns_affected' in context:
            context_text += f"- Columns processed: {', '.join(context['columns_affected'])}\n"
        
        if 'values_imputed' in context:
            context_text += f"- Values imputed: {context['values_imputed']}\n"
        
        if 'outliers_found' in context:
            context_text += f"- Outliers detected: {context['outliers_found']}\n"
        
        if 'parameters' in context:
            context_text += f"- Parameters used: {json.dumps(context['parameters'], indent=2)}\n"
        
        return context_text
    
    def explain_cleaning_report(self, 
                                 changes: List[str], 
                                 config: Dict,
                                 detail_level: str = 'detailed') -> str:
        """
        Generate a comprehensive explanation of all cleaning operations performed.
        
        Parameters:
        -----------
        changes : list
            List of changes applied (from cleaner.clean())
        config : dict
            Configuration used for cleaning
        detail_level : str
            'short' or 'detailed'
        
        Returns:
        --------
        str : Complete explanation
        """
        explanation = "# Data Cleaning Report - Detailed Explanation\n\n"
        
        # Missing values
        if 'missing' in config:
            strategy = config['missing'].get('strategy', 'unknown')
            explanation += "## Missing Values\n\n"
            explanation += self.explain('missing_values', strategy, detail_level)
            explanation += "\n\n---\n\n"
        
        # Outliers
        if 'outliers' in config:
            method = config['outliers'].get('method', 'iqr')
            explanation += "## Outlier Detection\n\n"
            explanation += self.explain('outliers', method, detail_level)
            explanation += "\n\n---\n\n"
        
        # Duplicates
        if 'duplicates' in config and config['duplicates'].get('drop'):
            explanation += "## Duplicate Removal\n\n"
            explanation += self.explain('duplicates', detail_level=detail_level)
            explanation += "\n\n---\n\n"
        
        # Standardization
        explanation += "## Column Standardization\n\n"
        explanation += self.explain('standardization', detail_level=detail_level)
        explanation += "\n\n---\n\n"
        
        # Summary of changes
        explanation += "## Summary of Changes Applied\n\n"
        for i, change in enumerate(changes, 1):
            explanation += f"{i}. {change}\n"
        
        return explanation
    
    def get_recommendation(self, profile: Dict) -> str:
        """
        Provide AI-like recommendations based on data profile.
        
        Parameters:
        -----------
        profile : dict
            Data profiling results
        
        Returns:
        --------
        str : Recommendations
        """
        recommendations = "# Data Cleaning Recommendations\n\n"
        
        # Missing values recommendations
        if 'missing_values' in profile:
            missing = profile['missing_values']
            high_missing = {k: v for k, v in missing.items() if v > 5}
            
            if high_missing:
                recommendations += "## Missing Values\n\n"
                recommendations += "**Columns with >5% missing data:**\n"
                for col, pct in high_missing.items():
                    recommendations += f"- {col}: {pct:.2f}%\n"
                    
                    if pct < 10:
                        recommendations += "  - *Recommendation:* Use median imputation (robust to outliers)\n"
                    elif pct < 30:
                        recommendations += "  - *Recommendation:* Consider if this column is necessary, or use mode/constant\n"
                    else:
                        recommendations += "  - *Recommendation:* Consider dropping this column (>30% missing)\n"
                recommendations += "\n"
        
        # Outliers recommendations
        if 'outlier_info' in profile:
            outlier_info = profile['outlier_info']
            if outlier_info:
                recommendations += "## Outliers\n\n"
                for col, info in outlier_info.items():
                    pct = info.get('percentage', 0)
                    if pct > 10:
                        recommendations += f"- {col}: {info['count']} outliers ({pct:.2f}%)\n"
                        recommendations += "  - *Recommendation:* Consider capping instead of removing (>10% of data)\n"
                    else:
                        recommendations += f"- {col}: {info['count']} outliers ({pct:.2f}%)\n"
                        recommendations += "  - *Recommendation:* Safe to remove or cap\n"
                recommendations += "\n"
        
        # Duplicates recommendations
        if 'duplicates' in profile:
            dup_pct = profile['duplicates'].get('percentage', 0)
            if dup_pct > 0:
                recommendations += "## Duplicates\n\n"
                recommendations += f"- Found {profile['duplicates']['count']} duplicate rows ({dup_pct:.2f}%)\n"
                if dup_pct > 5:
                    recommendations += "  - *Recommendation:* **High duplicate rate!** Investigate the source of duplicates\n"
                else:
                    recommendations += "  - *Recommendation:* Safe to remove duplicates\n"
                recommendations += "\n"
        
        return recommendations
