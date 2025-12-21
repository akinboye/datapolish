"""
AI-Powered Data Describer for PureData

This module provides intelligent data descriptions using statistical analysis
and rule-based AI approaches.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any


class DataDescriber:
    """
    Generates AI-powered descriptions of datasets.
    Provides both short summaries and detailed analyses.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the DataDescriber.
        
        Parameters:
        -----------
        df : pd.DataFrame
            The dataset to describe
        """
        self.df = df
        self.stats = self._compute_statistics()
    
    def _compute_statistics(self) -> Dict:
        """Compute comprehensive statistics about the dataset."""
        stats = {
            'shape': self.df.shape,
            'size': self.df.size,
            'memory_usage': self.df.memory_usage(deep=True).sum(),
            'dtypes': self.df.dtypes.value_counts().to_dict(),
            'missing': self.df.isnull().sum().sum(),
            'missing_pct': (self.df.isnull().sum().sum() / self.df.size) * 100,
            'duplicates': self.df.duplicated().sum(),
            'duplicates_pct': (self.df.duplicated().sum() / len(self.df)) * 100 if len(self.df) > 0 else 0,
        }
        
        # Numeric columns analysis
        numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            stats['numeric_summary'] = self.df[numeric_cols].describe().to_dict()
            stats['correlations'] = self._find_strong_correlations(numeric_cols)
        
        # Categorical columns analysis
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            stats['categorical_info'] = {}
            for col in categorical_cols:
                stats['categorical_info'][col] = {
                    'unique_count': self.df[col].nunique(),
                    'top_value': self.df[col].mode()[0] if not self.df[col].mode().empty else None,
                    'top_value_freq': self.df[col].value_counts().iloc[0] if len(self.df[col].value_counts()) > 0 else 0
                }
        
        # Datetime columns
        datetime_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        if datetime_cols:
            stats['datetime_info'] = {}
            for col in datetime_cols:
                stats['datetime_info'][col] = {
                    'min_date': self.df[col].min(),
                    'max_date': self.df[col].max(),
                    'range_days': (self.df[col].max() - self.df[col].min()).days if pd.notna(self.df[col].min()) else 0
                }
        
        return stats
    
    def _find_strong_correlations(self, numeric_cols: list, threshold: float = 0.7) -> list:
        """Find strong correlations between numeric columns."""
        if len(numeric_cols) < 2:
            return []
        
        corr_matrix = self.df[numeric_cols].corr()
        strong_corr = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > threshold:
                    strong_corr.append({
                        'col1': corr_matrix.columns[i],
                        'col2': corr_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        return strong_corr
    
    def describe(self, detail_level: int = 0) -> str:
        """
        Generate an AI-powered description of the dataset.
        
        Parameters:
        -----------
        detail_level : int
            0 = short summary (quick overview)
            1 = detailed description (comprehensive analysis)
        
        Returns:
        --------
        str : Dataset description
        """
        if detail_level == 0:
            return self._short_summary()
        elif detail_level == 1:
            return self._detailed_description()
        else:
            raise ValueError("detail_level must be 0 (short) or 1 (detailed)")
    
    def _short_summary(self) -> str:
        """Generate a short summary of the dataset."""
        rows, cols = self.stats['shape']
        memory_mb = self.stats['memory_usage'] / (1024 ** 2)
        
        summary = f"""
# Dataset Summary

**Quick Overview:**
- **Size:** {rows:,} rows × {cols} columns
- **Memory:** {memory_mb:.2f} MB
- **Missing Values:** {self.stats['missing']:,} ({self.stats['missing_pct']:.2f}%)
- **Duplicate Rows:** {self.stats['duplicates']:,} ({self.stats['duplicates_pct']:.2f}%)

**Column Types:**
"""
        
        for dtype, count in self.stats['dtypes'].items():
            summary += f"- {str(dtype)}: {count} columns\n"
        
        # Quick insights
        summary += "\n**Quick Insights:**\n"
        
        if self.stats['missing_pct'] > 10:
            summary += f"⚠️ High missing data rate ({self.stats['missing_pct']:.1f}%) - consider investigation\n"
        elif self.stats['missing_pct'] > 0:
            summary += f"✓ Low missing data rate ({self.stats['missing_pct']:.1f}%) - manageable\n"
        else:
            summary += "✓ No missing values - clean dataset\n"
        
        if self.stats['duplicates_pct'] > 5:
            summary += f"⚠️ High duplicate rate ({self.stats['duplicates_pct']:.1f}%) - review recommended\n"
        elif self.stats['duplicates_pct'] > 0:
            summary += f"✓ Few duplicates ({self.stats['duplicates_pct']:.1f}%) - can be cleaned\n"
        else:
            summary += "✓ No duplicates - unique records\n"
        
        # Data quality score
        quality_score = self._calculate_quality_score()
        summary += f"\n**Data Quality Score:** {quality_score}/100\n"
        
        if quality_score >= 90:
            summary += "🌟 Excellent - Ready for analysis\n"
        elif quality_score >= 70:
            summary += "✓ Good - Minor cleaning recommended\n"
        elif quality_score >= 50:
            summary += "⚠️ Fair - Cleaning needed\n"
        else:
            summary += "❌ Poor - Significant cleaning required\n"
        
        return summary
    
    def _detailed_description(self) -> str:
        """Generate a detailed description of the dataset."""
        rows, cols = self.stats['shape']
        memory_mb = self.stats['memory_usage'] / (1024 ** 2)
        
        description = f"""
# Comprehensive Dataset Analysis

## 📊 Basic Information

**Dataset Dimensions:**
- **Total Rows:** {rows:,}
- **Total Columns:** {cols}
- **Total Cells:** {self.stats['size']:,}
- **Memory Usage:** {memory_mb:.2f} MB ({memory_mb * 1024:.2f} KB)

**Data Types Distribution:**
"""
        
        for dtype, count in self.stats['dtypes'].items():
            pct = (count / cols) * 100
            description += f"- **{str(dtype)}:** {count} columns ({pct:.1f}%)\n"
        
        # Missing values analysis
        description += f"""

## 🔍 Data Quality Assessment

**Missing Values:**
- **Total Missing:** {self.stats['missing']:,} cells
- **Percentage:** {self.stats['missing_pct']:.2f}% of all data
"""
        
        # Missing by column
        missing_by_col = self.df.isnull().sum()
        missing_cols = missing_by_col[missing_by_col > 0]
        
        if len(missing_cols) > 0:
            description += "\n**Columns with Missing Values:**\n"
            for col, count in missing_cols.items():
                pct = (count / rows) * 100
                description += f"- `{col}`: {count:,} missing ({pct:.2f}%)\n"
        else:
            description += "\n✅ **No missing values** - Perfect!\n"
        
        # Duplicates analysis
        description += f"""

**Duplicate Rows:**
- **Count:** {self.stats['duplicates']:,}
- **Percentage:** {self.stats['duplicates_pct']:.2f}%
"""
        
        if self.stats['duplicates_pct'] > 5:
            description += "⚠️ **High duplicate rate** - Investigation recommended\n"
        elif self.stats['duplicates'] > 0:
            description += "✓ **Low duplicate rate** - Can be easily addressed\n"
        else:
            description += "✅ **No duplicates** - All records are unique\n"
        
        # Numeric columns analysis
        if 'numeric_summary' in self.stats:
            description += "\n## 📈 Numeric Columns Analysis\n\n"
            
            numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
            description += f"**Total Numeric Columns:** {len(numeric_cols)}\n\n"
            
            for col in numeric_cols:
                col_stats = self.stats['numeric_summary'][col]
                description += f"### `{col}`\n"
                description += f"- **Count:** {int(col_stats['count']):,} values\n"
                description += f"- **Mean:** {col_stats['mean']:.2f}\n"
                description += f"- **Median:** {col_stats['50%']:.2f}\n"
                description += f"- **Std Dev:** {col_stats['std']:.2f}\n"
                description += f"- **Range:** [{col_stats['min']:.2f}, {col_stats['max']:.2f}]\n"
                description += f"- **Q1-Q3:** [{col_stats['25%']:.2f}, {col_stats['75%']:.2f}]\n"
                
                # Distribution insights
                if col_stats['std'] > 0:
                    cv = (col_stats['std'] / col_stats['mean']) * 100 if col_stats['mean'] != 0 else 0
                    if cv < 10:
                        description += f"- **Variation:** Low (CV: {cv:.1f}%) - Stable values\n"
                    elif cv < 30:
                        description += f"- **Variation:** Moderate (CV: {cv:.1f}%)\n"
                    else:
                        description += f"- **Variation:** High (CV: {cv:.1f}%) - Wide spread\n"
                
                # Skewness detection
                skewness = self.df[col].skew()
                if abs(skewness) < 0.5:
                    description += f"- **Distribution:** Approximately symmetric (skew: {skewness:.2f})\n"
                elif skewness > 0.5:
                    description += f"- **Distribution:** Right-skewed (skew: {skewness:.2f}) - tail extends right\n"
                else:
                    description += f"- **Distribution:** Left-skewed (skew: {skewness:.2f}) - tail extends left\n"
                
                description += "\n"
            
            # Correlations
            if self.stats['correlations']:
                description += "**Strong Correlations Found:**\n"
                for corr in self.stats['correlations']:
                    description += f"- `{corr['col1']}` ↔ `{corr['col2']}`: {corr['correlation']:.3f}\n"
                description += "\n"
        
        # Categorical columns analysis
        if 'categorical_info' in self.stats:
            description += "\n## 🏷️ Categorical Columns Analysis\n\n"
            
            for col, info in self.stats['categorical_info'].items():
                description += f"### `{col}`\n"
                description += f"- **Unique Values:** {info['unique_count']:,}\n"
                description += f"- **Most Frequent:** '{info['top_value']}' (appears {info['top_value_freq']:,} times)\n"
                
                # Cardinality assessment
                cardinality_ratio = info['unique_count'] / rows
                if cardinality_ratio > 0.9:
                    description += f"- **Cardinality:** Very High ({cardinality_ratio:.1%}) - Nearly unique values\n"
                elif cardinality_ratio > 0.5:
                    description += f"- **Cardinality:** High ({cardinality_ratio:.1%}) - Many unique values\n"
                elif cardinality_ratio > 0.1:
                    description += f"- **Cardinality:** Medium ({cardinality_ratio:.1%})\n"
                else:
                    description += f"- **Cardinality:** Low ({cardinality_ratio:.1%}) - Few distinct values\n"
                
                description += "\n"
        
        # Datetime columns analysis
        if 'datetime_info' in self.stats:
            description += "\n## 📅 DateTime Columns Analysis\n\n"
            
            for col, info in self.stats['datetime_info'].items():
                description += f"### `{col}`\n"
                description += f"- **Earliest Date:** {info['min_date']}\n"
                description += f"- **Latest Date:** {info['max_date']}\n"
                description += f"- **Time Span:** {info['range_days']:,} days\n\n"
        
        # Overall assessment
        quality_score = self._calculate_quality_score()
        
        description += f"""

## 🎯 Overall Assessment

**Data Quality Score: {quality_score}/100**

"""
        
        if quality_score >= 90:
            description += """
**Verdict: Excellent! 🌟**
- Your dataset is in great shape
- Minimal cleaning needed
- Ready for analysis and modeling
"""
        elif quality_score >= 70:
            description += """
**Verdict: Good ✓**
- Overall good quality
- Minor cleaning recommended
- Should work well with preprocessing
"""
        elif quality_score >= 50:
            description += """
**Verdict: Fair ⚠️**
- Noticeable data quality issues
- Cleaning is recommended before analysis
- Address missing values and duplicates
"""
        else:
            description += """
**Verdict: Needs Attention ❌**
- Significant data quality issues
- Comprehensive cleaning required
- Review data collection process
"""
        
        # Recommendations
        description += "\n\n## 💡 Recommendations\n\n"
        
        if self.stats['missing_pct'] > 5:
            description += "1. **Address Missing Values:** Use appropriate imputation strategies\n"
        
        if self.stats['duplicates_pct'] > 1:
            description += "2. **Remove Duplicates:** Clean duplicate records\n"
        
        if 'correlations' in self.stats and self.stats['correlations']:
            description += "3. **Review Correlations:** Consider feature engineering or selection\n"
        
        if len(self.df.select_dtypes(include=['object']).columns) > 0:
            description += "4. **Encode Categorical Data:** Prepare for machine learning models\n"
        
        if self.stats['missing_pct'] == 0 and self.stats['duplicates_pct'] == 0:
            description += "✅ **Your data is clean!** Proceed with analysis.\n"
        
        return description
    
    def _calculate_quality_score(self) -> int:
        """Calculate an overall data quality score (0-100)."""
        score = 100
        
        # Penalize for missing values
        score -= min(self.stats['missing_pct'], 30)  # Max 30 point penalty
        
        # Penalize for duplicates
        score -= min(self.stats['duplicates_pct'], 20)  # Max 20 point penalty
        
        # Bonus for having diverse data types
        if len(self.stats['dtypes']) > 1:
            score += 5
        
        # Bonus for no issues
        if self.stats['missing_pct'] == 0 and self.stats['duplicates_pct'] == 0:
            score = min(score + 10, 100)
        
        return max(0, min(100, int(score)))
    
    def get_column_info(self, column_name: str) -> str:
        """
        Get detailed information about a specific column.
        
        Parameters:
        -----------
        column_name : str
            Name of the column
        
        Returns:
        --------
        str : Column description
        """
        if column_name not in self.df.columns:
            return f"Column '{column_name}' not found in dataset."
        
        col = self.df[column_name]
        dtype = col.dtype
        
        info = f"\n# Column: `{column_name}`\n\n"
        info += f"**Data Type:** {dtype}\n"
        info += f"**Non-Null Count:** {col.count():,} / {len(col):,}\n"
        info += f"**Missing Values:** {col.isnull().sum():,} ({(col.isnull().sum() / len(col) * 100):.2f}%)\n\n"
        
        if pd.api.types.is_numeric_dtype(dtype):
            info += "**Statistics:**\n"
            info += f"- Mean: {col.mean():.2f}\n"
            info += f"- Median: {col.median():.2f}\n"
            info += f"- Std Dev: {col.std():.2f}\n"
            info += f"- Min: {col.min():.2f}\n"
            info += f"- Max: {col.max():.2f}\n"
            info += f"- Unique Values: {col.nunique():,}\n"
        elif pd.api.types.is_object_dtype(dtype):
            info += "**Categories:**\n"
            info += f"- Unique Values: {col.nunique():,}\n"
            value_counts = col.value_counts().head(10)
            info += "- Top 10 Values:\n"
            for val, count in value_counts.items():
                info += f"  - '{val}': {count:,} ({(count/len(col)*100):.1f}%)\n"
        
        return info
