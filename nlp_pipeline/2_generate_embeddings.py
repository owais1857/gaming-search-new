import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np

print("Loading pre-trained NLP model...")
# This model is fast and effective for semantic search
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Reading consolidated data from all_data.csv...")
df = pd.read_csv('all_data.csv')

# We'll create embeddings based on the title and summary for better context
# First, ensure the summary column exists and is a string
if 'summary' not in df.columns:
    df['summary'] = ''
df['summary'] = df['summary'].astype(str).fillna('')

# Combine title and summary into a single text field
sentences = (df['title'] + ". " + df['summary']).tolist()

print(f"Generating embeddings for {len(sentences)} documents... (This may take a few moments)")

# Generate the embeddings. The model will show a progress bar.
embeddings = model.encode(sentences, show_progress_bar=True)

# --- Save the Embeddings and Corresponding URLs ---
output_embeddings_file = 'embeddings.npy'
output_urls_file = 'urls.csv'

print(f"\nSaving embeddings to {output_embeddings_file}...")
np.save(output_embeddings_file, embeddings)

print(f"Saving corresponding URLs to {output_urls_file}...")
df['url'].to_csv(output_urls_file, index=False)

print("\nEmbeddings generated and saved successfully! 🎉")