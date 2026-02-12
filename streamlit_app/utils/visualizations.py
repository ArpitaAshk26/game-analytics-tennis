import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_bar_chart(df, x, y, title, color=None):
    """Create a bar chart"""
    fig = px.bar(df, x=x, y=y, title=title, color=color,
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(showlegend=True if color else False)
    return fig

def create_pie_chart(df, names, values, title):
    """Create a pie chart"""
    fig = px.pie(df, names=names, values=values, title=title,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    return fig

def create_scatter_plot(df, x, y, title, color=None, size=None):
    """Create a scatter plot"""
    fig = px.scatter(df, x=x, y=y, title=title, color=color, size=size,
                     color_discrete_sequence=px.colors.qualitative.Bold)
    return fig

def create_line_chart(df, x, y, title, color=None):
    """Create a line chart"""
    fig = px.line(df, x=x, y=y, title=title, color=color,
                  color_discrete_sequence=px.colors.qualitative.Vivid)
    return fig

def create_metric_card(value, label, delta=None):
    """Helper to display metrics consistently"""
    return {"value": value, "label": label, "delta": delta}