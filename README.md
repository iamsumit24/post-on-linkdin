# LinkedIn Poster (Python)

Small repo to create and post a text message on LinkedIn using Python and LinkedIn's UGC API.

## What this repo contains
- `src/oauth_server.py` – tiny Flask app to run the OAuth Authorization Code flow and exchange a `code` for an access token (saves `token.json`).
- `src/post_linkedin.py` – script to post a text message to LinkedIn. It will fetch your author URN via `/me` if not provided.

## Important API facts
- Create posts using the User Generated Content endpoint: `POST https://api.linkedin.com/v2/ugcPosts`. All UGC requests require the `X-Restli-Protocol-Version: 2.0.0` header. :contentReference[oaicite:6]{index=6}  
- To post on behalf of a member you must request the `w_member_social` scope for your app. :contentReference[oaicite:7]{index=7}  
- Use OAuth2 Authorization Code Flow to get access tokens (tokens currently have a ~60-day lifetime). Plan to refresh tokens or re-authorize. :contentReference[oaicite:8]{index=8}  
- To determine the author URN use `GET https://api.linkedin.com/v2/me` (returns the `id` used to form `urn:li:person:{id}`). :contentReference[oaicite:9]{index=9}  
- If you plan to post images you must upload the image with the Images API and reference its URN in the post. :contentReference[oaicite:10]{index=10}

## Quick setup (dev/test)
1. Clone this repo.
2. `python -m venv venv && source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
3. `pip install -r requirements.txt`
4. Copy `.env.example` → `.env` and fill `CLIENT_ID` and `CLIENT_SECRET` and `REDIRECT_URI`. Optionally leave `ACCESS_TOKEN` empty and use the OAuth helper.

### Option A - Quick token (DEV only)
- On the LinkedIn Developer portal you can use the Token Generator (developer tools) to create a token for your app for quick tests. Paste that token as `ACCESS_TOKEN` in `.env`. :contentReference[oaicite:11]{index=11}

### Option B - Full OAuth flow (recommended for repeated runs)
1. Ensure your app has `Redirect URI` configured to the same `REDIRECT_URI` in `.env`.
2. Run `python src/oauth_server.py` then open `http://localhost:8000` and click the authorize link.
3. After approval LinkedIn will redirect to `/callback` and the token JSON will be saved to `token.json`. Copy `access_token` to your `.env` or pass it as `--token`.

## Post a message
