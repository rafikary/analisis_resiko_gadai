"""
Utility functions for data processing
"""
import pandas as pd
from typing import Optional


def normalize_columns(columns):
    """Normalize column names to lowercase and replace spaces with underscores"""
    return columns.str.lower().str.replace(' ', '_')


def find_column(df: pd.DataFrame, possible_names: list) -> Optional[str]:
    """Find column name from possible variations"""
    for name in possible_names:
        if name in df.columns:
            return name
    return None


def clean_numeric(value):
    """Clean and convert value to numeric"""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return value
    # Remove currency symbols, commas, etc
    if isinstance(value, str):
        cleaned = value.replace('Rp', '').replace('.', '').replace(',', '').strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def clean_datetime(value):
    """Clean and convert value to datetime"""
    if pd.isna(value):
        return None
    try:
        return pd.to_datetime(value)
    except:
        return None


def print_section(title: str, char: str = "="):
    """Print formatted section header"""
    print(f"\n{char * 80}")
    print(f"{title:^80}")
    print(f"{char * 80}\n")


def print_stats(df: pd.DataFrame, title: str = "Dataset Statistics"):
    """Print basic statistics about a dataframe"""
    print_section(title)
    print(f"Total Rows: {len(df):,}")
    print(f"Total Columns: {len(df.columns)}")
    print(f"\nColumn Names:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    print(f"\nMemory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
