from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_metric_chart(
    metric_data: List[Dict[str, Any]],
    metric_type: str,
    time_range: str = "Last 30 days",
) -> go.Figure:
    """
    Create an interactive chart for health metrics.

    Args:
        metric_data: List of metric records
        metric_type: Type of metric being visualized
        time_range: Time range for the chart

    Returns:
        plotly.graph_objects.Figure: Interactive chart
    """
    if not metric_data:
        # Return empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(title=f"{metric_type} - No Data Available")
        return fig

    # Convert to DataFrame
    df = pd.DataFrame(metric_data)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Get unit for labeling
    unit = df["unit"].iloc[0] if "unit" in df.columns and not df["unit"].isna().all() else ""

    # Create line chart with markers
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["value"],
            mode="lines+markers",
            name=metric_type,
            line=dict(width=3, color="#2E8B57"),
            marker=dict(size=8, color="#2E8B57"),
            hovertemplate="<b>%{fullData.name}</b><br>" + "Date: %{x}<br>" + "Value: %{y} " + unit + "<extra></extra>",
        )
    )

    # Add trend line if enough data points
    if len(df) > 2:
        # Simple linear trend
        import numpy as np

        x_numeric = np.arange(len(df))
        z = np.polyfit(x_numeric, df["value"], 1)
        p = np.poly1d(z)

        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=p(x_numeric),
                mode="lines",
                name="Trend",
                line=dict(width=2, color="rgba(46, 139, 87, 0.4)", dash="dash"),
                hoverinfo="skip",
            )
        )

    # Update layout
    fig.update_layout(
        title=f"{metric_type} Over Time",
        xaxis_title="Date",
        yaxis_title=f"{metric_type} ({unit})" if unit else metric_type,
        hovermode="x unified",
        showlegend=len(df) > 2,  # Show legend only if trend line exists
        template="plotly_white",
        height=400,
    )

    return fig


def create_metric_comparison_chart(patients_data: Dict[str, List[Dict[str, Any]]], metric_type: str) -> go.Figure:
    """
    Create a comparison chart for multiple patients.

    Args:
        patients_data: Dictionary with patient names as keys and metric data as values
        metric_type: Type of metric being compared

    Returns:
        plotly.graph_objects.Figure: Comparison chart
    """
    if not patients_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for comparison",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(title=f"{metric_type} Comparison - No Data Available")
        return fig

    fig = go.Figure()

    colors = px.colors.qualitative.Set1

    for i, (patient_name, data) in enumerate(patients_data.items()):
        if data:
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")

            unit = df["unit"].iloc[0] if "unit" in df.columns and not df["unit"].isna().all() else ""

            fig.add_trace(
                go.Scatter(
                    x=df["date"],
                    y=df["value"],
                    mode="lines+markers",
                    name=patient_name,
                    line=dict(width=2, color=colors[i % len(colors)]),
                    marker=dict(size=6),
                    hovertemplate="<b>%{fullData.name}</b><br>"
                    + "Date: %{x}<br>"
                    + "Value: %{y} "
                    + unit
                    + "<extra></extra>",
                )
            )

    fig.update_layout(
        title=f"{metric_type} Comparison Across Patients",
        xaxis_title="Date",
        yaxis_title=f"{metric_type}",
        hovermode="x unified",
        showlegend=True,
        template="plotly_white",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def create_patient_overview_chart(patient_metrics: List[Dict[str, Any]]) -> go.Figure:
    """
    Create an overview chart showing multiple metrics for a single patient.

    Args:
        patient_metrics: List of all metrics for a patient

    Returns:
        plotly.graph_objects.Figure: Overview chart
    """
    if not patient_metrics:
        fig = go.Figure()
        fig.add_annotation(
            text="No metrics available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(title="Patient Overview - No Data Available")
        return fig

    # Group by metric type
    metric_types = {}
    for metric in patient_metrics:
        metric_type = metric["metric_type"]
        if metric_type not in metric_types:
            metric_types[metric_type] = []
        metric_types[metric_type].append(metric)

    # Create subplots for different metric types
    from plotly.subplots import make_subplots

    num_metrics = len(metric_types)
    rows = (num_metrics + 1) // 2  # 2 columns
    cols = min(2, num_metrics)

    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=list(metric_types.keys()),
        vertical_spacing=0.1,
    )

    colors = px.colors.qualitative.Set1

    for i, (metric_type, data) in enumerate(metric_types.items()):
        row = (i // 2) + 1
        col = (i % 2) + 1

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["value"],
                mode="lines+markers",
                name=metric_type,
                line=dict(width=2, color=colors[i % len(colors)]),
                marker=dict(size=4),
                showlegend=False,
            ),
            row=row,
            col=col,
        )

    fig.update_layout(
        title="Patient Health Metrics Overview",
        height=300 * rows,
        template="plotly_white",
    )

    return fig


def create_metrics_distribution_chart(all_metrics: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a distribution chart showing the frequency of different metric types.

    Args:
        all_metrics: List of all metrics in the system

    Returns:
        plotly.graph_objects.Figure: Distribution chart
    """
    if not all_metrics:
        fig = go.Figure()
        fig.add_annotation(
            text="No metrics data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(title="Metrics Distribution - No Data Available")
        return fig

    # Count metric types
    metric_counts = {}
    for metric in all_metrics:
        metric_type = metric["metric_type"]
        metric_counts[metric_type] = metric_counts.get(metric_type, 0) + 1

    # Sort by frequency
    sorted_metrics = sorted(metric_counts.items(), key=lambda x: x[1], reverse=True)

    metric_types = [item[0] for item in sorted_metrics]
    counts = [item[1] for item in sorted_metrics]

    fig = go.Figure(
        data=[
            go.Bar(
                x=metric_types,
                y=counts,
                marker_color="#2E8B57",
                hovertemplate="<b>%{x}</b><br>" + "Count: %{y}<br>" + "<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="Distribution of Health Metric Types",
        xaxis_title="Metric Type",
        yaxis_title="Frequency",
        template="plotly_white",
        height=400,
        xaxis_tickangle=-45,
    )

    return fig


def create_activity_timeline_chart(activity_log: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a timeline chart showing system activity.

    Args:
        activity_log: List of activity records

    Returns:
        plotly.graph_objects.Figure: Timeline chart
    """
    if not activity_log:
        fig = go.Figure()
        fig.add_annotation(
            text="No activity data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(title="Activity Timeline - No Data Available")
        return fig

    # Group activities by date
    df = pd.DataFrame(activity_log)
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date

    activity_counts = df.groupby(["date", "type"]).size().reset_index(name="count")

    fig = px.bar(
        activity_counts,
        x="date",
        y="count",
        color="type",
        title="System Activity Timeline",
        labels={
            "date": "Date",
            "count": "Number of Activities",
            "type": "Activity Type",
        },
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    fig.update_layout(
        template="plotly_white",
        height=400,
        xaxis_tickangle=-45,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def create_health_score_gauge(patient_metrics: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a gauge chart representing overall health score.

    Args:
        patient_metrics: List of recent metrics for a patient

    Returns:
        plotly.graph_objects.Figure: Gauge chart
    """
    if not patient_metrics:
        score = 0
    else:
        # Simple health score calculation based on recent metrics
        # This is a simplified example - in practice, you'd use medical guidelines
        score = min(100, len(patient_metrics) * 10)  # 10 points per recent metric, max 100

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Health Score"},
            delta={"reference": 80},
            gauge={
                "axis": {"range": [None, 100]},
                "bar": {"color": "#2E8B57"},
                "steps": [
                    {"range": [0, 50], "color": "lightgray"},
                    {"range": [50, 80], "color": "gray"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 90,
                },
            },
        )
    )

    fig.update_layout(template="plotly_white", height=300)

    return fig
