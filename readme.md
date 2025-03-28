# LDS Conference Talk Clustering Tool

This tool analyzes and clusters LDS General Conference talks using both domain-agnostic and domain-informed approaches. It allows researchers to discover patterns and relationships between talks that might not be immediately apparent through traditional analysis.

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv ldscluster-env
   source ldscluster-env/bin/activate  # On Windows: ldscluster-env\Scripts\activate
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```
python main.py --dir ./path/to/talks --clusters 8 --interactive
```

Arguments:
- `--dir`: Directory containing talk text files (required)
- `--clusters`: Number of clusters to create (default: 8)
- `--interactive`: Create interactive visualization (optional)

### Input Format

The tool expects text files in the following format:
- Each talk should be a separate `.txt` file
- Filenames should follow this pattern: `YYYY_MM_Speaker_Title.txt`
- Example: `2023_04_Bednar_The_Faith_to_Ask_and_Then_Act.txt`

If filenames do not follow this pattern, metadata will be set to "Unknown".

## How It Works

1. **Text Preprocessing**: 
   - Two parallel pipelines: domain-agnostic and domain-aware
   - Domain-aware preprocessing filters out common LDS terminology

2. **Feature Extraction**:
   - Converts documents to TF-IDF vectors
   - Identifies distinctive terms for each approach

3. **Clustering**:
   - Performs K-means clustering on both sets of vectors
   - Generates cluster labels based on top terms

4. **Visualization**:
   - Basic matplotlib visualizations of clusters
   - Optional interactive Plotly visualization

5. **Analysis**:
   - Compares clusters between approaches
   - Identifies documents that change clusters

## Project Structure

- `talk_processor.py`: Handles document loading and preprocessing
- `talk_clusterer.py`: Implements the clustering algorithms
- `visualization.py`: Creates interactive visualizations
- `analysis.py`: Performs comparative analysis between approaches
- `main.py`: Main script that ties everything together

## Next Steps

Future enhancements could include:
- Improved domain knowledge incorporation
- Additional clustering algorithms
- Web-based user interface
- Temporal analysis of evolving themes

## License

MIT License
