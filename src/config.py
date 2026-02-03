"""Configuration constants for healthcare AI benchmark charts."""

# Health in Progress Substack theme
HP_THEME = {
    "bg_primary": "#1b142f",      # Deep dark purple
    "bg_secondary": "#29223b",    # Lighter purple for cards
    "accent": "#c8916e",          # Warm tan/bronze
    "text_primary": "#ffffff",    # White text
    "text_secondary": "#a8a3b3",  # Muted text
    "grid": "#3d3650",            # Subtle grid lines
}

# Provider color palette (adjusted for dark background)
PROVIDER_COLORS = {
    "OpenAI": "#34d399",       # Bright green (OpenAI)
    "Anthropic": "#fb923c",    # Bright orange (Anthropic)
    "Google": "#60a5fa",       # Bright blue (Google)
    "Meta": "#38bdf8",         # Sky blue (Meta)
    "DeepSeek": "#a78bfa",     # Light purple (DeepSeek)
    "AMBOSS": "#f87171",       # Bright red (AMBOSS)
    "Glass Health": "#4ade80", # Bright teal (Glass Health)
    "Moonshot AI": "#c4b5fd",  # Lavender (Moonshot AI)
    "Mistral AI": "#fbbf24",   # Bright amber (Mistral)
    "xAI": "#94a3b8",          # Light gray (xAI)
    "Other": "#9ca3af",        # Default gray
}

# Benchmark-specific configurations
BENCHMARKS = {
    "mast": {
        "id": "mast",
        "name": "MAST",
        "full_name": "Medical AI Safety and Trust",
        "title": "MAST Benchmark: Overall Scores vs Release Date",
        "y_axis_title": "Overall Score",
        "y_axis_range": [0.45, 0.65],
        "score_format": ".3f",
        "data_file": "metrics.csv",
        "source_name": "HealthRex Stanford",
        "source_url": "https://github.com/HealthRex/mast",
        "paper_url": "https://arxiv.org/abs/2412.03389",
    },
    "healthbench": {
        "id": "healthbench",
        "name": "HealthBench",
        "full_name": "OpenAI HealthBench",
        "title": "HealthBench: Overall Scores vs Release Date",
        "y_axis_title": "Overall Score",
        "y_axis_range": [0.1, 0.7],
        "score_format": ".2f",
        "data_file": "healthbench_scores.csv",
        "source_name": "OpenAI",
        "source_url": "https://openai.com/index/healthbench/",
        "paper_url": "https://arxiv.org/abs/2505.08775",
    },
    "medqa": {
        "id": "medqa",
        "name": "MedQA",
        "full_name": "MedQA (USMLE)",
        "title": "MedQA Benchmark: Accuracy vs Release Date",
        "y_axis_title": "Accuracy",
        "y_axis_range": [0.80, 1.0],
        "score_format": ".1%",
        "data_file": "medqa_scores.csv",
        "source_name": "Vals.ai",
        "source_url": "https://www.vals.ai/benchmarks/medqa",
        "paper_url": "https://arxiv.org/abs/2009.13081",
    },
    "medhelm": {
        "id": "medhelm",
        "name": "MedHELM",
        "full_name": "Stanford MedHELM",
        "title": "MedHELM Benchmark: Win Rate vs Release Date",
        "y_axis_title": "Win Rate",
        "y_axis_range": [0.3, 0.75],
        "score_format": ".0%",
        "data_file": "medhelm_scores.csv",
        "source_name": "Stanford CRFM",
        "source_url": "https://crfm.stanford.edu/helm/medhelm/latest/",
        "paper_url": "https://arxiv.org/abs/2505.23802",
    },
}

# Default benchmark
DEFAULT_BENCHMARK = "mast"

# Benchmark colors for frontier chart
BENCHMARK_COLORS = {
    'MAST': '#10A37F',        # Teal
    'HealthBench': '#D97706',  # Orange
    'MedQA': '#4285F4',        # Blue
    'MedHELM': '#6366F1'       # Purple
}

# Chart styling (shared across all benchmarks)
CHART_CONFIG = {
    "x_axis_title": "Model Release Date",
    "marker_size": 14,
    "marker_line_width": 2,
    "annotation_font_size": 11,
}

# Data source for MAST (live data)
MAST_METRICS_URL = "https://raw.githubusercontent.com/HealthRex/mast/main/leaderboards/harmdash/data/metrics.csv"

# Filter criteria for MAST data (column names match MAST CSV)
FILTER_CONFIG = {
    "team": "Solo Models",      # Column: Team
    "condition": "Advisor",     # Column: Condition
    "metric": "OverallScore",   # Column: Metric
}

# Models to annotate on chart (top performers)
TOP_MODELS_TO_ANNOTATE = 5
