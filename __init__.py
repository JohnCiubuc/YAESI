import webbrowser
import threading
from flask import Flask, request, redirect, session, jsonify
import requests
import base64
import os
import asyncio
from PyQt5.QtWidgets import QApplication

class YAESI:
    _character_id = -1

    def _get(self, url):
        return requests.get(url, headers=self._headers)

    def __init__(self, client_id, client_secret, scopes):
        self._CLIENT_ID = client_id
        self._CLIENT_SECRET = client_secret
        self._YA_ESI = "http://localhost:8635/"
        self._ESI = "https://esi.evetech.net/latest/"
        self._ESI_AUTH = "https://esi.evetech.net/"
        self._USER_AGENT = 'YAESI/1.0 (X11; Linux x86_64) Flask'
        self._AUTH_URL = 'https://login.eveonline.com/v2/oauth/authorize/'
        self._TOKEN_URL = 'https://login.eveonline.com/v2/oauth/token'
        self._SCOPES = scopes
        self._CHARACTER_ID = None

        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)
        self.app.add_url_rule('/', view_func=self._home)
        self.app.add_url_rule('/callback', view_func=self._callback)

        self.flask_thread = threading.Thread(target=self._run_flask_app)
        self.flask_thread.daemon = True
        self.flask_thread.start()

        # Open the browser
        webbrowser.open_new('http://localhost:8635')

    def _run_flask_app(self):
        self.app.run(port=8635)

    def _home(self):
        state = os.urandom(16).hex()
        session['state'] = state
        auth_params = {
            'response_type': 'code',
            'redirect_uri': self._YA_ESI + 'callback',
            'client_id': self._CLIENT_ID,
            'scope': self._SCOPES,
            'state': state
        }
        auth_url = requests.Request('GET', self._AUTH_URL, params=auth_params).prepare().url
        return redirect(auth_url)

    def _get_access_token(self, code):
        auth_str = f'{self._CLIENT_ID}:{self._CLIENT_SECRET}'
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()

        headers = {
            'Authorization': f'Basic {b64_auth_str}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': self._USER_AGENT
        }

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self._YA_ESI + 'callback'
        }

        response = requests.post(self._TOKEN_URL, headers=headers, data=data)
        self._token = response.json()['access_token']

        self._headers = {
            'Authorization': f'Bearer {self._token}',
            'User-Agent': self._USER_AGENT
        }

        verify_response = self._get(self._ESI_AUTH + 'verify')

        return str(verify_response.json()['CharacterID'])

    def _callback(self):
        if 'state' not in session or request.args.get('state') != session['state']:
            return 'State mismatch', 400

        code = request.args.get('code')
        if self._character_id == -1:
            self._character_id = self._get_access_token(code)
        return ""

    def character_location(self):
        location_url = self._ESI + "characters/" + self._character_id + '/location/'
        location_response = self._get(location_url)
        if location_response.status_code == 200:
            return location_response.json()
        return {'error': 'Character location not found or search failed.', 'location':location_url}

    def character_(self):
        location_url = self._ESI + "characters/" + str(self._character_id) + '/location/'
        location_response = self._get(location_url)
        if location_response.status_code == 200:
            return location_response.json()
        return {'error': 'Character location not found or search failed.', 'location':location_url}
