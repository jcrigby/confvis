from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt

class TalkClusterer:
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.pca = PCA(n_components=2)
    
    def vectorize(self, documents, column):
        """Convert documents to TF-IDF vectors."""
        return self.vectorizer.fit_transform(documents[column])
    
    def cluster(self, vectors):
        """Perform K-means clustering."""
        return self.kmeans.fit_predict(vectors)
    
    def get_cluster_labels(self, vectors, top_n=5):
        """Get top terms for each cluster."""
        # Get cluster centers
        centers = self.kmeans.cluster_centers_
        
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # For each cluster, find the most important terms
        labels = {}
        for i in range(self.n_clusters):
            # Sort features by importance for this cluster
            sorted_indices = np.argsort(centers[i])[::-1]
            
            # Get top N feature names
            top_features = [feature_names[j] for j in sorted_indices[:top_n]]
            labels[i] = top_features
        
        return labels
    
    def reduce_dimensions(self, vectors):
        """Reduce dimensions for visualization."""
        return self.pca.fit_transform(vectors.toarray())
    
    def plot_clusters(self, vectors, cluster_labels, title="Document Clusters"):
        """Create a simple plot of the clusters."""
        # Reduce dimensions
        points = self.reduce_dimensions(vectors)
        
        # Plot
        plt.figure(figsize=(10, 8))
        for i in range(self.n_clusters):
            # Get points in this cluster
            cluster_points = points[cluster_labels == i]
            
            # Plot points
            plt.scatter(
                cluster_points[:, 0], 
                cluster_points[:, 1], 
                label=f"Cluster {i}: {', '.join(self.cluster_labels[i][:3])}"
            )
        
        plt.title(title)
        plt.legend()
        plt.tight_layout()
        plt.show()