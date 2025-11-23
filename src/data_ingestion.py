class DataIngestion:
    def __init__(self):
        print('DataIngestion class initialized')

    @classmethod
    def generate_basic_stats(self, csv_data, context=None):
        """
        Generate a comprehensive summary report of any CSV dataset.
        
        :param csv_data: pandas.DataFrame, the input CSV data to analyze
        :param context: optional dict, containing additional analysis parameters or requirements
                       e.g., {'focus_columns': ['col1', 'col2'], 'target_variable': 'target'}
        :return: str, detailed summary report with statistics and insights
        """
        import numpy as np
        
        # Generate basic dataset statistics
        basic_stats = {
            "rows": len(csv_data),
            "columns": len(csv_data.columns),
            "missing_values": csv_data.isnull().sum().to_dict(),
            "dtypes": csv_data.dtypes.to_dict(),
            "memory_usage": csv_data.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
        }
        # Identify numeric and categorical columns
        numeric_cols = csv_data.select_dtypes(include=['int64', 'float64']).columns
        categorical_cols = csv_data.select_dtypes(include=['object', 'category', 'bool']).columns
        datetime_cols = csv_data.select_dtypes(include=['datetime64']).columns
        
        # Generate descriptive statistics for numeric columns
        numeric_stats = {}
        if len(numeric_cols) > 0:
            desc_stats = csv_data[numeric_cols].describe()
            numeric_stats = {
                "basic": desc_stats.to_dict(),
                "skew": csv_data[numeric_cols].skew().to_dict(),
                "kurtosis": csv_data[numeric_cols].kurtosis().to_dict()
            }
            
            # Calculate correlations if there are multiple numeric columns
            if len(numeric_cols) > 1:
                corr_matrix = csv_data[numeric_cols].corr()
                # Get top 5 strongest correlations (excluding self-correlations)
                correlations = []
                for i in range(len(numeric_cols)):
                    for j in range(i + 1, len(numeric_cols)):
                        correlations.append({
                            'col1': numeric_cols[i],
                            'col2': numeric_cols[j],
                            'correlation': corr_matrix.iloc[i, j]
                        })
                correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
                numeric_stats["top_correlations"] = correlations[:5]
        
        # Generate statistics for categorical columns
        categorical_stats = {}
        for col in categorical_cols:
            value_counts = csv_data[col].value_counts()
            unique_count = len(value_counts)
            categorical_stats[col] = {
                "unique_values": unique_count,
                "top_5_values": value_counts.head().to_dict(),
                "null_count": csv_data[col].isnull().sum(),
                "is_binary": unique_count == 2
            }
            if unique_count < 50:  # Only calculate entropy for reasonable cardinality
                probs = value_counts / len(csv_data)
                categorical_stats[col]["entropy"] = -np.sum(probs * np.log2(probs))
        
        # Datetime analysis if present
        datetime_stats = {}
        for col in datetime_cols:
            datetime_stats[col] = {
                "min": csv_data[col].min(),
                "max": csv_data[col].max(),
                "range_days": (csv_data[col].max() - csv_data[col].min()).days,
                "null_count": csv_data[col].isnull().sum()
            }
        
        # Return the computed statistics so callers can use them directly
        return basic_stats, numeric_stats, categorical_stats, datetime_stats
