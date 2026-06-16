# CineMatch

A polished Flask-based movie recommendation web app that suggests similar movies from a trained similarity model and presents the results with a modern, interactive UI.

Live demo: https://cinematch-z4tn.onrender.com

## What It Does

- Recommends movies based on a selected title.
- Shows the selected movie details, posters, trailers, and match reasons.
- Visualizes recommendation genre breakdown with a custom interactive chart.
- Lets users compare top recommendations side by side.
- Supports a watch queue and theme switching in the browser.
- Uses a responsive design that works across desktop and mobile devices.

## Key Features

- Interactive genre stats chart built with pure HTML, CSS, and JavaScript.
- Why-this-match panel with shared genres, cast, and similarity context.
- Mood wheel for changing the app’s visual theme.
- Motion-rich hero section and animated recommendation cards.
- Comparison view for the top movie matches.
- Hover previews, queue controls, and persistent localStorage state.
- Production-ready Render deployment with Gunicorn.

## Tech Stack

- Python
- Flask
- Pandas
- NumPy
- Scikit-learn
- Requests
- HTML, CSS, and JavaScript

## Project Structure

- `app.py` - Flask app, recommendation logic, and TMDB integration.
- `templates/index.html` - Main UI template.
- `static/style.css` - Styling, layout, and animations.
- `movie_list.pkl` - Movie metadata used by the recommender.
- `similarity.pkl` - Precomputed similarity matrix stored with Git LFS.
- `render.yaml` - Render deployment config.
- `Procfile` - Production start command.

## Local Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
python app.py
```

5. Open `http://127.0.0.1:5000` in your browser.

## Environment Variables

- `TMDB_API_KEY` - Required for poster and trailer lookups in production.
- `PORT` - Used by Render for the web server port.

## Deployment

This project is configured for Render using `render.yaml` and `Procfile`.

Production URL: https://cinematch-z4tn.onrender.com

## Notes

- Large model files are managed with Git LFS.
- The app is designed to degrade gracefully if an external TMDB request fails.
