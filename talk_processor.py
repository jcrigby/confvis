import os
import re
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class TalkProcessor:
    def __init__(self):
        self.stopwords = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # LDS-specific common terms for domain-aware processing
        self.lds_common_terms = {
            'church', 'lord', 'jesus', 'christ', 'god', 'savior', 
            'prophet', 'apostle', 'elder', 'sister', 'president',
            'priesthood', 'temple', 'testimony', 'gospel', 'amen'
        }
    
    def load_documents(self, directory):
        """Load documents from a directory and its subdirectories recursively."""
        documents = []
        
        # Check if directory exists
        if not os.path.exists(directory):
            print(f"Directory '{directory}' not found.")
            return pd.DataFrame(documents)
        
        # Check if directory is empty
        if not os.listdir(directory):
            print(f"Directory '{directory}' is empty.")
            return pd.DataFrame(documents)
        
        # Walk through all subdirectories recursively
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.txt'):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as file:
                            text = file.read()
                        
                        # Extract metadata from filename (assuming format: YYYY_MM_Speaker_Title.txt)
                        parts = filename[:-4].split('_')
                        if len(parts) >= 4:
                            year, month = parts[0], parts[1]
                            speaker = parts[2]
                            title = '_'.join(parts[3:])
                        else:
                            year, month, speaker, title = 'Unknown', 'Unknown', 'Unknown', filename[:-4]
                        
                        documents.append({
                            'id': filename[:-4],
                            'text': text,
                            'year': year,
                            'month': month,
                            'speaker': speaker,
                            'title': title
                        })
                    except Exception as e:
                        print(f"Error reading file {filepath}: {e}")
        
        if not documents:
            print("No valid documents found in the directory or its subdirectories.")
        else:
            print(f"Found {len(documents)} documents across all subdirectories.")
        
        return pd.DataFrame(documents)
    
    def preprocess_text(self, text, domain_aware=False):
        """Preprocess text for analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        tokens = [t for t in tokens if t not in self.stopwords]
        
        # Domain-specific processing
        if domain_aware:
            # Create an expanded list of LDS common terms
            # Adding more common LDS terms to remove for better differentiation
            expanded_lds_terms = self.lds_common_terms.union({
                'savior', 'redeemer', 'atonement', 'covenant', 'salvation',
                'commandment', 'blessing', 'pray', 'prayer', 'faith', 'spirit',
                'holy', 'sacred', 'eternal', 'heaven', 'revelation', 'prophet',
                'apostle', 'bishop', 'stake', 'ward', 'mission', 'missionary',
                'brother', 'sister', 'elder', 'conference', 'doctrine', 'scripture',
                'book', 'mormon', 'nephi', 'alma', 'moroni', 'helaman', 'ether',
                'mosiah', 'church', 'sunday', 'latter', 'day', 'saint', 'saints',
                'zion', 'temple', 'baptism', 'sacrament', 'priesthood', 'melchizedek',
                'aaronic', 'patriarch', 'patriarch', 'general', 'authority', 'quorum',
                'relief', 'society', 'young', 'women', 'men', 'primary', 'mutual'
            })
            
            # Remove LDS common terms
            tokens = [t for t in tokens if t not in expanded_lds_terms]
            
            # Here we could add more sophisticated processing:
            # - Identify scripture references
            # - Tag specific theological concepts
            # - etc.
        
        # Lemmatize
        tokens = [self.lemmatizer.lemmatize(t) for t in tokens]
        
        # Filter out short tokens (likely not meaningful)
        tokens = [t for t in tokens if len(t) > 2]
        
        # Return as space-separated string
        return ' ' + ' '.join(tokens)
    
    def process_documents(self, documents, domain_aware=False):
        """Process all documents in the dataframe."""
        # Create a copy of the dataframe
        df = documents.copy()
        
        # Apply preprocessing to each document
        preprocessing_type = 'domain_aware' if domain_aware else 'domain_agnostic'
        df[f'processed_{preprocessing_type}'] = df['text'].apply(
            lambda x: self.preprocess_text(x, domain_aware)
        )
        
        return df