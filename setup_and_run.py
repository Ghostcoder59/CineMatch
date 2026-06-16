import os
import shutil
import urllib.request
import pickle
import sys
import subprocess

# Define paths
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(WORKSPACE_DIR, "templates")
STATIC_DIR = os.path.join(WORKSPACE_DIR, "static")

MOVIES_CSV = os.path.join(WORKSPACE_DIR, "tmdb_5000_movies.csv")
CREDITS_CSV = os.path.join(WORKSPACE_DIR, "tmdb_5000_credits.csv")

MOVIE_LIST_PKL = os.path.join(WORKSPACE_DIR, "movie_list.pkl")
SIMILARITY_PKL = os.path.join(WORKSPACE_DIR, "similarity.pkl")

# Raw URLs for TMDB 5000 dataset
MOVIES_URL = "https://raw.githubusercontent.com/harshitcodes/tmdb_movie_data_analysis/master/tmdb-5000-movie-dataset/tmdb_5000_movies.csv"
CREDITS_URL = "https://raw.githubusercontent.com/harshitcodes/tmdb_movie_data_analysis/master/tmdb-5000-movie-dataset/tmdb_5000_credits.csv"

def print_banner(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60 + "\n")

def setup_directories():
    print_banner("Configuring Flask Project Structure...")
    # Create templates directory if it doesn't exist
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)
        print("Created templates/ directory.")
    
    # Create static directory if it doesn't exist
    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR)
        print("Created static/ directory.")
        
    # Move index.html to templates/ if it is in root
    root_index = os.path.join(WORKSPACE_DIR, "index.html")
    dest_index = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(root_index):
        shutil.move(root_index, dest_index)
        print("Moved index.html to templates/index.html")
    else:
        print("index.html not in root (it might already be in templates/)")
        
    # Move style.css to static/ if it is in root
    root_css = os.path.join(WORKSPACE_DIR, "style.css")
    dest_css = os.path.join(STATIC_DIR, "style.css")
    if os.path.exists(root_css):
        shutil.move(root_css, dest_css)
        print("Moved style.css to static/style.css")
    else:
        print("style.css not in root (it might already be in static/)")

def install_dependencies():
    print_banner("Checking and Installing Python Dependencies...")
    required_packages = ["flask", "requests", "pandas", "numpy", "scikit-learn"]
    
    for pkg in required_packages:
        module_name = "sklearn" if pkg == "scikit-learn" else pkg
        try:
            __import__(module_name)
            print(f"Package '{pkg}' is already installed.")
        except ImportError:
            print(f"Package '{pkg}' is missing. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

def download_file(url, filepath):
    print(f"Downloading {os.path.basename(filepath)} from {url}...")
    
    # Custom headers to avoid being blocked by GitHub
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    
    with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
        total_size = int(response.info().get('Content-Length', 0))
        block_size = 1024 * 1024  # 1 MB blocks
        downloaded = 0
        
        while True:
            buffer = response.read(block_size)
            if not buffer:
                break
            downloaded += len(buffer)
            out_file.write(buffer)
            if total_size > 0:
                percent = int(downloaded * 100 / total_size)
                print(f"Downloaded {percent}% ({downloaded / (1024*1024):.2f} / {total_size / (1024*1024):.2f} MB)...", end="\r")
            else:
                print(f"Downloaded {downloaded / (1024*1024):.2f} MB...", end="\r")
        print()
    print("Download completed successfully.")

def check_and_download_datasets():
    if os.path.exists(MOVIE_LIST_PKL) and os.path.exists(SIMILARITY_PKL):
        print("Pickle files already exist. No need to download datasets.")
        return
        
    print_banner("Preparing Dataset Files...")
    
    # Download movies csv if not exists
    if not os.path.exists(MOVIES_CSV):
        download_file(MOVIES_URL, MOVIES_CSV)
    else:
        print("tmdb_5000_movies.csv already exists.")
        
    # Download credits csv if not exists
    if not os.path.exists(CREDITS_CSV):
        try:
            download_file(CREDITS_URL, CREDITS_CSV)
        except Exception as e:
            print(f"Failed to download credits from primary URL: {e}")
            alt_credits_url = "https://raw.githubusercontent.com/vamshi121/TMDB-5000-Movie-Dataset/master/tmdb_5000_credits.csv"
            print(f"Trying alternative URL: {alt_credits_url}")
            download_file(alt_credits_url, CREDITS_CSV)
    else:
        print("tmdb_5000_credits.csv already exists.")

def generate_pickle_files():
    if os.path.exists(MOVIE_LIST_PKL) and os.path.exists(SIMILARITY_PKL):
        print("movie_list.pkl and similarity.pkl already exist.")
        return
        
    print_banner("Generating Pickle Files (Processing Datasets)...")
    
    import pandas as pd
    import numpy as np
    import ast
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    print("Loading datasets (this may take a few seconds)...")
    movies = pd.read_csv(MOVIES_CSV)
    credits = pd.read_csv(CREDITS_CSV)
    
    print("Merging datasets...")
    movies = movies.merge(credits, on='title')
    movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
    movies.dropna(inplace=True)
    movies.reset_index(drop=True, inplace=True)
    
    print("Preprocessing text data...")
    def convert(text):
        L = []
        for i in ast.literal_eval(text):
            L.append(i['name']) 
        return L 

    movies['genres'] = movies['genres'].apply(convert)
    movies['keywords'] = movies['keywords'].apply(convert)

    def convert3(text):
        L = []
        counter = 0
        for i in ast.literal_eval(text):
            if counter < 3:
                L.append(i['name'])
                counter += 1
            else:
                break
        return L 

    movies['cast'] = movies['cast'].apply(convert3)

    def fetch_director(text):
        L = []
        for i in ast.literal_eval(text):
            if i['job'] == 'Director':
                L.append(i['name'])
                break
        return L 

    movies['crew'] = movies['crew'].apply(fetch_director)

    # Save a clean copy of the columns for display in the UI
    movies_display = movies[['movie_id', 'title', 'overview', 'genres', 'cast', 'crew']].copy()

    def collapse(L):
        L1 = []
        for i in L:
            L1.append(i.replace(" ", ""))
        return L1

    movies['cast'] = movies['cast'].apply(collapse)
    movies['crew'] = movies['crew'].apply(collapse)
    movies['genres'] = movies['genres'].apply(collapse)
    movies['keywords'] = movies['keywords'].apply(collapse)

    movies['overview_split'] = movies['overview'].apply(lambda x: x.split() if isinstance(x, str) else [])
    movies['tags'] = movies['overview_split'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

    tags_string = movies['tags'].apply(lambda x: " ".join(x).lower())
    
    print("Vectorizing tags...")
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vector = cv.fit_transform(tags_string).toarray()
    
    print("Computing cosine similarity...")
    similarity = cosine_similarity(vector)
    
    print("Saving pickle files...")
    with open(MOVIE_LIST_PKL, 'wb') as f:
        pickle.dump(movies_display, f)
    with open(SIMILARITY_PKL, 'wb') as f:
        pickle.dump(similarity, f)
        
    print("Successfully generated movie_list.pkl and similarity.pkl!")
    
    # Cleanup large CSV files to save disk space
    try:
        os.remove(MOVIES_CSV)
        os.remove(CREDITS_CSV)
        print("Cleaned up temporary CSV files to free disk space.")
    except Exception as e:
        print(f"Could not delete temporary CSVs: {e}")

if __name__ == "__main__":
    setup_directories()
    install_dependencies()
    check_and_download_datasets()
    generate_pickle_files()
    
    print_banner("Setup Complete! Starting Flask App...")
    print("To start the app manually next time, run: python app.py")
    print("Launching Flask now...")
    
    subprocess.run([sys.executable, "app.py"])
