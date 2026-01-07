import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.sparse import hstack
import joblib
import os


def load_data(path=r"C:\Users\Millpark\Downloads\anime.csv"):
    df = pd.read_csv(path)
    # drop rows without rating
    df = df.dropna(subset=['rating']).reset_index(drop=True)
    return df


def preprocess(df):
    df = df.copy()
    # target
    y = df['rating'].astype(float)

    # genres -> text for TF-IDF
    genres = df['genre'].fillna('')
    tf = TfidfVectorizer(token_pattern=r"[^,]+", lowercase=True)
    X_genre = tf.fit_transform(genres)

    # type -> one-hot
    types = df['type'].fillna('Unknown').values.reshape(-1, 1)
    # scikit-learn versions differ: use sparse_output when available
    try:
        ohe = OneHotEncoder(sparse_output=True, handle_unknown='ignore')
    except TypeError:
        ohe = OneHotEncoder(sparse=True, handle_unknown='ignore')
    X_type = ohe.fit_transform(types)

    # episodes numeric
    eps = pd.to_numeric(df['episodes'], errors='coerce')
    eps = eps.fillna(eps.median()).values.reshape(-1, 1)

    # members log-transform
    members = pd.to_numeric(df['members'], errors='coerce').fillna(0).values.reshape(-1, 1)
    members = np.log1p(members)

    # combine sparse and dense
    X = hstack([X_genre, X_type, eps, members])

    preprocessors = {'tfidf_genre': tf, 'onehot_type': ohe}
    return X, y, preprocessors


def train_and_save(df, model_path='models/rating_predictor.pkl'):
    X, y, prep = preprocess(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # baseline: mean predictor
    mean_pred = np.full_like(y_test, y_train.mean(), dtype=float)
    # compatibility: older sklearn uses squared=False for RMSE
    try:
        rmse_base = mean_squared_error(y_test, mean_pred, squared=False)
    except TypeError:
        rmse_base = mean_squared_error(y_test, mean_pred) ** 0.5
    mae_base = mean_absolute_error(y_test, mean_pred)

    # model
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    try:
        rmse = mean_squared_error(y_test, y_pred, squared=False)
    except TypeError:
        rmse = mean_squared_error(y_test, y_pred) ** 0.5
    mae = mean_absolute_error(y_test, y_pred)

    print(f"Baseline RMSE: {rmse_base:.4f}, MAE: {mae_base:.4f}")
    print(f"Model RMSE: {rmse:.4f}, MAE: {mae:.4f}")

    # save pipeline
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump({'model': model, 'preprocessors': prep}, model_path)
    print(f"Saved model to {model_path}")


if __name__ == '__main__':
    df = load_data()
    train_and_save(df)
