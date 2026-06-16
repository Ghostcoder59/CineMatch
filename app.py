import pickle
import random
import requests
import os
from collections import Counter
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Function to fetch poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=1c98fa6b3edcd11ac5f26bf4eefed1bb&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get('poster_path', '')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    except Exception as e:
        print(f"Error fetching poster for ID {movie_id}: {e}")
    # Premium dark background fallback poster placeholder
    return "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?auto=format&fit=crop&q=80&w=500"

# Function to fetch movie trailer
def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=1c98fa6b3edcd11ac5f26bf4eefed1bb&language=en-US&append_to_response=videos"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            videos = data.get("videos", {}).get("results", [])
            for video in videos:
                if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                    video_key = video.get("key")
                    if video_key:
                        return f"https://www.youtube.com/embed/{video_key}"
    except Exception as e:
        print(f"Error fetching trailer for ID {movie_id}: {e}")
    return None


def as_list(value):
    return value if isinstance(value, list) else []


def build_match_reasons(selected_movie_data, movie_data, similarity_score):
    selected_genres = set(as_list(selected_movie_data.get('genres', [])))
    movie_genres = set(as_list(movie_data.get('genres', [])))
    selected_cast = set(as_list(selected_movie_data.get('cast', [])))
    movie_cast = set(as_list(movie_data.get('cast', [])))
    selected_director = as_list(selected_movie_data.get('crew', []))
    movie_director = as_list(movie_data.get('crew', []))

    reasons = []

    shared_genres = sorted(selected_genres & movie_genres)
    if shared_genres:
        reasons.append(f"Shared genres: {', '.join(shared_genres[:3])}")

    shared_cast = sorted(selected_cast & movie_cast)
    if shared_cast:
        reasons.append(f"Shared cast: {', '.join(shared_cast[:2])}")

    if selected_director and movie_director and selected_director[0] == movie_director[0]:
        reasons.append(f"Same director: {selected_director[0]}")

    if similarity_score >= 0.75:
        reasons.append("Very close semantic match in tone and subject matter")
    elif similarity_score >= 0.55:
        reasons.append("Strong thematic overlap with the selected movie")
    else:
        reasons.append("Keeps a similar cinematic vibe")

    return reasons[:3], shared_genres, shared_cast

# Function to recommend movies
def recommend(movie):
    matched = movies[movies['title'].str.lower() == movie.lower()]
    if matched.empty:
        return None, []
    
    index = matched.index[0]
    selected_movie_data = movies.iloc[index]
    
    # Extract clean details
    selected_movie_details = {
        'movie_id': selected_movie_data['movie_id'],
        'title': selected_movie_data['title'],
        'overview': selected_movie_data['overview'] if isinstance(selected_movie_data['overview'], str) else "",
        'genres': as_list(selected_movie_data.get('genres', [])),
        'cast': as_list(selected_movie_data.get('cast', [])),
        'director': as_list(selected_movie_data.get('crew', []))[0] if as_list(selected_movie_data.get('crew', [])) else "Unknown",
        'poster_url': fetch_poster(selected_movie_data['movie_id']),
        'trailer_url': fetch_trailer(selected_movie_data['movie_id'])
    }

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movies_list = []
    # Top 10 recommendations
    for i in distances[1:11]:
        movie_data = movies.iloc[i[0]]
        movie_id = movie_data['movie_id']
        similarity_score = round(float(i[1]), 3)
        reasons, shared_genres, shared_cast = build_match_reasons(selected_movie_data, movie_data, similarity_score)
        
        recommended_movies_list.append({
            'title': movie_data['title'],
            'poster_url': fetch_poster(movie_id),
            'trailer_url': fetch_trailer(movie_id),
            'overview': movie_data['overview'] if isinstance(movie_data['overview'], str) else "",
            'genres': as_list(movie_data.get('genres', [])),
            'cast': as_list(movie_data.get('cast', [])),
            'director': as_list(movie_data.get('crew', []))[0] if as_list(movie_data.get('crew', [])) else "Unknown",
            'match_score': similarity_score,
            'shared_genres': shared_genres,
            'shared_cast': shared_cast,
            'match_reasons': reasons
        })

    genre_counter = Counter()
    for movie_data in recommended_movies_list:
        genre_counter.update(movie_data.get('genres', []))

    top_genres = [genre for genre, _ in genre_counter.most_common(3)]
    top_match = recommended_movies_list[0]['title'] if recommended_movies_list else selected_movie_details['title']
    recommendation_story = (
        f"{selected_movie_details['title']} leans into {', '.join(selected_movie_details['genres'][:3]) or 'a mixed cinematic profile'}. "
        f"The closest match is {top_match}, with the strongest overlap clustering around {', '.join(top_genres) or 'tone and pacing'}."
    )

    compare_movies = []
    for movie_data in recommended_movies_list[:3]:
        compare_movies.append({
            'title': movie_data['title'],
            'match_score': movie_data['match_score'],
            'shared_genres': movie_data['shared_genres'],
            'shared_cast': movie_data['shared_cast'],
            'director': movie_data['director']
        })

    return selected_movie_details, recommended_movies_list, recommendation_story, compare_movies

# Load data
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

@app.route("/", methods=["GET", "POST"])
def index():
    selected_movie_details = None
    recommended_movies = []
    selected_movie_name = None
    genre_stats = []
    recommendation_story = None
    compare_movies = []

    # Check GET parameter first (enables click-to-browse)
    url_movie = request.args.get("movie")
    if url_movie:
        selected_movie_name = url_movie
        selected_movie_details, recommended_movies, recommendation_story, compare_movies = recommend(selected_movie_name)
    elif request.method == "POST":
        post_movie = request.form.get("movie")
        if post_movie:
            selected_movie_name = post_movie
            selected_movie_details, recommended_movies, recommendation_story, compare_movies = recommend(selected_movie_name)

    # Compute genre frequency distribution across all recommendations
    if recommended_movies:
        all_genres = []
        for m in recommended_movies:
            all_genres.extend(m.get('genres', []))
        genre_counts = Counter(all_genres)
        total = sum(genre_counts.values()) or 1
        # Sort descending by count, convert to list of dicts for JSON template rendering
        genre_stats = [{'genre': g, 'count': c, 'percent': round(c / total * 100, 1)}
                       for g, c in genre_counts.most_common()]

    return render_template("index.html", 
                           movies=movies['title'].tolist(), 
                           selected_movie_name=selected_movie_name,
                           selected_movie_details=selected_movie_details, 
                           recommended_movies=recommended_movies,
                           genre_stats=genre_stats,
                           recommendation_story=recommendation_story,
                           compare_movies=compare_movies)

@app.route("/random")
def random_movie():
    random_title = random.choice(movies['title'].tolist())
    return redirect(url_for('index', movie=random_title))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
