import os
import argparse
from analysis import analyze_talks
from visualization import create_interactive_visualization

def main():
    parser = argparse.ArgumentParser(description='Cluster LDS Conference Talks')
    parser.add_argument('--dir', type=str, required=True, help='Directory containing talk text files')
    parser.add_argument('--clusters', type=int, default=8, help='Number of clusters to create')
    parser.add_argument('--interactive', action='store_true', help='Create interactive visualization')
    parser.add_argument('--algorithm', type=str, default='kmeans', 
                        choices=['kmeans', 'hierarchical', 'dbscan'], 
                        help='Clustering algorithm to use')
    args = parser.parse_args()
    
    # Check if directory exists
    if not os.path.isdir(args.dir):
        print(f"Error: Directory '{args.dir}' does not exist")
        return
    
    # Analyze talks
    documents, agnostic_clusterer, aware_clusterer = analyze_talks(
        args.dir, args.clusters, args.algorithm
    )
    
    # Check if analysis was successful
    if documents is None:
        print("Analysis could not be completed. Please run the scraper to download conference talks first.")
        print("Example: python lds_talk_scraper.py --output ./talks --start 2010 --end 2023")
        return
    
    # Create interactive visualization if requested
    if args.interactive:
        create_interactive_visualization(
            documents,
            agnostic_clusterer.vectorize(documents, 'processed_domain_agnostic'),
            documents['agnostic_cluster'].values,
            aware_clusterer.vectorize(documents, 'processed_domain_aware'),
            documents['aware_cluster'].values,
            agnostic_clusterer.cluster_labels,
            aware_clusterer.cluster_labels
        )
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()