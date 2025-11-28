# Entrenamiento inicial SVD (offline) — ejecutar en máquina con recursos
import pandas as pd
import pickle
from surprise import Reader, Dataset, SVD

# Ajusta la ruta a tu ratings.csv (MovieLens 30M)
ratings_path = "data/ratings.csv"

print("Cargando ratings (puede tardar)...")
ratings = pd.read_csv(ratings_path)  # columnas: userId,movieId,rating,timestamp

reader = Reader(rating_scale=(0.5, 5))
data = Dataset.load_from_df(ratings[['userId','movieId','rating']], reader)

print("Construyendo trainset y entrenando SVD...")
trainset = data.build_full_trainset()
svd = SVD()
svd.fit(trainset)

# Guardar modelo
with open("model/svd_model.pkl","wb") as f:
    pickle.dump(svd, f)

print("Modelo guardado en model/svd_model.pkl")
