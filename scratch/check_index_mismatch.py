import pickle

# Load data
movies = pickle.load(open('movie_list.pkl', 'rb'))

g2000_matches = movies[movies['title'] == 'Godzilla 2000']
if not g2000_matches.empty:
    label_index = g2000_matches.index[0]
    
    # Get by label (.loc)
    movie_by_loc = movies.loc[label_index]
    # Get by position (.iloc)
    movie_by_iloc = movies.iloc[label_index]
    
    print(f"Godzilla 2000 index label: {label_index}")
    print(f"Movie at label index (using .loc): {movie_by_loc['title']}")
    print(f"Movie at integer position index (using .iloc): {movie_by_iloc['title']}")
