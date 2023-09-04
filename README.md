# Recomendador de Videojuegos para Usuarios de Steam

Steam, la plataforma multinacional de videojuegos, se enfrenta a un desafío crucial: proporcionar a sus usuarios una experiencia de juego personalizada y atractiva.
Con una vasta biblioteca de títulos, encontrar juegos que se adapten a los gustos y preferencias de cada usuario puede resultar abrumador. Los usuarios pueden sentirse perdidos entre miles de juegos disponibles,
lo que lleva a una experiencia de usuario menos satisfactoria y a la posibilidad de que algunos juegos de calidad pasen desapercibidos.

Por eso vengo a ofrecer un modelo de recomendacion basado en gusto de juegos que otros usuarios han jugado y pueden ser tu agrado y te voy a proporcionar la posibilidad de hacer otras consultas para que tengas mayor
informarcion que puede ser de tu interes.


## Consultas Disponibles

Entre las consultas que te permite el sistema de recomendacion tienes las siguentes:

1. **Recomendar Juegos Basados en el Historial de Compras**:
   - Descripción: Esta consulta recomienda juegos basados en el historial de compras del usuario.
   - Datos Requeridos:
     - ID de Usuario de Steam.
   - Ejemplo:
     
     Consulta: userdata(User_id="12345")
     
     ```

2. **Recomendar Juegos Basados en el Género Favorito**:
   - Descripción: Esta consulta recomienda juegos basados en el género de juego favorito del usuario.
   - Datos Requeridos:
     - ID de Usuario de Steam.
   - Ejemplo:
     
     Consulta: countreviews("2023-01-01", "2023-06-30")

     ```

3. **Posición del Género en el Ranking**:
   - Descripción: Esta consulta devuelve el puesto en el que se encuentra un género en el ranking de géneros, analizado bajo la columna PlayTimeForever.
   - Datos Requeridos:
     - Género.
   - Ejemplo:
     ```python
     Consulta: genre(Género="Aventura")
  
     ```

4. **Top 5 de Usuarios por Género**:
   - Descripción: Esta consulta devuelve el top 5 de usuarios con más horas de juego en el género dado, incluyendo su URL de perfil y su user_id.
   - Datos Requeridos:
     - Género.
   - Ejemplo:
     
     Consulta: userforgenre(Género="Estrategia")
     

5. **Información del Desarrollador**:
   - Descripción: Esta consulta devuelve la cantidad de items y el porcentaje de contenido gratuito por año para una empresa desarrolladora específica.
   - Datos Requeridos:
     - Nombre de la Empresa Desarrolladora.
   - Ejemplo:
     
     Consulta: developer(Desarrollador="Activision")
   
     ```

6. **Análisis de Sentimiento**:
   - Descripción: Según el año de lanzamiento, se devuelve una lista con la cantidad de registros de reseñas de usuarios que se encuentran categorizados con un análisis de sentimiento.
   - Datos Requeridos:
     - Año de Lanzamiento.
   - Ejemplo:
     
     Consulta: sentiment_analysis(año=2021)
     
     ```
7. **Modelo de Recomendacion**:
   -Descripción: Segun el id de un juego que te gusto recibiras 5 juegos con caracterizticas similares que peden ser de tu agrado jugar y pasar unas buenas horas.
   -Datos Requeridos:
     - Id del juego.
   -Ejemplo:
    Consulta:recomendacion_usuario( id de usuario= 12345) 
Estas consultas proporcionan una variedad de funcionalidades útiles para los usuarios de Steam y ayudarán a mejorar su experiencia en la plataforma.
