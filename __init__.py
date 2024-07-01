import webbrowser
from flask import Flask, request, redirect, session, jsonify
import requests
import base64
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_ID = '1d10ce402ccc42b6b69ee684b0d6a3e7'
CLIENT_SECRET = 'f7w7GXbmn459hq5dOd5bk8n2d4qp1lur5J3nXp5o'
REDIRECT_URI = 'http://localhost:8635/callback'
USER_AGENT = 'wormhole.checker.v1'
AUTH_URL = 'https://login.eveonline.com/v2/oauth/authorize/'
TOKEN_URL = 'https://login.eveonline.com/v2/oauth/token'
SCOPES = 'esi-location.read_location.v1'
API = "https://esi.evetech.net/"
CHARACTER_ID = None

@app.route('/')
def home():
    state = os.urandom(16).hex()
    session['state'] = state
    auth_params = {
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'scope': SCOPES,
        'state': state
    }
    auth_url = requests.Request('GET', AUTH_URL, params=auth_params).prepare().url
    return redirect(auth_url)


def get_access_token(code):
    auth_str = f'{CLIENT_ID}:{CLIENT_SECRET}'
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        'Authorization': f'Basic {b64_auth_str}',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': USER_AGENT
    }

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    access_token = response.json()['access_token']

    # Get Character ID
    verify_headers = {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': USER_AGENT
    }
    verify_response = requests.get(API + "verify", headers=verify_headers)
    print(verify_response)
    character_id = verify_response.json()['CharacterID']

    return access_token, character_id

@app.route('/callback')
def callback():
    if 'state' not in session or request.args.get('state') != session['state']:
        return 'State mismatch', 400

    code = request.args.get('code')
    token, character_id = get_access_token(code)
    character_location = get_character_location(token, character_id)
    return jsonify(character_location)

def get_character_location(token, character_id):
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': USER_AGENT
    }

    location_url = f'https://esi.evetech.net/latest/characters/{character_id}/location/'
    location_response = requests.get(location_url, headers=headers)
    if location_response.status_code == 200:
        return location_response.json()
    return {'error': 'Character location not found or search failed.'}

if __name__ == "__main__":
    webbrowser.open_new('http://localhost:8635')
    app.run(port=8635)
