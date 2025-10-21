"""
Social Content Aggregator
==========================

This module aggregates and displays content from various social media platforms
into a unified feed within the IDEA system.

Features:
- Fetch posts from Twitter, Facebook, Instagram, LinkedIn
- Unified content feed
- Content filtering and sorting
- Caching for performance

Author: Manus AI
Date: 2025-10-20
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json
import requests
from dataclasses import dataclass, asdict


@dataclass
class SocialPost:
    """Represents a social media post."""

    id: str
    platform: str
    author: str
    author_avatar: str
    content: str
    timestamp: datetime
    likes: int = 0
    comments: int = 0
    shares: int = 0
    media_urls: List[str] = None
    url: str = None
    hashtags: List[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class SocialMediaProvider(ABC):
    """Base class for social media providers."""

    def __init__(self, access_token: str):
        """
        Initialize provider.

        Args:
            access_token: API access token
        """
        self.access_token = access_token
        self.name = self.__class__.__name__

    @abstractmethod
    def fetch_posts(self, user_id: str, limit: int = 10) -> List[SocialPost]:
        """
        Fetch posts from the platform.

        Args:
            user_id: User ID on the platform
            limit: Maximum number of posts to fetch

        Returns:
            List of SocialPost objects
        """
        pass

    @abstractmethod
    def get_post_analytics(self, post_id: str) -> Dict:
        """
        Get analytics for a post.

        Args:
            post_id: Post ID

        Returns:
            Dictionary with analytics data
        """
        pass


class TwitterProvider(SocialMediaProvider):
    """Twitter API provider."""

    API_URL = "https://api.twitter.com/2"

    def fetch_posts(self, user_id: str, limit: int = 10) -> List[SocialPost]:
        """Fetch tweets from a user."""
        posts = []

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
            }

            # Get user tweets
            url = f"{self.API_URL}/users/{user_id}/tweets"
            params = {
                'max_results': min(limit, 100),
                'tweet.fields': 'created_at,public_metrics',
                'expansions': 'author_id',
                'user.fields': 'username,profile_image_url',
            }

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if 'data' not in data:
                return posts

            users = {u['id']: u for u in data.get('includes', {}).get('users', [])}

            for tweet in data['data']:
                user = users.get(tweet['author_id'], {})
                metrics = tweet.get('public_metrics', {})

                post = SocialPost(
                    id=tweet['id'],
                    platform='twitter',
                    author=user.get('username', 'Unknown'),
                    author_avatar=user.get('profile_image_url', ''),
                    content=tweet['text'],
                    timestamp=datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00')),
                    likes=metrics.get('like_count', 0),
                    comments=metrics.get('reply_count', 0),
                    shares=metrics.get('retweet_count', 0),
                    url=f"https://twitter.com/{user.get('username')}/status/{tweet['id']}",
                )

                posts.append(post)

        except Exception as e:
            print(f"Error fetching Twitter posts: {e}")

        return posts

    def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a tweet."""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
            }

            url = f"{self.API_URL}/tweets/{post_id}"
            params = {
                'tweet.fields': 'created_at,public_metrics,impression_count',
            }

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            metrics = data['data'].get('public_metrics', {})

            return {
                'platform': 'twitter',
                'post_id': post_id,
                'likes': metrics.get('like_count', 0),
                'comments': metrics.get('reply_count', 0),
                'shares': metrics.get('retweet_count', 0),
                'impressions': data['data'].get('impression_count', 0),
            }

        except Exception as e:
            print(f"Error fetching Twitter analytics: {e}")
            return {}


class FacebookProvider(SocialMediaProvider):
    """Facebook API provider."""

    API_URL = "https://graph.facebook.com/v12.0"

    def fetch_posts(self, user_id: str, limit: int = 10) -> List[SocialPost]:
        """Fetch posts from a Facebook page."""
        posts = []

        try:
            url = f"{self.API_URL}/{user_id}/feed"
            params = {
                'fields': 'id,message,story,created_time,likes.summary(true).limit(0),comments.summary(true).limit(0),shares',
                'limit': limit,
                'access_token': self.access_token,
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            for post in data.get('data', []):
                post_obj = SocialPost(
                    id=post['id'],
                    platform='facebook',
                    author='Facebook Page',
                    author_avatar='',
                    content=post.get('message', post.get('story', '')),
                    timestamp=datetime.fromisoformat(post['created_time'].replace('Z', '+00:00')),
                    likes=post.get('likes', {}).get('summary', {}).get('total_count', 0),
                    comments=post.get('comments', {}).get('summary', {}).get('total_count', 0),
                    shares=post.get('shares', {}).get('count', 0),
                    url=f"https://facebook.com/{post['id']}",
                )

                posts.append(post_obj)

        except Exception as e:
            print(f"Error fetching Facebook posts: {e}")

        return posts

    def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a Facebook post."""
        try:
            url = f"{self.API_URL}/{post_id}"
            params = {
                'fields': 'likes.summary(true).limit(0),comments.summary(true).limit(0),shares',
                'access_token': self.access_token,
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            return {
                'platform': 'facebook',
                'post_id': post_id,
                'likes': data.get('likes', {}).get('summary', {}).get('total_count', 0),
                'comments': data.get('comments', {}).get('summary', {}).get('total_count', 0),
                'shares': data.get('shares', {}).get('count', 0),
            }

        except Exception as e:
            print(f"Error fetching Facebook analytics: {e}")
            return {}


class LinkedInProvider(SocialMediaProvider):
    """LinkedIn API provider."""

    API_URL = "https://api.linkedin.com/v2"

    def fetch_posts(self, user_id: str, limit: int = 10) -> List[SocialPost]:
        """Fetch posts from a LinkedIn profile."""
        posts = []

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
            }

            url = f"{self.API_URL}/me/posts"
            params = {'count': limit}

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            for post in data.get('elements', []):
                post_obj = SocialPost(
                    id=post['id'],
                    platform='linkedin',
                    author='LinkedIn User',
                    author_avatar='',
                    content=post.get('commentary', ''),
                    timestamp=datetime.fromtimestamp(post.get('created', {}).get('time', 0) / 1000),
                    likes=post.get('likesSummary', {}).get('totalLikes', 0),
                    comments=post.get('commentsSummary', {}).get('totalComments', 0),
                    url=f"https://linkedin.com/feed/update/{post['id']}",
                )

                posts.append(post_obj)

        except Exception as e:
            print(f"Error fetching LinkedIn posts: {e}")

        return posts

    def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a LinkedIn post."""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
            }

            url = f"{self.API_URL}/posts/{post_id}"

            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            return {
                'platform': 'linkedin',
                'post_id': post_id,
                'likes': data.get('likesSummary', {}).get('totalLikes', 0),
                'comments': data.get('commentsSummary', {}).get('totalComments', 0),
                'impressions': data.get('impressionsSummary', {}).get('totalImpressions', 0),
            }

        except Exception as e:
            print(f"Error fetching LinkedIn analytics: {e}")
            return {}


class ContentAggregator:
    """Aggregates content from multiple social media platforms."""

    def __init__(self):
        """Initialize the aggregator."""
        self.providers: Dict[str, SocialMediaProvider] = {}
        self.cache: Dict[str, List[SocialPost]] = {}
        self.cache_ttl = timedelta(minutes=15)
        self.cache_time: Dict[str, datetime] = {}

    def register_provider(self, name: str, provider: SocialMediaProvider) -> None:
        """
        Register a social media provider.

        Args:
            name: Provider name
            provider: SocialMediaProvider instance
        """
        self.providers[name] = provider

    def fetch_aggregated_feed(self, limit: int = 50) -> List[SocialPost]:
        """
        Fetch aggregated feed from all providers.

        Args:
            limit: Maximum number of posts to return

        Returns:
            List of SocialPost objects sorted by timestamp
        """
        all_posts = []

        for provider_name, provider in self.providers.items():
            try:
                # Check cache
                if provider_name in self.cache:
                    cache_time = self.cache_time.get(provider_name)
                    if cache_time and datetime.utcnow() - cache_time < self.cache_ttl:
                        all_posts.extend(self.cache[provider_name])
                        continue

                # Fetch from provider
                posts = provider.fetch_posts('me', limit)
                self.cache[provider_name] = posts
                self.cache_time[provider_name] = datetime.utcnow()
                all_posts.extend(posts)

            except Exception as e:
                print(f"Error fetching from {provider_name}: {e}")

        # Sort by timestamp (newest first)
        all_posts.sort(key=lambda x: x.timestamp, reverse=True)

        return all_posts[:limit]

    def get_platform_feed(self, platform: str, limit: int = 20) -> List[SocialPost]:
        """
        Get feed from a specific platform.

        Args:
            platform: Platform name
            limit: Maximum number of posts

        Returns:
            List of SocialPost objects
        """
        if platform not in self.providers:
            return []

        try:
            provider = self.providers[platform]
            posts = provider.fetch_posts('me', limit)
            return posts

        except Exception as e:
            print(f"Error fetching from {platform}: {e}")
            return []

    def get_analytics(self, post_id: str, platform: str) -> Dict:
        """
        Get analytics for a post.

        Args:
            post_id: Post ID
            platform: Platform name

        Returns:
            Dictionary with analytics data
        """
        if platform not in self.providers:
            return {}

        try:
            provider = self.providers[platform]
            return provider.get_post_analytics(post_id)

        except Exception as e:
            print(f"Error fetching analytics: {e}")
            return {}

    def clear_cache(self, platform: str = None) -> None:
        """
        Clear cache.

        Args:
            platform: Platform name (optional, clears all if not specified)
        """
        if platform:
            if platform in self.cache:
                del self.cache[platform]
            if platform in self.cache_time:
                del self.cache_time[platform]
        else:
            self.cache.clear()
            self.cache_time.clear()


class SocialFeedWidget:
    """HTML component for displaying social feed."""

    @staticmethod
    def generate_feed_html(posts: List[SocialPost]) -> str:
        """
        Generate HTML for social feed.

        Args:
            posts: List of SocialPost objects

        Returns:
            HTML string for the feed
        """
        html = '<div class="social-feed">\n'

        for post in posts:
            html += SocialFeedWidget.generate_post_html(post)

        html += '</div>'
        return html

    @staticmethod
    def generate_post_html(post: SocialPost) -> str:
        """
        Generate HTML for a single post.

        Args:
            post: SocialPost object

        Returns:
            HTML string for the post
        """
        timestamp = post.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        html = f'''
<div class="social-post social-post-{post.platform}">
    <div class="post-header">
        <img src="{post.author_avatar}" alt="{post.author}" class="author-avatar" />
        <div class="author-info">
            <p class="author-name">{post.author}</p>
            <p class="platform-name">{post.platform}</p>
        </div>
        <p class="timestamp">{timestamp}</p>
    </div>
    
    <div class="post-content">
        <p>{post.content}</p>
    </div>
    
    <div class="post-stats">
        <span class="stat">
            <i class="icon-heart"></i> {post.likes} إعجاب
        </span>
        <span class="stat">
            <i class="icon-comment"></i> {post.comments} تعليق
        </span>
        <span class="stat">
            <i class="icon-share"></i> {post.shares} مشاركة
        </span>
    </div>
    
    <div class="post-actions">
        <a href="{post.url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary">
            عرض على {post.platform}
        </a>
    </div>
</div>
'''
        return html


# Global aggregator instance
content_aggregator = ContentAggregator()


if __name__ == "__main__":
    # Example usage
    print("Social Content Aggregator")
    print("=" * 50)

    # Register providers (with dummy tokens for demonstration)
    twitter_provider = TwitterProvider(access_token="your-twitter-token")
    facebook_provider = FacebookProvider(access_token="your-facebook-token")
    linkedin_provider = LinkedInProvider(access_token="your-linkedin-token")

    content_aggregator.register_provider('twitter', twitter_provider)
    content_aggregator.register_provider('facebook', facebook_provider)
    content_aggregator.register_provider('linkedin', linkedin_provider)

    # Fetch aggregated feed
    print("\nFetching aggregated feed...")
    feed = content_aggregator.fetch_aggregated_feed(limit=10)
    print(f"Fetched {len(feed)} posts")

    # Display posts
    for post in feed[:3]:
        print(f"\n{post.platform.upper()}: {post.author}")
        print(f"  {post.content[:100]}...")
        print(f"  Likes: {post.likes}, Comments: {post.comments}, Shares: {post.shares}")

    # Generate HTML
    print("\n\nHTML Feed:")
    html = SocialFeedWidget.generate_feed_html(feed[:3])
    print(html)

