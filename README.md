# Healthcare AI Benchmark Charts

Interactive visualizations of multiple healthcare AI benchmarks, including:

- **MAST** (Medical AI Safety and Trust)
- **HealthBench** (OpenAI)
- **MedQA** (USMLE)
- **MedHELM** (Stanford)

## Features

- **Frontier Chart**: Multi-line visualization showing state-of-the-art progression across all four benchmarks
- Fetches live data from MAST leaderboard
- Loads curated benchmark results from other sources
- Generates interactive Plotly charts with model performance over time
- Exports both HTML (interactive) and PNG (static) formats
- Tabbed view for easy benchmark comparison
- Styled to match Health in Progress Substack theme

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

This will:
1. Fetch/load benchmark data
2. Generate interactive charts
3. Save outputs to the `output/` directory

## Output

- **`healthcare_benchmark_frontier.html`** - **Frontier chart** showing state-of-the-art progression
- **`healthcare_benchmark_frontier.png`** - Static frontier chart image
- `healthcare_ai_benchmarks.html` - Tabbed view of all benchmarks
- Individual benchmark charts as HTML and PNG files

## Project Structure

```
.
├── main.py              # Main entry point
├── requirements.txt     # Python dependencies
├── data/                # Benchmark data files
├── src/                 # Source modules
│   ├── config.py        # Benchmark configurations
│   ├── fetch_data.py    # Data fetching/loading
│   ├── process_data.py  # Data processing
│   └── visualize.py     # Chart generation
└── output/              # Generated charts
```

## License

MIT
