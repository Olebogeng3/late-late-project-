# Simple Book Recommender

This folder contains a minimal content-based recommender using the provided `books_data.json` dataset and a small Flask API.

Quick start

1. Create a virtualenv and install requirements:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the API:

```bash
python app.py
```

3. Query recommendations:

GET http://localhost:5000/recommend?title=Sapiens%3A%20A%20Brief%20History%20of%20Humankind&n=5

Notes

- The recommender is TF-IDF on title+description with cosine similarity.
- This is a simple baseline; for large datasets or production use, consider persistence, caching, and more advanced models.
