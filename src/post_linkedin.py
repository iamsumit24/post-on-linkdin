# src/post_linkedin.py
"""
Usage (quick):
  - Fill .env or set env vars LINKEDIN_ACCESS_TOKEN / LINKEDIN_AUTHOR_URN
  - python src/post_linkedin.py --message "Hello from Sumit via API"

This script:
 - Optionally fetches the author URN using /me if AUTHOR_URN not provided.
 - Posts a text-only UGC post via POST https://api.linkedin.com/v2/ugcPosts
"""
import os
import argparse
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://api.linkedin.com/v2"
RESTLI_HEADER = {"X-Restli-Protocol-Version": "2.0.0"}

def get_access_token():
    # priority: explicit env var ACCESS_TOKEN, otherwise LINKEDIN_ACCESS_TOKEN
    return os.getenv("ACCESS_TOKEN") or os.getenv("LINKEDIN_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")

def get_author_urn(access_token):
    """
    GET /me to discover the member id and return urn:li:person:{id}
    Requires a valid access token with profile scopes.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        **RESTLI_HEADER,
        "Accept": "application/json"
    }
    resp = requests.get(f"{API_BASE}/me", headers=headers)
    if resp.status_code != 200:
        raise SystemExit(f"Failed to fetch /me: {resp.status_code} {resp.text}")
    data = resp.json()
    # docs: /me returns an 'id' used as person id
    person_id = data.get("id")
    if not person_id:
        raise SystemExit(f"Could not find 'id' in /me response: {data}")
    return f"urn:li:person:{person_id}"

def post_text(access_token, author_urn, text, visibility="PUBLIC"):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        **RESTLI_HEADER
    }

    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": visibility
        }
    }

    url = f"{API_BASE}/ugcPosts"
    resp = requests.post(url, headers=headers, json=payload)
    try:
        j = resp.json()
    except Exception:
        j = resp.text
    return resp.status_code, j

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--message", "-m", required=True, help="Message text to post")
    parser.add_argument("--author", help="Author URN (urn:li:person:...) - optional")
    parser.add_argument("--token", help="Access token - optional (env var preferred)")
    args = parser.parse_args()

    access_token = args.token or get_access_token()
    if not access_token:
        raise SystemExit("No access token provided. Set ACCESS_TOKEN env var or pass --token. Use oauth_server.py to obtain one.")

    author = args.author or os.getenv("AUTHOR_URN") or os.getenv("LINKEDIN_AUTHOR_URN")
    if not author:
        print("Author URN not provided — fetching via /me ...")
        author = get_author_urn(access_token)
        print("Detected author urn:", author)

    status, body = post_text(access_token, author, args.message)
    print("Status:", status)
    print("Response:", json.dumps(body, indent=2))

if __name__ == "__main__":
    main()
