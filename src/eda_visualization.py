import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Optional

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def generate_visualizations(df: pd.DataFrame, output_dir: Optional[Path] = None) -> List[str]:
    """
    Generate comprehensive EDA visualizations from a DataFrame.
    
    Args:
        df: Input DataFrame to visualize
        output_dir: Directory to save visualization files. If None, uses a default 'visualizations' folder.
    
    Returns:
        List of paths to saved visualization files
    """
    if output_dir is None:
        output_dir = Path(__file__).resolve().parents[1] / "reports" / "visualizations"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    
    try:
        # 1. Correlation Heatmap
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            plt.figure(figsize=(10, 8))
            correlation_matrix = numeric_df.corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                       fmt='.2f', square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
            plt.title('Correlation Heatmap of Numeric Variables', fontsize=14, fontweight='bold')
            plt.tight_layout()
            heatmap_path = output_dir / "01_correlation_heatmap.png"
            plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
            plt.close()
            saved_files.append(str(heatmap_path))
            print(f"✓ Saved correlation heatmap to {heatmap_path}")
        
        # 2. Histograms for numeric columns
        numeric_cols = numeric_df.columns.tolist()
        if numeric_cols:
            n_cols = min(3, len(numeric_cols))
            n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
            if n_rows == 1 and n_cols == 1:
                axes = [axes]
            else:
                axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
            
            for idx, col in enumerate(numeric_cols):
                if idx < len(axes):
                    axes[idx].hist(numeric_df[col].dropna(), bins=30, color='skyblue', edgecolor='black', alpha=0.7)
                    axes[idx].set_title(f'Distribution of {col}', fontweight='bold')
                    axes[idx].set_xlabel(col)
                    axes[idx].set_ylabel('Frequency')
                    axes[idx].grid(True, alpha=0.3)
            
            # Hide unused subplots
            for idx in range(len(numeric_cols), len(axes)):
                axes[idx].set_visible(False)
            
            plt.tight_layout()
            histograms_path = output_dir / "02_histograms.png"
            plt.savefig(histograms_path, dpi=300, bbox_inches='tight')
            plt.close()
            saved_files.append(str(histograms_path))
            print(f"✓ Saved histograms to {histograms_path}")
        
        # 3. Box plots for numeric columns
        if numeric_cols:
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
            if n_rows == 1 and n_cols == 1:
                axes = [axes]
            else:
                axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
            
            for idx, col in enumerate(numeric_cols):
                if idx < len(axes):
                    axes[idx].boxplot(numeric_df[col].dropna(), vert=True)
                    axes[idx].set_title(f'Box Plot of {col}', fontweight='bold')
                    axes[idx].set_ylabel(col)
                    axes[idx].grid(True, alpha=0.3)
            
            # Hide unused subplots
            for idx in range(len(numeric_cols), len(axes)):
                axes[idx].set_visible(False)
            
            plt.tight_layout()
            boxplots_path = output_dir / "03_boxplots.png"
            plt.savefig(boxplots_path, dpi=300, bbox_inches='tight')
            plt.close()
            saved_files.append(str(boxplots_path))
            print(f"✓ Saved box plots to {boxplots_path}")
        
        # 4. Categorical value counts
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            n_cat_cols = min(3, len(categorical_cols))
            n_cat_rows = (len(categorical_cols) + n_cat_cols - 1) // n_cat_cols
            
            fig, axes = plt.subplots(n_cat_rows, n_cat_cols, figsize=(15, 5 * n_cat_rows))
            if n_cat_rows == 1 and n_cat_cols == 1:
                axes = [axes]
            else:
                axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
            
            for idx, col in enumerate(categorical_cols):
                if idx < len(axes):
                    top_categories = df[col].value_counts().head(10)
                    axes[idx].barh(range(len(top_categories)), top_categories.values, color='lightcoral')
                    axes[idx].set_yticks(range(len(top_categories)))
                    axes[idx].set_yticklabels(top_categories.index)
                    axes[idx].set_title(f'Top 10: {col}', fontweight='bold')
                    axes[idx].set_xlabel('Count')
                    axes[idx].grid(True, alpha=0.3, axis='x')
            
            # Hide unused subplots
            for idx in range(len(categorical_cols), len(axes)):
                axes[idx].set_visible(False)
            
            plt.tight_layout()
            categorical_path = output_dir / "04_categorical_distributions.png"
            plt.savefig(categorical_path, dpi=300, bbox_inches='tight')
            plt.close()
            saved_files.append(str(categorical_path))
            print(f"✓ Saved categorical distributions to {categorical_path}")
        
        # 5. Missing data visualization
        plt.figure(figsize=(12, 6))
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            missing_data_pct = (missing_data / len(df)) * 100
            missing_data_pct = missing_data_pct[missing_data_pct > 0].sort_values(ascending=False)
            missing_data_pct.plot(kind='barh', color='orange', edgecolor='black')
            plt.title('Missing Data Percentage by Column', fontsize=14, fontweight='bold')
            plt.xlabel('Percentage Missing (%)')
            plt.grid(True, alpha=0.3, axis='x')
        else:
            plt.text(0.5, 0.5, 'No Missing Data Found', 
                    horizontalalignment='center', verticalalignment='center',
                    fontsize=14, transform=plt.gca().transAxes)
            plt.title('Missing Data Analysis', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        missing_path = output_dir / "05_missing_data.png"
        plt.savefig(missing_path, dpi=300, bbox_inches='tight')
        plt.close()
        saved_files.append(str(missing_path))
        print(f"✓ Saved missing data visualization to {missing_path}")
        
        # 6. Data type distribution
        plt.figure(figsize=(10, 6))
        dtype_counts = df.dtypes.value_counts()
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        plt.pie(dtype_counts.values, labels=[str(dt) for dt in dtype_counts.index], 
               autopct='%1.1f%%', colors=colors, startangle=90)
        plt.title('Data Type Distribution', fontsize=14, fontweight='bold')
        plt.tight_layout()
        dtype_path = output_dir / "06_datatype_distribution.png"
        plt.savefig(dtype_path, dpi=300, bbox_inches='tight')
        plt.close()
        saved_files.append(str(dtype_path))
        print(f"✓ Saved data type distribution to {dtype_path}")
        
        print(f"\n✅ All visualizations saved to: {output_dir}")
        return saved_files
        
    except Exception as e:
        print(f"❌ Error generating visualizations: {str(e)}")
        raise