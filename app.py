import streamlit as st
import pandas as pd
import os
import pickle

st.set_page_config(page_title="CineWise", layout="wide")

# Rutas
USERS_CSV = "data/users.csv"
MOVIES_CSV = "model/movies.csv"
MODEL_PKL = "model/svd_model.pkl"
USER_RATINGS = "data/user_ratings.csv"

# Crear directorios/archivos si no existen
os.makedirs("data", exist_ok=True)
os.makedirs("model", exist_ok=True)
if not os.path.exists(USERS_CSV):
    pd.DataFrame(columns=["userId","name","genres"]).to_csv(USERS_CSV, index=False)
if not os.path.exists(USER_RATINGS):
    pd.DataFrame(columns=["userId","movieId","rating"]).to_csv(USER_RATINGS, index=False)

@st.cache_resource
def load_model():
    if os.path.exists(MODEL_PKL):
        with open(MODEL_PKL,"rb") as f:
            return pickle.load(f)
    return None

@st.cache_data
def load_movies():
    if os.path.exists(MOVIES_CSV):
        return pd.read_csv(MOVIES_CSV)
    return pd.DataFrame(columns=["movieId","title","genres"])

model = load_model()
movies = load_movies()
users = pd.read_csv(USERS_CSV)

st.title("🎬 CineWise — Recomendador de películas")

# --- Login / Registro ---
st.sidebar.header("Cuenta")
username = st.sidebar.text_input("Nombre de usuario")
if "userId" not in st.session_state:
    st.session_state["logged"] = False

if st.sidebar.button("Continuar"):
    if username == "":
        st.sidebar.warning("Introduce un nombre de usuario")
    else:
        if username in users["name"].values:
            user = users[users["name"]==username].iloc[0]
            st.session_state["userId"] = int(user["userId"])
            st.session_state["logged"] = True
            st.sidebar.success(f"Bienvenido/a {username}")
        else:
            st.sidebar.info("Nuevo usuario: selecciona géneros favoritos")
            all_genres = sorted(list({g for sub in movies["genres"].fillna("").str.split("|") for g in sub if g}))
            fav = st.sidebar.multiselect("Géneros favoritos", all_genres)
            if st.sidebar.button("Crear usuario"):
                new_id = int(users["userId"].max())+1 if len(users) else 1
                new_row = {"userId": new_id, "name": username, "genres": ",".join(fav)}
                users = pd.concat([users, pd.DataFrame([new_row])], ignore_index=True)
                users.to_csv(USERS_CSV, index=False)
                st.session_state["userId"] = new_id
                st.session_state["logged"] = True
                st.sidebar.success("Usuario creado")

# Si no está logueado, mostrar ayuda
if not st.session_state.get("logged", False):
    st.info("Regístrate o inicia sesión en la barra lateral para ver recomendaciones.")
    st.stop()

# --- Páginas (simple routing) ---
page = st.sidebar.selectbox("Ir a", ["Recomendaciones","Valorar películas","Mi perfil"])

userId = st.session_state["userId"]

if page == "Recomendaciones":
    st.header("Recomendaciones personalizadas")
    st.write(f"Usuario ID: {userId}")
    if model is None:
        st.warning("Modelo no encontrado. Entrena el modelo (model/svd_model.pkl) o copia el pickle.")
    else:
        with st.spinner("Generando recomendaciones... (puede tardar)"):
            # evitar calcular para todos si movies muy grande: sample pequeñas para demo
            movie_ids = movies["movieId"].unique()
            preds = []
            for mid in movie_ids:
                try:
                    est = model.predict(userId, int(mid)).est
                except:
                    est = 0.0
                preds.append((mid, est))
            preds = sorted(preds, key=lambda x: x[1], reverse=True)[:20]
            rec_ids = [p[0] for p in preds]
            recs = movies[movies["movieId"].isin(rec_ids)].copy()
            recs["pred_rating"] = [p[1] for p in preds]
            st.dataframe(recs[["movieId","title","genres","pred_rating"]].reset_index(drop=True))

elif page == "Valorar películas":
    st.header("Valora una película")
    movies_small = movies.copy()
    if movies_small.empty:
        st.warning("movies.csv no encontrado en model/.")
    else:
        title = st.selectbox("Película", movies_small["title"].tolist()[:5000])
        rating = st.slider("Puntuación", 1, 5, 3)
        if st.button("Guardar valoración"):
            mid = int(movies_small[movies_small["title"]==title]["movieId"].iloc[0])
            row = {"userId": userId, "movieId": mid, "rating": rating}
            ur = pd.read_csv(USER_RATINGS)
            ur = pd.concat([ur, pd.DataFrame([row])], ignore_index=True)
            ur.to_csv(USER_RATINGS, index=False)
            st.success("Valoración guardada. Estas nuevas valoraciones pueden usarse para reentrenar el modelo offline.")

elif page == "Mi perfil":
    st.header("Mi perfil")
    user_row = users[users["userId"]==userId].iloc[0]
    st.write("Nombre:", user_row["name"])
    st.write("Géneros favoritos:", user_row["genres"])
    st.write("Tus últimas valoraciones:")
    ur = pd.read_csv(USER_RATINGS)
    st.dataframe(ur[ur["userId"]==userId].merge(movies, on="movieId", how="left")[["movieId","title","rating"]].tail(20))
