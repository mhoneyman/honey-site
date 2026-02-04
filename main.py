#!/usr/bin/env python3
"""
Healthcare AI Benchmark Charts - Main entry point.

Generates interactive visualizations of multiple healthcare AI benchmarks:
- MAST (Medical AI Safety and Trust)
- HealthBench (OpenAI)
- MedQA (USMLE)
- MedHELM (Stanford)

Styled to match Health in Progress Substack theme.
"""

from pathlib import Path
import pandas as pd

from src.config import BENCHMARKS, FILTER_CONFIG
from src.fetch_data import fetch_mast_metrics, load_release_dates, load_benchmark_data
from src.process_data import filter_mast_metrics, merge_with_dates, calculate_frontier
from src.visualize import create_benchmark_chart, create_tabbed_benchmark_page, save_chart, create_frontier_chart


def load_mast_data(data_dir: Path) -> pd.DataFrame:
    """Load and process MAST benchmark data."""
    metrics_cache = data_dir / 'metrics.csv'
    dates_file = data_dir / 'model_release_dates.csv'

    # Fetch MAST metrics
    metrics_df = fetch_mast_metrics(metrics_cache)
    dates_df = load_release_dates(dates_file)

    # Filter and merge
    filtered = filter_mast_metrics(metrics_df)
    merged = merge_with_dates(filtered, dates_df)

    # Sort by score
    merged = merged.sort_values('score', ascending=False)

    # Calculate CI bounds if available
    if 'ci_width' in merged.columns:
        merged['score_lower'] = merged['score'] - merged['ci_width']
        merged['score_upper'] = merged['score'] + merged['ci_width']

    return merged


def load_other_benchmark(data_dir: Path, benchmark_id: str) -> pd.DataFrame:
    """Load pre-curated benchmark data."""
    benchmark = BENCHMARKS[benchmark_id]
    data_file = data_dir / benchmark['data_file']

    if not data_file.exists():
        print(f"  Warning: {data_file} not found, skipping {benchmark_id}")
        return pd.DataFrame()

    df = pd.read_csv(data_file)
    df['release_date'] = pd.to_datetime(df['release_date'])

    # Sort by score
    df = df.sort_values('score', ascending=False)

    return df


def main():
    """Run the full healthcare AI benchmark chart generation pipeline."""
    # Define paths
    project_dir = Path(__file__).parent
    data_dir = project_dir / 'data'
    output_dir = project_dir / 'output'

    print("=" * 70)
    print("Healthcare AI Benchmark Chart Generator")
    print("=" * 70)

    # Load all benchmark data
    benchmark_data = {}

    # 1. MAST (live data)
    print("\n[1/4] Loading MAST benchmark data...")
    try:
        mast_df = load_mast_data(data_dir)
        if len(mast_df) > 0:
            benchmark_data['mast'] = mast_df
            print(f"  Loaded {len(mast_df)} models")
    except Exception as e:
        print(f"  Error loading MAST: {e}")

    # 2. HealthBench
    print("\n[2/4] Loading HealthBench data...")
    try:
        healthbench_df = load_other_benchmark(data_dir, 'healthbench')
        if len(healthbench_df) > 0:
            benchmark_data['healthbench'] = healthbench_df
            print(f"  Loaded {len(healthbench_df)} models")
    except Exception as e:
        print(f"  Error loading HealthBench: {e}")

    # 3. MedQA
    print("\n[3/4] Loading MedQA data...")
    try:
        medqa_df = load_other_benchmark(data_dir, 'medqa')
        if len(medqa_df) > 0:
            benchmark_data['medqa'] = medqa_df
            print(f"  Loaded {len(medqa_df)} models")
    except Exception as e:
        print(f"  Error loading MedQA: {e}")

    # 4. MedHELM
    print("\n[4/4] Loading MedHELM data...")
    try:
        medhelm_df = load_other_benchmark(data_dir, 'medhelm')
        if len(medhelm_df) > 0:
            benchmark_data['medhelm'] = medhelm_df
            print(f"  Loaded {len(medhelm_df)} models")
    except Exception as e:
        print(f"  Error loading MedHELM: {e}")

    # Summary
    print("\n" + "-" * 70)
    print("Summary of loaded benchmarks:")
    for bid, df in benchmark_data.items():
        config = BENCHMARKS[bid]
        print(f"  {config['name']:15} {len(df):3} models  Source: {config['source_name']}")

    # Calculate frontiers for each benchmark
    print("\n" + "-" * 70)
    print("Calculating benchmark frontiers...")
    frontier_data = {}
    for bid, df in benchmark_data.items():
        if len(df) > 0:
            benchmark_name = BENCHMARKS[bid]['name']
            frontier_df = calculate_frontier(df, benchmark_name)
            frontier_data[bid] = frontier_df
            print(f"  {benchmark_name:15} {len(frontier_df):2} frontier points")

    # Generate frontier charts (both themes)
    if frontier_data:
        print("\nGenerating frontier charts...")
        print("  - White background version...")
        frontier_fig_white = create_frontier_chart(frontier_data, use_dark_theme=False)
        save_chart(frontier_fig_white, output_dir, 'healthcare_benchmark_frontier_white', enable_click_toggle=True)

        print("  - Dark background version...")
        frontier_fig_dark = create_frontier_chart(frontier_data, use_dark_theme=True)
        save_chart(frontier_fig_dark, output_dir, 'healthcare_benchmark_frontier_dark', enable_click_toggle=True)

    # Generate tabbed charts (both themes)
    print("\n" + "-" * 70)
    print("Generating tabbed benchmark charts...")
    print("  - White background version...")
    create_tabbed_benchmark_page(benchmark_data, output_dir, use_dark_theme=False)
    print("  - Dark background version...")
    create_tabbed_benchmark_page(benchmark_data, output_dir, use_dark_theme=True)

    # Generate individual charts for each benchmark (both themes)
    print("\nGenerating individual benchmark charts...")
    for bid, df in benchmark_data.items():
        if len(df) > 0:
            print(f"  {BENCHMARKS[bid]['name']}:")

            # White background version
            print(f"    - White background...")
            fig_white = create_benchmark_chart(df, bid, use_dark_theme=False)
            save_chart(fig_white, output_dir, f'{bid}_benchmark_chart_white')

            # Dark background version
            print(f"    - Dark background...")
            fig_dark = create_benchmark_chart(df, bid, use_dark_theme=True)
            save_chart(fig_dark, output_dir, f'{bid}_benchmark_chart_dark')

    print("\n" + "=" * 70)
    print("Done! Output files (white background):")
    print(f"  - {output_dir / 'healthcare_benchmark_frontier_white.html'}")
    print(f"  - {output_dir / 'healthcare_benchmark_frontier_white.png'}")
    print(f"  - {output_dir / 'healthcare_ai_benchmarks_white.html'} (tabbed view)")
    for bid in benchmark_data.keys():
        print(f"  - {output_dir / f'{bid}_benchmark_chart_white.html'}")
        print(f"  - {output_dir / f'{bid}_benchmark_chart_white.png'}")

    print("\nOutput files (dark background):")
    print(f"  - {output_dir / 'healthcare_benchmark_frontier_dark.html'}")
    print(f"  - {output_dir / 'healthcare_benchmark_frontier_dark.png'}")
    print(f"  - {output_dir / 'healthcare_ai_benchmarks_dark.html'} (tabbed view)")
    for bid in benchmark_data.keys():
        print(f"  - {output_dir / f'{bid}_benchmark_chart_dark.html'}")
        print(f"  - {output_dir / f'{bid}_benchmark_chart_dark.png'}")
    print("=" * 70)


if __name__ == '__main__':
    main()
