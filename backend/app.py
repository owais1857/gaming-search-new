from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

# --- 1. INITIALIZATION ---
print("Loading all models and data...")
model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index('../nlp_pipeline/faiss_index.bin')
df = pd.read_csv('../nlp_pipeline/all_data.csv')
print("Initialization Complete. API is ready.")

# --- 2. THE RANKING FUNCTION (OUR "ML" MODEL) ---
def rank_results(results, role):
    developer_keywords = ['job', 'developer', 'engineer', 'programmer', 'artist', 'designer']
    gamer_keywords = ['review', 'guide', 'gameplay', 'news', 'update']

    ranked_results = []
    for result in results:
        score = result['distance'] 
        title = str(result['title']).lower()

        if role == 'developer':
            if result['source'] == 'WorkWithIndies':
                score += 0.5
            if any(keyword in title for keyword in developer_keywords):
                score += 0.2
        
        elif role == 'gamer':
            if result['source'] in ['IGN', 'GameSpot', 'Reddit']:
                score += 0.2
            if any(keyword in title for keyword in gamer_keywords):
                score += 0.1

        result['score'] = score
        ranked_results.append(result)

    return sorted(ranked_results, key=lambda x: x['score'])

# --- 3. FLASK API SETUP ---
app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    role = data.get('role', 'gamer')
    
    if not query:
        return jsonify({"error": "Query is missing"}), 400

    query_embedding = model.encode([query])
    k = 20
    distances, indices = index.search(query_embedding.astype('float32'), k)
    
    initial_results = []
    for i, idx in enumerate(indices[0]):
        # *** THIS IS THE FIX ***
        # Get the summary and check if it's NaN. If so, replace with an empty string.
        summary = df.iloc[idx].get('summary', '')
        if pd.isna(summary):
            summary = ''

        initial_results.append({
            "title": df.iloc[idx]['title'],
            "url": df.iloc[idx]['url'],
            "source": df.iloc[idx]['source'],
            "summary": summary, # Use the cleaned summary
            "distance": float(distances[0][i]) 
        })
    
    final_results = rank_results(initial_results, role)

    return jsonify(final_results[:5])

if __name__ == '__main__':
    app.run(debug=True, port=5001)