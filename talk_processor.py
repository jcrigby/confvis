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
        """Load documents from a directory."""
        documents = []
        
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                filepath = os.path.join(directory, filename)
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
            # Remove LDS common terms
            tokens = [t for t in tokens if t not in self.lds_common_terms]
            
            # Here we could add more sophisticated processing:
            # - Identify scripture references
            # - Tag specific theological concepts
            # - etc.
        
        # Lemmatize
        tokens = [self.lemmatizer.lemmatize(t) for t in tokens]
        
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