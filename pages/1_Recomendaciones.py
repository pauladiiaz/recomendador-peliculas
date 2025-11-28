# Si usas sistema pages/ de Streamlit, copia este contenido en pages/1_Recomendaciones.py
import streamlit as st
import pandas as pd
import pickle, os

MODEL_PKL = "model/svd_model.pkl"
MOVIES_CSV = "model/movies.csv"

with open(MODEL_PKL,"rb") as f:
    model = pickle.load(f)
movies = pd.read_csv(MOVIES_CSV)

userId = st.session_state.get("userId", None)
st.title("Recomendaciones")
if userId is None:
    st.info("Inicia sesión primero.")
else:
    st.write("Usuario ID:", userId)
    st.write("Calculando recomendaciones...")
    preds = []
    for mid in movies["movieId"].unique():
        preds.append((mid, model.predict(userId, int(mid)).est))
    preds = sorted(preds, key=lambda x: x[1], reverse=True)[:20]
    rec_ids = [p[0] for p in preds]
    recs = movies[movies["movieId"].isin(rec_ids)].copy()
    recs["pred_rating"] = [p[1] for p in preds]
    st.dataframe(recs[["movieId","title","genres","pred_rating"]])
