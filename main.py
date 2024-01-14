import streamlit as st
import pickle
import pandas as pd
import requests


def fetch_poster(movie_id):
    base_url = "https://image.tmdb.org/t/p/w500"
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US')
    data = response.json()

    if 'poster_path' in data and data['poster_path']:
        return f"{base_url}{data['poster_path']}"
    else:
        return None


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

if 'page' not in st.session_state:
    st.session_state.page = 'main_page'

if st.session_state.page == 'main_page':
    st.title('Movie Recommendation System')

    search_query = st.text_input("Search")
    search_button = st.button("Search")

    if search_button and search_query:
        st.session_state.search_query = search_query
        st.session_state.page = 'search_results'

    st.header('Top Rated Movies')
    if 'vote_average' in movies.columns:
        top_movies = movies.sort_values(by='vote_average', ascending=False).head(25)

        columns_top_movies = st.columns(5)
        for i in range(0, len(top_movies), 5):
            for j in range(5):
                index = i + j
                if index < len(top_movies):
                    with columns_top_movies[j]:
                        movie_title = top_movies.iloc[index]['title']
                        movie_poster = fetch_poster(top_movies.iloc[index]['movie_id'])
                        st.image(movie_poster, caption=movie_title, use_column_width=True)
                        if st.button(f"View Details", key=f"top_button_{index}"):
                            st.session_state.selected_movie = movie_title
                            st.session_state.page = 'movie_details'

    st.header('Popular Movies')
    if 'popularity' in movies.columns:
        popular_movies = movies.sort_values(by='popularity', ascending=False).head(25)
        columns_popular_movies = st.columns(5)
        for i in range(0, len(popular_movies), 5):
            for j in range(5):
                index = i + j
                if index < len(popular_movies):
                    with columns_popular_movies[j]:
                        movie_title = popular_movies.iloc[index]['title']
                        movie_poster = fetch_poster(popular_movies.iloc[index]['movie_id'])
                        st.image(movie_poster, caption=movie_title, use_column_width=True)
                        if st.button(f"View Details", key=f"popular_button_{index}"):
                            # Redirect to a separate page with movie details
                            st.session_state.selected_movie = movie_title
                            st.session_state.page = 'movie_details'

elif st.session_state.page == 'search_results':
    st.title(f"Search Results for '{st.session_state.search_query}'")
    search_results = movies[movies['title'].str.contains(st.session_state.search_query, case=False)]
    if not search_results.empty:
        columns_search_results = st.columns(5)
        for k in range(min(len(search_results), 5)):
            with columns_search_results[k]:
                movie_title = search_results.iloc[k]['title']
                movie_poster = fetch_poster(search_results.iloc[k]['movie_id'])
                st.image(movie_poster, caption=movie_title, use_column_width=True)
                if st.button(f"View Details", key=f"search_button_{k}"):
                    st.session_state.selected_movie = movie_title
                    st.session_state.page = 'movie_details'
    else:
        st.write("No results found. Please try another search.")

elif st.session_state.page == 'movie_details':
    st.title(st.session_state.selected_movie)
    st.image(fetch_poster(movies[movies['title'] == st.session_state.selected_movie]['movie_id'].values[0]),
             caption=st.session_state.selected_movie, use_column_width=True)

    selected_movie = st.session_state.selected_movie
    overview = movies[movies['title'] == selected_movie]['overview'].values[0]
    if isinstance(overview, list):
        overview = ' '.join(overview)
    cleaned_overview = overview.replace(',', '')

    st.write(f"Description: {cleaned_overview}")

    genres = movies[movies['title'] == selected_movie]['genres'].values[0]
    st.write("Genres:")
    for genre in genres:
        st.write(f"- {genre}")

    cast = movies[movies['title'] == selected_movie]['cast'].values[0]
    st.write("Cast:")
    st.write(", ".join(cast))

    st.header("Recommended Movies")
    recommended_names, recommended_posters = recommend(st.session_state.selected_movie)
    columns_recommend = st.columns(5)
    for k in range(5):
        with columns_recommend[k]:
            st.text(recommended_names[k])
            st.image(recommended_posters[k], use_column_width=True)
    if st.button("Back"):
        st.session_state.page = 'main_page'
