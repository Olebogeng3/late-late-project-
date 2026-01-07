from flask import Flask, request, jsonify
from recommender import Recommender

app = Flask(__name__)

# initialize recommender once
R = Recommender()


@app.route('/recommend', methods=['GET'])
def recommend():
    title = request.args.get('title')
    if not title:
        return jsonify({'error': 'title query parameter is required'}), 400

    try:
        n = int(request.args.get('n', 5))
    except ValueError:
        n = 5

    recs = R.recommend(title, top_n=n)
    return jsonify({'query': title, 'results': recs})


@app.route('/vector', methods=['GET'])
def vector():
    title = request.args.get('title')
    if not title:
        return jsonify({'error': 'title query parameter is required'}), 400

    vec = R.get_tfidf_vector(title)
    if vec is None:
        return jsonify({'error': 'title not found'}), 404
    return jsonify({'title': title, 'vector_length': len(vec), 'vector': vec})


@app.route('/similarities', methods=['GET'])
def similarities():
    title = request.args.get('title')
    if not title:
        return jsonify({'error': 'title query parameter is required'}), 400

    sims = R.get_similarity_vector(title)
    if sims is None:
        return jsonify({'error': 'title not found'}), 404
    return jsonify({'title': title, 'similarities': sims})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
