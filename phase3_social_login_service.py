"""
Social Login Service
====================

This module provides OAuth 2.0 integration for social login functionality,
allowing users to authenticate using their social media accounts.

Supported Platforms:
- Google
- Facebook
- GitHub

Author: Manus AI
Date: 2025-10-20
"""

from typing import Dict, Optional, Tuple
from abc import ABC, abstractmethod
import json
import requests
from datetime import datetime, timedelta
import hashlib
import secrets


class OAuthProvider(ABC):
    """Base class for OAuth providers."""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize OAuth provider.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: Redirect URI after authentication
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.name = self.__class__.__name__

    @abstractmethod
    def get_authorization_url(self, state: str, scope: str = None) -> str:
        """
        Get authorization URL for user to visit.

        Args:
            state: State parameter for CSRF protection
            scope: OAuth scopes to request

        Returns:
            Authorization URL
        """
        pass

    @abstractmethod
    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth provider

        Returns:
            Token response dictionary
        """
        pass

    @abstractmethod
    def get_user_info(self, access_token: str) -> Dict:
        """
        Get user information using access token.

        Args:
            access_token: OAuth access token

        Returns:
            User information dictionary
        """
        pass


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth 2.0 implementation."""

    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def get_authorization_url(self, state: str, scope: str = None) -> str:
        """Get Google authorization URL."""
        if scope is None:
            scope = "openid email profile"

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'state': state,
            'access_type': 'offline',
        }

        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTHORIZATION_URL}?{query_string}"

    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for Google access token."""
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
        }

        try:
            response = requests.post(self.TOKEN_URL, data=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to exchange code for token: {e}")

    def get_user_info(self, access_token: str) -> Dict:
        """Get user information from Google."""
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(self.USER_INFO_URL, headers=headers)
            response.raise_for_status()
            user_data = response.json()

            return {
                'id': user_data.get('id'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'picture': user_data.get('picture'),
                'provider': 'google',
            }
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to get user info: {e}")


class FacebookOAuthProvider(OAuthProvider):
    """Facebook OAuth 2.0 implementation."""

    AUTHORIZATION_URL = "https://www.facebook.com/v12.0/dialog/oauth"
    TOKEN_URL = "https://graph.facebook.com/v12.0/oauth/access_token"
    USER_INFO_URL = "https://graph.facebook.com/me"

    def get_authorization_url(self, state: str, scope: str = None) -> str:
        """Get Facebook authorization URL."""
        if scope is None:
            scope = "public_profile,email"

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': scope,
            'state': state,
            'response_type': 'code',
        }

        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTHORIZATION_URL}?{query_string}"

    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for Facebook access token."""
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
        }

        try:
            response = requests.get(self.TOKEN_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to exchange code for token: {e}")

    def get_user_info(self, access_token: str) -> Dict:
        """Get user information from Facebook."""
        params = {
            'fields': 'id,name,email,picture',
            'access_token': access_token,
        }

        try:
            response = requests.get(self.USER_INFO_URL, params=params)
            response.raise_for_status()
            user_data = response.json()

            return {
                'id': user_data.get('id'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'picture': user_data.get('picture', {}).get('data', {}).get('url'),
                'provider': 'facebook',
            }
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to get user info: {e}")


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth 2.0 implementation."""

    AUTHORIZATION_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_INFO_URL = "https://api.github.com/user"

    def get_authorization_url(self, state: str, scope: str = None) -> str:
        """Get GitHub authorization URL."""
        if scope is None:
            scope = "user:email"

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': scope,
            'state': state,
        }

        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTHORIZATION_URL}?{query_string}"

    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for GitHub access token."""
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
        }

        headers = {'Accept': 'application/json'}

        try:
            response = requests.post(self.TOKEN_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to exchange code for token: {e}")

    def get_user_info(self, access_token: str) -> Dict:
        """Get user information from GitHub."""
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json',
        }

        try:
            response = requests.get(self.USER_INFO_URL, headers=headers)
            response.raise_for_status()
            user_data = response.json()

            return {
                'id': user_data.get('id'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'picture': user_data.get('avatar_url'),
                'provider': 'github',
            }
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to get user info: {e}")


class SocialLoginManager:
    """Manages social login functionality."""

    def __init__(self):
        """Initialize the social login manager."""
        self.providers: Dict[str, OAuthProvider] = {}
        self.sessions: Dict[str, Dict] = {}

    def register_provider(self, name: str, provider: OAuthProvider) -> None:
        """
        Register an OAuth provider.

        Args:
            name: Provider name
            provider: OAuthProvider instance
        """
        self.providers[name] = provider

    def get_authorization_url(self, provider_name: str) -> Tuple[str, str]:
        """
        Get authorization URL for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Tuple of (authorization_url, state)
        """
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not registered")

        state = secrets.token_urlsafe(32)
        provider = self.providers[provider_name]
        auth_url = provider.get_authorization_url(state)

        # Store state for verification
        self.sessions[state] = {
            'provider': provider_name,
            'created_at': datetime.utcnow().isoformat(),
        }

        return auth_url, state

    def handle_callback(self, provider_name: str, code: str, state: str) -> Dict:
        """
        Handle OAuth callback.

        Args:
            provider_name: Name of the provider
            code: Authorization code
            state: State parameter

        Returns:
            User information dictionary
        """
        # Verify state
        if state not in self.sessions:
            raise ValueError("Invalid state parameter")

        session = self.sessions[state]
        if session['provider'] != provider_name:
            raise ValueError("Provider mismatch")

        # Clean up session
        del self.sessions[state]

        # Get provider
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not registered")

        provider = self.providers[provider_name]

        # Exchange code for token
        token_response = provider.exchange_code_for_token(code)
        access_token = token_response.get('access_token')

        if not access_token:
            raise ValueError("Failed to get access token")

        # Get user info
        user_info = provider.get_user_info(access_token)

        return {
            'user': user_info,
            'token': access_token,
            'provider': provider_name,
        }

    def link_social_account(self, user_id: str, provider_name: str, social_id: str) -> None:
        """
        Link a social account to a user.

        Args:
            user_id: IDEA system user ID
            provider_name: OAuth provider name
            social_id: Social media user ID
        """
        # TODO: Store in database
        pass

    def unlink_social_account(self, user_id: str, provider_name: str) -> None:
        """
        Unlink a social account from a user.

        Args:
            user_id: IDEA system user ID
            provider_name: OAuth provider name
        """
        # TODO: Remove from database
        pass


class SocialLoginButton:
    """HTML component for social login buttons."""

    @staticmethod
    def generate_button(provider_name: str, auth_url: str) -> str:
        """
        Generate HTML for a social login button.

        Args:
            provider_name: Name of the provider
            auth_url: Authorization URL

        Returns:
            HTML string for the button
        """
        button_text = f"تسجيل الدخول عبر {provider_name}"
        icon = SocialLoginButton._get_provider_icon(provider_name)

        return f'''
<a href="{auth_url}" class="social-login-btn social-login-{provider_name.lower()}">
    {icon}
    <span>{button_text}</span>
</a>
'''

    @staticmethod
    def generate_buttons(auth_urls: Dict[str, str]) -> str:
        """
        Generate HTML for multiple social login buttons.

        Args:
            auth_urls: Dictionary mapping provider names to auth URLs

        Returns:
            HTML string for the buttons
        """
        html = '<div class="social-login-buttons">\n'

        for provider_name, auth_url in auth_urls.items():
            html += SocialLoginButton.generate_button(provider_name, auth_url)

        html += '</div>'
        return html

    @staticmethod
    def _get_provider_icon(provider_name: str) -> str:
        """Get icon for a provider."""
        icons = {
            'google': '🔵',
            'facebook': '📘',
            'github': '🐙',
        }
        return icons.get(provider_name.lower(), '→')


# Global social login manager instance
social_login = SocialLoginManager()


if __name__ == "__main__":
    # Example usage
    print("Social Login Service")
    print("=" * 50)

    # Register providers (with dummy credentials for demonstration)
    google_provider = GoogleOAuthProvider(
        client_id="your-google-client-id",
        client_secret="your-google-client-secret",
        redirect_uri="https://idea-system.com/auth/google/callback"
    )

    facebook_provider = FacebookOAuthProvider(
        client_id="your-facebook-app-id",
        client_secret="your-facebook-app-secret",
        redirect_uri="https://idea-system.com/auth/facebook/callback"
    )

    github_provider = GitHubOAuthProvider(
        client_id="your-github-client-id",
        client_secret="your-github-client-secret",
        redirect_uri="https://idea-system.com/auth/github/callback"
    )

    social_login.register_provider('google', google_provider)
    social_login.register_provider('facebook', facebook_provider)
    social_login.register_provider('github', github_provider)

    # Generate authorization URLs
    print("\nAuthorization URLs:")
    for provider_name in ['google', 'facebook', 'github']:
        auth_url, state = social_login.get_authorization_url(provider_name)
        print(f"\n{provider_name.upper()}:")
        print(f"  URL: {auth_url[:80]}...")
        print(f"  State: {state}")

    # Generate HTML buttons
    print("\n\nHTML Buttons:")
    auth_urls = {
        'Google': 'https://accounts.google.com/o/oauth2/v2/auth?...',
        'Facebook': 'https://www.facebook.com/v12.0/dialog/oauth?...',
        'GitHub': 'https://github.com/login/oauth/authorize?...',
    }
    buttons = SocialLoginButton.generate_buttons(auth_urls)
    print(buttons)

