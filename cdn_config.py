"""
تكوين شبكة توصيل المحتوى (CDN) لنظام IDEA
يتضمن تكوين CloudFlare و AWS CloudFront و MaxCDN
"""

import os
from django.conf import settings

class CDNConfig:
    """فئة تكوين CDN"""
    
    def __init__(self):
        self.cdn_providers = {
            'cloudflare': {
                'enabled': os.getenv('CLOUDFLARE_ENABLED', 'false').lower() == 'true',
                'zone_id': os.getenv('CLOUDFLARE_ZONE_ID', ''),
                'api_token': os.getenv('CLOUDFLARE_API_TOKEN', ''),
                'base_url': os.getenv('CLOUDFLARE_BASE_URL', 'https://cdn.ideateeam.com'),
                'cache_ttl': int(os.getenv('CLOUDFLARE_CACHE_TTL', '86400')),  # 24 hours
            },
            'aws_cloudfront': {
                'enabled': os.getenv('AWS_CLOUDFRONT_ENABLED', 'false').lower() == 'true',
                'distribution_id': os.getenv('AWS_CLOUDFRONT_DISTRIBUTION_ID', ''),
                'domain_name': os.getenv('AWS_CLOUDFRONT_DOMAIN', ''),
                'access_key': os.getenv('AWS_ACCESS_KEY_ID', ''),
                'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY', ''),
                'region': os.getenv('AWS_REGION', 'us-east-1'),
            },
            'maxcdn': {
                'enabled': os.getenv('MAXCDN_ENABLED', 'false').lower() == 'true',
                'alias': os.getenv('MAXCDN_ALIAS', ''),
                'key': os.getenv('MAXCDN_KEY', ''),
                'secret': os.getenv('MAXCDN_SECRET', ''),
                'base_url': os.getenv('MAXCDN_BASE_URL', ''),
            }
        }
        
        self.static_file_types = [
            'css', 'js', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg',
            'woff', 'woff2', 'ttf', 'eot', 'ico', 'pdf', 'mp4', 'webm'
        ]
        
    def get_active_provider(self):
        """الحصول على مزود CDN النشط"""
        for provider, config in self.cdn_providers.items():
            if config['enabled']:
                return provider, config
        return None, None
    
    def get_cdn_url(self, file_path):
        """الحصول على رابط CDN للملف"""
        provider, config = self.get_active_provider()
        
        if not provider:
            return file_path
            
        if provider == 'cloudflare':
            return f"{config['base_url']}{file_path}"
        elif provider == 'aws_cloudfront':
            return f"https://{config['domain_name']}{file_path}"
        elif provider == 'maxcdn':
            return f"{config['base_url']}{file_path}"
            
        return file_path
    
    def should_use_cdn(self, file_path):
        """تحديد ما إذا كان يجب استخدام CDN للملف"""
        if not file_path:
            return False
            
        file_extension = file_path.split('.')[-1].lower()
        return file_extension in self.static_file_types
    
    def purge_cache(self, file_paths=None):
        """مسح ذاكرة التخزين المؤقت لـ CDN"""
        provider, config = self.get_active_provider()
        
        if not provider:
            return False
            
        try:
            if provider == 'cloudflare':
                return self._purge_cloudflare_cache(config, file_paths)
            elif provider == 'aws_cloudfront':
                return self._purge_cloudfront_cache(config, file_paths)
            elif provider == 'maxcdn':
                return self._purge_maxcdn_cache(config, file_paths)
        except Exception as e:
            print(f"خطأ في مسح ذاكرة التخزين المؤقت: {e}")
            return False
            
        return False
    
    def _purge_cloudflare_cache(self, config, file_paths):
        """مسح ذاكرة التخزين المؤقت لـ CloudFlare"""
        import requests
        
        headers = {
            'Authorization': f'Bearer {config["api_token"]}',
            'Content-Type': 'application/json'
        }
        
        if file_paths:
            # مسح ملفات محددة
            data = {
                'files': [f"{config['base_url']}{path}" for path in file_paths]
            }
        else:
            # مسح جميع الملفات
            data = {'purge_everything': True}
        
        response = requests.post(
            f'https://api.cloudflare.com/client/v4/zones/{config["zone_id"]}/purge_cache',
            json=data,
            headers=headers
        )
        
        return response.status_code == 200
    
    def _purge_cloudfront_cache(self, config, file_paths):
        """مسح ذاكرة التخزين المؤقت لـ AWS CloudFront"""
        import boto3
        from datetime import datetime
        
        client = boto3.client(
            'cloudfront',
            aws_access_key_id=config['access_key'],
            aws_secret_access_key=config['secret_key'],
            region_name=config['region']
        )
        
        paths = file_paths if file_paths else ['/*']
        
        response = client.create_invalidation(
            DistributionId=config['distribution_id'],
            InvalidationBatch={
                'Paths': {
                    'Quantity': len(paths),
                    'Items': paths
                },
                'CallerReference': str(datetime.now().timestamp())
            }
        )
        
        return 'Invalidation' in response
    
    def _purge_maxcdn_cache(self, config, file_paths):
        """مسح ذاكرة التخزين المؤقت لـ MaxCDN"""
        import requests
        import hashlib
        import hmac
        import time
        
        # تنفيذ MaxCDN API authentication
        timestamp = str(int(time.time()))
        auth_string = f"{config['alias']}+{config['key']}+{timestamp}"
        auth_hash = hmac.new(
            config['secret'].encode(),
            auth_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'Authorization': f'MaxCDN {config["alias"]}:{auth_hash}:{timestamp}',
            'Content-Type': 'application/json'
        }
        
        if file_paths:
            # مسح ملفات محددة
            for path in file_paths:
                response = requests.delete(
                    f'https://rws.maxcdn.com/{config["alias"]}/zones/pull.json/cache',
                    json={'files': [path]},
                    headers=headers
                )
                if response.status_code != 200:
                    return False
        else:
            # مسح جميع الملفات
            response = requests.delete(
                f'https://rws.maxcdn.com/{config["alias"]}/zones/pull.json/cache',
                headers=headers
            )
            return response.status_code == 200
            
        return True

# إعداد CDN العام
cdn_config = CDNConfig()

def get_static_url(file_path):
    """دالة مساعدة للحصول على رابط الملف الثابت مع CDN"""
    if cdn_config.should_use_cdn(file_path):
        return cdn_config.get_cdn_url(file_path)
    return file_path

def purge_cdn_cache(file_paths=None):
    """دالة مساعدة لمسح ذاكرة التخزين المؤقت"""
    return cdn_config.purge_cache(file_paths)
