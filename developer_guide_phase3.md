# دليل المطورين: تحسينات الأداء والتوسع (المرحلة الثالثة)

## الملخص

يوضح هذا الدليل التحسينات الرئيسية التي تم إجراؤها على نظام IDEA لتعزيز أدائه وقابليته للتوسع. تغطي هذه التحسينات تحسين قاعدة البيانات، وتكامل شبكة توصيل المحتوى (CDN)، وتنفيذ موازنة الأحمال (Load Balancing)، بالإضافة إلى إعداد أدوات المراقبة واختبار الأداء.

## 1. تحسين قاعدة البيانات

لتحسين أداء قاعدة البيانات، تم التركيز على فهرسة الجداول وتحسين الاستعلامات.

### 1.1. إضافة الفهارس (Indexes)

تم إضافة فهارس على الأعمدة المستخدمة بشكل متكرر في عمليات البحث والتصفية والربط بين الجداول. على سبيل المثال، في ملف `idea_cms_project/cms/models.py`، يمكن إضافة فهارس إلى الحقول التي تُستخدم كـ `ForeignKey` أو التي يتم البحث فيها بشكل متكرر.

**مثال:**

```python
# idea_cms_project/cms/models.py

from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=255, db_index=True) # إضافة فهرس هنا
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_index=True) # إضافة فهرس هنا
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, db_index=True) # إضافة فهرس هنا
    # ... حقول أخرى

    class Meta:
        indexes = [
            models.Index(fields=["name", "status"]),
        ]
```

بعد تعديل `models.py`، يجب تشغيل أوامر الترحيل:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 1.2. تحسين الاستعلامات

تم مراجعة الاستعلامات البطيئة في Django وتحسينها باستخدام تقنيات مثل `select_related` و `prefetch_related` لتقليل عدد استعلامات قاعدة البيانات.

**مثال:**

```python
# بدلاً من:
projects = Project.objects.filter(status="active")
for project in projects:
    print(project.client.name) # كل وصول يجلب العميل باستعلام جديد

# استخدم:
projects = Project.objects.select_related("client").filter(status="active")
for project in projects:
    print(project.client.name) # يجلب العملاء في استعلام واحد
```

## 2. تكامل شبكة توصيل المحتوى (CDN)

تم تكامل CDN لتحسين سرعة تحميل الملفات الثابتة. يتطلب ذلك تعديلات في إعدادات Django و Nginx.

### 2.1. إعدادات Django

في `idea_cms_project/idea_cms/settings.py`، تم إضافة إعدادات CDN:

```python
# إعدادات CDN
CDN_ENABLED = os.getenv("CDN_ENABLED", "false").lower() == "true"
CLOUDFLARE_ENABLED = os.getenv("CLOUDFLARE_ENABLED", "false").lower() == "true"
CLOUDFLARE_ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID", ")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", ")
CLOUDFLARE_BASE_URL = os.getenv("CLOUDFLARE_BASE_URL", "https://cdn.ideateeam.com")

# إعدادات AWS CloudFront
AWS_CLOUDFRONT_ENABLED = os.getenv("AWS_CLOUDFRONT_ENABLED", "false").lower() == "true"
AWS_CLOUDFRONT_DISTRIBUTION_ID = os.getenv("AWS_CLOUDFRONT_DISTRIBUTION_ID", ")
AWS_CLOUDFRONT_DOMAIN = os.getenv("AWS_CLOUDFRONT_DOMAIN", ")

# إعدادات التخزين المؤقت
CACHE_MIDDLEWARE_ENABLED = True
STATIC_FILES_CACHE_TTL = 31536000  # سنة واحدة
MEDIA_FILES_CACHE_TTL = 2592000   # شهر واحد
HTML_CACHE_TTL = 3600             # ساعة واحدة

# إعدادات الضغط
COMPRESSION_ENABLED = True
COMPRESSION_MIN_SIZE = 1024  # 1KB

# استخدام CDN لـ STATIC_URL و MEDIA_URL إذا كان مفعلاً
if CDN_ENABLED:
    STATIC_URL = CLOUDFLARE_BASE_URL + ")
    MEDIA_URL = CLOUDFLARE_BASE_URL + ")
```

وتم إضافة `CDNMiddleware` و `CompressionMiddleware` و `CacheControlMiddleware` إلى `MIDDLEWARE` في نفس الملف.

### 2.2. إعداد Nginx

تم تعديل ملف `nginx_load_balancer.conf` لخدمة الملفات الثابتة والوسائط مع رؤوس (headers) التخزين المؤقت المناسبة، كما هو موضح في قسم موازنة الأحمال.

## 3. موازنة الأحمال (Load Balancing) باستخدام Nginx

تم إعداد Nginx كموازن أحمال لتوزيع الطلبات على خوادم التطبيق المختلفة (Django, WebSocket, Chatbot).

### 3.1. تكوين Nginx (`nginx_load_balancer.conf`)

تم إنشاء ملف `nginx_load_balancer.conf` (موجود في جذر المشروع) لتحديد `upstream` للخوادم وتكوين قواعد التوجيه والتخزين المؤقت وتحديد المعدل.

**النقاط الرئيسية في التكوين:**

*   **Upstream Definitions**: تعريف مجموعات الخوادم الخلفية (مثل `idea_backend`, `websocket_backend`, `chatbot_backend`).
*   **Load Balancing Strategy**: استخدام `least_conn` لتوزيع الطلبات على الخوادم الأقل اتصالاً.
*   **SSL/TLS Configuration**: إعداد شهادات SSL لـ HTTPS.
*   **Static and Media Files**: توجيه طلبات الملفات الثابتة والوسائط مع التخزين المؤقت المناسب.
*   **API Endpoints**: توجيه طلبات API إلى `idea_backend` مع التخزين المؤقت وتحديد المعدل.
*   **WebSocket Proxy**: إعداد توجيه خاص لطلبات WebSocket.
*   **Chatbot Proxy**: توجيه طلبات الشات بوت.
*   **Admin Protection**: حماية لوحة تحكم Django Admin بتقييد الوصول.
*   **Health Check Endpoint**: نقطة نهاية `/health/` لفحص صحة التطبيق.

### 3.2. إدارة الخوادم المتعددة (`manage_servers.py`)

تم إنشاء سكريبت `manage_servers.py` (موجود في جذر المشروع) لتبسيط عملية تشغيل وإيقاف وإعادة تشغيل ومراقبة خوادم Django و WebSocket و Chatbot المتعددة. يستخدم هذا السكريبت `psutil` لمراقبة العمليات.

**الاستخدام:**

```bash
python manage_servers.py start    # تشغيل جميع الخوادم
python manage_servers.py stop     # إيقاف جميع الخوادم
python manage_servers.py restart  # إعادة تشغيل جميع الخوادم
python manage_servers.py status   # عرض حالة الخوادم
python manage_servers.py health   # فحص صحة الخوادم
```

## 4. مراقبة الأداء (Prometheus و Grafana)

تم إعداد Prometheus و Grafana لمراقبة أداء النظام بشكل مستمر.

### 4.1. `docker-compose.production.yml`

يحتوي هذا الملف (موجود في جذر المشروع) على تعريفات الخدمات لـ Prometheus و Grafana و Node Exporter، بالإضافة إلى خوادم Django و WebSocket و Chatbot المتعددة وقاعدة البيانات Redis و PostgreSQL.

### 4.2. `monitoring/prometheus.yml`

يحدد هذا الملف (موجود في `monitoring/`) أهداف المراقبة لـ Prometheus، بما في ذلك خوادم Django و WebSocket و Chatbot و Nginx و PostgreSQL و Redis و Elasticsearch و Celery.

### 4.3. `monitoring/alert_rules.yml`

يحتوي هذا الملف (موجود في `monitoring/`) على قواعد التنبيه لـ Prometheus، والتي تقوم بتنبيه المسؤولين في حالة وجود مشاكل مثل توقف الخوادم، ارتفاع استخدام المعالج أو الذاكرة، أو ارتفاع معدلات الأخطاء.

## 5. اختبار الأداء والتوسع (Locust)

تم استخدام Locust لإجراء اختبارات التحميل على النظام.

### 5.1. `locustfile.py`

يحتوي هذا الملف (موجود في جذر المشروع) على سيناريوهات اختبار التحميل التي تحاكي سلوك المستخدمين المختلفين، بما في ذلك تصفح الصفحات، استخدام الشات بوت، وإرسال رسائل WebSocket، والوصول إلى لوحات التحكم.

**الاستخدام:**

```bash
python3 -m locust -f locustfile.py --web-host 127.0.0.1 --host http://127.0.0.1
```

ثم يمكن الوصول إلى واجهة Locust الرسومية عبر المتصفح على `http://localhost:8089` (أو المنفذ المحدد).

### 5.2. تحليل النتائج

بعد انتهاء اختبار التحميل، يتم إنشاء ملفات `locust_report_stats.csv` و `locust_report.html` التي توفر تحليلاً مفصلاً لأداء النظام، بما في ذلك متوسط أوقات الاستجابة، ومعدلات الطلبات، ومعدلات الفشل.

## الخلاصة

توفر هذه التحسينات بنية تحتية قوية ومرنة لنظام IDEA، مما يضمن أداءً عاليًا وقابلية للتوسع واستقرارًا. يجب على المطورين الجدد مراجعة هذه الوثائق لفهم كيفية عمل النظام وكيفية المساهمة في تطويره المستقبلي.
