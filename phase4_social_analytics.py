"""
Social Media Analytics
======================

This module provides comprehensive analytics for social media performance,
including engagement metrics, reach analysis, and trend tracking.

Features:
- Engagement metrics calculation
- Reach and impression analysis
- Trend tracking
- Performance comparison
- Analytics dashboard generation

Author: Manus AI
Date: 2025-10-20
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from collections import defaultdict


@dataclass
class EngagementMetrics:
    """Represents engagement metrics for a post."""

    post_id: str
    platform: str
    likes: int
    comments: int
    shares: int
    impressions: int = 0
    reach: int = 0
    timestamp: datetime = None

    def get_engagement_rate(self) -> float:
        """Calculate engagement rate."""
        if self.reach == 0:
            return 0
        total_engagement = self.likes + self.comments + self.shares
        return (total_engagement / self.reach) * 100

    def get_total_engagement(self) -> int:
        """Get total engagement."""
        return self.likes + self.comments + self.shares

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'post_id': self.post_id,
            'platform': self.platform,
            'likes': self.likes,
            'comments': self.comments,
            'shares': self.shares,
            'impressions': self.impressions,
            'reach': self.reach,
            'engagement_rate': self.get_engagement_rate(),
            'total_engagement': self.get_total_engagement(),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class PlatformStats:
    """Represents statistics for a platform."""

    platform: str
    total_posts: int
    total_followers: int
    total_engagement: int
    average_engagement_rate: float
    top_post_id: str = None
    top_post_engagement: int = 0


class AnalyticsCalculator:
    """Calculates analytics metrics."""

    @staticmethod
    def calculate_engagement_rate(likes: int, comments: int, shares: int, reach: int) -> float:
        """
        Calculate engagement rate.

        Args:
            likes: Number of likes
            comments: Number of comments
            shares: Number of shares
            reach: Number of people reached

        Returns:
            Engagement rate as percentage
        """
        if reach == 0:
            return 0
        total_engagement = likes + comments + shares
        return (total_engagement / reach) * 100

    @staticmethod
    def calculate_sentiment_score(comments: List[str]) -> float:
        """
        Calculate sentiment score from comments.

        Args:
            comments: List of comment texts

        Returns:
            Sentiment score between -1 (negative) and 1 (positive)
        """
        # Simple sentiment analysis (can be improved with NLP)
        positive_words = ['excellent', 'great', 'amazing', 'wonderful', 'fantastic', 'love', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'poor']

        positive_count = 0
        negative_count = 0

        for comment in comments:
            comment_lower = comment.lower()
            for word in positive_words:
                if word in comment_lower:
                    positive_count += 1
            for word in negative_words:
                if word in comment_lower:
                    negative_count += 1

        total = positive_count + negative_count
        if total == 0:
            return 0

        return (positive_count - negative_count) / total

    @staticmethod
    def calculate_growth_rate(current: int, previous: int) -> float:
        """
        Calculate growth rate.

        Args:
            current: Current value
            previous: Previous value

        Returns:
            Growth rate as percentage
        """
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100


class SocialAnalyticsDashboard:
    """Generates analytics dashboard data."""

    def __init__(self):
        """Initialize the dashboard."""
        self.metrics_history: List[EngagementMetrics] = []
        self.platform_stats: Dict[str, PlatformStats] = {}

    def add_metrics(self, metrics: EngagementMetrics) -> None:
        """
        Add engagement metrics.

        Args:
            metrics: EngagementMetrics object
        """
        self.metrics_history.append(metrics)

    def get_platform_stats(self, platform: str) -> Optional[PlatformStats]:
        """
        Get statistics for a platform.

        Args:
            platform: Platform name

        Returns:
            PlatformStats object or None
        """
        if platform not in self.platform_stats:
            return None

        return self.platform_stats[platform]

    def calculate_all_stats(self) -> Dict[str, PlatformStats]:
        """
        Calculate statistics for all platforms.

        Returns:
            Dictionary mapping platform names to PlatformStats
        """
        platform_data: Dict[str, List[EngagementMetrics]] = defaultdict(list)

        for metrics in self.metrics_history:
            platform_data[metrics.platform].append(metrics)

        stats = {}

        for platform, metrics_list in platform_data.items():
            total_posts = len(metrics_list)
            total_engagement = sum(m.get_total_engagement() for m in metrics_list)
            total_reach = sum(m.reach for m in metrics_list)

            average_engagement_rate = 0
            if total_reach > 0:
                average_engagement_rate = (total_engagement / total_reach) * 100

            # Find top post
            top_post = max(metrics_list, key=lambda m: m.get_total_engagement(), default=None)

            stats[platform] = PlatformStats(
                platform=platform,
                total_posts=total_posts,
                total_followers=0,  # Would be fetched from API
                total_engagement=total_engagement,
                average_engagement_rate=average_engagement_rate,
                top_post_id=top_post.post_id if top_post else None,
                top_post_engagement=top_post.get_total_engagement() if top_post else 0,
            )

        self.platform_stats = stats
        return stats

    def get_engagement_trend(self, platform: str, days: int = 30) -> List[Tuple[str, int]]:
        """
        Get engagement trend for a platform.

        Args:
            platform: Platform name
            days: Number of days to analyze

        Returns:
            List of (date, engagement) tuples
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        relevant_metrics = [
            m for m in self.metrics_history
            if m.platform == platform and m.timestamp and m.timestamp >= cutoff_date
        ]

        # Group by date
        daily_engagement: Dict[str, int] = defaultdict(int)
        for metrics in relevant_metrics:
            date_str = metrics.timestamp.strftime('%Y-%m-%d')
            daily_engagement[date_str] += metrics.get_total_engagement()

        # Sort by date
        trend = sorted(daily_engagement.items())
        return trend

    def get_top_posts(self, platform: str = None, limit: int = 10) -> List[EngagementMetrics]:
        """
        Get top posts by engagement.

        Args:
            platform: Filter by platform (optional)
            limit: Maximum number of posts

        Returns:
            List of top EngagementMetrics
        """
        metrics = self.metrics_history
        if platform:
            metrics = [m for m in metrics if m.platform == platform]

        # Sort by total engagement
        sorted_metrics = sorted(
            metrics,
            key=lambda m: m.get_total_engagement(),
            reverse=True
        )

        return sorted_metrics[:limit]

    def get_best_posting_time(self, platform: str) -> Optional[str]:
        """
        Get best posting time for a platform.

        Args:
            platform: Platform name

        Returns:
            Best posting hour (0-23) or None
        """
        platform_metrics = [m for m in self.metrics_history if m.platform == platform]

        if not platform_metrics:
            return None

        # Group by hour
        hourly_engagement: Dict[int, List[int]] = defaultdict(list)
        for metrics in platform_metrics:
            if metrics.timestamp:
                hour = metrics.timestamp.hour
                hourly_engagement[hour].append(metrics.get_total_engagement())

        # Calculate average engagement per hour
        avg_by_hour = {
            hour: sum(engagements) / len(engagements)
            for hour, engagements in hourly_engagement.items()
        }

        if not avg_by_hour:
            return None

        best_hour = max(avg_by_hour, key=avg_by_hour.get)
        return f"{best_hour:02d}:00"


class AnalyticsDashboardHTML:
    """Generates HTML for analytics dashboard."""

    @staticmethod
    def generate_dashboard(dashboard: SocialAnalyticsDashboard) -> str:
        """
        Generate HTML for analytics dashboard.

        Args:
            dashboard: SocialAnalyticsDashboard object

        Returns:
            HTML string for the dashboard
        """
        stats = dashboard.calculate_all_stats()
        top_posts = dashboard.get_top_posts(limit=5)

        html = '''
<div class="analytics-dashboard">
    <h2>تحليلات التواصل الاجتماعي</h2>
    
    <div class="stats-grid">
'''

        # Platform stats
        for platform, stat in stats.items():
            html += f'''
        <div class="stat-card stat-card-{platform}">
            <h3>{platform.upper()}</h3>
            <div class="stat-item">
                <span class="label">المنشورات:</span>
                <span class="value">{stat.total_posts}</span>
            </div>
            <div class="stat-item">
                <span class="label">إجمالي التفاعل:</span>
                <span class="value">{stat.total_engagement}</span>
            </div>
            <div class="stat-item">
                <span class="label">معدل التفاعل:</span>
                <span class="value">{stat.average_engagement_rate:.2f}%</span>
            </div>
        </div>
'''

        html += '''
    </div>
    
    <div class="top-posts">
        <h3>أفضل المنشورات</h3>
        <table>
            <thead>
                <tr>
                    <th>المنصة</th>
                    <th>الإعجابات</th>
                    <th>التعليقات</th>
                    <th>المشاركات</th>
                    <th>إجمالي التفاعل</th>
                </tr>
            </thead>
            <tbody>
'''

        for post in top_posts:
            html += f'''
                <tr>
                    <td>{post.platform}</td>
                    <td>{post.likes}</td>
                    <td>{post.comments}</td>
                    <td>{post.shares}</td>
                    <td><strong>{post.get_total_engagement()}</strong></td>
                </tr>
'''

        html += '''
            </tbody>
        </table>
    </div>
</div>
'''

        return html


# Global analytics instance
social_analytics = SocialAnalyticsDashboard()


if __name__ == "__main__":
    # Example usage
    print("Social Media Analytics")
    print("=" * 50)

    # Add sample metrics
    now = datetime.utcnow()
    metrics_data = [
        EngagementMetrics('post_1', 'twitter', 150, 20, 30, 5000, 10000, now),
        EngagementMetrics('post_2', 'twitter', 200, 25, 40, 6000, 12000, now - timedelta(days=1)),
        EngagementMetrics('post_3', 'facebook', 300, 50, 60, 8000, 15000, now),
        EngagementMetrics('post_4', 'linkedin', 100, 15, 20, 3000, 8000, now - timedelta(days=2)),
    ]

    for metrics in metrics_data:
        social_analytics.add_metrics(metrics)

    # Calculate stats
    print("\nPlatform Statistics:")
    stats = social_analytics.calculate_all_stats()
    for platform, stat in stats.items():
        print(f"\n{platform.upper()}:")
        print(f"  Total Posts: {stat.total_posts}")
        print(f"  Total Engagement: {stat.total_engagement}")
        print(f"  Average Engagement Rate: {stat.average_engagement_rate:.2f}%")

    # Get top posts
    print("\n\nTop Posts:")
    top_posts = social_analytics.get_top_posts(limit=3)
    for post in top_posts:
        print(f"  {post.platform}: {post.get_total_engagement()} engagements")

    # Generate HTML
    print("\n\nHTML Dashboard:")
    html = AnalyticsDashboardHTML.generate_dashboard(social_analytics)
    print(html[:500] + "...")

