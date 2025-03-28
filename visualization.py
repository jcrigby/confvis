import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from talk_clusterer import TalkClusterer

def create_interactive_visualization(documents, agnostic_vectors, agnostic_labels, 
                                     aware_vectors, aware_labels, 
                                     agnostic_cluster_labels, aware_cluster_labels):
    """Create interactive visualizations comparing both clustering approaches."""
    # Initialize clusterers for dimension reduction
    agnostic_clusterer = TalkClusterer()
    aware_clusterer = TalkClusterer()
    
    # Reduce dimensions for visualization
    agnostic_points = agnostic_clusterer.reduce_dimensions(agnostic_vectors)
    aware_points = aware_clusterer.reduce_dimensions(aware_vectors)
    
    # Create a subplot with two side-by-side scatter plots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Domain-Agnostic Clustering", "Domain-Aware Clustering"),
        specs=[[{"type": "scatter"}, {"type": "scatter"}]]
    )
    
    # Create data for hover text
    hover_data = [
        f"Title: {row['title']}<br>Speaker: {row['speaker']}<br>Year: {row['year']}"
        for _, row in documents.iterrows()
    ]
    
    # Add domain-agnostic scatter plot
    for i in range(max(agnostic_labels) + 1):
        mask = agnostic_labels == i
        fig.add_trace(
            go.Scatter(
                x=agnostic_points[mask, 0],
                y=agnostic_points[mask, 1],
                mode="markers",
                marker=dict(size=10),
                name=f"Cluster {i}: {', '.join(agnostic_cluster_labels[i][:3])}",
                text=[hover_data[j] for j, m in enumerate(mask) if m],
                hoverinfo="text"
            ),
            row=1, col=1
        )
    
    # Add domain-aware scatter plot
    for i in range(max(aware_labels) + 1):
        mask = aware_labels == i
        fig.add_trace(
            go.Scatter(
                x=aware_points[mask, 0],
                y=aware_points[mask, 1],
                mode="markers",
                marker=dict(size=10),
                name=f"Cluster {i}: {', '.join(aware_cluster_labels[i][:3])}",
                text=[hover_data[j] for j, m in enumerate(mask) if m],
                hoverinfo="text"
            ),
            row=1, col=2
        )
    
    # Update layout
    fig.update_layout(
        title="Comparison of Clustering Approaches",
        height=600,
        width=1200,
        showlegend=True
    )
    
    # Show the figure
    fig.show()
    
    # Save as HTML for future reference
    fig.write_html("cluster_comparison.html")