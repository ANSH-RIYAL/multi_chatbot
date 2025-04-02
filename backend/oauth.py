from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
from fastapi import HTTPException, status
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# OAuth configuration
GOOGLE_CLIENT_SECRETS_FILE = "client_secrets.json"
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/generative-language.runtime',
    'https://www.googleapis.com/auth/userinfo.email'
]

class OAuthManager:
    def __init__(self):
        self.tokens_file = "data/oauth_tokens.json"
        self.tokens = self._load_tokens()

    def _load_tokens(self):
        """Load OAuth tokens from file"""
        if os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_tokens(self):
        """Save OAuth tokens to file"""
        os.makedirs(os.path.dirname(self.tokens_file), exist_ok=True)
        with open(self.tokens_file, 'w') as f:
            json.dump(self.tokens, f)

    def get_google_auth_url(self, email: str) -> str:
        """Get Google OAuth authorization URL"""
        try:
            flow = Flow.from_client_secrets_file(
                GOOGLE_CLIENT_SECRETS_FILE,
                scopes=GOOGLE_SCOPES,
                redirect_uri="http://localhost:8000/api/oauth/google/callback"
            )
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                login_hint=email
            )
            return auth_url
        except Exception as e:
            logger.error(f"Error creating Google auth URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create authorization URL"
            )

    async def handle_google_callback(self, code: str, email: str):
        """Handle Google OAuth callback"""
        try:
            flow = Flow.from_client_secrets_file(
                GOOGLE_CLIENT_SECRETS_FILE,
                scopes=GOOGLE_SCOPES,
                redirect_uri="http://localhost:8000/api/oauth/google/callback"
            )
            
            flow.fetch_token(code=code)
            credentials = flow.credentials

            # Save tokens
            self.tokens[email] = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            self._save_tokens()
            
            return {"message": "Successfully authenticated with Google"}
        except Exception as e:
            logger.error(f"Error handling Google callback: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete authentication"
            )

    def get_google_credentials(self, email: str) -> Credentials:
        """Get Google credentials for a user"""
        if email not in self.tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated with Google"
            )

        token_data = self.tokens[email]
        credentials = Credentials(
            token=token_data['token'],
            refresh_token=token_data['refresh_token'],
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
        )

        if credentials.expired:
            credentials.refresh(Request())
            # Update stored token
            token_data['token'] = credentials.token
            self._save_tokens()

        return credentials 