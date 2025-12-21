"""
Core data cleaning functionality for PureData
"""

import pandas as pd
import numpy as np
import json
import subprocess
from pathlib import Path
from difflib import SequenceMatcher
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from scipy import stats


def fuzzy_dedup_group(args):
    """Helper function for parallel fuzzy deduplication within a group."""
    group_df, fuzzy_cols, threshold, global_indices = args
    indices_to_drop_rel = set()
    n = len(group_df)
    for i in range(n):
        if i in indices_to_drop_rel:
            continue
        for j in range(i + 1, n):
            if j in indices_to_drop_rel:
                continue
            sim_scores = []
            for col in fuzzy_cols:
                val_i = group_df.iloc[i][col]
                val_j = group_df.iloc[j][col]
                if pd.notna(val_i) and pd.notna(val_j) and val_i != val_j:
                    sim_scores.append(SequenceMatcher(None, str(val_i), str(val_j)).ratio())
            if sim_scores and np.mean(sim_scores) > threshold:
                indices_to_drop_rel.add(j)
    keep_rel = [i for i in range(n) if i not in indices_to_drop_rel]
    keep_global = [global_indices[i] for i in keep_rel]
    num_dropped = n - len(keep_global)
    return keep_global, num_dropped


def detect_outliers_col(args):
    """Helper function for parallel outlier detection in a single column."""
    col, df, outlier_config = args
    method = outlier_config.get('method', 'iqr')
    params = outlier_config.get('params', {})
    
    if df[col].notna().sum() == 0:
        return col, None
    
    if method == 'iqr':
        multiplier = params.get('multiplier', 1.5)
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0:
            return col, None
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        out_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        out_count = out_mask.sum()
        return col, {
            'method': method,
            'count': out_count,
            'percentage': (out_count / len(df)) * 100,
            'bounds': {'lower': lower_bound, 'upper': upper_bound},
            'multiplier': multiplier
        }
    elif method == 'zscore':
        threshold = params.get('threshold', 3.0)
        mean_val = df[col].mean()
        std_val = df[col].std()
        if std_val == 0:
            return col, None
        z_scores = np.abs((df[col] - mean_val) / std_val)
        out_mask = z_scores > threshold
        out_count = out_mask.sum()
        return col, {
            'method': method,
            'count': out_count,
            'percentage': (out_count / len(df)) * 100,
            'threshold': threshold,
            'mean': mean_val,
            'std': std_val
        }
    else:
        raise ValueError(f"Unsupported outlier method: {method}")


class DataCleaner:
    """A comprehensive data cleaning pipeline for CSV, Excel, and JSON files."""
    
    def __init__(self, file_path, sample_size=None, max_mem_gb=4, num_workers=None):
        """
        Initialize the DataCleaner.
        
        Parameters:
        -----------
        file_path : str or Path
            Path to the data file (CSV, Excel, or JSON)
        sample_size : int, optional
            Maximum number of rows to load (for large datasets)
        max_mem_gb : float, default=4
            Maximum memory in GB to use for loading data
        num_workers : int, optional
            Number of parallel workers (defaults to CPU count)
        """
        self.file_path = Path(file_path)
        self.sample_size = sample_size
        self.max_mem_gb = max_mem_gb
        self.num_workers = num_workers or multiprocessing.cpu_count()
        self.df = None
        self.is_sampled = False
        self.original_size = None
        self.report = {}
        self._load_data()
    
    def _load_data(self):
        """Auto-detect and load data into pandas DataFrame."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        ext = self.file_path.suffix.lower()
        try:
            if ext == '.csv':
                chunk = pd.read_csv(self.file_path, nrows=10000)
                est_rows = self._estimate_total_rows_csv(self.file_path)
                est_mem_gb = (est_rows * chunk.shape[1] * 8) / (1024**3)
                if est_mem_gb > self.max_mem_gb:
                    self.df = pd.read_csv(self.file_path, nrows=self.sample_size or 100000)
                    self.is_sampled = True
                    self.original_size = est_rows
                else:
                    self.df = pd.read_csv(self.file_path)
            elif ext in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.file_path)
                if len(self.df) > (self.sample_size or 100000):
                    self.df = self.df.sample(n=self.sample_size or 100000).reset_index(drop=True)
                    self.is_sampled = True
                    self.original_size = len(self.df)
            elif ext == '.json':
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                self.df = pd.DataFrame(data)
                if len(self.df) > (self.sample_size or 100000):
                    self.df = self.df.sample(n=self.sample_size or 100000).reset_index(drop=True)
                    self.is_sampled = True
                    self.original_size = len(data)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
            
            if self.sample_size and len(self.df) > self.sample_size:
                self.df = self.df.sample(n=self.sample_size).reset_index(drop=True)
                self.is_sampled = True
            
            self.report['original_shape'] = (self.original_size or len(self.df), self.df.shape[1])
            self.report['sampled'] = self.is_sampled
            self.report['loaded_shape'] = self.df.shape
        except Exception as e:
            raise ValueError(f"Error loading file: {e}")
    
    def _estimate_total_rows_csv(self, path):
        """Rough estimate of total rows in CSV."""
        try:
            result = subprocess.run(['wc', '-l', str(path)], capture_output=True, text=True, check=True)
            return int(result.stdout.strip().split()[0]) - 1
        except:
            with open(path, 'r') as f:
                lines = len(f.readlines())
            return lines - 1
    
    def view_as_image(self, rows=None, save_path=None, figsize=None, title=None, 
                      show_index=True, show_dtypes=False):
        """
        Display DataFrame as an image with optional scrollable view.
        
        Parameters:
        -----------
        rows : int or None, default=None
            Number of rows to display:
            - None: Display all rows (full table)
            - Positive int (e.g., 10): Display first N rows
            - Negative int (e.g., -10): Display last N rows
            - 0: Display only column headers
        save_path : str, optional
            Path to save the image. If None, displays interactively.
        figsize : tuple, optional
            Figure size as (width, height). Auto-calculated if None.
        title : str, optional
            Title for the table. Auto-generated if None.
        show_index : bool, default=True
            Whether to show DataFrame index
        show_dtypes : bool, default=False
            Whether to show data types in column headers
        
        Returns:
        --------
        str : Path where image was saved (if save_path provided)
        
        Examples:
        ---------
        # Display full table
        cleaner.view_as_image()
        
        # Display first 10 rows
        cleaner.view_as_image(rows=10)
        
        # Display last 10 rows
        cleaner.view_as_image(rows=-10)
        
        # Save to file
        cleaner.view_as_image(rows=20, save_path='data_preview.png')
        
        # Customize appearance
        cleaner.view_as_image(rows=5, title='Patient Data Sample', 
                             show_dtypes=True, figsize=(15, 8))
        """
        if self.df is None:
            raise ValueError("No data loaded.")
        
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import Rectangle
        import numpy as np
        
        # Determine which rows to display
        if rows is None:
            # Display all rows
            display_df = self.df.copy()
            row_info = f"All {len(self.df)} rows"
        elif rows == 0:
            # Display only headers - create empty display with one dummy row
            display_df = self.df.head(1).copy()
            row_info = "Column headers only"
            headers_only = True
        elif rows > 0:
            # Display first N rows
            display_df = self.df.head(rows)
            row_info = f"First {min(rows, len(self.df))} rows"
            headers_only = False
        else:
            # Display last N rows (negative number)
            display_df = self.df.tail(abs(rows))
            row_info = f"Last {min(abs(rows), len(self.df))} rows"
            headers_only = False
        
        # Prepare data for display
        if show_dtypes:
            # Add data types to column names
            col_headers = [f"{col}\n({self.df[col].dtype})" for col in display_df.columns]
        else:
            col_headers = list(display_df.columns)
        
        # Convert DataFrame to display format
        if show_index:
            # Include index as first column
            index_name = display_df.index.name or 'Index'
            cell_data = []
            for idx, row in display_df.iterrows():
                cell_data.append([str(idx)] + [str(val) for val in row])
            col_headers = [index_name] + col_headers
        else:
            cell_data = [[str(val) for val in row] for row in display_df.values]
        
        # If headers only, clear the cell data but keep structure
        if rows == 0:
            cell_data = []
        
        # Calculate figure size if not provided
        if figsize is None:
            n_rows = len(cell_data) + 1  # +1 for header
            n_cols = len(col_headers)
            
            # Dynamic sizing based on content
            width = max(12, min(n_cols * 1.5, 25))
            height = max(4, min(n_rows * 0.4 + 1, 20))
            figsize = (width, height)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        ax.axis('tight')
        ax.axis('off')
        
        # Generate title
        if title is None:
            title = f"DataFrame Preview - {row_info}\nShape: {self.df.shape[0]} rows × {self.df.shape[1]} columns"
        
        # Create table
        if len(cell_data) > 0:
            # Table with data
            table = ax.table(
                cellText=cell_data,
                colLabels=col_headers,
                cellLoc='left',
                loc='center',
                bbox=[0, 0, 1, 1]
            )
        else:
            # Headers only - create table with empty row
            empty_row = ['' for _ in col_headers]
            table = ax.table(
                cellText=[empty_row],
                colLabels=col_headers,
                cellLoc='left',
                loc='center',
                bbox=[0, 0, 1, 1]
            )
            # Make the empty row invisible
            table[(1, 0)].set_height(0.001)
            for j in range(len(col_headers)):
                table[(1, j)].set_alpha(0)
        
        # Style the table
        table.auto_set_font_size(False)
        
        # Adjust font size based on table size
        if len(cell_data) > 50 or len(col_headers) > 15:
            font_size = 6
        elif len(cell_data) > 20 or len(col_headers) > 10:
            font_size = 8
        else:
            font_size = 9
        
        table.set_fontsize(font_size)
        
        # Style headers
        for i in range(len(col_headers)):
            cell = table[(0, i)]
            cell.set_facecolor('#4472C4')
            cell.set_text_props(weight='bold', color='white')
            cell.set_height(0.05)
        
        # Style data cells with alternating colors
        for i in range(1, len(cell_data) + 1):
            for j in range(len(col_headers)):
                cell = table[(i, j)]
                if i % 2 == 0:
                    cell.set_facecolor('#E7E6E6')
                else:
                    cell.set_facecolor('#F2F2F2')
                cell.set_height(0.04)
        
        # Highlight index column if shown
        if show_index:
            for i in range(len(cell_data) + 1):
                cell = table[(i, 0)]
                current_color = cell.get_facecolor()
                # Darken the color slightly for index
                if i == 0:
                    cell.set_facecolor('#2E5090')
                else:
                    cell.set_facecolor(tuple(max(0, c - 0.1) for c in current_color[:3]) + (1,))
        
        # Add title
        plt.title(title, fontsize=12, fontweight='bold', pad=20)
        
        # Add info footer
        footer_text = f"Total dataset: {self.df.shape[0]} rows × {self.df.shape[1]} columns"
        if rows is not None and rows != 0:
            if rows > 0:
                footer_text += f" | Showing: rows 0-{min(rows, len(self.df))-1}"
            else:
                start_idx = max(0, len(self.df) - abs(rows))
                footer_text += f" | Showing: rows {start_idx}-{len(self.df)-1}"
        
        plt.figtext(0.5, 0.02, footer_text, ha='center', fontsize=8, 
                   style='italic', color='gray')
        
        plt.tight_layout()
        
        # Save or display
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            return save_path
        else:
            plt.show()
            return None
    
    def analyze_correlation(self, col1=None, col2=None, threshold=0.3, method='pearson'):
        """
        Analyze correlation between columns and generate detailed report.
        
        Parameters:
        -----------
        col1 : str, optional
            First column name. If provided with col2, analyzes specific pair.
        col2 : str, optional
            Second column name. If provided with col1, analyzes specific pair.
        threshold : float, default=0.3
            Minimum absolute correlation to report (for all-pairs analysis)
        method : str, default='pearson'
            Correlation method: 'pearson', 'spearman', or 'kendall'
        
        Returns:
        --------
        dict : Correlation analysis report containing:
            - 'correlation_value': float (if specific pair)
            - 'strength': str (weak/moderate/strong/very strong)
            - 'direction': str (positive/negative)
            - 'interpretation': str (detailed explanation)
            - 'all_correlations': list (if analyzing all pairs)
            - 'top_positive': list (strongest positive correlations)
            - 'top_negative': list (strongest negative correlations)
        
        Examples:
        ---------
        # Analyze specific pair
        report = cleaner.analyze_correlation('Age', 'Blood_Pressure')
        
        # Analyze all pairs above threshold
        report = cleaner.analyze_correlation(threshold=0.5)
        
        # Use different method
        report = cleaner.analyze_correlation('Height', 'Weight', method='spearman')
        """
        if self.df is None:
            raise ValueError("No data loaded.")
        
        numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) < 2:
            return {
                'error': 'Need at least 2 numeric columns for correlation analysis',
                'numeric_columns': numeric_cols
            }
        
        # Specific pair analysis
        if col1 is not None and col2 is not None:
            if col1 not in self.df.columns:
                raise ValueError(f"Column '{col1}' not found. Available: {list(self.df.columns)}")
            if col2 not in self.df.columns:
                raise ValueError(f"Column '{col2}' not found. Available: {list(self.df.columns)}")
            
            if col1 not in numeric_cols:
                raise ValueError(f"Column '{col1}' must be numeric. Type: {self.df[col1].dtype}")
            if col2 not in numeric_cols:
                raise ValueError(f"Column '{col2}' must be numeric. Type: {self.df[col2].dtype}")
            
            return self._analyze_pair_correlation(col1, col2, method)
        
        # All-pairs analysis
        return self._analyze_all_correlations(numeric_cols, threshold, method)
    
    def _analyze_pair_correlation(self, col1: str, col2: str, method: str = 'pearson'):
        """Analyze correlation between a specific pair of columns."""
        # Calculate correlation
        valid_data = self.df[[col1, col2]].dropna()
        
        if len(valid_data) < 3:
            return {
                'error': f'Insufficient data for correlation. Only {len(valid_data)} valid pairs.',
                'col1': col1,
                'col2': col2
            }
        
        if method == 'pearson':
            corr = valid_data[col1].corr(valid_data[col2], method='pearson')
        elif method == 'spearman':
            corr = valid_data[col1].corr(valid_data[col2], method='spearman')
        elif method == 'kendall':
            corr = valid_data[col1].corr(valid_data[col2], method='kendall')
        else:
            raise ValueError(f"Invalid method: {method}. Use 'pearson', 'spearman', or 'kendall'")
        
        # Classify strength
        abs_corr = abs(corr)
        if abs_corr < 0.3:
            strength = "Weak"
        elif abs_corr < 0.5:
            strength = "Moderate"
        elif abs_corr < 0.7:
            strength = "Strong"
        else:
            strength = "Very Strong"
        
        # Determine direction
        direction = "Positive" if corr > 0 else "Negative"
        
        # Generate interpretation
        interpretation = self._generate_correlation_interpretation(
            col1, col2, corr, strength, direction, method
        )
        
        # Statistical details
        n = len(valid_data)
        missing = len(self.df) - n
        
        return {
            'col1': col1,
            'col2': col2,
            'correlation_value': round(corr, 4),
            'strength': strength,
            'direction': direction,
            'method': method,
            'interpretation': interpretation,
            'n_samples': n,
            'missing_pairs': missing,
            'summary': f"{strength} {direction.lower()} correlation ({corr:.4f})"
        }
    
    def _analyze_all_correlations(self, numeric_cols: list, threshold: float, method: str):
        """Analyze correlations between all numeric column pairs."""
        # Calculate correlation matrix
        corr_matrix = self.df[numeric_cols].corr(method=method)
        
        all_correlations = []
        
        # Extract all pairs
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                col1 = numeric_cols[i]
                col2 = numeric_cols[j]
                corr = corr_matrix.iloc[i, j]
                
                if abs(corr) >= threshold:
                    abs_corr = abs(corr)
                    if abs_corr < 0.3:
                        strength = "Weak"
                    elif abs_corr < 0.5:
                        strength = "Moderate"
                    elif abs_corr < 0.7:
                        strength = "Strong"
                    else:
                        strength = "Very Strong"
                    
                    all_correlations.append({
                        'col1': col1,
                        'col2': col2,
                        'correlation': round(corr, 4),
                        'strength': strength,
                        'direction': 'Positive' if corr > 0 else 'Negative'
                    })
        
        # Sort by absolute correlation
        all_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        # Get top positive and negative
        positive = [c for c in all_correlations if c['correlation'] > 0]
        negative = [c for c in all_correlations if c['correlation'] < 0]
        
        return {
            'method': method,
            'threshold': threshold,
            'total_pairs': len(all_correlations),
            'all_correlations': all_correlations,
            'top_positive': positive[:5],
            'top_negative': negative[:5],
            'numeric_columns': numeric_cols,
            'summary': self._generate_summary_text(all_correlations, threshold)
        }
    
    def _generate_correlation_interpretation(self, col1: str, col2: str, corr: float, 
                                            strength: str, direction: str, method: str):
        """Generate human-readable interpretation of correlation."""
        interpretation = f"**Correlation Analysis: {col1} vs {col2}**\n\n"
        interpretation += f"**Correlation Coefficient:** {corr:.4f}\n"
        interpretation += f"**Strength:** {strength}\n"
        interpretation += f"**Direction:** {direction}\n"
        interpretation += f"**Method:** {method.capitalize()}\n\n"
        
        interpretation += "**What this means:**\n"
        
        if direction == "Positive":
            interpretation += f"As {col1} increases, {col2} tends to increase as well. "
        else:
            interpretation += f"As {col1} increases, {col2} tends to decrease. "
        
        if strength == "Very Strong":
            interpretation += "This is a very strong relationship - the two variables move together very consistently.\n"
        elif strength == "Strong":
            interpretation += "This is a strong relationship - the two variables show a clear tendency to move together.\n"
        elif strength == "Moderate":
            interpretation += "This is a moderate relationship - there's a noticeable tendency but also considerable variation.\n"
        else:
            interpretation += "This is a weak relationship - the two variables have little tendency to move together.\n"
        
        interpretation += f"\n**Practical interpretation:**\n"
        if abs(corr) > 0.7:
            interpretation += f"- {col1} and {col2} are highly related and may provide redundant information.\n"
            interpretation += f"- In predictive models, you might consider using only one of these variables.\n"
            interpretation += f"- Changes in one variable are strongly associated with changes in the other.\n"
        elif abs(corr) > 0.5:
            interpretation += f"- {col1} and {col2} have a notable relationship worth investigating.\n"
            interpretation += f"- They share significant information but also have independent variation.\n"
            interpretation += f"- Both variables may be useful in analysis, providing complementary insights.\n"
        elif abs(corr) > 0.3:
            interpretation += f"- {col1} and {col2} show a moderate association.\n"
            interpretation += f"- They are somewhat related but largely independent.\n"
            interpretation += f"- Both variables provide mostly unique information.\n"
        else:
            interpretation += f"- {col1} and {col2} show little linear relationship.\n"
            interpretation += f"- They appear to be largely independent variables.\n"
            interpretation += f"- Each provides unique, non-overlapping information.\n"
        
        interpretation += f"\n**Statistical notes:**\n"
        interpretation += f"- Correlation does not imply causation\n"
        interpretation += f"- {method.capitalize()} correlation measures linear relationships\n"
        if method == 'pearson':
            interpretation += f"- Sensitive to outliers and assumes normal distribution\n"
        elif method == 'spearman':
            interpretation += f"- Ranks-based, robust to outliers and non-linear monotonic relationships\n"
        else:
            interpretation += f"- Ranks-based, measures ordinal association\n"
        
        return interpretation
    
    def _generate_summary_text(self, correlations: list, threshold: float):
        """Generate summary text for all-pairs correlation analysis."""
        if not correlations:
            return f"No correlations found above threshold of {threshold}"
        
        summary = f"Found {len(correlations)} correlation pairs above threshold ({threshold}).\n\n"
        
        very_strong = [c for c in correlations if abs(c['correlation']) >= 0.7]
        strong = [c for c in correlations if 0.5 <= abs(c['correlation']) < 0.7]
        moderate = [c for c in correlations if 0.3 <= abs(c['correlation']) < 0.5]
        
        summary += f"Breakdown:\n"
        summary += f"- Very Strong (|r| ≥ 0.7): {len(very_strong)}\n"
        summary += f"- Strong (0.5 ≤ |r| < 0.7): {len(strong)}\n"
        summary += f"- Moderate (0.3 ≤ |r| < 0.5): {len(moderate)}\n"
        
        return summary
    
    def drop_columns(self, *columns):
        """
        Drop one or more columns from the dataset.
        
        Parameters:
        -----------
        *columns : str or int
            Column names (str) or column indices (int, 0-based) to drop.
            Can pass multiple columns as separate arguments.
        
        Returns:
        --------
        list : Names of columns that were dropped
        
        Examples:
        ---------
        # Drop by column name
        cleaner.drop_columns('Age', 'Gender')
        
        # Drop by index (0-based)
        cleaner.drop_columns(0, 2)  # drops first and third columns
        
        # Mix names and indices
        cleaner.drop_columns('Age', 2, 'Gender')
        
        Raises:
        -------
        ValueError : If column doesn't exist or index is out of range
        """
        if self.df is None:
            raise ValueError("No data loaded.")
        
        if not columns:
            raise ValueError("No columns specified to drop.")
        
        # Convert all arguments to column names
        cols_to_drop = []
        for col in columns:
            if isinstance(col, int):
                # Handle integer index (0-based)
                if col < 0 or col >= len(self.df.columns):
                    raise ValueError(f"Column index {col} is out of range. Valid range: 0-{len(self.df.columns)-1}")
                cols_to_drop.append(self.df.columns[col])
            elif isinstance(col, str):
                # Handle column name
                if col not in self.df.columns:
                    raise ValueError(f"Column '{col}' does not exist. Available columns: {list(self.df.columns)}")
                cols_to_drop.append(col)
            else:
                raise ValueError(f"Invalid column specifier: {col}. Must be str (name) or int (index).")
        
        # Remove duplicates while preserving order
        cols_to_drop = list(dict.fromkeys(cols_to_drop))
        
        # Drop the columns
        self.df = self.df.drop(columns=cols_to_drop)
        
        # Update report
        if 'columns_dropped' not in self.report:
            self.report['columns_dropped'] = []
        self.report['columns_dropped'].extend(cols_to_drop)
        
        return cols_to_drop
    
    def profile(self, sample_frac=0.1, outlier_config=None):
        """
        Generate data profiling report.
        
        Parameters:
        -----------
        sample_frac : float, default=0.1
            Fraction of data to use for profiling (if dataset is large)
        outlier_config : dict, optional
            Configuration for outlier detection
            Example: {'method': 'iqr', 'params': {'multiplier': 1.5}}
        
        Returns:
        --------
        dict : Profiling report containing missing values, types, outliers, and statistics
        """
        if self.df is None:
            raise ValueError("No data loaded.")
        
        df_profile = self.df
        if len(df_profile) > 10000:
            df_profile = df_profile.sample(frac=sample_frac).reset_index(drop=True)
        
        missing = df_profile.isnull().sum() / len(df_profile) * 100
        
        type_info = {}
        for col in df_profile.columns:
            inferred_type = str(df_profile[col].dtype)
            nunique = df_profile[col].nunique()
            type_info[col] = {
                'dtype': inferred_type,
                'nunique': nunique,
                'is_categorical': (inferred_type == 'object' and nunique < 50)
            }
        
        outlier_info = {}
        numeric_cols = df_profile.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols and outlier_config:
            with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
                args_list = [(col, df_profile, outlier_config) for col in numeric_cols]
                futures = {executor.submit(detect_outliers_col, args): args[0] for args in args_list}
                for future in as_completed(futures):
                    col, result = future.result()
                    if result is not None:
                        outlier_info[col] = result
        
        stats_info = {}
        for col in numeric_cols:
            stats_info[col] = {
                'mean': df_profile[col].mean(),
                'median': df_profile[col].median(),
                'std': df_profile[col].std(),
                'min': df_profile[col].min(),
                'max': df_profile[col].max()
            }
        
        duplicates_count = df_profile.duplicated().sum()
        duplicates_pct = (duplicates_count / len(df_profile)) * 100
        
        self.report['profiling'] = {
            'missing_values': missing.to_dict(),
            'type_info': type_info,
            'outlier_info': outlier_info,
            'stats': stats_info,
            'duplicates': {'count': duplicates_count, 'percentage': duplicates_pct},
            'profiled_on_sample': len(df_profile) < len(self.df)
        }
        return self.report['profiling']
    
    def clean(self, config):
        """
        Clean data based on configuration.
        
        Parameters:
        -----------
        config : dict
            Cleaning configuration dictionary
            
        Example config:
        {
            'missing': {
                'strategy': 'median',  # 'drop', 'mean', 'median', 'mode', 'constant'
                'columns': ['col1', 'col2'],  # optional
                'fill_value': 'Unknown'  # for 'constant' strategy
            },
            'outliers': {
                'method': 'iqr',  # 'iqr' or 'zscore'
                'params': {'multiplier': 1.5},  # or {'threshold': 3.0} for zscore
                'action': 'drop_rows',  # 'drop_rows' or 'cap'
                'columns': ['col1', 'col2']  # optional
            },
            'duplicates': {
                'drop': True,
                'subset': ['col1', 'col2']  # optional
            }
        }
        
        Returns:
        --------
        list : List of cleaning changes applied
        """
        if self.df is None:
            raise ValueError("No data loaded.")
        
        changes = []
        outlier_config = config.get('outliers', {})
        missing_config = config.get('missing', {})
        
        # Handle missing values
        if 'missing' in config:
            strategy = config['missing'].get('strategy', 'drop')
            columns = config['missing'].get('columns', None)
            if columns is None:
                if strategy in ['mean', 'median']:
                    columns = self.df.select_dtypes(include=['number']).columns.tolist()
                else:
                    columns = self.df.columns.tolist()
            elif not isinstance(columns, list):
                columns = [columns]
            
            if strategy == 'drop':
                before = len(self.df)
                self.df.dropna(subset=columns, inplace=True)
                after = len(self.df)
                changes.append(f"Dropped {before - after} rows with missing values in {columns}.")
            elif strategy in ['mean', 'median', 'mode', 'constant']:
                for col in columns:
                    if col not in self.df.columns:
                        continue
                    missing_count = self.df[col].isnull().sum()
                    if missing_count == 0:
                        continue
                    
                    if strategy == 'mean' and pd.api.types.is_numeric_dtype(self.df[col]):
                        fill_val = self.df[col].mean()
                    elif strategy == 'median' and pd.api.types.is_numeric_dtype(self.df[col]):
                        fill_val = self.df[col].median()
                    elif strategy == 'mode':
                        fill_val = self.df[col].mode()[0] if not self.df[col].mode().empty else np.nan
                    elif strategy == 'constant':
                        fill_val = config['missing'].get('fill_value', 'Unknown')
                    else:
                        continue
                    
                    self.df[col].fillna(fill_val, inplace=True)
                    changes.append(f"Imputed {missing_count} missing values in '{col}' with {strategy}.")
        
        # Drop duplicates
        if 'duplicates' in config and config['duplicates'].get('drop', False):
            before = len(self.df)
            subset = config['duplicates'].get('subset', None)
            self.df.drop_duplicates(subset=subset, keep='first', inplace=True)
            after = len(self.df)
            changes.append(f"Dropped {before - after} exact duplicate rows.")
        
        # Remove outliers
        if 'outliers' in config:
            out_cfg = config['outliers']
            method = out_cfg.get('method', 'iqr')
            params = out_cfg.get('params', {})
            action = out_cfg.get('action', 'drop_rows')
            columns = out_cfg.get('columns', self.df.select_dtypes(include=['number']).columns.tolist())
            
            outlier_config_obj = {'method': method, 'params': params}
            outlier_mask_overall = pd.Series([False] * len(self.df), index=self.df.index)
            
            with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
                args_list = [(col, self.df, outlier_config_obj) for col in columns if col in self.df.columns]
                futures = {executor.submit(detect_outliers_col, args): args[0] for args in args_list}
                for future in as_completed(futures):
                    col, result = future.result()
                    if result is None:
                        continue
                    
                    if method == 'iqr':
                        lb = result['bounds']['lower']
                        ub = result['bounds']['upper']
                        col_mask = (self.df[col] < lb) | (self.df[col] > ub)
                    elif method == 'zscore':
                        mean_val = result['mean']
                        std_val = result['std']
                        threshold = result['threshold']
                        z_scores = np.abs((self.df[col] - mean_val) / std_val)
                        col_mask = z_scores > threshold
                    else:
                        continue
                    
                    if action == 'drop_rows':
                        outlier_mask_overall |= col_mask
                    elif action == 'cap':
                        if method == 'iqr':
                            self.df.loc[self.df[col] < lb, col] = lb
                            self.df.loc[self.df[col] > ub, col] = ub
                            changes.append(f"Capped outliers in '{col}'.")
            
            if action == 'drop_rows':
                before = len(self.df)
                self.df = self.df[~outlier_mask_overall].reset_index(drop=True)
                after = len(self.df)
                changes.append(f"Removed {before - after} rows with outliers ({method} method).")
        
        # Standardize column names
        original_cols = list(self.df.columns)
        self.df.columns = self.df.columns.str.strip().str.replace(r'[^\w\s]', '_', regex=True).str.lower().str.replace(r'\s+', '_', regex=True)
        changes.append(f"Standardized column names.")
        
        self.report['cleaning_changes'] = changes
        self.report['cleaned_shape'] = self.df.shape
        self.report['outlier_config'] = outlier_config
        self.report['missing_config'] = missing_config
        return changes
    
    def export(self, output_path=None, fmt='csv'):
        """
        Export cleaned data and report.
        
        Parameters:
        -----------
        output_path : str or Path, optional
            Path where to save the cleaned data. If not provided, saves to 
            './puredata_output/' directory with auto-generated filename.
        fmt : str, default='csv'
            Output format ('csv', 'xlsx', or 'json')
        
        Returns:
        --------
        tuple : (data_path, report_path)
        """
        if self.df is None:
            raise ValueError("No data to export.")
        
        # If no output path specified, use default directory
        if output_path is None:
            # Create default output directory
            default_dir = Path('./puredata_output')
            default_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = self.file_path.stem if self.file_path else 'cleaned_data'
            output_path = default_dir / f"{base_name}_cleaned_{timestamp}.{fmt}"
        else:
            output_path = Path(output_path)
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add extension if not present
        if output_path.suffix == '' and '.' not in str(output_path):
            output_path = output_path.with_suffix(f'.{fmt}')
        
        # Export data in specified format
        if fmt == 'csv':
            self.df.to_csv(output_path, index=False)
        elif fmt in ['xlsx', 'xls']:
            self.df.to_excel(output_path, index=False)
        elif fmt == 'json':
            self.df.to_json(output_path, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported export format: {fmt}")
        
        # Save report
        report_path = output_path.parent / f"{output_path.stem}_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2, default=str)
        
        return output_path, report_path
    
    def save(self, path=None, fmt='csv', include_report=True):
        """
        Convenient method to save cleaned data.
        Alias for export() with simpler interface.
        
        Parameters:
        -----------
        path : str or Path, optional
            Where to save. If None, saves to './puredata_output/' with auto-generated name
        fmt : str, default='csv'
            Format: 'csv', 'xlsx', or 'json'
        include_report : bool, default=True
            Whether to save the cleaning report as JSON
        
        Returns:
        --------
        str or tuple : 
            If include_report=True: (data_path, report_path)
            If include_report=False: data_path only
        
        Examples:
        ---------
        >>> cleaner.save()  # Saves to ./puredata_output/data_cleaned_20240101_120000.csv
        >>> cleaner.save('my_clean_data.csv')  # Saves to specified path
        >>> cleaner.save('output/data.xlsx', fmt='xlsx')  # Saves as Excel
        >>> cleaner.save(include_report=False)  # Only save data, no report
        """
        data_path, report_path = self.export(path, fmt)
        
        if not include_report:
            # Remove the report file if user doesn't want it
            if report_path.exists():
                report_path.unlink()
            return str(data_path)
        
        return str(data_path), str(report_path)
    
    def get_dataframe(self):
        """
        Get the cleaned DataFrame.
        
        Returns:
        --------
        pd.DataFrame : The cleaned data
        """
        return self.df
    
    def get_report(self):
        """
        Get the cleaning report.
        
        Returns:
        --------
        dict : The cleaning report
        """
        return self.report
    
    def explain_cleaning(self, detail_level: str = 'detailed') -> str:
        """
        Get AI-powered explanation of the cleaning process.
        
        Parameters:
        -----------
        detail_level : str
            'short' or 'detailed' explanation
        
        Returns:
        --------
        str : Explanation of cleaning operations
        """
        from .explainer import CleaningExplainer
        
        if 'cleaning_changes' not in self.report:
            return "No cleaning operations have been performed yet. Run clean() first."
        
        explainer = CleaningExplainer()
        
        # Get the config used for cleaning
        config = {}
        if 'missing_config' in self.report:
            config['missing'] = self.report['missing_config']
        if 'outlier_config' in self.report:
            config['outliers'] = self.report['outlier_config']
        if 'duplicates' in self.report.get('profiling', {}):
            config['duplicates'] = {'drop': True}
        
        return explainer.explain_cleaning_report(
            self.report['cleaning_changes'],
            config,
            detail_level
        )
    
    def describe_data(self, detail_level: int = 0) -> str:
        """
        Get AI-powered description of the dataset.
        
        Parameters:
        -----------
        detail_level : int
            0 = short summary
            1 = detailed analysis
        
        Returns:
        --------
        str : Dataset description
        """
        from .describer import DataDescriber
        
        if self.df is None:
            return "No data loaded."
        
        describer = DataDescriber(self.df)
        return describer.describe(detail_level)
    
    def get_recommendations(self) -> str:
        """
        Get AI-powered recommendations for data cleaning.
        
        Returns:
        --------
        str : Cleaning recommendations
        """
        from .explainer import CleaningExplainer
        
        if 'profiling' not in self.report:
            # Profile first if not done
            self.profile()
        
        explainer = CleaningExplainer()
        return explainer.get_recommendation(self.report['profiling'])
    
    def visualize(self, plot_type: str = 'overview', **kwargs):
        """
        Create visualizations of the data.
        
        Parameters:
        -----------
        plot_type : str
            Type of plot: 'overview', 'missing', 'distribution', 
            'correlation', 'outliers', 'categorical'
        **kwargs : additional arguments
            save_path : str, path to save the plot
            columns : list, specific columns to plot
            figsize : tuple, figure size
        
        Returns:
        --------
        None (displays plot)
        """
        from .visualizer import DataVisualizer
        
        if self.df is None:
            print("No data loaded.")
            return
        
        viz = DataVisualizer(self.df)
        
        if plot_type == 'overview':
            viz.plot_data_overview(save_path=kwargs.get('save_path'))
        elif plot_type == 'missing':
            viz.plot_missing_values(
                figsize=kwargs.get('figsize', (12, 6)),
                save_path=kwargs.get('save_path')
            )
        elif plot_type == 'distribution':
            viz.plot_distribution(
                columns=kwargs.get('columns'),
                figsize=kwargs.get('figsize', (15, 10)),
                save_path=kwargs.get('save_path')
            )
        elif plot_type == 'correlation':
            viz.plot_correlation_matrix(
                figsize=kwargs.get('figsize', (12, 10)),
                save_path=kwargs.get('save_path')
            )
        elif plot_type == 'outliers':
            viz.plot_outliers_boxplot(
                columns=kwargs.get('columns'),
                figsize=kwargs.get('figsize', (15, 8)),
                save_path=kwargs.get('save_path')
            )
        elif plot_type == 'categorical':
            viz.plot_categorical_distribution(
                columns=kwargs.get('columns'),
                top_n=kwargs.get('top_n', 10),
                figsize=kwargs.get('figsize', (15, 10)),
                save_path=kwargs.get('save_path')
            )
        else:
            print(f"Unknown plot type: {plot_type}")
            print("Available types: overview, missing, distribution, correlation, outliers, categorical")
    
    def compare_before_after(self, cleaned_df, save_path: str = None):
        """
        Visualize comparison between original and cleaned data.
        
        Parameters:
        -----------
        cleaned_df : pd.DataFrame
            The cleaned dataset
        save_path : str, optional
            Path to save the comparison plot
        """
        from .visualizer import DataVisualizer
        
        viz = DataVisualizer(self.df)
        viz.plot_before_after_cleaning(cleaned_df, save_path=save_path)
