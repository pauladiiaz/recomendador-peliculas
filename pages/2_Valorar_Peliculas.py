import streamlit as st
import pandas as pd
import os

MOVIES_CSV = "model/movies.csv"
USER_RATINGS = "data/user_ratings.csv"

movies = pd.read_csv(MOVIES_CSV)
userId = st.session_state.get("userId", None)

st.title("Valorar películas")
if userId is None:
    st.info("Inicia sesión primero.")
else:
    title = st.selectbox("Película", movies["title"].tolist()[:5000])
    rating = st.slider("Puntuación", 1, 5, 3)
    if st.button("Guardar valoración"):
        mid = int(movies[movies["title"]==title]["movieId"].iloc[0])
        if not os.path.exists(USER_RATINGS):
            pd.DataFrame(columns=["userId","movieId","rating"]).to_csv(USER_RATINGS, index=False)
        ur = pd.read_csv(USER_RATINGS)
        ur = pd.concat([ur, pd.DataFrame([{"userId":userId,"movieId":mid,"rating":rating}])], ignore_index=True)
        ur.to_csv(USER_RATINGS, index=False)
        st.success("Valoración guardada.")
