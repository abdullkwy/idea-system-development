"""
خدمات التكامل مع المنصات الخارجية
Meta Business API و X (Twitter) API
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
from .models import IntegrationSettings, PlatformReport, AdCampaign
logger = logging.getLogger(__name__)


class MetaBusinessIntegration:
    """
    خدمة التكامل مع Meta Business API
    لإدارة الحملات الإعلانية وجلب التقارير
    """
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.settings = self._get_settings()
    
    def _get_settings(self) -> Dict[str, str]:
        """جلب إعدادات Meta Business من قاعدة البيانات"""
        try:
            integration = IntegrationSettings.objects.get(platform='meta_business')
            return {
                'app_id': integration.api_key,
                'app_secret': integration.api_secret,
                'access_token': integration.access_token
            }
        except IntegrationSettings.DoesNotExist:
            logger.warning("Meta Business integration settings not found")
            return {}
    
    def test_connection(self) -> Dict[str, Any]:
        """اختبار الاتصال مع Meta Business API"""
        if not self.settings.get('access_token'):
            return {
                'success': False,
                'error': 'Access token not configured'
            }
        
        try:
            url = f"{self.base_url}/me"
            params = {
                'access_token': self.settings['access_token'],
                'fields': 'id,name'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': data,
                    'message': f"Connected to account: {data.get('name', 'Unknown')}"
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code}",
                    'details': response.text
                }
                
        except requests.RequestException as e:
            logger.error(f"Meta Business connection test failed: {e}")
            return {
                'success': False,
                'error': f"Connection failed: {str(e)}"
            }
    
    def get_ad_accounts(self) -> List[Dict[str, Any]]:
        """جلب قائمة حسابات الإعلانات"""
        if not self.settings.get('access_token'):
            return []
        
        try:
            url = f"{self.base_url}/me/adaccounts"
            params = {
                'access_token': self.settings['access_token'],
                'fields': 'id,name,account_status,currency,timezone_name'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Failed to get ad accounts: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Error getting ad accounts: {e}")
            return []
    
    def get_campaigns(self, ad_account_id: str) -> List[Dict[str, Any]]:
        """جلب قائمة الحملات الإعلانية"""
        if not self.settings.get('access_token'):
            return []
        
        try:
            url = f"{self.base_url}/{ad_account_id}/campaigns"
            params = {
                'access_token': self.settings['access_token'],
                'fields': 'id,name,status,objective,created_time,updated_time'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Failed to get campaigns: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Error getting campaigns: {e}")
            return []
    
    def get_campaign_insights(self, campaign_id: str, date_range: int = 7) -> Dict[str, Any]:
        """جلب إحصائيات الحملة الإعلانية"""
        if not self.settings.get('access_token'):
            return {}
        
        try:
            # تحديد نطاق التاريخ
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=date_range)
            
            url = f"{self.base_url}/{campaign_id}/insights"
            params = {
                'access_token': self.settings['access_token'],
                'fields': 'impressions,clicks,spend,reach,frequency,ctr,cpc,cpm,cpp',
                'time_range': json.dumps({
                    'since': start_date.strftime('%Y-%m-%d'),
                    'until': end_date.strftime('%Y-%m-%d')
                })
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                insights = data.get('data', [])
                if insights:
                    return insights[0]  # أول نتيجة
                return {}
            else:
                logger.error(f"Failed to get campaign insights: {response.status_code}")
                return {}
                
        except requests.RequestException as e:
            logger.error(f"Error getting campaign insights: {e}")
            return {}
    
    def create_campaign(self, ad_account_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء حملة إعلانية جديدة"""
        if not self.settings.get('access_token'):
            return {'success': False, 'error': 'Access token not configured'}
        
        try:
            url = f"{self.base_url}/{ad_account_id}/campaigns"
            data = {
                'access_token': self.settings['access_token'],
                'name': campaign_data.get('name'),
                'objective': campaign_data.get('objective', 'TRAFFIC'),
                'status': campaign_data.get('status', 'PAUSED'),
                'special_ad_categories': campaign_data.get('special_ad_categories', [])
            }
            
            response = requests.post(url, data=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'campaign_id': result.get('id'),
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code}",
                    'details': response.text
                }
                
        except requests.RequestException as e:
            logger.error(f"Error creating campaign: {e}")
            return {
                'success': False,
                'error': f"Request failed: {str(e)}"
            }
    
    def sync_campaigns_data(self) -> Dict[str, Any]:
        """مزامنة بيانات الحملات مع قاعدة البيانات"""
        try:
            ad_accounts = self.get_ad_accounts()
            synced_campaigns = 0
            
            for account in ad_accounts:
                account_id = account['id']
                campaigns = self.get_campaigns(account_id)
                
                for campaign in campaigns:
                    # حفظ أو تحديث الحملة في قاعدة البيانات
                    campaign_obj, created = AdCampaigns.objects.update_or_create(
                        platform='meta_business',
                        external_id=campaign['id'],
                        defaults={
                            'name': campaign['name'],
                            'status': campaign['status'],
                            'objective': campaign.get('objective', ''),
                            'account_id': account_id,
                            'created_date': datetime.fromisoformat(
                                campaign['created_time'].replace('Z', '+00:00')
                            ).date(),
                            'data': campaign
                        }
                    )
                    
                    # جلب الإحصائيات
                    insights = self.get_campaign_insights(campaign['id'])
                    if insights:
                        # حفظ التقرير
                        PlatformReports.objects.update_or_create(
                            platform='meta_business',
                            campaign_id=campaign['id'],
                            report_date=datetime.now().date(),
                            defaults={
                                'impressions': int(insights.get('impressions', 0)),
                                'clicks': int(insights.get('clicks', 0)),
                                'spend': float(insights.get('spend', 0)),
                                'reach': int(insights.get('reach', 0)),
                                'ctr': float(insights.get('ctr', 0)),
                                'cpc': float(insights.get('cpc', 0)),
                                'cpm': float(insights.get('cpm', 0)),
                                'data': insights
                            }
                        )
                    
                    synced_campaigns += 1
            
            return {
                'success': True,
                'synced_campaigns': synced_campaigns,
                'message': f"Synced {synced_campaigns} campaigns successfully"
            }
            
        except Exception as e:
            logger.error(f"Error syncing campaigns data: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class XTwitterIntegration:
    """
    خدمة التكامل مع X (Twitter) API
    لإدارة المحتوى والحملات الإعلانية
    """
    
    def __init__(self):
        self.base_url = "https://api.twitter.com/2"
        self.ads_url = "https://ads-api.twitter.com/12"
        self.settings = self._get_settings()
    
    def _get_settings(self) -> Dict[str, str]:
        """جلب إعدادات X من قاعدة البيانات"""
        try:
            integration = IntegrationSettings.objects.get(platform='x_twitter')
            return {
                'api_key': integration.api_key,
                'api_secret': integration.api_secret,
                'access_token': integration.access_token,
                'access_token_secret': integration.additional_settings.get('access_token_secret', '')
            }
        except IntegrationSettings.DoesNotExist:
            logger.warning("X Twitter integration settings not found")
            return {}
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """إنشاء headers للمصادقة"""
        if not self.settings.get('access_token'):
            return {}
        
        return {
            'Authorization': f"Bearer {self.settings['access_token']}",
            'Content-Type': 'application/json'
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """اختبار الاتصال مع X API"""
        if not self.settings.get('access_token'):
            return {
                'success': False,
                'error': 'Access token not configured'
            }
        
        try:
            url = f"{self.base_url}/users/me"
            headers = self._get_auth_headers()
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('data', {})
                return {
                    'success': True,
                    'data': user_data,
                    'message': f"Connected to account: @{user_data.get('username', 'Unknown')}"
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code}",
                    'details': response.text
                }
                
        except requests.RequestException as e:
            logger.error(f"X Twitter connection test failed: {e}")
            return {
                'success': False,
                'error': f"Connection failed: {str(e)}"
            }
    
    def get_user_tweets(self, user_id: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """جلب التغريدات الأخيرة"""
        if not self.settings.get('access_token'):
            return []
        
        try:
            if not user_id:
                # جلب معرف المستخدم الحالي
                me_response = self.test_connection()
                if not me_response['success']:
                    return []
                user_id = me_response['data']['id']
            
            url = f"{self.base_url}/users/{user_id}/tweets"
            headers = self._get_auth_headers()
            params = {
                'max_results': min(max_results, 100),
                'tweet.fields': 'created_at,public_metrics,context_annotations'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Failed to get tweets: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Error getting tweets: {e}")
            return []
    
    def post_tweet(self, text: str, media_ids: List[str] = None) -> Dict[str, Any]:
        """نشر تغريدة جديدة"""
        if not self.settings.get('access_token'):
            return {'success': False, 'error': 'Access token not configured'}
        
        try:
            url = f"{self.base_url}/tweets"
            headers = self._get_auth_headers()
            
            data = {'text': text}
            if media_ids:
                data['media'] = {'media_ids': media_ids}
            
            response = requests.post(url, headers=headers, json=data, timeout=15)
            
            if response.status_code == 201:
                result = response.json()
                return {
                    'success': True,
                    'tweet_id': result['data']['id'],
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code}",
                    'details': response.text
                }
                
        except requests.RequestException as e:
            logger.error(f"Error posting tweet: {e}")
            return {
                'success': False,
                'error': f"Request failed: {str(e)}"
            }
    
    def get_tweet_analytics(self, tweet_id: str) -> Dict[str, Any]:
        """جلب إحصائيات التغريدة"""
        if not self.settings.get('access_token'):
            return {}
        
        try:
            url = f"{self.base_url}/tweets/{tweet_id}"
            headers = self._get_auth_headers()
            params = {
                'tweet.fields': 'public_metrics,non_public_metrics,organic_metrics'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                tweet_data = data.get('data', {})
                return tweet_data.get('public_metrics', {})
            else:
                logger.error(f"Failed to get tweet analytics: {response.status_code}")
                return {}
                
        except requests.RequestException as e:
            logger.error(f"Error getting tweet analytics: {e}")
            return {}
    
    def get_ads_accounts(self) -> List[Dict[str, Any]]:
        """جلب حسابات الإعلانات"""
        if not self.settings.get('access_token'):
            return []
        
        try:
            url = f"{self.ads_url}/accounts"
            headers = self._get_auth_headers()
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Failed to get ads accounts: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Error getting ads accounts: {e}")
            return []
    
    def sync_content_data(self) -> Dict[str, Any]:
        """مزامنة بيانات المحتوى مع قاعدة البيانات"""
        try:
            tweets = self.get_user_tweets(max_results=50)
            synced_tweets = 0
            
            for tweet in tweets:
                # حفظ التغريدة كحملة محتوى
                campaign_obj, created = AdCampaigns.objects.update_or_create(
                    platform='x_twitter',
                    external_id=tweet['id'],
                    defaults={
                        'name': f"Tweet: {tweet['text'][:50]}...",
                        'status': 'active',
                        'objective': 'engagement',
                        'created_date': datetime.fromisoformat(
                            tweet['created_at'].replace('Z', '+00:00')
                        ).date(),
                        'data': tweet
                    }
                )
                
                # جلب الإحصائيات
                analytics = self.get_tweet_analytics(tweet['id'])
                if analytics:
                    # حفظ التقرير
                    PlatformReports.objects.update_or_create(
                        platform='x_twitter',
                        campaign_id=tweet['id'],
                        report_date=datetime.now().date(),
                        defaults={
                            'impressions': analytics.get('impression_count', 0),
                            'clicks': analytics.get('url_link_clicks', 0),
                            'reach': analytics.get('impression_count', 0),
                            'engagement_rate': analytics.get('like_count', 0) + analytics.get('retweet_count', 0),
                            'data': analytics
                        }
                    )
                
                synced_tweets += 1
            
            return {
                'success': True,
                'synced_content': synced_tweets,
                'message': f"Synced {synced_tweets} tweets successfully"
            }
            
        except Exception as e:
            logger.error(f"Error syncing content data: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class IntegrationManager:
    """
    مدير التكاملات الرئيسي
    لإدارة جميع المنصات الخارجية
    """
    
    def __init__(self):
        self.meta_business = MetaBusinessIntegration()
        self.x_twitter = XTwitterIntegration()
    
    def test_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """اختبار جميع الاتصالات"""
        results = {}
        
        # اختبار Meta Business
        results['meta_business'] = self.meta_business.test_connection()
        
        # اختبار X Twitter
        results['x_twitter'] = self.x_twitter.test_connection()
        
        return results
    
    def sync_all_data(self) -> Dict[str, Dict[str, Any]]:
        """مزامنة جميع البيانات"""
        results = {}
        
        # مزامنة Meta Business
        results['meta_business'] = self.meta_business.sync_campaigns_data()
        
        # مزامنة X Twitter
        results['x_twitter'] = self.x_twitter.sync_content_data()
        
        return results
    
    def get_unified_report(self, date_range: int = 7) -> Dict[str, Any]:
        """إنشاء تقرير موحد من جميع المنصات"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=date_range)
            
            # جلب تقارير من جميع المنصات
            reports = PlatformReports.objects.filter(
                report_date__gte=start_date,
                report_date__lte=end_date
            )
            
            # تجميع البيانات
            unified_data = {
                'total_impressions': 0,
                'total_clicks': 0,
                'total_spend': 0,
                'total_reach': 0,
                'platforms': {},
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
            for report in reports:
                platform = report.platform
                
                if platform not in unified_data['platforms']:
                    unified_data['platforms'][platform] = {
                        'impressions': 0,
                        'clicks': 0,
                        'spend': 0,
                        'reach': 0,
                        'campaigns': 0
                    }
                
                # تجميع البيانات
                unified_data['total_impressions'] += report.impressions or 0
                unified_data['total_clicks'] += report.clicks or 0
                unified_data['total_spend'] += report.spend or 0
                unified_data['total_reach'] += report.reach or 0
                
                unified_data['platforms'][platform]['impressions'] += report.impressions or 0
                unified_data['platforms'][platform]['clicks'] += report.clicks or 0
                unified_data['platforms'][platform]['spend'] += report.spend or 0
                unified_data['platforms'][platform]['reach'] += report.reach or 0
                unified_data['platforms'][platform]['campaigns'] += 1
            
            # حساب المعدلات
            if unified_data['total_impressions'] > 0:
                unified_data['overall_ctr'] = (unified_data['total_clicks'] / unified_data['total_impressions']) * 100
            else:
                unified_data['overall_ctr'] = 0
            
            if unified_data['total_clicks'] > 0:
                unified_data['overall_cpc'] = unified_data['total_spend'] / unified_data['total_clicks']
            else:
                unified_data['overall_cpc'] = 0
            
            return {
                'success': True,
                'data': unified_data
            }
            
        except Exception as e:
            logger.error(f"Error generating unified report: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# دوال مساعدة للاستخدام في Views
def get_integration_manager():
    """إنشاء مثيل من مدير التكاملات"""
    return IntegrationManager()


def cache_platform_data(platform: str, data: Dict[str, Any], timeout: int = 3600):
    """حفظ بيانات المنصة في الذاكرة المؤقتة"""
    cache_key = f"platform_data_{platform}_{datetime.now().strftime('%Y%m%d')}"
    cache.set(cache_key, data, timeout)


def get_cached_platform_data(platform: str) -> Optional[Dict[str, Any]]:
    """جلب بيانات المنصة من الذاكرة المؤقتة"""
    cache_key = f"platform_data_{platform}_{datetime.now().strftime('%Y%m%d')}"
    return cache.get(cache_key)

