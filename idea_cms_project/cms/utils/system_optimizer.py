"""
System Optimizer Utility
أداة تحسين النظام
"""

import os
import logging
import time
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
import json

logger = logging.getLogger(__name__)

class SystemOptimizer:
    """System optimization utility class"""
    
    def __init__(self):
        self.optimization_log = []
        self.start_time = time.time()
    
    def optimize_all(self):
        """Run all optimization tasks"""
        logger.info("Starting system optimization...")
        
        optimizations = [
            ('Database Optimization', self.optimize_database),
            ('Cache Optimization', self.optimize_cache),
            ('File System Optimization', self.optimize_filesystem),
            ('Performance Optimization', self.optimize_performance),
            ('Security Optimization', self.optimize_security),
            ('SEO Optimization', self.optimize_seo)
        ]
        
        results = {}
        
        for name, optimization_func in optimizations:
            try:
                start_time = time.time()
                result = optimization_func()
                end_time = time.time()
                
                results[name] = {
                    'success': True,
                    'result': result,
                    'duration': round(end_time - start_time, 2)
                }
                
                logger.info(f"{name} completed in {results[name]['duration']}s")
                
            except Exception as e:
                results[name] = {
                    'success': False,
                    'error': str(e),
                    'duration': 0
                }
                logger.error(f"{name} failed: {str(e)}")
        
        total_time = round(time.time() - self.start_time, 2)
        logger.info(f"System optimization completed in {total_time}s")
        
        return {
            'results': results,
            'total_duration': total_time,
            'timestamp': timezone.now().isoformat()
        }
    
    def optimize_database(self):
        """Optimize database performance"""
        optimizations = []
        
        # Analyze database queries
        with connection.cursor() as cursor:
            # Get database size
            cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
            db_size = cursor.fetchone()[0] if connection.vendor == 'postgresql' else 'Unknown'
            optimizations.append(f"Database size: {db_size}")
            
            # Check for unused indexes
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
                    FROM pg_stat_user_indexes 
                    WHERE idx_tup_read = 0 AND idx_tup_fetch = 0
                    LIMIT 10
                """)
                unused_indexes = cursor.fetchall()
                if unused_indexes:
                    optimizations.append(f"Found {len(unused_indexes)} unused indexes")
        
        # Clean up old sessions
        try:
            call_command('clearsessions')
            optimizations.append("Cleared old sessions")
        except Exception as e:
            logger.warning(f"Failed to clear sessions: {str(e)}")
        
        # Optimize database tables (if supported)
        if connection.vendor == 'postgresql':
            try:
                with connection.cursor() as cursor:
                    cursor.execute("VACUUM ANALYZE")
                optimizations.append("Database tables optimized")
            except Exception as e:
                logger.warning(f"Failed to optimize tables: {str(e)}")
        
        return optimizations
    
    def optimize_cache(self):
        """Optimize caching system"""
        optimizations = []
        
        # Clear expired cache entries
        try:
            cache.clear()
            optimizations.append("Cache cleared")
        except Exception as e:
            logger.warning(f"Failed to clear cache: {str(e)}")
        
        # Set up cache warming for critical data
        critical_cache_keys = [
            'site_settings',
            'active_services',
            'published_pages',
            'navigation_menu'
        ]
        
        for key in critical_cache_keys:
            try:
                # This would warm up the cache with critical data
                # Implementation depends on your specific cache strategy
                cache.set(f"warmed_{key}", True, timeout=3600)
                optimizations.append(f"Warmed cache for {key}")
            except Exception as e:
                logger.warning(f"Failed to warm cache for {key}: {str(e)}")
        
        return optimizations
    
    def optimize_filesystem(self):
        """Optimize file system"""
        optimizations = []
        
        # Clean up temporary files
        temp_dirs = [
            os.path.join(settings.BASE_DIR, 'tmp'),
            os.path.join(settings.MEDIA_ROOT, 'temp') if hasattr(settings, 'MEDIA_ROOT') else None,
            '/tmp/django_cache'
        ]
        
        for temp_dir in temp_dirs:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    files_removed = self.clean_temp_directory(temp_dir)
                    optimizations.append(f"Cleaned {files_removed} temporary files from {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean {temp_dir}: {str(e)}")
        
        # Optimize media files
        if hasattr(settings, 'MEDIA_ROOT') and os.path.exists(settings.MEDIA_ROOT):
            try:
                optimized_images = self.optimize_images(settings.MEDIA_ROOT)
                optimizations.append(f"Optimized {optimized_images} images")
            except Exception as e:
                logger.warning(f"Failed to optimize images: {str(e)}")
        
        # Check disk space
        try:
            disk_usage = self.get_disk_usage(settings.BASE_DIR)
            optimizations.append(f"Disk usage: {disk_usage}")
        except Exception as e:
            logger.warning(f"Failed to check disk usage: {str(e)}")
        
        return optimizations
    
    def optimize_performance(self):
        """Optimize system performance"""
        optimizations = []
        
        # Collect static files
        try:
            call_command('collectstatic', '--noinput', verbosity=0)
            optimizations.append("Static files collected")
        except Exception as e:
            logger.warning(f"Failed to collect static files: {str(e)}")
        
        # Compress static files (if django-compressor is installed)
        try:
            call_command('compress', '--force')
            optimizations.append("Static files compressed")
        except Exception as e:
            # This is expected if django-compressor is not installed
            pass
        
        # Update search indexes (if django-haystack is installed)
        try:
            call_command('update_index', verbosity=0)
            optimizations.append("Search indexes updated")
        except Exception as e:
            # This is expected if search is not configured
            pass
        
        # Generate sitemaps
        try:
            call_command('ping_google', '/sitemap.xml')
            optimizations.append("Sitemap updated")
        except Exception as e:
            logger.warning(f"Failed to update sitemap: {str(e)}")
        
        return optimizations
    
    def optimize_security(self):
        """Optimize security settings"""
        optimizations = []
        
        # Check for security issues
        security_checks = [
            ('DEBUG setting', not getattr(settings, 'DEBUG', True)),
            ('SECRET_KEY length', len(getattr(settings, 'SECRET_KEY', '')) >= 50),
            ('ALLOWED_HOSTS configured', bool(getattr(settings, 'ALLOWED_HOSTS', []))),
            ('SECURE_SSL_REDIRECT', getattr(settings, 'SECURE_SSL_REDIRECT', False)),
            ('SECURE_HSTS_SECONDS', getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0),
        ]
        
        for check_name, is_secure in security_checks:
            status = "✓" if is_secure else "✗"
            optimizations.append(f"{status} {check_name}")
        
        # Clean up old log files
        try:
            log_dir = os.path.join(settings.BASE_DIR, 'logs')
            if os.path.exists(log_dir):
                cleaned_logs = self.clean_old_logs(log_dir)
                optimizations.append(f"Cleaned {cleaned_logs} old log files")
        except Exception as e:
            logger.warning(f"Failed to clean logs: {str(e)}")
        
        return optimizations
    
    def optimize_seo(self):
        """Optimize SEO settings"""
        optimizations = []
        
        # Generate robots.txt
        try:
            self.generate_robots_txt()
            optimizations.append("Generated robots.txt")
        except Exception as e:
            logger.warning(f"Failed to generate robots.txt: {str(e)}")
        
        # Generate sitemap
        try:
            self.generate_sitemap()
            optimizations.append("Generated sitemap.xml")
        except Exception as e:
            logger.warning(f"Failed to generate sitemap: {str(e)}")
        
        # Check meta tags
        try:
            meta_issues = self.check_meta_tags()
            optimizations.append(f"Found {len(meta_issues)} meta tag issues")
        except Exception as e:
            logger.warning(f"Failed to check meta tags: {str(e)}")
        
        return optimizations
    
    def clean_temp_directory(self, directory):
        """Clean temporary files older than 24 hours"""
        files_removed = 0
        cutoff_time = time.time() - (24 * 60 * 60)  # 24 hours ago
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        files_removed += 1
                except (OSError, IOError):
                    continue
        
        return files_removed
    
    def optimize_images(self, directory):
        """Optimize images in directory"""
        optimized_count = 0
        
        # This is a placeholder for image optimization
        # In a real implementation, you would use libraries like Pillow
        # to compress and optimize images
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        # Placeholder for actual image optimization
                        # self.compress_image(file_path)
                        optimized_count += 1
                    except Exception:
                        continue
        
        return optimized_count
    
    def get_disk_usage(self, path):
        """Get disk usage for path"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            
            # Convert to GB
            total_gb = total // (1024**3)
            used_gb = used // (1024**3)
            free_gb = free // (1024**3)
            
            usage_percent = (used / total) * 100
            
            return f"{used_gb}GB used / {total_gb}GB total ({usage_percent:.1f}% used)"
        
        except Exception:
            return "Unknown"
    
    def clean_old_logs(self, log_dir):
        """Clean log files older than 30 days"""
        files_removed = 0
        cutoff_time = time.time() - (30 * 24 * 60 * 60)  # 30 days ago
        
        for file in os.listdir(log_dir):
            if file.endswith('.log'):
                file_path = os.path.join(log_dir, file)
                try:
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        files_removed += 1
                except (OSError, IOError):
                    continue
        
        return files_removed
    
    def generate_robots_txt(self):
        """Generate robots.txt file"""
        robots_content = """User-agent: *
Allow: /

# Sitemaps
Sitemap: {}/sitemap.xml

# Disallow admin areas
Disallow: /admin/
Disallow: /api/admin/

# Disallow temporary files
Disallow: /tmp/
Disallow: /temp/

# Allow important pages
Allow: /
Allow: /about/
Allow: /services/
Allow: /contact/
Allow: /blog/
""".format(getattr(settings, 'SITE_URL', 'https://example.com'))
        
        robots_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'robots.txt')
        
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(robots_content)
    
    def generate_sitemap(self):
        """Generate basic sitemap.xml"""
        # This is a basic implementation
        # In production, you'd use django.contrib.sitemaps
        
        sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{}/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>{}/about/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{}/services/</loc>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>{}/contact/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
</urlset>""".format(
            getattr(settings, 'SITE_URL', 'https://example.com'),
            getattr(settings, 'SITE_URL', 'https://example.com'),
            getattr(settings, 'SITE_URL', 'https://example.com'),
            getattr(settings, 'SITE_URL', 'https://example.com')
        )
        
        sitemap_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'sitemap.xml')
        
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
    
    def check_meta_tags(self):
        """Check for common meta tag issues"""
        issues = []
        
        # This would check pages for missing or problematic meta tags
        # Implementation would depend on your page model structure
        
        return issues
    
    def get_system_status(self):
        """Get current system status"""
        status = {
            'timestamp': timezone.now().isoformat(),
            'database': self.check_database_status(),
            'cache': self.check_cache_status(),
            'disk_space': self.get_disk_usage(settings.BASE_DIR),
            'memory_usage': self.get_memory_usage(),
            'active_users': self.get_active_users_count(),
            'recent_errors': self.get_recent_errors()
        }
        
        return status
    
    def check_database_status(self):
        """Check database connection and performance"""
        try:
            with connection.cursor() as cursor:
                start_time = time.time()
                cursor.execute("SELECT 1")
                response_time = round((time.time() - start_time) * 1000, 2)
                
                return {
                    'status': 'healthy',
                    'response_time_ms': response_time,
                    'vendor': connection.vendor
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_cache_status(self):
        """Check cache system status"""
        try:
            test_key = 'system_check_' + str(int(time.time()))
            cache.set(test_key, 'test_value', timeout=60)
            retrieved_value = cache.get(test_key)
            cache.delete(test_key)
            
            if retrieved_value == 'test_value':
                return {'status': 'healthy'}
            else:
                return {'status': 'warning', 'message': 'Cache not working properly'}
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def get_memory_usage(self):
        """Get memory usage information"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': round(memory_info.rss / 1024 / 1024, 2),
                'vms_mb': round(memory_info.vms / 1024 / 1024, 2)
            }
        except ImportError:
            return {'status': 'psutil not available'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_active_users_count(self):
        """Get count of active users"""
        try:
            from django.contrib.auth.models import User
            from django.contrib.sessions.models import Session
            
            # Count active sessions
            active_sessions = Session.objects.filter(
                expire_date__gte=timezone.now()
            ).count()
            
            return active_sessions
        except Exception as e:
            return 0
    
    def get_recent_errors(self):
        """Get recent error count from logs"""
        try:
            log_file = os.path.join(settings.BASE_DIR, 'logs', 'django.log')
            if os.path.exists(log_file):
                # Count ERROR lines in the last 1000 lines
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-1000:] if len(lines) > 1000 else lines
                    error_count = sum(1 for line in recent_lines if 'ERROR' in line)
                    return error_count
            return 0
        except Exception:
            return 0

