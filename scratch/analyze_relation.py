import pickle

# Load data
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Print columns and movie info
print("Columns in movie_list.pkl:", movies.columns)

godzilla = movies[movies['title'].str.contains('Godzilla', case=False)]
transamerica = movies[movies['title'].str.contains('Transamerica', case=False)]

print("\n--- Godzilla Movies found ---")
for idx, row in godzilla.iterrows():
    print(f"Index: {idx} | ID: {row['movie_id']} | Title: {row['title']}")
    print(f"  Genres: {row['genres']}")
    print(f"  Cast: {row['cast']}")
    print(f"  Crew/Director: {row['crew']}")
    print(f"  Overview: {row['overview']}")

print("\n--- Transamerica Movie found ---")
for idx, row in transamerica.iterrows():
    print(f"Index: {idx} | ID: {row['movie_id']} | Title: {row['title']}")
    print(f"  Genres: {row['genres']}")
    print(f"  Cast: {row['cast']}")
    print(f"  Crew/Director: {row['crew']}")
    print(f"  Overview: {row['overview']}")

# Find similarity score between Godzilla 2000 and Transamerica
g2000_matches = movies[movies['title'] == 'Godzilla 2000']
trans_matches = movies[movies['title'] == 'Transamerica']

if not g2000_matches.empty and not trans_matches.empty:
    g_idx = g2000_matches.index[0]
    t_idx = trans_matches.index[0]
    score = similarity[g_idx][t_idx]
    print(f"\nSimilarity score between 'Godzilla 2000' (idx {g_idx}) and 'Transamerica' (idx {t_idx}): {score:.4f}")
    
    # Let's check what words they share in the tags vector
    # In setup_and_run.py, tags are overview + genres + keywords + cast + crew
    # Let's rebuild their tags and see overlapping words
    # We need keywords to see tags. Wait, did we save keywords? In setup_and_run.py, we only kept:
    # ['movie_id', 'title', 'overview', 'genres', 'cast', 'crew']
    # Let's inspect the tags of these index positions if we can regenerate them.
    # Actually, we can just print the exact words in movies_display or look at what words they share in their raw attributes.
