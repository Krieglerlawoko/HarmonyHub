from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
#from app import db, Song

def get_recommendations(genre):
    """
    Generate music recommendations based on genre.
    
    Args:
        genre (str): The genre for which recommendations are requested.
    
    Returns:
        list: A list of recommended songs of the specified genre.
    """
    recommended_songs = Song.query.filter_by(genre=genre).all()
    return recommended_songs

def content_based_recommendations(songs, user_preferences, k=5):
    """
    Generate music recommendations using content-based filtering.
    
    Args:
        songs (list): List of Song objects.
        user_preferences (str): User's preferred genre or attributes.
        k (int): Number of recommendations to generate.
    
    Returns:
        list: A list of recommended songs.
    """
    # Vectorize song attributes using TF-IDF
    vectorizer = TfidfVectorizer()
    song_attributes = [song.title + ' ' + song.artist + ' ' + song.genre for song in songs]
    song_vectors = vectorizer.fit_transform(song_attributes)
    
    # Vectorize user preferences
    user_preference_vector = vectorizer.transform([user_preferences])
    
    # Calculate cosine similarity between songs and user preferences
    similarity_scores = cosine_similarity(song_vectors, user_preference_vector)
    
    # Sort songs based on similarity scores
    sorted_indices = np.argsort(-similarity_scores.flatten())
    
    # Get recommended song indices
    recommended_song_indices = sorted_indices[:k]
    
    return recommended_song_indices
