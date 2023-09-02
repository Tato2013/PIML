import pandas as pd
import numpy as np
from fastapi import FastAPI, Query

app = FastAPI()

#DataFrame a utilizar
reviews=pd.read_parquet('reviews.parquet')
steam=pd.read_parquet('steam.parquet')
item=pd.read_parquet('item.parquet')


#Mensaje

@app.get('/')
def root():
    """ Mensaje de bienvenida """
    return {"message" : "Bienvenidos!"}

#Funcio API

#Funcion para devolver dinero gastado y recomendaciones

@app.get('/user_id/{user_id}')
def userdata(user_id: str):
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
        'total_spent': total_spent,
        'total_items_bought': total_items_bought,
        'recommendation_percentage': recommendation_percentage
    }
    
    return result_dict



@app.get('/reviews/{start_date}/{end_date}')

def countreviews(start_date: str, end_date: str):
    # Convertir las fechas de inicio y fin a objetos datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filtrar las reviews entre las fechas dadas
    filtered_reviews = reviews[(reviews['posted'] >= start_date) & (reviews['posted'] <= end_date)]
    
    # Calcular la cantidad de usuarios únicos que realizaron reviews en el período
    unique_users = filtered_reviews['user_id'].nunique()
    
    # Calcular el porcentaje de recomendación
    recommendation_percentage = (filtered_reviews['recommend'].sum() / len(filtered_reviews)) * 100
    
    result = {
        'unique_users': unique_users,
        'recommendation_percentage': recommendation_percentage
    }
    
    return result



@app.get('/steam/{genero}')

def genre(género: str):
    # Asegúrate de que 'steam' e 'item' son accesibles dentro de esta función
    global steam, item

    # Unir los DataFrames en base a la columna 'item_id'
    df_merged = pd.merge(steam, item, on='item_id')

    # Calcula la suma total de 'playtime_forever' para cada género
    playtime_por_género = df_merged.loc[:, 'action':'web publishing'].multiply(df_merged['playtime_forever'], axis="index").sum()

    # Crea un ranking de géneros por 'playtime_forever'
    ranking = playtime_por_género.sort_values(ascending=False)

    # Encuentra el puesto del género dado en el ranking
    puesto = ranking.index.get_loc(género) + 1

    # Devuelve un diccionario con el género y su puesto
    return {género: puesto}



@app.get('/genero/{genero}')

def userforgenre(genero: str):
    # Filtrar el DataFrame 'steam' por el género deseado
    genre_items = steam[steam[genero] == 1]
    
    # Merge de 'genre_items' con 'item' para obtener la información de PlayTimeForever y user_url
    merged_data = genre_items.merge(item[['item_id', 'playtime_forever', 'user_id', 'user_url']], left_on='item_id', right_on='item_id', how='inner')
    
    # Agrupar por 'user_id' y sumar las horas de juego
    user_playtime = merged_data.groupby('user_id')['playtime_forever'].sum().reset_index()
    
    # Ordenar los datos por PlayTimeForever en orden descendente y obtener el top 5
    top_users = user_playtime.sort_values(by='playtime_forever', ascending=False).head(5)
    
    # Agregar las URLs de los usuarios al resultado final
    top_users = top_users.merge(item[['user_id', 'user_url']], on='user_id', how='left')
    
    # Convertir el DataFrame a un diccionario y devolverlo
    return top_users[['user_id', 'user_url', 'playtime_forever']].to_dict('records')




@app.get('/developer/{desarrolador}')


def developer(desarrollador: str):
    # Filtrar el DataFrame 'steam' por el desarrollador deseado y crear una copia
    dev_items = steam[steam['developer'] == desarrollador].copy()
    
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