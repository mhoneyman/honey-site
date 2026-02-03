# Healthcare AI Benchmark Frontier Chart

## Overview

The **Frontier Chart** visualizes how state-of-the-art performance has improved over time across four major healthcare AI benchmarks. Each benchmark is represented as a colored line showing only the points where new performance records were set.

## What is a Frontier?

A "frontier" represents the progression of best-known performance over time. The frontier chart answers the question: "What was the best score achievable on each benchmark at any given point in time?"

### Frontier Calculation Algorithm

For each benchmark:
1. Load all model scores with release dates
2. Sort by release date (ascending)
3. Calculate cumulative maximum score at each date
4. Keep only points where a new record was set (score improved)
5. Convert to percentage scale (0-100%)
6. Plot as connected line with markers

## Benchmarks Included

| Benchmark | Color | Description | Metric |
|-----------|-------|-------------|--------|
| **MAST** | Teal (#10A37F) | Medical AI Safety Testing | Overall Score (safety-focused primary care) |
| **HealthBench** | Orange (#D97706) | OpenAI HealthBench | Overall Score (comprehensive healthcare eval) |
| **MedQA** | Blue (#4285F4) | Medical Question Answering | Accuracy (USMLE-style questions) |
| **MedHELM** | Purple (#6366F1) | Medical Holistic Evaluation | Win Rate (holistic medical capability) |

## Current Frontier Points

### MAST (4 frontier points)
- **May 13, 2024**: GPT-4o → 53.6%
- **Jan 20, 2025**: DeepSeek R1 → 58.1%
- **Mar 25, 2025**: Gemini 2.5 Pro → 59.9%
- **Nov 10, 2025**: AMBOSS LiSA 1.0 → 62.3% ⭐ Current SOTA

### HealthBench (5 frontier points)
- **Mar 01, 2023**: GPT-3.5 Turbo → 16.0%
- **Aug 06, 2024**: GPT-4o → 32.0%
- **Dec 05, 2024**: o1 → 42.0%
- **Apr 14, 2025**: GPT-4.1 → 48.0%
- **Apr 16, 2025**: o3 → 60.0% ⭐ Current SOTA

### MedQA (4 frontier points)
- **Apr 09, 2024**: GPT-4 Turbo → 86.7%
- **May 13, 2024**: GPT-4o → 88.7%
- **Sep 12, 2024**: o1-preview → 93.0%
- **Dec 05, 2024**: o1 → 96.5% ⭐ Current SOTA

### MedHELM (4 frontier points)
- **Mar 04, 2024**: Claude 3 Opus → 45.0%
- **May 13, 2024**: GPT-4o → 52.0%
- **Oct 22, 2024**: Claude 3.5 Sonnet → 58.0%
- **Jan 20, 2025**: DeepSeek R1 → 66.0% ⭐ Current SOTA

## Key Insights

1. **MedQA shows highest absolute performance**: Reaching 96.5% accuracy (approaching human expert level on USMLE questions)

2. **HealthBench shows most improvement**: Growing from 16% (Mar 2023) to 60% (Apr 2025) - a 44 percentage point increase

3. **MAST and MedHELM lag behind**: Both still under 70%, suggesting these benchmarks capture harder or more nuanced medical capabilities

4. **GPT-4o was a major milestone**: Set new records on all four benchmarks in May 2024

5. **Specialized models emerging**: AMBOSS LiSA 1.0 (medical-specific) achieves SOTA on MAST despite being newer

## Outputs

The frontier chart is generated in two formats:

- **`healthcare_benchmark_frontier.html`** - Interactive Plotly chart with hover tooltips
- **`healthcare_benchmark_frontier.png`** - Static PNG image (1200x700, 2x scale)

## Technical Details

### Code Structure

- **`src/config.py`**: `BENCHMARK_COLORS` dict mapping benchmark names to colors
- **`src/process_data.py`**: `calculate_frontier()` function for frontier calculation
- **`src/visualize.py`**: `create_frontier_chart()` function for chart generation
- **`main.py`**: Orchestrates loading data → calculating frontiers → generating chart

### Data Sources

All benchmark data is pre-curated in the `data/` directory:
- `metrics.csv` - MAST scores (live from GitHub)
- `healthbench_scores.csv` - HealthBench scores
- `medqa_scores.csv` - MedQA scores
- `medhelm_scores.csv` - MedHELM scores
- `model_release_dates.csv` - Model release dates

### Styling

- Clean white background (suitable for papers and presentations)
- Four distinct colors for easy visual distinction
- Text labels on each point showing model name
- Connected lines showing progression over time
- Legend positioned on right side
- Hover tooltips with full details
