from talk_processor import TalkProcessor
from talk_clusterer import TalkClusterer

def analyze_talks(directory, n_clusters=5):
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
    agnostic_clusterer = TalkClusterer(n_clusters=n_clusters)
    aware_clusterer = TalkClusterer(n_clusters=n_clusters)
    
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
        print(f"\nCluster {i}:")
        print(f"  Domain-Agnostic: {', '.join(agnostic_clusterer.cluster_labels[i])}")
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
            print(f"Domain-Agnostic Cluster: {doc['agnostic_cluster']} - {', '.join(agnostic_clusterer.cluster_labels[doc['agnostic_cluster']])}")
            print(f"Domain-Aware Cluster: {doc['aware_cluster']} - {', '.join(aware_clusterer.cluster_labels[doc['aware_cluster']])}")
    
    return documents, agnostic_clusterer, aware_clusterer