from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import numpy as np
import matplotlib.pyplot as plt

class TalkClusterer:
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        # Adjust max_features and use character n-grams for better separation
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2),  # Include both unigrams and bigrams
            min_df=3             # Ignore terms that appear in fewer than 3 documents
        )
        # Use higher max_iter and n_init for better convergence
        self.kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            max_iter=500,
            n_init=20
        )
        self.pca = PCA(n_components=2)
    
    def vectorize(self, documents, column):
        """Convert documents to TF-IDF vectors."""
        return self.vectorizer.fit_transform(documents[column])
    
    def cluster(self, vectors):
        """Perform K-means clustering."""
        return self.kmeans.fit_predict(vectors)
    
    def get_cluster_labels(self, vectors, top_n=5):
        """Get top terms for each cluster."""
        # For DBSCAN, the number of clusters isn't known in advance
        if self.algorithm == 'dbscan':
            unique_labels = np.unique(self.clustering.labels_)
            n_clusters = len([l for l in unique_labels if l != -1])  # Exclude noise points (-1)
        else:
            n_clusters = self.n_clusters
        
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Initialize labels dictionary
        labels = {}
        
        if self.algorithm == 'kmeans':
            # Get cluster centers from KMeans
            centers = self.clustering.cluster_centers_
            
            # For each cluster, find the most important terms
            for i in range(n_clusters):
                # Sort features by importance for this cluster
                sorted_indices = np.argsort(centers[i])[::-1]
                
                # Get top N feature names
                top_features = [feature_names[j] for j in sorted_indices[:top_n]]
                labels[i] = top_features
        else:
            # For hierarchical and DBSCAN, compute average TF-IDF values
            # Get unique labels from clustering (excluding -1 for DBSCAN noise)
            unique_labels = np.unique(self.clustering.labels_)
            if self.algorithm == 'dbscan':
                unique_labels = [l for l in unique_labels if l != -1]
            
            for i in unique_labels:
                # Get vectors belonging to this cluster
                if self.algorithm == 'dbscan' and i == -1:
                    # Skip noise points
                    continue
                
                cluster_vectors = vectors[self.clustering.labels_ == i]
                
                # If cluster is empty, skip
                if cluster_vectors.shape[0] == 0:
                    labels[i] = ["empty_cluster"]
                    continue
                
                # Compute average TF-IDF values for this cluster
                avg_tfidf = cluster_vectors.mean(axis=0)
                
                # Convert to array and get top features
                avg_tfidf_array = np.asarray(avg_tfidf).flatten()
                sorted_indices = np.argsort(avg_tfidf_array)[::-1]
                
                # Get top N feature names
                top_features = [feature_names[j] for j in sorted_indices[:top_n]]
                labels[i] = top_features
        
        return labels
    
    def reduce_dimensions(self, vectors):
        """Reduce dimensions for visualization using t-SNE."""
        # Use t-SNE for better separation
        tsne = TSNE(n_components=2, perplexity=30, learning_rate=200, random_state=42)
        return tsne.fit_transform(vectors.toarray())
    
    def plot_clusters(self, vectors, cluster_labels, title="Document Clusters"):
        """Create a simple plot of the clusters."""
        # Reduce dimensions
        points = self.reduce_dimensions(vectors)
        
        # Plot
        plt.figure(figsize=(12, 10))
        
        # Create a scatter plot for each cluster
        for i in range(self.n_clusters):
            # Get points in this cluster
            cluster_points = points[cluster_labels == i]
            
            # Skip if no points in this cluster
            if len(cluster_points) == 0:
                continue
            
            # Plot points with transparency and edge color
            plt.scatter(
                cluster_points[:, 0], 
                cluster_points[:, 1], 
                alpha=0.7,  # Add transparency
                edgecolor='k',  # Add black edge to points
                linewidth=0.5,  # Thin edge
                s=80,  # Slightly larger point size
                label=f"Cluster {i}: {', '.join(self.cluster_labels[i][:3])}"
            )
        
        # Improve plot formatting
        plt.title(title, fontsize=16)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust legend position and font size
        plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1), fontsize=10)
        
        plt.tight_layout()
        plt.show()