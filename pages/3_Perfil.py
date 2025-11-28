import streamlit as st
import pandas as pd

USERS_CSV = "data/users.csv"
MOVIES_CSV = "model/movies.csv"
USER_RATINGS = "data/user_ratings.csv"

users = pd.read_csv(USERS_CSV)
movies = pd.read_csv(MOVIES_CSV)
userId = st.session_state.get("userId", None)

st.title("Mi perfil")
if userId is None:
    st.info("Inicia sesión primero.")
else:
    user = users[users["userId"]==userId].iloc[0]
    st.write("Nombre:", user["name"])
    st.write("Géneros favoritos:", user["genres"])
    if os.path.exists(USER_RATINGS):
        ur = pd.read_csv(USER_RATINGS)
        my = ur[ur["userId"]==userId].merge(movies, on="movieId", how="left")
        st.dataframe(my[["movieId","title","rating"]].tail(20))
