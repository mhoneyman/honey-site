"""Create Plotly visualizations for healthcare AI benchmark data."""

import json
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

from .config import PROVIDER_COLORS, CHART_CONFIG, TOP_MODELS_TO_ANNOTATE, HP_THEME, BENCHMARKS, BENCHMARK_COLORS


def create_benchmark_chart(df: pd.DataFrame, benchmark_id: str, use_dark_theme: bool = True) -> go.Figure:
    """
    Create interactive scatter chart for a specific benchmark.

    Args:
        df: Prepared chart data with scores, dates, providers
        benchmark_id: ID of the benchmark being visualized
        use_dark_theme: If True, use HP_THEME dark colors; if False, use white background

    Returns:
        Plotly Figure object
    """
    benchmark = BENCHMARKS[benchmark_id]

    # Set theme colors
    if use_dark_theme:
        bg_color = HP_THEME['bg_primary']
        bg_secondary = HP_THEME['bg_secondary']
        grid_color = HP_THEME['grid']
        text_color = HP_THEME['text_primary']
        text_secondary = HP_THEME['text_secondary']
        accent_color = HP_THEME['accent']
        marker_line_color = HP_THEME['bg_primary']
    else:
        bg_color = 'white'
        bg_secondary = 'rgba(255, 255, 255, 0.9)'
        grid_color = '#e5e7eb'
        text_color = '#1f2937'
        text_secondary = '#6b7280'
        accent_color = '#f59e0b'  # Amber for trendline
        marker_line_color = 'white'

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

    # Update marker styling
    fig.update_traces(
        marker=dict(
            size=CHART_CONFIG['marker_size'],
            line=dict(
                width=CHART_CONFIG['marker_line_width'],
                color=marker_line_color
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
                color=accent_color,
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
            arrowcolor=text_secondary,
            ax=0,
            ay=-35,
            font=dict(
                size=CHART_CONFIG['annotation_font_size'],
                color=text_color,
            ),
            bgcolor=bg_secondary,
            borderpad=3,
            bordercolor=grid_color,
            borderwidth=1,
        )

    # Apply theme
    fig.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(
            family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            size=12,
            color=text_color,
        ),
        title=dict(
            text=benchmark['title'],
            font=dict(size=18, color=text_color),
            x=0.5,
            xanchor='center',
        ),
        xaxis=dict(
            title=dict(
                text=CHART_CONFIG['x_axis_title'],
                font=dict(color=text_secondary),
            ),
            showgrid=True,
            gridcolor=grid_color,
            gridwidth=1,
            tickformat='%b %Y',
            dtick='M2',
            tickfont=dict(color=text_secondary),
            linecolor=grid_color,
            zerolinecolor=grid_color,
        ),
        yaxis=dict(
            title=dict(
                text=benchmark['y_axis_title'],
                font=dict(color=text_secondary),
            ),
            showgrid=True,
            gridcolor=grid_color,
            gridwidth=1,
            range=benchmark['y_axis_range'],
            tickformat='.2f',
            tickfont=dict(color=text_secondary),
            linecolor=grid_color,
            zerolinecolor=grid_color,
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            bgcolor=bg_secondary,
            bordercolor=grid_color,
            borderwidth=1,
            font=dict(color=text_color, size=11),
        ),
        margin=dict(l=60, r=40, t=100, b=60),
        hoverlabel=dict(
            bgcolor=bg_secondary,
            font_size=12,
            font_family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            font_color=text_color,
            bordercolor=accent_color,
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


def create_tabbed_benchmark_page(benchmark_data: dict, output_dir: Path, use_dark_theme: bool = True):
    """
    Create a single HTML page with tabs for each benchmark.

    Args:
        benchmark_data: Dictionary mapping benchmark_id to DataFrame
        output_dir: Directory to save output files
        use_dark_theme: If True, use HP_THEME dark colors; if False, use white background
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate figure JSON for each benchmark, decoding binary data
    figures_json = {}
    for benchmark_id, df in benchmark_data.items():
        if len(df) > 0:
            fig = create_benchmark_chart(df, benchmark_id, use_dark_theme=use_dark_theme)
            # Get figure dict and decode any binary-encoded arrays
            fig_dict = fig.to_plotly_json()
            decoded = _decode_binary_data(fig_dict)
            figures_json[benchmark_id] = json.dumps(decoded)

    # Set theme colors
    if use_dark_theme:
        bg_primary = HP_THEME['bg_primary']
        bg_secondary = HP_THEME['bg_secondary']
        text_primary = HP_THEME['text_primary']
        text_secondary = HP_THEME['text_secondary']
        grid_color = HP_THEME['grid']
        accent_color = HP_THEME['accent']
    else:
        bg_primary = 'white'
        bg_secondary = '#f9fafb'
        text_primary = '#1f2937'
        text_secondary = '#6b7280'
        grid_color = '#e5e7eb'
        accent_color = '#f59e0b'

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
            background: {bg_primary};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: {text_primary};
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
            margin-bottom: 8px;
        }}
        .tabs {{
            display: flex;
            gap: 8px;
            padding: 20px 0 16px 0;
            flex-wrap: wrap;
            justify-content: center;
            flex-shrink: 0;
        }}
        .tab {{
            padding: 10px 20px;
            background: {bg_secondary};
            border: 1px solid {grid_color};
            border-radius: 6px;
            cursor: pointer;
            color: {text_secondary};
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        .tab:hover {{
            background: {grid_color};
            color: {text_primary};
        }}
        .tab.active {{
            background: {accent_color};
            border-color: {accent_color};
            color: {bg_primary};
        }}
        .attributions {{
            padding: 12px 0;
            text-align: center;
            font-size: 12px;
            color: {text_secondary};
            border-top: 1px solid {grid_color};
        }}
        .attribution {{
            display: none;
        }}
        .attribution.active {{
            display: block;
        }}
        .attribution a {{
            color: {accent_color};
            text-decoration: none;
        }}
        .attribution a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            padding: 12px 0;
            text-align: center;
            font-size: 11px;
            color: {text_secondary};
        }}
        .footer a {{
            color: {accent_color};
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
    theme_suffix = '_dark' if use_dark_theme else '_white'
    output_path = output_dir / f'healthcare_ai_benchmarks{theme_suffix}.html'
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"Saved tabbed benchmark chart to {output_path}")

    # Also save embeddable version
    embed_path = output_dir / f'healthcare_ai_benchmarks{theme_suffix}_embed.html'
    with open(embed_path, 'w') as f:
        f.write(html_content)
    print(f"Saved embeddable chart to {embed_path}")

    return output_path


def create_frontier_chart(frontier_data: dict, use_dark_theme: bool = False) -> go.Figure:
    """
    Create frontier chart showing state-of-the-art progression across benchmarks.

    Args:
        frontier_data: Dictionary mapping benchmark_id to frontier DataFrame
        use_dark_theme: If True, use HP_THEME dark colors; if False, use white background

    Returns:
        Plotly Figure with multi-line frontier chart
    """
    fig = go.Figure()

    # Set theme colors
    if use_dark_theme:
        bg_color = HP_THEME['bg_primary']
        grid_color = HP_THEME['grid']
        text_color = HP_THEME['text_primary']
        text_secondary = HP_THEME['text_secondary']
        marker_line_color = HP_THEME['bg_primary']
        legend_bg = HP_THEME['bg_secondary']
        legend_border = HP_THEME['grid']
    else:
        bg_color = 'white'
        grid_color = '#e5e7eb'
        text_color = '#1f2937'
        text_secondary = '#6b7280'
        marker_line_color = 'white'
        legend_bg = 'rgba(255, 255, 255, 0.9)'
        legend_border = '#d1d5db'

    # Add a line for each benchmark
    for benchmark_id, df in frontier_data.items():
        if len(df) == 0:
            continue

        benchmark_name = BENCHMARKS[benchmark_id]['name']
        color = BENCHMARK_COLORS[benchmark_name]

        # Determine which points to label (first of each model family)
        # Extract base model names by removing suffixes like "mini", "preview", "pro", etc.
        model_families_seen = set()
        show_text = []

        for model_name in df['model']:
            # Extract base family name (e.g., "GPT-4o" from "GPT-4o mini")
            base_name = model_name.split()[0]  # Take first word

            # For models like "Claude 3.5 Sonnet", keep first two words if numeric
            parts = model_name.split()
            if len(parts) > 1 and any(char.isdigit() for char in parts[1]):
                base_name = f"{parts[0]} {parts[1]}"

            # Show label only for first occurrence of each family
            if base_name not in model_families_seen:
                show_text.append(model_name)
                model_families_seen.add(base_name)
            else:
                show_text.append('')  # Empty string = no label

        # Add step line with markers and selective text
        fig.add_trace(go.Scatter(
            x=df['release_date'],
            y=df['score_pct'],
            mode='lines+markers+text',
            name=benchmark_name,
            line=dict(color=color, width=3, shape='hv'),  # Step chart: horizontal then vertical
            marker=dict(
                size=10,
                color=color,
                line=dict(width=2, color=marker_line_color)
            ),
            text=show_text,
            textposition='top center',
            textfont=dict(size=9, color=color),
            customdata=df['model'],  # Store full model name for hover and click
            hovertemplate=(
                '<b>%{customdata}</b><br>' +
                f'{benchmark_name}: %{{y:.1f}}%<br>' +
                'Released: %{x|%b %d, %Y}<br>' +
                '<extra></extra>'
            ),
        ))

    # Update layout
    fig.update_layout(
        title=dict(
            text='Healthcare AI Benchmark Frontiers',
            font=dict(size=20, color=text_color),
            x=0.5,
            xanchor='center',
        ),
        xaxis=dict(
            title=dict(
                text='Release Date',
                font=dict(color=text_secondary),
            ),
            showgrid=True,
            gridcolor=grid_color,
            gridwidth=1,
            tickformat='%b %Y',
            dtick='M3',
            linecolor=grid_color,
            tickfont=dict(color=text_secondary),
        ),
        yaxis=dict(
            title=dict(
                text='Score (%)',
                font=dict(color=text_secondary),
            ),
            showgrid=True,
            gridcolor=grid_color,
            gridwidth=1,
            range=[0, 100],
            ticksuffix='%',
            linecolor=grid_color,
            tickfont=dict(color=text_secondary),
        ),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(
            family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            size=12,
            color=text_color,
        ),
        legend=dict(
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.02,
            bgcolor=legend_bg,
            bordercolor=legend_border,
            borderwidth=1,
            font=dict(size=12, color=text_color),
        ),
        margin=dict(l=60, r=150, t=80, b=60),
        hovermode='closest',
    )

    return fig


def save_chart(fig: go.Figure, output_dir: Path, base_name: str = 'mast_benchmark_chart', enable_click_toggle: bool = False):
    """
    Save chart as HTML (interactive, embeddable) and PNG (static).

    Args:
        fig: Plotly Figure object
        output_dir: Directory to save outputs
        base_name: Base filename without extension
        enable_click_toggle: If True, add JavaScript to toggle labels on click (for frontier charts)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save interactive HTML (full page version)
    html_path = output_dir / f'{base_name}.html'

    if enable_click_toggle:
        # Save with custom HTML including click-to-toggle functionality
        html_string = fig.to_html(
            include_plotlyjs='cdn',
            full_html=True,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            }
        )

        # Add JavaScript for click-to-toggle labels
        toggle_script = """
        <script>
        // Wait for Plotly to be loaded
        setTimeout(function() {
            var plotDiv = document.querySelector('.plotly-graph-div');

            if (plotDiv) {
                plotDiv.on('plotly_click', function(data) {
                    var point = data.points[0];
                    var traceIndex = point.curveNumber;
                    var pointIndex = point.pointIndex;

                    // Get current figure data
                    var currentText = plotDiv.data[traceIndex].text;
                    if (!currentText) return;

                    // Create new text array
                    var newText = Array.isArray(currentText) ? [...currentText] : [currentText];

                    // Toggle label
                    if (newText[pointIndex] === '' || !newText[pointIndex]) {
                        // Show label from customdata
                        newText[pointIndex] = point.customdata;
                    } else {
                        // Hide label
                        newText[pointIndex] = '';
                    }

                    // Update the plot
                    Plotly.restyle(plotDiv, {'text': [newText]}, traceIndex);
                });
            }
        }, 100);
        </script>
        </body>
        """

        html_string = html_string.replace('</body>', toggle_script)

        with open(html_path, 'w') as f:
            f.write(html_string)
    else:
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
