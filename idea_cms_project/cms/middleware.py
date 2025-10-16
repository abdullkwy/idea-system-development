import json
import time
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.conf import settings
from .models import VisitorTracking


class VisitorTrackingMiddleware(MiddlewareMixin):
    """
    Middleware لتتبع الزوار تلقائياً
    يسجل كل زيارة للموقع مع معلومات مفصلة عن الزائر
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """معالجة الطلب قبل الوصول للـ view"""
        # تسجيل وقت بداية الطلب
        request._visitor_tracking_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """معالجة الاستجابة بعد الـ view"""
        # تجاهل طلبات API والملفات الثابتة
        if self._should_track_request(request):
            self._track_visitor(request, response)
        
        return response
    
    def _should_track_request(self, request):
        """تحديد ما إذا كان يجب تتبع هذا الطلب"""
        # تجاهل طلبات API
        if request.path.startswith('/api/'):
            return False
        
        # تجاهل الملفات الثابتة
        static_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf']
        if any(request.path.endswith(ext) for ext in static_extensions):
            return False
        
        # تجاهل طلبات AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return False
        
        # تجاهل طلبات البوتات (اختياري)
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        bot_indicators = ['bot', 'crawler', 'spider', 'scraper']
        if any(indicator in user_agent for indicator in bot_indicators):
            return False
        
        return True
    
    def _track_visitor(self, request, response):
        """تسجيل بيانات الزائر"""
        try:
            # حساب مدة الزيارة
            start_time = getattr(request, '_visitor_tracking_start_time', time.time())
            visit_duration = int((time.time() - start_time) * 1000)  # بالميلي ثانية
            
            # استخراج معلومات الطلب
            session_key = request.session.session_key or 'anonymous'
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            referrer = request.META.get('HTTP_REFERER', '')
            
            # معلومات الصفحة
            page_url = request.build_absolute_uri()
            page_title = self._extract_page_title(response)
            
            # تحليل User Agent
            device_info = self._parse_user_agent(user_agent)
            
            # تحديد ما إذا كانت الزيارة bounce (زيارة صفحة واحدة فقط)
            is_bounce = self._is_bounce_visit(request, visit_duration)
            
            # معلومات الموقع الجغرافي (يمكن تحسينها باستخدام خدمة GeoIP)
            location_info = self._get_location_info(ip_address)
            
            # إنشاء سجل تتبع الزائر
            VisitorTracking.objects.create(
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer,
                page_url=page_url,
                page_title=page_title,
                visit_duration=visit_duration,
                is_bounce=is_bounce,
                device_type=device_info['device_type'],
                browser=device_info['browser'],
                operating_system=device_info['operating_system'],
                country=location_info['country'],
                city=location_info['city']
            )
            
        except Exception as e:
            # تسجيل الخطأ دون إيقاف الطلب
            if settings.DEBUG:
                print(f"خطأ في تتبع الزائر: {e}")
    
    def _get_client_ip(self, request):
        """الحصول على عنوان IP الحقيقي للعميل"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
    
    def _extract_page_title(self, response):
        """استخراج عنوان الصفحة من HTML"""
        try:
            if hasattr(response, 'content') and response.get('Content-Type', '').startswith('text/html'):
                content = response.content.decode('utf-8', errors='ignore')
                # البحث عن تاج title
                import re
                title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                if title_match:
                    return title_match.group(1).strip()
        except:
            pass
        return 'صفحة غير محددة'
    
    def _parse_user_agent(self, user_agent):
        """تحليل User Agent لاستخراج معلومات الجهاز والمتصفح"""
        user_agent_lower = user_agent.lower()
        
        # تحديد نوع الجهاز
        device_type = 'desktop'
        if any(mobile in user_agent_lower for mobile in ['mobile', 'android', 'iphone']):
            device_type = 'mobile'
        elif any(tablet in user_agent_lower for tablet in ['tablet', 'ipad']):
            device_type = 'tablet'
        
        # تحديد المتصفح
        browser = 'غير محدد'
        if 'chrome' in user_agent_lower and 'edg' not in user_agent_lower:
            browser = 'Chrome'
        elif 'firefox' in user_agent_lower:
            browser = 'Firefox'
        elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
            browser = 'Safari'
        elif 'edg' in user_agent_lower:
            browser = 'Edge'
        elif 'opera' in user_agent_lower:
            browser = 'Opera'
        
        # تحديد نظام التشغيل
        operating_system = 'غير محدد'
        if 'windows' in user_agent_lower:
            operating_system = 'Windows'
        elif 'mac' in user_agent_lower and 'iphone' not in user_agent_lower and 'ipad' not in user_agent_lower:
            operating_system = 'macOS'
        elif 'linux' in user_agent_lower and 'android' not in user_agent_lower:
            operating_system = 'Linux'
        elif 'android' in user_agent_lower:
            operating_system = 'Android'
        elif 'iphone' in user_agent_lower or 'ipad' in user_agent_lower:
            operating_system = 'iOS'
        
        return {
            'device_type': device_type,
            'browser': browser,
            'operating_system': operating_system
        }
    
    def _is_bounce_visit(self, request, visit_duration):
        """تحديد ما إذا كانت الزيارة bounce"""
        # اعتبار الزيارة bounce إذا كانت أقل من 30 ثانية
        return visit_duration < 30000  # 30 ثانية بالميلي ثانية
    
    def _get_location_info(self, ip_address):
        """الحصول على معلومات الموقع الجغرافي"""
        # يمكن تحسين هذا باستخدام خدمة GeoIP مثل MaxMind
        # حالياً نعيد قيم افتراضية
        return {
            'country': 'المملكة العربية السعودية',
            'city': 'الرياض'
        }


class CORSMiddleware(MiddlewareMixin):
    """
    Middleware لإضافة headers الـ CORS
    يسمح للواجهة الأمامية بالوصول للـ APIs
    """
    
    def process_response(self, request, response):
        """إضافة headers الـ CORS"""
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response['Access-Control-Max-Age'] = '86400'
        
        return response
    
    def process_request(self, request):
        """معالجة طلبات OPTIONS للـ preflight"""
        if request.method == 'OPTIONS':
            from django.http import HttpResponse
            response = HttpResponse()
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response['Access-Control-Max-Age'] = '86400'
            return response
        
        return None


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware لإضافة headers الأمان
    """
    
    def process_response(self, request, response):
        """إضافة headers الأمان"""
        # منع تضمين الموقع في iframe من مواقع أخرى
        response['X-Frame-Options'] = 'SAMEORIGIN'
        
        # منع تخمين نوع المحتوى
        response['X-Content-Type-Options'] = 'nosniff'
        
        # تفعيل حماية XSS في المتصفحات
        response['X-XSS-Protection'] = '1; mode=block'
        
        # إجبار استخدام HTTPS (في الإنتاج)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response




# CDN Middleware Classes
import re
import sys
import os

# إضافة المسار الجذر للمشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from cdn_config import cdn_config
except ImportError:
    cdn_config = None

class CDNMiddleware(MiddlewareMixin):
    """
    Middleware لتحويل روابط الملفات الثابتة إلى روابط CDN
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cdn_enabled = cdn_config is not None and cdn_config.get_active_provider()[0] is not None
        
        # أنماط regex للملفات الثابتة
        self.static_patterns = [
            r'(/static/[^"\'>\s]+\.(?:css|js|png|jpg|jpeg|gif|webp|svg|woff|woff2|ttf|eot|ico|pdf|mp4|webm))',
            r'(/media/[^"\'>\s]+\.(?:png|jpg|jpeg|gif|webp|svg|pdf|mp4|webm))',
        ]
        
        super().__init__(get_response)
    
    def __call__(self, request):
        response = self.get_response(request)
        
        if self.cdn_enabled and self._should_process_response(response):
            response = self._process_response(response)
            
        return response
    
    def _should_process_response(self, response):
        """تحديد ما إذا كان يجب معالجة الاستجابة"""
        return (
            response.status_code == 200 and
            response.get('Content-Type', '').startswith('text/html') and
            hasattr(response, 'content')
        )
    
    def _process_response(self, response):
        """معالجة الاستجابة وتحويل روابط الملفات الثابتة"""
        try:
            content = response.content.decode('utf-8')
            
            for pattern in self.static_patterns:
                content = re.sub(
                    pattern,
                    self._replace_static_url,
                    content
                )
            
            response.content = content.encode('utf-8')
            response['Content-Length'] = len(response.content)
            
        except Exception as e:
            # في حالة حدوث خطأ، نعيد الاستجابة الأصلية
            print(f"خطأ في CDN Middleware: {e}")
            
        return response
    
    def _replace_static_url(self, match):
        """استبدال رابط الملف الثابت برابط CDN"""
        original_url = match.group(1)
        
        if cdn_config and cdn_config.should_use_cdn(original_url):
            cdn_url = cdn_config.get_cdn_url(original_url)
            return cdn_url
            
        return original_url


class CacheControlMiddleware(MiddlewareMixin):
    """
    Middleware لإضافة headers التحكم في التخزين المؤقت
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # إعدادات التخزين المؤقت للملفات المختلفة
        self.cache_settings = {
            'static': {
                'max_age': 31536000,  # سنة واحدة
                'extensions': ['css', 'js', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'woff', 'woff2', 'ttf', 'eot', 'ico']
            },
            'media': {
                'max_age': 2592000,  # شهر واحد
                'extensions': ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'pdf', 'mp4', 'webm']
            },
            'html': {
                'max_age': 3600,  # ساعة واحدة
                'extensions': ['html']
            }
        }
        
        super().__init__(get_response)
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # إضافة headers التخزين المؤقت
        self._add_cache_headers(request, response)
        
        return response
    
    def _add_cache_headers(self, request, response):
        """إضافة headers التحكم في التخزين المؤقت"""
        path = request.path
        
        # تحديد نوع الملف
        file_type = self._get_file_type(path)
        
        if file_type:
            cache_setting = self.cache_settings.get(file_type)
            if cache_setting:
                max_age = cache_setting['max_age']
                
                # إضافة headers التخزين المؤقت
                response['Cache-Control'] = f'public, max-age={max_age}'
                response['Expires'] = self._get_expires_date(max_age)
                
                # إضافة ETag للملفات الثابتة
                if file_type in ['static', 'media']:
                    response['ETag'] = f'"{hash(path)}"'
    
    def _get_file_type(self, path):
        """تحديد نوع الملف بناءً على المسار"""
        if path.startswith('/static/'):
            extension = path.split('.')[-1].lower()
            if extension in self.cache_settings['static']['extensions']:
                return 'static'
        elif path.startswith('/media/'):
            extension = path.split('.')[-1].lower()
            if extension in self.cache_settings['media']['extensions']:
                return 'media'
        elif path.endswith('.html') or '.' not in path.split('/')[-1]:
            return 'html'
            
        return None
    
    def _get_expires_date(self, max_age):
        """حساب تاريخ انتهاء الصلاحية"""
        from datetime import datetime, timedelta
        from email.utils import formatdate
        
        expires_date = datetime.utcnow() + timedelta(seconds=max_age)
        return formatdate(expires_date.timestamp(), usegmt=True)


class CompressionMiddleware(MiddlewareMixin):
    """
    Middleware لضغط المحتوى (Gzip)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # أنواع المحتوى التي يجب ضغطها
        self.compressible_types = [
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/json',
            'application/xml',
            'text/xml',
            'text/plain'
        ]
        
        super().__init__(get_response)
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # ضغط المحتوى إذا كان مدعوماً
        if self._should_compress(request, response):
            response = self._compress_response(response)
            
        return response
    
    def _should_compress(self, request, response):
        """تحديد ما إذا كان يجب ضغط الاستجابة"""
        # التحقق من دعم العميل للضغط
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        if 'gzip' not in accept_encoding:
            return False
            
        # التحقق من نوع المحتوى
        content_type = response.get('Content-Type', '').split(';')[0]
        if content_type not in self.compressible_types:
            return False
            
        # التحقق من حجم المحتوى (لا نضغط الملفات الصغيرة)
        if len(response.content) < 1024:  # أقل من 1KB
            return False
            
        # التحقق من عدم وجود ضغط مسبق
        if response.get('Content-Encoding'):
            return False
            
        return True
    
    def _compress_response(self, response):
        """ضغط محتوى الاستجابة"""
        import gzip
        
        try:
            # ضغط المحتوى
            compressed_content = gzip.compress(response.content)
            
            # تحديث الاستجابة
            response.content = compressed_content
            response['Content-Encoding'] = 'gzip'
            response['Content-Length'] = len(compressed_content)
            
            # إضافة Vary header
            vary = response.get('Vary', '')
            if 'Accept-Encoding' not in vary:
                if vary:
                    vary += ', Accept-Encoding'
                else:
                    vary = 'Accept-Encoding'
                response['Vary'] = vary
                
        except Exception as e:
            print(f"خطأ في ضغط المحتوى: {e}")
            
        return response
