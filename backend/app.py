from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

# --- 1. INITIALIZATION ---
print("Loading all models and data...")

# Load the AI model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the FAISS index
index = faiss.read_index('../nlp_pipeline/faiss_index.bin')

# Load the original data to display results
df = pd.read_csv('../nlp_pipeline/all_data.csv')

print("Initialization Complete. API is ready.")

# --- 2. THE RANKING FUNCTION (OUR "ML" MODEL) ---
def rank_results(results, role):
    # This is our heuristic-based ML ranking.
    # We assign scores based on the user's role.
    
    # Define keywords for each role
    developer_keywords = ['job', 'developer', 'engineer', 'programmer', 'artist', 'designer']
    gamer_keywords = ['review', 'guide', 'gameplay', 'news', 'update']

    ranked_results = []
    for result in results:
        score = result['distance'] # Start with the semantic similarity score
        title = str(result['title']).lower()

        # Boost score based on role
        if role == 'developer':
            if result['source'] == 'WorkWithIndies':
                score += 0.5 # Big boost for direct job source
            if any(keyword in title for keyword in developer_keywords):
                score += 0.2 # Small boost for keywords
        
        elif role == 'gamer':
            if result['source'] in ['IGN', 'GameSpot', 'Reddit']:
                score += 0.2 # Boost for gamer-centric sources
            if any(keyword in title for keyword in gamer_keywords):
                score += 0.1 # Small boost for keywords

        result['score'] = score
        ranked_results.append(result)

    # Sort results by the new score (lowest is best for L2 distance)
    return sorted(ranked_results, key=lambda x: x['score'])

# --- 3. FLASK API SETUP ---
app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    role = data.get('role', 'gamer') # Default to 'gamer' if no role is provided
    
    if not query:
        return jsonify({"error": "Query is missing"}), 400

    # Convert the query to an embedding
    query_embedding = model.encode([query])
    
    k = 20 # Retrieve more results initially to give the ranker options
    distances, indices = index.search(query_embedding.astype('float32'), k)
    
    # Prepare initial results
    initial_results = []
    for i, idx in enumerate(indices[0]):
        initial_results.append({
            "title": df.iloc[idx]['title'],
            "url": df.iloc[idx]['url'],
            "source": df.iloc[idx]['source'],
            "summary": df.iloc[idx].get('summary', ''), # Use .get for safety
            "distance": distances[0][i]
        })
    
    # Re-rank results based on the role
    final_results = rank_results(initial_results, role)

    # Return the top 5 after ranking
    return jsonify(final_results[:5])

if __name__ == '__main__':
    app.run(debug=True, port=5001)