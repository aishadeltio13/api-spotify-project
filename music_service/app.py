import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    has_creds = "Yes" if client_id else "No"
    
    return jsonify({
        "service": "Music Service",
        "status": "Running",
        "credentials_loaded": has_creds,
        "port": 5001
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)