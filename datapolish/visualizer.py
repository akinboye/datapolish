"""
Data Visualization Module for PureData

Provides comprehensive data visualization capabilities using matplotlib.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Tuple, Union
from pathlib import Path


class DataVisualizer:
    """
    Generates various visualizations for data analysis and cleaning insights.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the DataVisualizer.
        
        Parameters:
        -----------
        df : pd.DataFrame
            The dataset to visualize
        """
        self.df = df
        # Set style for better-looking plots
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def plot_missing_values(self, 
                            figsize: Tuple[int, int] = (12, 6),
                            save_path: Optional[str] = None) -> None:
        """
        Visualize missing values in the dataset.
        
        Parameters:
        -----------
        figsize : tuple
            Figure size (width, height)
        save_path : str, optional
            Path to save the figure
        """
        missing_counts = self.df.isnull().sum()
        missing_pct = (missing_counts / len(self.df)) * 100
        
        # Filter to only columns with missing values
        missing_data = pd.DataFrame({
            'Count': missing_counts[missing_counts > 0],
            'Percentage': missing_pct[missing_pct > 0]
        }).sort_values('Count', ascending=False)
        
        if len(missing_data) == 0:
            print("No missing values to visualize!")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Count plot
        missing_data['Count'].plot(kind='barh', ax=ax1, color='coral')
        ax1.set_xlabel('Number of Missing Values', fontsize=12)
        ax1.set_ylabel('Columns', fontsize=12)
        ax1.set_title('Missing Values Count by Column', fontsize=14, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Percentage plot
        missing_data['Percentage'].plot(kind='barh', ax=ax2, color='skyblue')
        ax2.set_xlabel('Percentage Missing (%)', fontsize=12)
        ax2.set_ylabel('Columns', fontsize=12)
        ax2.set_title('Missing Values Percentage by Column', fontsize=14, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def plot_distribution(self, 
                         columns: Optional[List[str]] = None,
                         figsize: Tuple[int, int] = (15, 10),
                         save_path: Optional[str] = None) -> None:
        """
        Plot distributions of numeric columns.
        
        Parameters:
        -----------
        columns : list, optional
            Specific columns to plot. If None, plots all numeric columns
        figsize : tuple
            Figure size (width, height)
        save_path : str, optional
            Path to save the figure
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['number']).columns.tolist()
        else:
            columns = [c for c in columns if c in self.df.columns and pd.api.types.is_numeric_dtype(self.df[c])]
        
        if not columns:
            print("No numeric columns to visualize!")
            return
        
        n_cols = min(3, len(columns))
        n_rows = (len(columns) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        if n_rows == 1 and n_cols == 1:
            axes = np.array([axes])
        axes = axes.flatten() if isinstance(axes, np.ndarray) else [axes]
        
        for idx, col in enumerate(columns):
            ax = axes[idx]
            data = self.df[col].dropna()
            
            # Histogram with KDE
            ax.hist(data, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
            ax2 = ax.twinx()
            data.plot(kind='kde', ax=ax2, color='red', linewidth=2)
            
            ax.set_xlabel(col, fontsize=10)
            ax.set_ylabel('Frequency', fontsize=10)
            ax2.set_ylabel('Density', fontsize=10)
            ax.set_title(f'Distribution of {col}', fontsize=11, fontweight='bold')
            ax.grid(alpha=0.3)
        
        # Hide unused subplots
        for idx in range(len(columns), len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def plot_correlation_matrix(self,
                                 figsize: Tuple[int, int] = (12, 10),
                                 save_path: Optional[str] = None) -> None:
        """
        Plot correlation matrix heatmap for numeric columns.
        
        Parameters:
        -----------
        figsize : tuple
            Figure size (width, height)
        save_path : str, optional
            Path to save the figure
        """
        numeric_df = self.df.select_dtypes(include=['number'])
        
        if len(numeric_df.columns) < 2:
            print("Need at least 2 numeric columns for correlation matrix!")
            return
        
        corr = numeric_df.corr()
        
        plt.figure(figsize=figsize)
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', 
                    center=0, square=True, linewidths=1,
                    cbar_kws={"shrink": 0.8})
        
        plt.title('Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def plot_outliers_boxplot(self,
                               columns: Optional[List[str]] = None,
                               figsize: Tuple[int, int] = (15, 8),
                               save_path: Optional[str] = None) -> None:
        """
        Plot boxplots to visualize outliers.
        
        Parameters:
        -----------
        columns : list, optional
            Specific columns to plot. If None, plots all numeric columns
        figsize : tuple
            Figure size (width, height)
        save_path : str, optional
            Path to save the figure
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['number']).columns.tolist()
        else:
            columns = [c for c in columns if c in self.df.columns and pd.api.types.is_numeric_dtype(self.df[c])]
        
        if not columns:
            print("No numeric columns to visualize!")
            return
        
        n_cols = min(4, len(columns))
        n_rows = (len(columns) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        if n_rows == 1 and n_cols == 1:
            axes = np.array([axes])
        axes = axes.flatten() if isinstance(axes, np.ndarray) else [axes]
        
        for idx, col in enumerate(columns):
            ax = axes[idx]
            data = self.df[col].dropna()
            
            bp = ax.boxplot(data, vert=True, patch_artist=True,
                           boxprops=dict(facecolor='lightblue', alpha=0.7),
                           medianprops=dict(color='red', linewidth=2),
                           whiskerprops=dict(color='blue', linewidth=1.5),
                           capprops=dict(color='blue', linewidth=1.5),
                           flierprops=dict(marker='o', markerfacecolor='red', 
                                          markersize=5, alpha=0.5))
            
            ax.set_ylabel('Value', fontsize=10)
            ax.set_title(f'{col}', fontsize=11, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            ax.set_xticklabels([''])
        
        # Hide unused subplots
        for idx in range(len(columns), len(axes)):
            axes[idx].axis('off')
        
        fig.suptitle('Outlier Detection - Box Plots', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def plot_categorical_distribution(self,
                                       columns: Optional[List[str]] = None,
                                       top_n: int = 10,
                                       figsize: Tuple[int, int] = (15, 10),
                                       save_path: Optional[str] = None) -> None:
        """
        Plot distribution of categorical columns.
        
        Parameters:
        -----------
        columns : list, optional
            Specific columns to plot. If None, plots all categorical columns
        top_n : int
            Number of top categories to display
        figsize : tuple
            Figure size (width, height)
        save_path : str, optional
            Path to save the figure
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        else:
            columns = [c for c in columns if c in self.df.columns]
        
        if not columns:
            print("No categorical columns to visualize!")
            return
        
        n_cols = min(2, len(columns))
        n_rows = (len(columns) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        if n_rows == 1 and n_cols == 1:
            axes = np.array([axes])
        axes = axes.flatten() if isinstance(axes, np.ndarray) else [axes]
        
        for idx, col in enumerate(columns):
            ax = axes[idx]
            value_counts = self.df[col].value_counts().head(top_n)
            
            value_counts.plot(kind='barh', ax=ax, color='teal', alpha=0.7)
            ax.set_xlabel('Count', fontsize=10)
            ax.set_ylabel('Category', fontsize=10)
            ax.set_title(f'Top {top_n} Values in {col}', fontsize=11, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
            # Add value labels
            for i, v in enumerate(value_counts):
                ax.text(v, i, f' {v:,}', va='center', fontsize=9)
        
        # Hide unused subplots
        for idx in range(len(columns), len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def plot_data_overview(self, save_path: Optional[str] = None) -> None:
        """
        Create a comprehensive overview dashboard of the dataset.
        
        Parameters:
        -----------
        save_path : str, optional
            Path to save the figure
        """
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Missing values
        ax1 = fig.add_subplot(gs[0, :2])
        missing_counts = self.df.isnull().sum()
        missing_data = missing_counts[missing_counts > 0].sort_values(ascending=False)
        if len(missing_data) > 0:
            missing_data.plot(kind='barh', ax=ax1, color='coral')
            ax1.set_title('Missing Values by Column', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Count')
        else:
            ax1.text(0.5, 0.5, 'No Missing Values', ha='center', va='center', 
                    fontsize=14, transform=ax1.transAxes)
            ax1.set_title('Missing Values', fontsize=12, fontweight='bold')
        
        # 2. Data types
        ax2 = fig.add_subplot(gs[0, 2])
        dtype_counts = self.df.dtypes.value_counts()
        ax2.pie(dtype_counts.values, labels=dtype_counts.index, autopct='%1.1f%%',
                startangle=90, colors=sns.color_palette('pastel'))
        ax2.set_title('Data Types Distribution', fontsize=12, fontweight='bold')
        
        # 3. Duplicates
        ax3 = fig.add_subplot(gs[1, 0])
        dup_count = self.df.duplicated().sum()
        unique_count = len(self.df) - dup_count
        ax3.pie([unique_count, dup_count], labels=['Unique', 'Duplicates'],
                autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'lightcoral'])
        ax3.set_title(f'Duplicate Rows\n(Total: {dup_count:,})', fontsize=12, fontweight='bold')
        
        # 4. Numeric columns stats
        numeric_cols = self.df.select_dtypes(include=['number']).columns[:5]
        if len(numeric_cols) > 0:
            ax4 = fig.add_subplot(gs[1, 1:])
            self.df[numeric_cols].boxplot(ax=ax4, patch_artist=True)
            ax4.set_title('Distribution of Top 5 Numeric Columns', fontsize=12, fontweight='bold')
            ax4.set_ylabel('Value')
            ax4.grid(alpha=0.3)
        
        # 5. Dataset info
        ax5 = fig.add_subplot(gs[2, :])
        ax5.axis('off')
        
        info_text = f"""
        Dataset Overview
        {'=' * 50}
        
        Dimensions: {self.df.shape[0]:,} rows × {self.df.shape[1]} columns
        Memory Usage: {self.df.memory_usage(deep=True).sum() / (1024**2):.2f} MB
        
        Missing Values: {self.df.isnull().sum().sum():,} ({(self.df.isnull().sum().sum() / self.df.size * 100):.2f}%)
        Duplicates: {dup_count:,} ({(dup_count / len(self.df) * 100):.2f}%)
        
        Numeric Columns: {len(self.df.select_dtypes(include=['number']).columns)}
        Categorical Columns: {len(self.df.select_dtypes(include=['object', 'category']).columns)}
        DateTime Columns: {len(self.df.select_dtypes(include=['datetime64']).columns)}
        """
        
        ax5.text(0.1, 0.5, info_text, fontsize=11, family='monospace',
                verticalalignment='center', transform=ax5.transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        fig.suptitle('Data Quality Dashboard', fontsize=18, fontweight='bold', y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Dashboard saved to: {save_path}")
        
        plt.show()
    
    def plot_before_after_cleaning(self,
                                    cleaned_df: pd.DataFrame,
                                    figsize: Tuple[int, int] = (14, 6),
                                    save_path: Optional[str] = None) -> None:
        """
        Compare the dataset before and after cleaning.
        
        Parameters:
        -----------
        cleaned_df : pd.DataFrame
            The cleaned dataset
        figsize : tuple
            Figure size (width, height)
        save_path : str, optional
            Path to save the figure
        """
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        # Missing values comparison
        before_missing = self.df.isnull().sum().sum()
        after_missing = cleaned_df.isnull().sum().sum()
        
        axes[0].bar(['Before', 'After'], [before_missing, after_missing], 
                   color=['coral', 'lightgreen'])
        axes[0].set_title('Missing Values', fontsize=12, fontweight='bold')
        axes[0].set_ylabel('Count')
        axes[0].grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate([before_missing, after_missing]):
            axes[0].text(i, v, f'{v:,}', ha='center', va='bottom')
        
        # Duplicates comparison
        before_dup = self.df.duplicated().sum()
        after_dup = cleaned_df.duplicated().sum()
        
        axes[1].bar(['Before', 'After'], [before_dup, after_dup],
                   color=['coral', 'lightgreen'])
        axes[1].set_title('Duplicate Rows', fontsize=12, fontweight='bold')
        axes[1].set_ylabel('Count')
        axes[1].grid(axis='y', alpha=0.3)
        
        for i, v in enumerate([before_dup, after_dup]):
            axes[1].text(i, v, f'{v:,}', ha='center', va='bottom')
        
        # Row count comparison
        before_rows = len(self.df)
        after_rows = len(cleaned_df)
        
        axes[2].bar(['Before', 'After'], [before_rows, after_rows],
                   color=['skyblue', 'lightblue'])
        axes[2].set_title('Total Rows', fontsize=12, fontweight='bold')
        axes[2].set_ylabel('Count')
        axes[2].grid(axis='y', alpha=0.3)
        
        for i, v in enumerate([before_rows, after_rows]):
            axes[2].text(i, v, f'{v:,}', ha='center', va='bottom')
        
        fig.suptitle('Before vs After Cleaning Comparison', 
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Comparison plot saved to: {save_path}")
        
        plt.show()
