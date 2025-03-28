import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from talk_clusterer import TalkClusterer
from sklearn.manifold import TSNE
import numpy as np

def create_interactive_visualization(documents, agnostic_vectors, agnostic_labels, 
                                     aware_vectors, aware_labels, 
                                     agnostic_cluster_labels, aware_cluster_labels):
    """Create interactive visualizations comparing both clustering approaches."""
    # Use t-SNE for better separation
    print("Reducing dimensions with t-SNE (this may take a minute)...")
    
    # Use different perplexity and learning rate for better separation
    tsne_agnostic = TSNE(n_components=2, perplexity=30, learning_rate=200, random_state=42)
    tsne_aware = TSNE(n_components=2, perplexity=30, learning_rate=200, random_state=42)
    
    # Reduce dimensions
    agnostic_points = tsne_agnostic.fit_transform(agnostic_vectors.toarray())
    aware_points = tsne_aware.fit_transform(aware_vectors.toarray())
    
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
        # Skip empty clusters
        if not any(mask):
            continue
            
        fig.add_trace(
            go.Scatter(
                x=agnostic_points[mask, 0],
                y=agnostic_points[mask, 1],
                mode="markers",
                marker=dict(
                    size=10,
                    opacity=0.7,
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                name=f"Cluster {i}: {', '.join(agnostic_cluster_labels[i][:3])}",
                text=[hover_data[j] for j, m in enumerate(mask) if m],
                hoverinfo="text"
            ),
            row=1, col=1
        )
    
    # Add domain-aware scatter plot
    for i in range(max(aware_labels) + 1):
        mask = aware_labels == i
        # Skip empty clusters
        if not any(mask):
            continue
            
        fig.add_trace(
            go.Scatter(
                x=aware_points[mask, 0],
                y=aware_points[mask, 1],
                mode="markers",
                marker=dict(
                    size=10,
                    opacity=0.7,
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                name=f"Cluster {i}: {', '.join(aware_cluster_labels[i][:3])}",
                text=[hover_data[j] for j, m in enumerate(mask) if m],
                hoverinfo="text"
            ),
            row=1, col=2
        )
    
    # Update layout
    fig.update_layout(
        title="Comparison of Clustering Approaches",
        height=700,
        width=1400,
        showlegend=True,
        legend=dict(
            font=dict(size=10),
            itemsizing='constant'
        )
    )
    
    # Customize axes for better visualization
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', zeroline=False)
    
    # Show the figure
    fig.show()
    
    # Save as HTML for future reference
    fig.write_html("cluster_comparison.html")