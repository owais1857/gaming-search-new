import numpy as np
import faiss

print("Loading embeddings from embeddings.npy...")
embeddings = np.load('embeddings.npy').astype('float32')

# The dimension of our embeddings is 384 for the 'all-MiniLM-L6-v2' model
d = embeddings.shape[1]

print(f"Building FAISS index for {embeddings.shape[0]} vectors of dimension {d}...")

# We will use a simple L2 (Euclidean distance) index
index = faiss.IndexFlatL2(d)
index.add(embeddings)

output_index_file = 'faiss_index.bin'
print(f"Saving index to {output_index_file}...")
faiss.write_index(index, output_index_file)

print("\nIndex built and saved successfully! Ready to search. 🚀")