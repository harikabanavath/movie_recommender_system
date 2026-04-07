import streamlit as st
import gdown
import os
import pickle
import numpy as np

movies_list = pickle.load(open('movies.pkl', 'rb'))
movies = pickle.load(open('movies.pkl', 'rb'))
movies_data = pickle.load(open('movies_data.pkl', 'rb'))
movies_list = movies_list['title'].values

st.markdown("""
    <style> 
    h1, h2, h3, .stMarkdown h1{
        color: #0076BE;
        text-align: center; 
    } 
    
    .stButton>button {
        background-color: white; 
        color: #7ED348; 
        border-radius: 10px; 
        font-weight: 700; 
        font-size: 18px; 
    } 
    .stButton>button:hover {
        background-color: black; 
        color: #95D8EB; 
        transform: scale(1.11); 
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<h1>MOVIE RECOMMENDER SYSTEM</h1>", unsafe_allow_html=True)

url_link = "https://drive.google.com/uc?id=1EyCSTQp5zERn5APs4HrKy5YM9nk25TzW"
output = "similar.pkl"

if not os.path.exists(output):
    gdown.download(url_link, output, quiet=False)
with open(output, 'rb') as f:
    similarity = pickle.load(f)

#recommends top 5 movies most similar to the input movie
def recommend(movie, top_k=5):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    top_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:top_k+1]

    recommended_movies = []
    for i in top_indices:
        recommended_movies.append(movies.iloc[i[0]].title)

    return recommended_movies

#how many of my top 5 recommended movies share at least one genre with the input movie
def eval_rec(movie_title, top_k=5):
    movie_index = movies[movies['title'] == movie_title].index[0]
    distances = similarity[movie_index]

    top_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:top_k+1]

    target_genres = set(movies_data.iloc[movie_index]['genres'])
    precision_scores = []

    for i in top_indices:
        recommended_genres = set(movies_data.iloc[i[0]]['genres'])
        overlap = len(target_genres & recommended_genres)
        precision_scores.append(1 if overlap > 0 else 0)

    precision = np.mean(precision_scores)
    return precision

#how many different genres are represented in recommendations
def evaluate_diversity(movie_title, top_k=5):
    movie_index = movies[movies['title'] == movie_title].index[0]
    distances = similarity[movie_index]
    top_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:top_k+1]

    all_genres = set()
    for i in top_indices:
        all_genres.update(movies_data.iloc[i[0]]['genres'])

    diversity_score = len(all_genres) / top_k

    return diversity_score

#how unique are my recommendations compared to the input movie
def evaluate_novelty(movie_title, top_k=5):
    movie_index = movies[movies['title'] == movie_title].index[0]
    distances = similarity[movie_index]
    top_movies = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:top_k+1]

    top_indices = [i[0] for i in top_movies]
    similarity_scores = [i[1] for i in top_movies]
    avg_similarity = np.mean(similarity_scores)
    novelty_score = 1 - avg_similarity

    return novelty_score

selected_movie_name = st.selectbox(
    'got a good movie in mind?',
    movies_list)

if st.button('RECOMMEND'):
    recommendations = recommend(selected_movie_name)
    st.subheader('RECOMMENDED MOVIES')
    for i in recommendations:
        st.write(i)

    st.subheader('RECOMMENDATION INSIGHTS')
    st.write('precision = ', eval_rec(selected_movie_name))
    st.write('diversity score = ', evaluate_diversity(selected_movie_name))
    st.write('novelty score = ', evaluate_novelty(selected_movie_name))