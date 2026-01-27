"""Process and merge MAST benchmark data with release dates."""

import pandas as pd
from pathlib import Path

from .config import FILTER_CONFIG


def filter_mast_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter MAST metrics to Solo Models, Advisor condition, OverallScore.

    Args:
        df: Raw MAST metrics DataFrame

    Returns:
        Filtered DataFrame with relevant rows
    """
    filtered = df[
        (df['Team'] == FILTER_CONFIG['team']) &
        (df['Condition'] == FILTER_CONFIG['condition']) &
        (df['Metric'] == FILTER_CONFIG['metric'])
    ].copy()

    # Normalize column names to lowercase for consistency
    filtered = filtered.rename(columns={
        'Model': 'model',
        'Provider': 'provider',
        'mean': 'score',
        'ci': 'ci_width',
    })

    print(f"Filtered to {len(filtered)} models (Solo Models, Advisor, OverallScore)")
    return filtered


def merge_with_dates(metrics_df: pd.DataFrame, dates_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge MAST metrics with release dates.

    Args:
        metrics_df: Filtered MAST metrics
        dates_df: Model release dates

    Returns:
        Merged DataFrame with scores and dates
    """
    # Merge on model name
    merged = pd.merge(
        metrics_df,
        dates_df,
        on='model',
        how='inner',
        suffixes=('_metrics', '_dates')
    )

    # Handle provider column - prefer dates file, fall back to metrics
    if 'provider_dates' in merged.columns and 'provider_metrics' in merged.columns:
        merged['provider'] = merged['provider_dates'].fillna(merged['provider_metrics'])
        merged = merged.drop(columns=['provider_dates', 'provider_metrics'])

    print(f"Merged {len(merged)} models with release dates")
    return merged


def prepare_chart_data(metrics_df: pd.DataFrame, dates_df: pd.DataFrame) -> pd.DataFrame:
    """
    Full pipeline to prepare data for charting.

    Args:
        metrics_df: Raw MAST metrics
        dates_df: Release dates

    Returns:
        Chart-ready DataFrame
    """
    filtered = filter_mast_metrics(metrics_df)
    merged = merge_with_dates(filtered, dates_df)

    # Sort by score descending for annotation priority
    merged = merged.sort_values('score', ascending=False)

    # Calculate confidence interval bounds from ci_width
    if 'ci_width' in merged.columns:
        merged['score_lower'] = merged['score'] - merged['ci_width']
        merged['score_upper'] = merged['score'] + merged['ci_width']

    return merged
