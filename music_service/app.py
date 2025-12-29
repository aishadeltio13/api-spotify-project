import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# 1. Configuración: Cargamos las credenciales y las URLs de Spotify
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
# URL para pedir el Token
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
# URL para buscar datos
SPOTIFY_API_URL = 'https://api.spotify.com/v1/search'

def get_spotify_token():
    """
    Función auxiliar: Solo se encarga de conseguir el Token.
    """
    # Preparamos los datos para identificarnos
    credenciales = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    # Hacemos la llamada a la puerta de seguridad de Spotify
    response = requests.post(SPOTIFY_TOKEN_URL, data=credenciales)
    
    # Devolvemos solo el texto del token
    return response.json().get('access_token')

@app.route('/search', methods=['GET'])
def search_music():
    """
    Función Principal: Recibe tu petición de Postman y orquesta todo.
    """
    # 1. Capturamos Postman 
    busqueda_usuario = request.args.get('q')

    # 2. Llamamos a la función de arriba para conseguir el Token
    token = get_spotify_token()

    # 3. Preparamos la petición a la base de datos de música
    headers = {
        "Authorization": f"Bearer {token}"  # Pegamos el pase VIP en la frente
    }
    params = {
        "q": busqueda_usuario,
        "type": "track",
        "limit": 3  # Pedimos solo 3 resultados para no saturar
    }

    # 4. Llamamos a Spotify
    respuesta_spotify = requests.get(SPOTIFY_API_URL, headers=headers, params=params)

    # 5. EL RETORNO: Flask coge estos datos y los envía de vuelta a Postman
    return jsonify(respuesta_spotify.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)