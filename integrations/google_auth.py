import os
from typing import Optional, Dict
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

# Load environment variables
config = Config()
config.update({
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
    "GOOGLE_REDIRECT_URI": os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
})


def build_google_oauth_client():
    """
    Build and return a Google OAuth client using Authlib.
    """
    oauth = OAuth(config)
    oauth.register(
        name='google',
        client_id=config.get("GOOGLE_CLIENT_ID"),
        client_secret=config.get("GOOGLE_CLIENT_SECRET"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    return oauth


def get_login_url(oauth_client, redirect_uri: Optional[str] = None) -> str:
    """
    Generate the Google OAuth login URL.
    
    Args:
        oauth_client: The OAuth client instance
        redirect_uri: Optional override for redirect URI
    
    Returns:
        The authorization URL
    """
    # Placeholder - will be implemented with actual OAuth flow
    return "https://accounts.google.com/o/oauth2/v2/auth"


def exchange_code(oauth_client, code: str) -> Optional[Dict]:
    """
    Exchange authorization code for access token.
    
    Args:
        oauth_client: The OAuth client instance
        code: The authorization code from callback
    
    Returns:
        Token dictionary or None if failed
    """
    # Placeholder - will be implemented with actual OAuth flow
    return None


def get_user_info(oauth_client, token: Dict) -> Optional[Dict]:
    """
    Get user information from Google using the access token.
    
    Args:
        oauth_client: The OAuth client instance
        token: The token dictionary
    
    Returns:
        User information dictionary or None if failed
    """
    # Placeholder - will be implemented with actual OAuth flow
    return None
