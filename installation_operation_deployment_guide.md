# دليل التثبيت والتشغيل والنشر لنظام IDEA

## 1. المقدمة

يوفر هذا الدليل إرشادات مفصلة لتثبيت وتشغيل ونشر نظام IDEA، والذي يتضمن واجهة خلفية مبنية على Django CMS، وواجهة أمامية React، بالإضافة إلى ميزات متقدمة مثل الشات بوت، WebSockets، CDN، وموازنة الأحمال.

## 2. المتطلبات الأساسية

لضمان عمل النظام بشكل صحيح، تأكد من توفر المتطلبات التالية:

*   **نظام التشغيل:** Ubuntu 20.04+ (موصى به) أو أي نظام تشغيل يدعم Docker.
*   **Docker و Docker Compose:** لتشغيل البيئة المعزولة.
*   **Git:** لاستنساخ المستودع.
*   **Python 3.8+:** لتشغيل سكريبتات الإدارة.
*   **Node.js و npm/yarn:** لتطوير الواجهة الأمامية (إذا لزم الأمر).

## 3. التثبيت والتشغيل المحلي (بيئة التطوير)

### 3.1. استنساخ المستودع

```bash
git clone https://github.com/abdullkwy/idea-system-development.git
cd idea-system-development
```

### 3.2. إعداد ملفات البيئة

أنشئ ملف `.env` في جذر المشروع بناءً على `env.example` (إذا كان موجوداً) وقم بتكوين المتغيرات اللازمة مثل مفاتيح API وقواعد البيانات.

### 3.3. تشغيل الخدمات باستخدام Docker Compose

للتشغيل السريع لجميع مكونات النظام (Django, PostgreSQL, Redis, Nginx, React Frontend, Chatbot, WebSocket) في بيئة تطوير:

```bash
docker-compose up --build
```

سيقوم هذا الأمر ببناء صور Docker وتشغيل جميع الخدمات. قد يستغرق الأمر بعض الوقت في المرة الأولى.

### 3.4. الوصول إلى النظام

*   **الواجهة الأمامية (React):** عادةً ما تكون متاحة على `http://localhost:3000`.
*   **الواجهة الخلفية (Django Admin):** عادةً ما تكون متاحة على `http://localhost:8000/admin`.
*   **Nginx (كموازن أحمال/خادم ثابت):** قد يكون متاحاً على `http://localhost:80` أو منفذ آخر حسب التكوين.

## 4. النشر (بيئة الإنتاج)

للنشر في بيئة إنتاج، يوصى باستخدام ملف `docker-compose.production.yml` الذي يتضمن ميزات مثل موازنة الأحمال والمراقبة.

### 4.1. إعداد ملفات البيئة للإنتاج

أنشئ ملف `.env.production` وقم بتكوين المتغيرات الحساسة والخاصة بالإنتاج، مثل `SECRET_KEY`، `DATABASE_URL`، `ALLOWED_HOSTS`، وإعدادات CDN ومفاتيح API لـ OpenAI.

### 4.2. تشغيل الخدمات في الإنتاج

```bash
docker-compose -f docker-compose.production.yml up --build -d
```

سيقوم هذا الأمر بتشغيل الخدمات في الخلفية (`-d`) مع بناء الصور (`--build`).

### 4.3. تكوين Nginx (موازن الأحمال)

ملف `nginx_load_balancer.conf` (الموجود في جذر المشروع) هو التكوين الرئيسي لـ Nginx الذي يعمل كموازن أحمال وخادم للملفات الثابتة. تأكد من تعديل هذا الملف ليناسب أسماء النطاقات (domains) وشهادات SSL الخاصة بك.

**الخطوات الأساسية:**

1.  **تعديل `nginx_load_balancer.conf`:** قم بتحديث `server_name`، مسارات شهادات SSL، وأي إعدادات أخرى خاصة بالبيئة.
2.  **إعادة تحميل Nginx:** بعد أي تغييرات في تكوين Nginx، تأكد من إعادة تحميله:
    ```bash
    docker-compose -f docker-compose.production.yml exec nginx nginx -s reload
    ```

### 4.4. إدارة الخوادم (Django, WebSocket, Chatbot)

يمكنك استخدام السكريبت `manage_servers.py` (الموجود في جذر المشروع) لإدارة خوادم Django و WebSocket و Chatbot المتعددة.

**أمثلة على الاستخدام:**

```bash
python manage_servers.py start    # تشغيل جميع الخوادم
python manage_servers.py stop     # إيقاف جميع الخوادم
python manage_servers.py restart  # إعادة تشغيل جميع الخوادم
python manage_servers.py status   # عرض حالة الخوادم
python manage_servers.py health   # فحص صحة الخوادم
```

### 4.5. المراقبة (Prometheus و Grafana)

يتم تضمين Prometheus و Grafana في ملف `docker-compose.production.yml` للمراقبة. يمكنك الوصول إليهما عادةً على المنافذ التالية (تأكد من تكوينها في ملف Docker Compose):

*   **Prometheus:** `http://localhost:9090`
*   **Grafana:** `http://localhost:3000` (قد يتطلب تسجيل الدخول ببيانات اعتماد افتراضية مثل `admin/admin`)

## 5. استكشاف الأخطاء وإصلاحها

*   **مشاكل Docker Compose:** تأكد من أن Docker يعمل وأن جميع المنافذ المطلوبة متاحة.
*   **أخطاء Django:** تحقق من سجلات Django للحصول على تفاصيل الأخطاء.
*   **مشاكل الاتصال:** تأكد من أن جدران الحماية (firewalls) تسمح بالاتصالات على المنافذ المطلوبة (مثل 80، 443، 5000، 3001).
*   **مشاكل CDN:** تحقق من إعدادات CDN الخاصة بك وتأكد من أن الملفات الثابتة يتم تقديمها بشكل صحيح.

## 6. تحديثات النظام

للتحديثات المستقبلية، قم بسحب أحدث التغييرات من المستودع وإعادة بناء وتشغيل الخدمات:

```bash
git pull origin master
docker-compose -f docker-compose.production.yml up --build -d
```

**ملاحظة:** قد تحتاج إلى تشغيل `python manage.py makemigrations` و `python manage.py migrate` داخل حاوية Django بعد سحب التغييرات التي تتضمن تعديلات على نماذج قاعدة البيانات.
