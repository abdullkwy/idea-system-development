"""
Social Sharing Service
======================

This module provides social sharing functionality that allows users to share
content from the IDEA system on various social media platforms.

Features:
- Share buttons for multiple platforms (Twitter, Facebook, LinkedIn, WhatsApp)
- Meta tags generation for Open Graph and Twitter Cards
- URL shortening and tracking
- Share analytics

Author: Manus AI
Date: 2025-10-20
"""

from typing import Dict, List, Optional
from urllib.parse import urlencode, quote
from datetime import datetime
import json


class SocialPlatform:
    """Base class for social media platforms."""

    def __init__(self, name: str, share_url: str):
        """
        Initialize a social platform.

        Args:
            name: Platform name
            share_url: Base URL for sharing
        """
        self.name = name
        self.share_url = share_url

    def generate_share_link(self, content: Dict[str, str]) -> str:
        """
        Generate a share link for the platform.

        Args:
            content: Content to share (title, url, description, etc.)

        Returns:
            Share link URL
        """
        raise NotImplementedError


class TwitterShare(SocialPlatform):
    """Twitter sharing implementation."""

    def __init__(self):
        super().__init__("Twitter", "https://twitter.com/intent/tweet")

    def generate_share_link(self, content: Dict[str, str]) -> str:
        """
        Generate a Twitter share link.

        Args:
            content: Content dictionary with 'url', 'text', 'hashtags'

        Returns:
            Twitter share link
        """
        params = {
            'url': content.get('url', ''),
            'text': content.get('text', ''),
            'hashtags': content.get('hashtags', ''),
        }
        query_string = urlencode({k: v for k, v in params.items() if v})
        return f"{self.share_url}?{query_string}"


class FacebookShare(SocialPlatform):
    """Facebook sharing implementation."""

    def __init__(self):
        super().__init__("Facebook", "https://www.facebook.com/sharer/sharer.php")

    def generate_share_link(self, content: Dict[str, str]) -> str:
        """
        Generate a Facebook share link.

        Args:
            content: Content dictionary with 'url'

        Returns:
            Facebook share link
        """
        params = {
            'u': content.get('url', ''),
            'quote': content.get('text', ''),
        }
        query_string = urlencode({k: v for k, v in params.items() if v})
        return f"{self.share_url}?{query_string}"


class LinkedInShare(SocialPlatform):
    """LinkedIn sharing implementation."""

    def __init__(self):
        super().__init__("LinkedIn", "https://www.linkedin.com/sharing/share-offsite/")

    def generate_share_link(self, content: Dict[str, str]) -> str:
        """
        Generate a LinkedIn share link.

        Args:
            content: Content dictionary with 'url'

        Returns:
            LinkedIn share link
        """
        params = {
            'url': content.get('url', ''),
        }
        query_string = urlencode({k: v for k, v in params.items() if v})
        return f"{self.share_url}?{query_string}"


class WhatsAppShare(SocialPlatform):
    """WhatsApp sharing implementation."""

    def __init__(self):
        super().__init__("WhatsApp", "https://wa.me/")

    def generate_share_link(self, content: Dict[str, str]) -> str:
        """
        Generate a WhatsApp share link.

        Args:
            content: Content dictionary with 'text', 'url'

        Returns:
            WhatsApp share link
        """
        message = content.get('text', '')
        url = content.get('url', '')
        if url:
            message = f"{message}\n{url}"

        encoded_message = quote(message)
        return f"https://wa.me/?text={encoded_message}"


class EmailShare(SocialPlatform):
    """Email sharing implementation."""

    def __init__(self):
        super().__init__("Email", "mailto:")

    def generate_share_link(self, content: Dict[str, str]) -> str:
        """
        Generate an email share link.

        Args:
            content: Content dictionary with 'subject', 'body', 'to'

        Returns:
            Email share link
        """
        subject = quote(content.get('subject', ''))
        body = quote(content.get('body', ''))
        to = content.get('to', '')

        return f"mailto:{to}?subject={subject}&body={body}"


class MetaTagGenerator:
    """Generate meta tags for social sharing (Open Graph, Twitter Cards)."""

    @staticmethod
    def generate_open_graph_tags(content: Dict[str, str]) -> Dict[str, str]:
        """
        Generate Open Graph meta tags.

        Args:
            content: Content dictionary with og_title, og_description, og_image, og_url, og_type

        Returns:
            Dictionary of Open Graph meta tags
        """
        return {
            'og:title': content.get('og_title', ''),
            'og:description': content.get('og_description', ''),
            'og:image': content.get('og_image', ''),
            'og:url': content.get('og_url', ''),
            'og:type': content.get('og_type', 'website'),
            'og:site_name': content.get('og_site_name', 'IDEA System'),
        }

    @staticmethod
    def generate_twitter_card_tags(content: Dict[str, str]) -> Dict[str, str]:
        """
        Generate Twitter Card meta tags.

        Args:
            content: Content dictionary with twitter_card, twitter_title, twitter_description, twitter_image, twitter_creator

        Returns:
            Dictionary of Twitter Card meta tags
        """
        return {
            'twitter:card': content.get('twitter_card', 'summary_large_image'),
            'twitter:title': content.get('twitter_title', ''),
            'twitter:description': content.get('twitter_description', ''),
            'twitter:image': content.get('twitter_image', ''),
            'twitter:creator': content.get('twitter_creator', '@IDEA'),
        }

    @staticmethod
    def generate_html_meta_tags(content: Dict[str, str]) -> str:
        """
        Generate HTML meta tag strings.

        Args:
            content: Content dictionary

        Returns:
            HTML meta tag strings
        """
        og_tags = MetaTagGenerator.generate_open_graph_tags(content)
        twitter_tags = MetaTagGenerator.generate_twitter_card_tags(content)

        html = []
        for key, value in og_tags.items():
            if value:
                html.append(f'<meta property="{key}" content="{value}" />')

        for key, value in twitter_tags.items():
            if value:
                html.append(f'<meta name="{key}" content="{value}" />')

        return '\n'.join(html)


class SocialSharingManager:
    """Manages social sharing functionality."""

    def __init__(self):
        """Initialize the social sharing manager."""
        self.platforms = {
            'twitter': TwitterShare(),
            'facebook': FacebookShare(),
            'linkedin': LinkedInShare(),
            'whatsapp': WhatsAppShare(),
            'email': EmailShare(),
        }
        self.share_history: List[Dict] = []

    def get_share_links(self, content: Dict[str, str]) -> Dict[str, str]:
        """
        Get share links for all platforms.

        Args:
            content: Content to share

        Returns:
            Dictionary mapping platform names to share links
        """
        share_links = {}
        for platform_name, platform in self.platforms.items():
            try:
                share_links[platform_name] = platform.generate_share_link(content)
            except Exception as e:
                print(f"Error generating share link for {platform_name}: {e}")

        return share_links

    def get_share_link(self, platform: str, content: Dict[str, str]) -> Optional[str]:
        """
        Get share link for a specific platform.

        Args:
            platform: Platform name
            content: Content to share

        Returns:
            Share link URL or None if platform not found
        """
        if platform not in self.platforms:
            return None

        return self.platforms[platform].generate_share_link(content)

    def track_share(self, platform: str, content_id: str, user_id: str = None) -> None:
        """
        Track a share action.

        Args:
            platform: Platform name
            content_id: ID of shared content
            user_id: ID of user sharing
        """
        self.share_history.append({
            'platform': platform,
            'content_id': content_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
        })

    def get_share_stats(self, content_id: str = None) -> Dict:
        """
        Get sharing statistics.

        Args:
            content_id: Filter by content ID (optional)

        Returns:
            Dictionary with sharing statistics
        """
        filtered_history = self.share_history
        if content_id:
            filtered_history = [h for h in self.share_history if h['content_id'] == content_id]

        stats = {
            'total_shares': len(filtered_history),
            'by_platform': {},
            'by_user': {},
        }

        for share in filtered_history:
            platform = share['platform']
            user_id = share['user_id']

            stats['by_platform'][platform] = stats['by_platform'].get(platform, 0) + 1
            if user_id:
                stats['by_user'][user_id] = stats['by_user'].get(user_id, 0) + 1

        return stats


class ShareButton:
    """HTML component for share buttons."""

    @staticmethod
    def generate_share_buttons(content: Dict[str, str], platforms: List[str] = None) -> str:
        """
        Generate HTML for share buttons.

        Args:
            content: Content to share
            platforms: List of platforms to include (default: all)

        Returns:
            HTML string for share buttons
        """
        if platforms is None:
            platforms = ['twitter', 'facebook', 'linkedin', 'whatsapp', 'email']

        manager = SocialSharingManager()
        share_links = manager.get_share_links(content)

        html = '<div class="share-buttons">\n'

        for platform in platforms:
            if platform in share_links:
                link = share_links[platform]
                icon = ShareButton._get_platform_icon(platform)
                html += f'''
    <a href="{link}" target="_blank" rel="noopener noreferrer" class="share-btn share-btn-{platform}" title="مشاركة على {platform}">
        {icon}
        <span>{platform}</span>
    </a>
'''

        html += '</div>'
        return html

    @staticmethod
    def _get_platform_icon(platform: str) -> str:
        """Get icon HTML for a platform."""
        icons = {
            'twitter': '𝕏',
            'facebook': 'f',
            'linkedin': 'in',
            'whatsapp': 'W',
            'email': '✉',
        }
        return icons.get(platform, '→')


class ShareWidget:
    """Complete share widget component."""

    @staticmethod
    def generate_widget(content: Dict[str, str], widget_id: str = 'share-widget') -> str:
        """
        Generate a complete share widget.

        Args:
            content: Content to share
            widget_id: Widget ID for styling

        Returns:
            HTML string for the widget
        """
        meta_tags = MetaTagGenerator.generate_html_meta_tags(content)
        share_buttons = ShareButton.generate_share_buttons(content)

        html = f'''
<!-- Share Widget -->
<div id="{widget_id}" class="share-widget">
    <h3>مشاركة المحتوى</h3>
    {share_buttons}
</div>

<!-- Meta Tags for Social Sharing -->
{meta_tags}
'''
        return html


# Global sharing manager instance
social_sharing = SocialSharingManager()


if __name__ == "__main__":
    # Example usage
    print("Social Sharing Service")
    print("=" * 50)

    # Sample content
    content = {
        'url': 'https://idea-system.com/projects/123',
        'text': 'تحقق من مشروعنا الجديد على نظام IDEA',
        'hashtags': 'IDEA,مشاريع,حلول',
        'og_title': 'مشروع جديد على IDEA',
        'og_description': 'اكتشف حلولنا المبتكرة',
        'og_image': 'https://idea-system.com/images/project.jpg',
        'og_url': 'https://idea-system.com/projects/123',
        'twitter_title': 'مشروع جديد على IDEA',
        'twitter_description': 'اكتشف حلولنا المبتكرة',
        'twitter_image': 'https://idea-system.com/images/project.jpg',
    }

    # Generate share links
    share_links = social_sharing.get_share_links(content)
    print("\nShare Links:")
    for platform, link in share_links.items():
        print(f"- {platform}: {link[:80]}...")

    # Generate meta tags
    print("\n\nMeta Tags:")
    meta_tags = MetaTagGenerator.generate_html_meta_tags(content)
    print(meta_tags)

    # Track shares
    social_sharing.track_share('twitter', 'project_123', 'user_456')
    social_sharing.track_share('facebook', 'project_123', 'user_456')

    # Get statistics
    stats = social_sharing.get_share_stats('project_123')
    print("\n\nShare Statistics:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    # Generate share widget
    print("\n\nShare Widget HTML:")
    widget = ShareWidget.generate_widget(content)
    print(widget)

