# Importar librerías necesarias
from fastapi import FastAPI, HTTPException
import pandas as pd
from datetime import datetime

# Inicializar la aplicación FastAPI
app = FastAPI(
    title='API de Sistema de Recomendación de Películas',
    description='API para consultas sobre un sistema de recomendación de películas'
)

# Funciones auxiliares
def clean_data(movies_df, credits_df):
    # Ejemplo de limpieza de datos, ajustar según sea necesario
    movies_df['release_date'] = pd.to_datetime(movies_df['release_date'], errors='coerce')
    credits_df['cast'] = credits_df['cast'].apply(eval)
    credits_df['crew'] = credits_df['crew'].apply(eval)
    return movies_df, credits_df

def get_month_number(month):
    months = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    return months.get(month.lower(), None)

def get_weekday_english(day):
    days = {
        'lunes': 'Monday', 'martes': 'Tuesday', 'miércoles': 'Wednesday',
        'jueves': 'Thursday', 'viernes': 'Friday', 'sábado': 'Saturday', 'domingo': 'Sunday'
    }
    return days.get(day.lower(), None)

# Cargar los datasets y limpiar datos al cargar la aplicación
movies_df = pd.read_csv('movies_dataset.csv')
credits_df = pd.read_csv('credits.csv')
movies_df, credits_df = clean_data(movies_df, credits_df)

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Bienvenido al API de Sistema de Recomendación de Películas"}

@app.get("/cantidad_filmaciones_mes/")
def cantidad_filmaciones_mes(Mes: str):
    month_num = get_month_number(Mes)
    if month_num is None:
        raise HTTPException(status_code=400, detail="Mes inválido")
    
    count = movies_df[movies_df['release_date'].dt.month == month_num].shape[0]
    return {"mes": Mes, "cantidad": count}

@app.get("/cantidad_filmaciones_dia/")
def cantidad_filmaciones_dia(Dia: str):
    weekday = get_weekday_english(Dia)
    if weekday is None:
        raise HTTPException(status_code=400, detail="Día inválido")
    
    count = movies_df[movies_df['release_date'].dt.day_name() == weekday].shape[0]
    return {"dia": Dia, "cantidad": count}

@app.get("/score_titulo/")
def score_titulo(titulo_de_la_filmacion: str):
    movie = movies_df[movies_df['title'].str.lower() == titulo_de_la_filmacion.lower()]
    if movie.empty:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    movie_info = movie.iloc[0]
    return {
        "titulo": movie_info['title'],
        "año": movie_info['release_date'].year,
        "score": movie_info['vote_average']
    }

@app.get("/votos_titulo/")
def votos_titulo(titulo_de_la_filmacion: str):
    movie = movies_df[movies_df['title'].str.lower() == titulo_de_la_filmacion.lower()]
    if movie.empty:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    movie_info = movie.iloc[0]
    if movie_info['vote_count'] < 2000:
        return {"mensaje": "La película no cumple con la condición de tener al menos 2000 valoraciones"}
    
    return {
        "titulo": movie_info['title'],
        "año": movie_info['release_date'].year,
        "total_votos": movie_info['vote_count'],
        "promedio_votos": movie_info['vote_average']
    }

@app.get("/get_actor/")
def get_actor(nombre_actor: str):
    actor_movies = credits_df[credits_df['cast'].apply(lambda x: any(actor['name'].lower() == nombre_actor.lower() for actor in x))]
    if actor_movies.empty:
        raise HTTPException(status_code=404, detail="Actor no encontrado")
    
    total_return = actor_movies['return'].sum()
    avg_return = actor_movies['return'].mean()
    count = actor_movies.shape[0]
    
    return {
        "actor": nombre_actor,
        "cantidad_filmaciones": count,
        "retorno_total": total_return,
        "retorno_promedio": avg_return
    }

@app.get("/get_director/")
def get_director(nombre_director: str):
    director_movies = credits_df[credits_df['crew'].apply(lambda x: any(crew['name'].lower() == nombre_director.lower() and crew['job'].lower() == 'director' for crew in x))]
    if director_movies.empty:
        raise HTTPException(status_code=404, detail="Director no encontrado")
    
    director_info = []
    for _, row in director_movies.iterrows():
        movie = movies_df[movies_df['id'] == row['id']].iloc[0]
        director_info.append({
            "titulo": movie['title'],
            "fecha_lanzamiento": movie['release_date'],
            "retorno_individual": movie['return'],
            "costo": movie['budget'],
            "ganancia": movie['revenue']
        })
    
    total_return = director_movies['return'].sum()
    
    return {
        "director": nombre_director,
        "retorno_total": total_return,
        "peliculas": director_info
    }
