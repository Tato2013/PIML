import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Path
from sklearn.neighbors import NearestNeighbors
from fastapi.responses import JSONResponse
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

app = FastAPI()


    
    
#DataFrame a utilizar
reviews=pd.read_parquet('reviews.parquet')
steam=pd.read_parquet('steam.parquet')
item=pd.read_parquet('item.parquet')
play_time=pd.read_parquet('play_time.parquet')
ranking_genero = pd.read_parquet('raking_genero.parquet')

# Variables globales

features = None
nn = None
game_ids = None

@app.on_event("startup")
async def load_data():
    global df_steam, features, nn, game_ids

    
    # Selecciona las características relevantes para la similitud (por ejemplo, action, adventure, strategy)
    features = steam[['action', 'adventure', 'strategy','early access','indie','free to play']]  # Añade todas las características relevantes
    
    # Crea un modelo NearestNeighbors basado en similitud coseno
    nn = NearestNeighbors(n_neighbors=6, metric='cosine')
    nn.fit(features)
    
    # Almacena los IDs de los juegos para acceder fácilmente
    game_ids = steam['item_id'].tolist()

def recomendacion_juego(id_producto, similarity_matrix, num_recomendaciones=5):
    
    indice_juego_consulta = obtener_indice_por_id(id_producto)
    
    if indice_juego_consulta is None:
        return None  
    
    # Obtén las puntuaciones de similitud del juego de consulta con todos los juegos
    similitudes_con_juego_consulta = similarity_matrix[indice_juego_consulta]
    
    # Enumera los juegos y sus puntuaciones de similitud con respecto al juego de consulta
    juegos_y_similitudes = list(enumerate(similitudes_con_juego_consulta))
    
    # Ordena la lista por similitud en orden descendente
    juegos_y_similitudes_ordenados = sorted(juegos_y_similitudes, key=lambda x: x[1], reverse=True)
    
    # Selecciona los juegos más similares (excluyendo el juego de consulta en sí)
    juegos_recomendados = juegos_y_similitudes_ordenados[1:num_recomendaciones + 1]
    
    # Obtiene los nombres de los juegos recomendados en una lista
    nombres_recomendados = [obtener_nombre_por_indice(indice) for indice, _ in juegos_recomendados]
    
    return nombres_recomendados

# Función auxiliar para obtener el nombre del juego por su índice
def obtener_nombre_por_indice(indice):
    # Implementa la lógica para obtener el nombre del juego por su índice
    # Debes ajustar esto según cómo estén estructurados tus datos
    
    # Ejemplo: Supongamos que los nombres de los juegos están en una columna 'appname'
    return steam.iloc[indice]['appname']

# Función auxiliar para obtener el índice del juego por su ID de producto
def obtener_indice_por_id(id_producto):
    # Implementa la lógica para obtener el índice del juego por su ID de producto
    # Debes ajustar esto según cómo estén estructurados tus datos
    
    # Ejemplo: Supongamos que los IDs de producto están en una columna 'productid'
    return steam[steam['item_id'] == id_producto].index[0]

#Mensaje

@app.get('/')
def root():
    """ Mensaje de bienvenida """
    return {"message" : "Bienvenidos!"}

#Funcio API

#Funcion para devolver dinero gastado y recomendaciones

@app.get('/user_id/{user_id}')
def userdata(user_id: str):
    # Validar que el usuario exista en tus datos
    if user_id not in item['user_id'].values:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Filtrar los datos relevantes del usuario en df_item y hacer el join con steam
    user_data = item[item['user_id'] == user_id].explode('item_id').merge(
        steam[['item_id', 'price']], on='item_id', how='left')
    
    # Calcular el total gastado por el usuario
    total_spent = user_data['price'].sum()
    
    # Obtener la cantidad total de items comprados por el usuario
    total_items_bought = user_data['item_id'].count()
    
    # Filtrar las reseñas del usuario en df_reviews
    user_reviews = reviews[reviews['user_id'] == user_id]
    
    # Calcular el total de recomendaciones del usuario
    total_recommendations = user_reviews['recommend'].sum()
    
    # Calcular el porcentaje de recomendación sobre el total comprado
    recommendation_percentage = (total_recommendations / total_items_bought) * 100
    
    # Crear el diccionario con los resultados
    result_dict = {
        'Total Gastado': int(total_spent),
        'Total Comprado': int(total_items_bought),
        'Porcentaje de Recomendacion': float(recommendation_percentage)
    }
    
    return result_dict




@app.get('/reviews/{start_date}/{end_date}')
def countreviews(start_date: str, end_date: str):
    # Verificar el formato de las fechas ingresadas
    
    date_format = "%Y-%m-%d"
    try:
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha incorrecto. Utilice 'YYYY-MM-DD'.")
    
    reviews['posted'] = pd.to_datetime(reviews['posted'], format='%Y-%m-%d')
    
    # Filtrar las reviews entre las fechas dadas
    filtered_reviews = reviews[(reviews['posted'] >= start_date) & (reviews['posted'] <= end_date)]
    
    # Calcular la cantidad de usuarios únicos que realizaron reviews en el período
    unique_users = filtered_reviews['user_id'].nunique()
    
    # Calcular el porcentaje de recomendación
    total_reviews = len(filtered_reviews)
    if total_reviews > 0:
        recommendation_percentage = (filtered_reviews['recommend'].sum() / total_reviews) * 100
    else:
        recommendation_percentage = 0.0
    
    result = {
        'Cantidad de usuarios': unique_users,
        'Porcentaje de recomendaciones ': recommendation_percentage
    }
    
    return result



@app.get('/steam/{genero}')
def genre(genero: str):
    # Filtra las filas en 'ranking_genero' para encontrar el género especificado
    genero_info = ranking_genero[ranking_genero['genre'] == genero]

    # Verifica si el género especificado se encuentra en el DataFrame
    if genero_info.empty:
        return {genero: "No encontrado en los datos"}

    # Obtiene el puesto en el ranking para el género especificado
    position = genero_info.index[0] + 1  # Suma 1 para obtener un ranking 1-indexed

    # Convierte el resultado a una cadena antes de devolverlo como respuesta JSON
    result = {genero: str(position)}

    return result



@app.get('/userforgenre/{genero}')
def userforgenre(genero: str):
    # Filtra el DataFrame 'steam' por el género deseado
    genre_items = steam[steam[genero] == 1]
    
    genre_items['item_id'] = genre_items['item_id'].astype(str)
    play_time['item_id'] = play_time['item_id'].astype(str)
    # Fusiona 'genre_items' con 'play_time' utilizando 'item_id' como clave de fusión
    merged_steam_playtime = genre_items.merge(play_time, on='item_id', how='inner')
    
    # Fusiona el resultado anterior con 'item' utilizando 'user_id' como clave de fusión
    final_merged_data = merged_steam_playtime.merge(item[['user_id', 'user_url']], on='user_id', how='inner')
    
    # Agrupa por 'user_id' y suma las horas de juego
    user_playtime = final_merged_data.groupby('user_id')['playtime_forever'].sum().reset_index()
    
    # Ordena los datos por PlayTimeForever en orden descendente y obtiene el top 5
    top_users = user_playtime.sort_values(by='playtime_forever', ascending=False).head(5)
    
    # Agrega las URLs de los usuarios al resultado final
    top_users = top_users.merge(item[['user_id', 'user_url']], on='user_id', how='left')
    
    # Convierte el DataFrame a un diccionario y devuélvelo
    return top_users[['user_id', 'user_url', 'playtime_forever']].to_dict('records')



@app.get('/developer/{desarrollador}')
def developer(desarrollador: str):
    # Filtrar el DataFrame 'steam' por el desarrollador deseado y crear una copia
    dev_items = steam[steam['developer'] == desarrollador].copy()
    
    # Convertir la columna 'releasedate' a tipo datetime
    dev_items['releasedate'] = pd.to_datetime(dev_items['releasedate'])
    
    # Crear una columna 'is_free' que es True si el precio es 0 y False en caso contrario
    dev_items['is_free'] = dev_items['price'] == 0
    
    # Agrupar por año y calcular la cantidad total de juegos y el porcentaje que eran gratuitos
    dev_stats = dev_items.groupby(dev_items['releasedate'].dt.year).agg({'price': 'count', 'is_free': 'mean'})
    
    # Convertir la proporción de juegos gratuitos a un porcentaje
    dev_stats['is_free'] = dev_stats['is_free'] * 100
    
    # Renombrar las columnas para que sean más descriptivas
    dev_stats.rename(columns={'price': 'Cantidad de juegos', 'is_free': 'Porcentaje de juegos gratuitos'}, inplace=True)
    
    # Convertir el DataFrame a un diccionario y devolverlo
    return dev_stats.to_dict('index')



@app.get('/sentiment/{sentimiento}')

def sentiment_analysis(año: int):
    # Unir los DataFrames en base a una columna común
    df_merged = pd.merge(steam, reviews, left_on='item_id', right_on='item_id')

    # Convierte 'releasedate' a datetime y extrae el año
    df_merged['year'] = pd.to_datetime(df_merged['releasedate']).dt.year

    # Filtra el DataFrame por el año dado
    df_año = df_merged[df_merged['year'] == año]

    # Cuenta las ocurrencias de cada sentimiento
    conteo_sentimientos = df_año['sentiment_analysis'].value_counts().to_dict()

    # Cambia los valores numéricos a etiquetas de texto
    etiquetas_sentimientos = {0: 'Malo', 1: 'Neutral', 2: 'Positivo'}
    conteo_sentimientos = {etiquetas_sentimientos[k]: v for k, v in conteo_sentimientos.items()}

    return conteo_sentimientos



def map_game_ids_to_names(game_ids):
    # Utiliza tu DataFrame de juegos "steam" para mapear los IDs a nombres de juegos
    game_names = []
    for game_id in game_ids:
        game_name = steam[steam['item_id'] == game_id]['appname'].values[0]
        game_names.append(game_name)
    return game_names

@app.get('/recomendacion/{game_id}')
def recomendacion(game_id: int):
    '''Ingresa el ID de un juego y obtén una lista de 5 juegos recomendados similares.'''
    
    # Verifica si el ID de juego ingresado se encuentra en el DataFrame
    if game_id not in game_ids:
        return 'El juego no se encuentra en la base de datos.'
    else:
        # Encuentra el índice correspondiente al ID del juego
        index = game_ids.index(game_id)
        
        # Calcula la similitud entre juegos y obtén los juegos más similares
        similarities = cosine_similarity([features.iloc[index]], features)
        similar_games_indices = similarities.argsort()[0][-6:-1]  # Excluye el juego en sí mismo
        
        # Obtiene los IDs de los juegos recomendados
        recommended_game_ids = [game_ids[i] for i in similar_games_indices]
        
        # Mapea los IDs a nombres de juegos
        recommended_game_names = map_game_ids_to_names(recommended_game_ids)
        
        return recommended_game_names