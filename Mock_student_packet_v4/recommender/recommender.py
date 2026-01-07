import json
import os
from difflib import get_close_matches

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Recommender:
    def __init__(self, data_path=None):
        if data_path is None:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            data_path = os.path.join(base, 'books_data.json')

        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.df = pd.DataFrame(data)
        if 'description' not in self.df.columns:
            self.df['description'] = ''
        if 'title' not in self.df.columns:
            raise ValueError('Dataset must contain title field')

        self.tfidf = None
        self.tfidf_matrix = None
        self._build_index()

    def _build_index(self):
        corpus = (self.df['title'].fillna('') + ' ' + self.df['description'].fillna(''))
        self.tfidf = TfidfVectorizer(stop_words='english', max_df=0.8)
        self.tfidf_matrix = self.tfidf.fit_transform(corpus)

    def _find_title_index(self, title_query):
        titles = self.df['title'].astype(str).tolist()
        # exact match first
        for i, t in enumerate(titles):
            if t.strip().lower() == title_query.strip().lower():
                return i
        # fuzzy match fallback
        matches = get_close_matches(title_query, titles, n=1, cutoff=0.5)
        if matches:
            return titles.index(matches[0])
        return None

    def recommend(self, title_query, top_n=5):
        idx = self._find_title_index(title_query)
        if idx is None:
            return []

        query_vec = self.tfidf_matrix[idx]
        sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        # exclude the query itself
        sims[idx] = -1
        top_indices = np.argsort(-sims)[:top_n]

        results = []
        for i in top_indices:
            results.append({
                'title': self.df.at[i, 'title'],
                'product_id': self.df.at[i, 'product_id'] if 'product_id' in self.df.columns else None,
                'score': float(sims[i])
            })
        return results

    def get_tfidf_vector(self, title_query):
        """Return the TF-IDF vector (dense list) for a given title_query."""
        idx = self._find_title_index(title_query)
        if idx is None:
            return None
        vec = self.tfidf_matrix[idx]
        return vec.toarray().flatten().tolist()

    def get_similarity_vector(self, title_query):
        """Return cosine similarity scores between the query and all items."""
        idx = self._find_title_index(title_query)
        if idx is None:
            return None
        query_vec = self.tfidf_matrix[idx]
        sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        return sims.tolist()

    def save_matrices(self, out_dir=None):
        """Save TF-IDF matrix and similarity matrix to files in out_dir (npz)."""
        import os
        import scipy.sparse

        if out_dir is None:
            out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        os.makedirs(out_dir, exist_ok=True)

        tfidf_path = os.path.join(out_dir, 'tfidf_matrix.npz')
        scipy.sparse.save_npz(tfidf_path, self.tfidf_matrix)

        # compute full pairwise similarity (may be memory heavy for large datasets)
        sim = cosine_similarity(self.tfidf_matrix)
        sim_path = os.path.join(out_dir, 'similarity_matrix.npy')
        np.save(sim_path, sim)

        vocab_path = os.path.join(out_dir, 'tfidf_vocabulary.json')
        with open(vocab_path, 'w', encoding='utf-8') as f:
            json.dump(self.tfidf.vocabulary_, f)

        return {'tfidf': tfidf_path, 'similarity': sim_path, 'vocab': vocab_path}


if __name__ == '__main__':
    r = Recommender()
    sample = r.recommend('Sapiens: A Brief History of Humankind', top_n=5)
    print('Recommendations for Sapiens:')
    for s in sample:
        print(s)
