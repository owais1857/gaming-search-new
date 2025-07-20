import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

print("Loading tools for search...")
# Load the AI model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the FAISS index
index = faiss.read_index('faiss_index.bin')

# Load the original data to display results
df = pd.read_csv('all_data.csv')
print("Ready to search!")
print("--------------------")

# This creates an endless loop to ask for queries. Press Ctrl+C to exit.
while True:
    query = input("Enter your search query: ")
    
    # Convert the query to an embedding
    query_embedding = model.encode([query])
    
    # The number of results to retrieve
    k = 5 
    
    # Perform the search
    distances, indices = index.search(query_embedding.astype('float32'), k)
    
    print("\n--- Search Results ---")
    for i, idx in enumerate(indices[0]):
        # Get the title and URL from our original dataframe
        title = df.iloc[idx]['title']
        url = df.iloc[idx]['url']
        source = df.iloc[idx]['source']
        
        print(f"{i+1}. Title: {title}")
        print(f"   Source: {source}")
        print(f"   URL: {url}\n")
    print("--------------------")