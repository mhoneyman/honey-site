"""Fetch and cache benchmark data from multiple sources."""

import requests
import pandas as pd
from pathlib import Path

from .config import MAST_METRICS_URL, BENCHMARKS


def fetch_mast_metrics(cache_path: Path, force_refresh: bool = False) -> pd.DataFrame:
    """
    Download MAST metrics.csv and cache locally.

    Args:
        cache_path: Path to save/load cached CSV
        force_refresh: If True, download even if cache exists

    Returns:
        DataFrame with MAST metrics
    """
    if cache_path.exists() and not force_refresh:
        print(f"Loading cached MAST metrics from {cache_path}")
        return pd.read_csv(cache_path)

    print(f"Downloading MAST metrics from {MAST_METRICS_URL}")
    response = requests.get(MAST_METRICS_URL, timeout=30)
    response.raise_for_status()

    # Save to cache
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(response.text)
    print(f"Cached metrics to {cache_path}")

    return pd.read_csv(cache_path)


def load_release_dates(dates_path: Path) -> pd.DataFrame:
    """
    Load manually curated model release dates.

    Args:
        dates_path: Path to release dates CSV

    Returns:
        DataFrame with model names and release dates
    """
    df = pd.read_csv(dates_path)
    df['release_date'] = pd.to_datetime(df['release_date'])
    return df


def load_benchmark_data(data_dir: Path, benchmark_id: str) -> pd.DataFrame:
    """
    Load data for a specific benchmark.

    Args:
        data_dir: Directory containing benchmark data files
        benchmark_id: ID of the benchmark to load (mast, healthbench, medqa, medhelm)

    Returns:
        DataFrame with benchmark scores and metadata
    """
    if benchmark_id not in BENCHMARKS:
        raise ValueError(f"Unknown benchmark: {benchmark_id}. Available: {list(BENCHMARKS.keys())}")

    benchmark = BENCHMARKS[benchmark_id]
    data_file = data_dir / benchmark['data_file']

    if not data_file.exists():
        raise FileNotFoundError(f"Benchmark data file not found: {data_file}")

    df = pd.read_csv(data_file)

    # Convert release_date to datetime
    if 'release_date' in df.columns:
        df['release_date'] = pd.to_datetime(df['release_date'])

    # Add benchmark metadata
    df['benchmark_id'] = benchmark_id
    df['benchmark_name'] = benchmark['name']

    return df


def load_all_benchmarks(data_dir: Path, release_dates_df: pd.DataFrame = None) -> dict:
    """
    Load all available benchmark data.

    Args:
        data_dir: Directory containing benchmark data files
        release_dates_df: Optional DataFrame with release dates to merge

    Returns:
        Dictionary mapping benchmark_id to DataFrame
    """
    all_data = {}

    for benchmark_id in BENCHMARKS:
        try:
            df = load_benchmark_data(data_dir, benchmark_id)
            print(f"Loaded {len(df)} models for {benchmark_id}")
            all_data[benchmark_id] = df
        except FileNotFoundError as e:
            print(f"Warning: {e}")
            continue

    return all_data


def load_benchmark_metadata(data_dir: Path) -> pd.DataFrame:
    """
    Load benchmark metadata with source attributions.

    Args:
        data_dir: Directory containing metadata file

    Returns:
        DataFrame with benchmark metadata
    """
    metadata_path = data_dir / 'benchmark_metadata.csv'

    if metadata_path.exists():
        return pd.read_csv(metadata_path)

    # Return default metadata from config if file doesn't exist
    rows = []
    for benchmark_id, config in BENCHMARKS.items():
        rows.append({
            'benchmark_id': benchmark_id,
            'benchmark_name': config['name'],
            'source_name': config['source_name'],
            'source_url': config['source_url'],
            'paper_url': config.get('paper_url', ''),
        })

    return pd.DataFrame(rows)
