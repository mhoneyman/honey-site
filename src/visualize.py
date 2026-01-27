"""Create Plotly visualizations for healthcare AI benchmark data."""

import json
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

from .config import PROVIDER_COLORS, CHART_CONFIG, TOP_MODELS_TO_ANNOTATE, HP_THEME, BENCHMARKS


def create_benchmark_chart(df: pd.DataFrame, benchmark_id: str) -> go.Figure:
    """
    Create interactive scatter chart for a specific benchmark.
    Styled to match Health in Progress Substack theme.

    Args:
        df: Prepared chart data with scores, dates, providers
        benchmark_id: ID of the benchmark being visualized

    Returns:
        Plotly Figure object
    """
    benchmark = BENCHMARKS[benchmark_id]

    # Create base scatter plot
    fig = px.scatter(
        df,
        x='release_date',
        y='score',
        color='provider',
        color_discrete_map=PROVIDER_COLORS,
        hover_name='model',
        hover_data={
            'score': ':.3f',
            'release_date': '|%B %d, %Y',
            'provider': True,
        },
        title=benchmark['title'],
    )

    # Update marker styling for dark theme
    fig.update_traces(
        marker=dict(
            size=CHART_CONFIG['marker_size'],
            line=dict(
                width=CHART_CONFIG['marker_line_width'],
                color=HP_THEME['bg_primary']
            )
        )
    )

    # Add error bars for confidence intervals if available
    if 'score_lower' in df.columns and 'score_upper' in df.columns:
        for provider in df['provider'].unique():
            provider_data = df[df['provider'] == provider]
            color = PROVIDER_COLORS.get(provider, PROVIDER_COLORS['Other'])

            fig.add_trace(go.Scatter(
                x=provider_data['release_date'],
                y=provider_data['score'],
                error_y=dict(
                    type='data',
                    symmetric=False,
                    array=provider_data['score_upper'] - provider_data['score'],
                    arrayminus=provider_data['score'] - provider_data['score_lower'],
                    color=color,
                    thickness=1.5,
                    width=4,
                ),
                mode='markers',
                marker=dict(size=0.1, color=color),
                showlegend=False,
                hoverinfo='skip',
            ))

    # Add trendline (line of best fit)
    if len(df) >= 2:
        # Get date range
        date_min = df['release_date'].min()
        date_max = df['release_date'].max()

        # Convert dates to numeric (days from min) for regression
        x_numeric = (df['release_date'] - date_min).dt.days.values
        y_values = df['score'].values

        # Linear regression
        slope, intercept = np.polyfit(x_numeric, y_values, 1)

        # Calculate trend line endpoints (just 2 points for a straight line)
        x_end_days = (date_max - date_min).days
        y_start = intercept
        y_end = slope * x_end_days + intercept

        fig.add_trace(go.Scatter(
            x=[date_min, date_max],
            y=[y_start, y_end],
            mode='lines',
            name='Trendline',
            line=dict(
                color=HP_THEME['accent'],
                width=2.5,
                dash='dash',
            ),
            hovertemplate='Trend: %{y:.3f}<extra></extra>',
        ))

    # Add annotations for top models
    top_models = df.nlargest(TOP_MODELS_TO_ANNOTATE, 'score')
    for _, row in top_models.iterrows():
        fig.add_annotation(
            x=row['release_date'],
            y=row['score'],
            text=row['model'],
            showarrow=True,
            arrowhead=0,
            arrowsize=0.5,
            arrowwidth=1,
            arrowcolor=HP_THEME['text_secondary'],
            ax=0,
            ay=-35,
            font=dict(
                size=CHART_CONFIG['annotation_font_size'],
                color=HP_THEME['text_primary'],
            ),
            bgcolor=HP_THEME['bg_secondary'],
            borderpad=3,
            bordercolor=HP_THEME['grid'],
            borderwidth=1,
        )

    # Apply Health in Progress dark theme
    fig.update_layout(
        plot_bgcolor=HP_THEME['bg_primary'],
        paper_bgcolor=HP_THEME['bg_primary'],
        font=dict(
            family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            size=12,
            color=HP_THEME['text_primary'],
        ),
        title=dict(
            text=benchmark['title'],
            font=dict(size=18, color=HP_THEME['text_primary']),
            x=0.5,
            xanchor='center',
        ),
        xaxis=dict(
            title=dict(
                text=CHART_CONFIG['x_axis_title'],
                font=dict(color=HP_THEME['text_secondary']),
            ),
            showgrid=True,
            gridcolor=HP_THEME['grid'],
            gridwidth=1,
            tickformat='%b %Y',
            dtick='M2',
            tickfont=dict(color=HP_THEME['text_secondary']),
            linecolor=HP_THEME['grid'],
            zerolinecolor=HP_THEME['grid'],
        ),
        yaxis=dict(
            title=dict(
                text=benchmark['y_axis_title'],
                font=dict(color=HP_THEME['text_secondary']),
            ),
            showgrid=True,
            gridcolor=HP_THEME['grid'],
            gridwidth=1,
            range=benchmark['y_axis_range'],
            tickformat='.2f',
            tickfont=dict(color=HP_THEME['text_secondary']),
            linecolor=HP_THEME['grid'],
            zerolinecolor=HP_THEME['grid'],
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            bgcolor=HP_THEME['bg_secondary'],
            bordercolor=HP_THEME['grid'],
            borderwidth=1,
            font=dict(color=HP_THEME['text_primary'], size=11),
        ),
        margin=dict(l=60, r=40, t=100, b=60),
        hoverlabel=dict(
            bgcolor=HP_THEME['bg_secondary'],
            font_size=12,
            font_family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            font_color=HP_THEME['text_primary'],
            bordercolor=HP_THEME['accent'],
        ),
    )

    return fig


def _decode_binary_data(obj):
    """
    Recursively decode Plotly's binary-encoded arrays to regular lists.
    Also converts numpy arrays and Timestamps to JSON-serializable types.
    """
    import base64
    import struct

    if isinstance(obj, dict):
        # Check if this is a binary-encoded array
        if 'dtype' in obj and 'bdata' in obj:
            dtype = obj['dtype']
            bdata = obj['bdata']
            binary = base64.b64decode(bdata)

            # Decode based on dtype
            if dtype == 'f8':  # 64-bit float
                count = len(binary) // 8
                values = struct.unpack('<' + 'd' * count, binary)
                return list(values)
            elif dtype == 'f4':  # 32-bit float
                count = len(binary) // 4
                values = struct.unpack('<' + 'f' * count, binary)
                return list(values)
            elif dtype == 'i4':  # 32-bit int
                count = len(binary) // 4
                values = struct.unpack('<' + 'i' * count, binary)
                return list(values)
            elif dtype == 'i8':  # 64-bit int
                count = len(binary) // 8
                values = struct.unpack('<' + 'q' * count, binary)
                return list(values)
            else:
                # Unknown dtype, return as-is
                return obj
        else:
            return {k: _decode_binary_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_decode_binary_data(item) for item in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        # Handle datetime64 arrays specially - keep as ISO strings
        if np.issubdtype(obj.dtype, np.datetime64):
            return [str(pd.Timestamp(x)) for x in obj]
        return obj.tolist()
    elif hasattr(obj, 'isoformat'):  # Timestamp/datetime
        return obj.isoformat()
    else:
        return obj


def create_tabbed_benchmark_page(benchmark_data: dict, output_dir: Path):
    """
    Create a single HTML page with tabs for each benchmark.

    Args:
        benchmark_data: Dictionary mapping benchmark_id to DataFrame
        output_dir: Directory to save output files
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate figure JSON for each benchmark, decoding binary data
    figures_json = {}
    for benchmark_id, df in benchmark_data.items():
        if len(df) > 0:
            fig = create_benchmark_chart(df, benchmark_id)
            # Get figure dict and decode any binary-encoded arrays
            fig_dict = fig.to_plotly_json()
            decoded = _decode_binary_data(fig_dict)
            figures_json[benchmark_id] = json.dumps(decoded)

    # Build attribution HTML
    attributions = []
    for benchmark_id, config in BENCHMARKS.items():
        if benchmark_id in figures_json:
            attributions.append(f'''
                <div class="attribution" data-benchmark="{benchmark_id}">
                    <strong>{config['full_name']}</strong><br>
                    Source: <a href="{config['source_url']}" target="_blank">{config['source_name']}</a>
                    {f' · <a href="{config["paper_url"]}" target="_blank">Paper</a>' if config.get('paper_url') else ''}
                </div>
            ''')

    # Generate the tabbed HTML page
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Healthcare AI Benchmarks</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{
            width: 100%;
            height: 100%;
            background: {HP_THEME['bg_primary']};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: {HP_THEME['text_primary']};
        }}
        .container {{
            display: flex;
            flex-direction: column;
            height: 100%;
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        #chart {{
            flex: 1;
            min-height: 0;
        }}
        .tabs {{
            display: flex;
            gap: 8px;
            padding: 16px 0;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .tab {{
            padding: 10px 20px;
            background: {HP_THEME['bg_secondary']};
            border: 1px solid {HP_THEME['grid']};
            border-radius: 6px;
            cursor: pointer;
            color: {HP_THEME['text_secondary']};
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        .tab:hover {{
            background: {HP_THEME['grid']};
            color: {HP_THEME['text_primary']};
        }}
        .tab.active {{
            background: {HP_THEME['accent']};
            border-color: {HP_THEME['accent']};
            color: {HP_THEME['bg_primary']};
        }}
        .attributions {{
            padding: 12px 0;
            text-align: center;
            font-size: 12px;
            color: {HP_THEME['text_secondary']};
            border-top: 1px solid {HP_THEME['grid']};
        }}
        .attribution {{
            display: none;
        }}
        .attribution.active {{
            display: block;
        }}
        .attribution a {{
            color: {HP_THEME['accent']};
            text-decoration: none;
        }}
        .attribution a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            padding: 12px 0;
            text-align: center;
            font-size: 11px;
            color: {HP_THEME['text_secondary']};
        }}
        .footer a {{
            color: {HP_THEME['accent']};
            text-decoration: none;
        }}
    </style>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
</head>
<body>
    <div class="container">
        <div id="chart"></div>
        <div class="tabs">
            {''.join(f'<div class="tab{" active" if i == 0 else ""}" data-benchmark="{bid}">{BENCHMARKS[bid]["name"]}</div>' for i, bid in enumerate(figures_json.keys()))}
        </div>
        <div class="attributions">
            {''.join(attributions)}
        </div>
        <div class="footer">
            Data compiled for <a href="https://healthinprogress.substack.com" target="_blank">Health in Progress</a> ·
            Last updated: {pd.Timestamp.now().strftime('%B %Y')}
        </div>
    </div>
    <script>
        // Store all figure data (each value is already valid JSON from Plotly)
        var figures = {{}};
        {chr(10).join(f'        figures["{bid}"] = {fig_json};' for bid, fig_json in figures_json.items())}

        var config = {{
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            responsive: true
        }};

        // Initialize with first benchmark
        var currentBenchmark = '{list(figures_json.keys())[0]}';
        Plotly.newPlot('chart', figures[currentBenchmark].data, figures[currentBenchmark].layout, config);
        document.querySelector('.attribution[data-benchmark="' + currentBenchmark + '"]').classList.add('active');

        // Tab click handlers
        document.querySelectorAll('.tab').forEach(function(tab) {{
            tab.addEventListener('click', function() {{
                var benchmark = this.getAttribute('data-benchmark');

                // Update active tab
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');

                // Update attribution
                document.querySelectorAll('.attribution').forEach(a => a.classList.remove('active'));
                document.querySelector('.attribution[data-benchmark="' + benchmark + '"]').classList.add('active');

                // Update chart
                Plotly.react('chart', figures[benchmark].data, figures[benchmark].layout, config);
                currentBenchmark = benchmark;
            }});
        }});

        // Responsive resize
        window.addEventListener('resize', function() {{
            Plotly.Plots.resize('chart');
        }});
    </script>
</body>
</html>'''

    # Save the tabbed HTML
    output_path = output_dir / 'healthcare_ai_benchmarks.html'
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"Saved tabbed benchmark chart to {output_path}")

    # Also save embeddable version
    embed_path = output_dir / 'healthcare_ai_benchmarks_embed.html'
    with open(embed_path, 'w') as f:
        f.write(html_content)
    print(f"Saved embeddable chart to {embed_path}")

    return output_path


def save_chart(fig: go.Figure, output_dir: Path, base_name: str = 'mast_benchmark_chart'):
    """
    Save chart as HTML (interactive, embeddable) and PNG (static).

    Args:
        fig: Plotly Figure object
        output_dir: Directory to save outputs
        base_name: Base filename without extension
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save interactive HTML (full page version)
    html_path = output_dir / f'{base_name}.html'
    fig.write_html(
        html_path,
        include_plotlyjs='cdn',
        full_html=True,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        }
    )
    print(f"Saved interactive chart to {html_path}")

    # Save static PNG
    png_path = output_dir / f'{base_name}.png'
    fig.write_image(png_path, width=1200, height=700, scale=2)
    print(f"Saved static chart to {png_path}")
