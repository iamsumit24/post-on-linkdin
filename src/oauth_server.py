# src/oauth_server.py
"""
A tiny Flask helper to perform Authorization Code Flow with LinkedIn and exchange the code for an access token.

Steps:
1. Add your CLIENT_ID, CLIENT_SECRET, REDIRECT_URI in .env
2. Run: python src/oauth_server.py
3. Open http://localhost:8000/ and click the "Authorize" link.
4. After approving, LinkedIn redirects to /callback and the script exchanges the code for a token and saves token.json
"""
import os
import secrets
import requests
import json
from flask import Flask, redirect, request, url_for, jsonify
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/callback")
SCOPES = os.getenv("SCOPES", "w_member_social r_liteprofile r_emailaddress")
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

app = Flask(__name__)
STATE = secrets.token_urlsafe(16)

@app.route("/")
def index():
    if not CLIENT_ID:
        return "<h3>Set CLIENT_ID and CLIENT_SECRET in your .env first</h3>"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": STATE,
        "scope": SCOPES
    }
    auth_link = requests.Request('GET', AUTH_URL, params=params).prepare().url
    return f"<h3>LinkedIn OAuth helper</h3><p><a href='{auth_link}'>Authorize with LinkedIn</a></p>"

@app.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        return f"Error returned: {error} - {request.args.get('error_description')}"
    code = request.args.get("code")
    state = request.args.get("state")
    if state != STATE:
        return "Invalid state. CSRF check failed.", 400
    # Exchange code for access token
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(TOKEN_URL, data=data, headers=headers)
    if r.status_code != 200:
        return f"Failed to get token: {r.status_code} {r.text}", 400
    token_resp = r.json()
    # Save token (for dev only)
    with open("token.json", "w") as f:
        json.dump(token_resp, f, indent=2)
    return jsonify(token_resp)

if __name__ == "__main__":
    # dev server
    app.run(host="0.0.0.0", port=8000, debug=True)
