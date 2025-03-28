from talk_processor import TalkProcessor
from talk_clusterer import TalkClusterer

def analyze_talks(directory, n_clusters=5, algorithm='kmeans'):
    """Analyze talks using both domain-aware and domain-agnostic approaches."""
    # Initialize processor
    processor = TalkProcessor()
    
    # Load documents
    print("Loading documents...")
    documents = processor.load_documents(directory)
    print(f"Loaded {len(documents)} documents")
    
    # Check if any documents were found
    if len(documents) == 0:
        print("No documents found in the directory. Please run the scraper first or check the directory path.")
        return None, None, None
    
    # Process documents with both approaches
    print("Processing documents...")
    documents = processor.process_documents(documents, domain_aware=False)
    documents = processor.process_documents(documents, domain_aware=True)
    
    # Initialize clusterers
    print(f"Using clustering algorithm: {algorithm}")
    agnostic_clusterer = TalkClusterer(n_clusters=n_clusters, algorithm=algorithm)
    aware_clusterer = TalkClusterer(n_clusters=n_clusters, algorithm=algorithm)
    
    # Vectorize and cluster with domain-agnostic approach
    print("Clustering with domain-agnostic approach...")
    agnostic_vectors = agnostic_clusterer.vectorize(documents, 'processed_domain_agnostic')
    agnostic_labels = agnostic_clusterer.cluster(agnostic_vectors)
    agnostic_clusterer.cluster_labels = agnostic_clusterer.get_cluster_labels(agnostic_vectors)
    
    # Vectorize and cluster with domain-aware approach
    print("Clustering with domain-aware approach...")
    aware_vectors = aware_clusterer.vectorize(documents, 'processed_domain_aware')
    aware_labels = aware_clusterer.cluster(aware_vectors)
    aware_clusterer.cluster_labels = aware_clusterer.get_cluster_labels(aware_vectors)
    
    # Add cluster labels to dataframe
    documents['agnostic_cluster'] = agnostic_labels
    documents['aware_cluster'] = aware_labels
    
    # Plot clusters
    print("Plotting clusters...")
    agnostic_clusterer.plot_clusters(
        agnostic_vectors, 
        agnostic_labels, 
        "Domain-Agnostic Clusters"
    )
    aware_clusterer.plot_clusters(
        aware_vectors, 
        aware_labels, 
        "Domain-Aware Clusters"
    )
    
    # Compare clusters
    print("\nCluster comparisons:")
    for i in range(n_clusters):
        # Check if this cluster exists in agnostic_clusterer.cluster_labels
        if i in agnostic_clusterer.cluster_labels:
            print(f"\nCluster {i}:")
            print(f"  Domain-Agnostic: {', '.join(agnostic_clusterer.cluster_labels[i])}")
        
        # Check if this cluster exists in aware_clusterer.cluster_labels
        if i in aware_clusterer.cluster_labels:
            if i not in agnostic_clusterer.cluster_labels:
                print(f"\nCluster {i}:")
            print(f"  Domain-Aware: {', '.join(aware_clusterer.cluster_labels[i])}")
    
    # Find documents that change clusters
    changed_docs = documents[documents['agnostic_cluster'] != documents['aware_cluster']]
    print(f"\n{len(changed_docs)} documents changed clusters between approaches")
    
    if len(changed_docs) > 0:
        print("\nSample documents that changed clusters:")
        sample = changed_docs.sample(min(5, len(changed_docs)))
        for _, doc in sample.iterrows():
            print(f"\nTitle: {doc['title']}")
            print(f"Speaker: {doc['speaker']}")
            
            # Check if this cluster exists in agnostic_clusterer.cluster_labels
            if doc['agnostic_cluster'] in agnostic_clusterer.cluster_labels:
                print(f"Domain-Agnostic Cluster: {doc['agnostic_cluster']} - {', '.join(agnostic_clusterer.cluster_labels[doc['agnostic_cluster']])}")
            else:
                print(f"Domain-Agnostic Cluster: {doc['agnostic_cluster']} - No label available")
            
            # Check if this cluster exists in aware_clusterer.cluster_labels
            if doc['aware_cluster'] in aware_clusterer.cluster_labels:
                print(f"Domain-Aware Cluster: {doc['aware_cluster']} - {', '.join(aware_clusterer.cluster_labels[doc['aware_cluster']])}")
            else:
                print(f"Domain-Aware Cluster: {doc['aware_cluster']} - No label available")
    
    return documents, agnostic_clusterer, aware_clusterer