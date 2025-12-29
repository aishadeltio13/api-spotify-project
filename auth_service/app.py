import os
import requests
import jwt  # <--- NUEVO: Para crear tokens
import datetime # <--- NUEVO: Para poner fecha de caducidad
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# CLAVE SECRETA (Es la "firma" del portero de discoteca)
# Solo el servidor la conoce. Si alguien intenta falsificar el token, no coincidirá.
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def to_json(self):
        return { "id": self.id, "username": self.username }

class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cancion = db.Column(db.String(100), nullable=False)
    artista = db.Column(db.String(100), nullable=False)
    opinion = db.Column(db.String(200), nullable=False)
    imagen_url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "cancion": self.cancion,
            "artista": self.artista,
            "opinion": self.opinion,
            "imagen_url": self.imagen_url,
            "user_id": self.user_id
        }

with app.app_context():
    db.create_all()

# --- RUTAS ---

@app.route('/register', methods=['POST'])
def registrar_usuario():
    datos = request.json
    if Usuario.query.filter_by(username=datos['username']).first():
        return jsonify({"error": "El usuario ya existe"}), 409
    
    nuevo_usuario = Usuario(username=datos['username'], password=datos['password'])
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario registrado", "usuario": nuevo_usuario.to_json()})

# --- LOGIN (Token) ---
@app.route('/login', methods=['POST'])
def login():
    datos = request.json
    # 1. Buscamos al usuario por nombre
    usuario = Usuario.query.filter_by(username=datos['username']).first()
    
    # 2. Comprobamos si existe y si la contraseña coincide
    if not usuario or usuario.password != datos['password']:
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    # 3. GENERAMOS EL TOKEN 
    token = jwt.encode({
        'user_id': usuario.id, 
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30) # Caduca en 30 min
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({"mensaje": "Login correcto", "token": token})

# --- GUARDAR NOTA (PROTEGIDO) ---
@app.route('/notas', methods=['POST'])
def guardar_nota():
    # 1. BUSCAMOS EL TOKEN EN LA CABECERA
    token_recibido = request.headers.get('Authorization') 
    
    if not token_recibido:
        return jsonify({"error": "Falta el token. ¿Hiciste login?"}), 401

    try:
        # Limpiamos el string "Bearer " si viene con él
        if "Bearer " in token_recibido:
            token_recibido = token_recibido.split(" ")[1]

        # 2. DECIFRAMOS EL TOKEN 
        datos_token = jwt.decode(token_recibido, app.config['SECRET_KEY'], algorithms=["HS256"])
        
        # Sacamos el ID del usuario del token
        usuario_id_autenticado = datos_token['user_id']
        
    except:
        return jsonify({"error": "Token inválido o caducado"}), 401

    # -------------------------------------------------------
    # Usamos el ID del token para llamar al otro servicio y obtener la imagen
    # -------------------------------------------------------
    datos = request.json
    cancion_buscada = datos['cancion']
    
    print(f"Usuario ID {usuario_id_autenticado} guarda nota sobre: {cancion_buscada}...")

    # Buscamos foto
    url_foto = "Sin imagen"
    try:
        respuesta = requests.get(f"http://music_service:5000/search?q={cancion_buscada}")
        if respuesta.status_code == 200:
            url_foto = respuesta.json()['tracks']['items'][0]['album']['images'][0]['url']
    except Exception as e:
        print(f"Error music_service: {e}")

    # Guardamos la nota usando el ID que venía en el Token (NO el del JSON)
    nueva_nota = Nota(
        cancion=cancion_buscada, 
        artista=datos['artista'], 
        opinion=datos['mi_opinion'],
        imagen_url=url_foto,
        user_id=usuario_id_autenticado # <--- ID DEL TOKEN 
    )
    
    db.session.add(nueva_nota)
    db.session.commit()
    
    return jsonify({"mensaje": "Nota guardada", "nota": nueva_nota.to_json()})

@app.route('/notas', methods=['GET'])
def leer_notas():
    todas_las_notas = Nota.query.all()
    return jsonify([nota.to_json() for nota in todas_las_notas])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)