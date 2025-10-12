# دليل المطورين - تحديثات المرحلة الثانية لنظام IDEA

## الملخص

يوضح هذا الدليل التحديثات والميزات الجديدة التي تم إضافتها إلى نظام IDEA في المرحلة الثانية من التطوير. يهدف هذا الدليل إلى مساعدة المطورين على فهم كيفية عمل هذه الميزات وكيفية دمجها وصيانتها.

## 1. الشات بوت المتقدم (AI Chatbot)

تم تطوير شات بوت متقدم باستخدام Flask و OpenAI API لتوفير تجربة تفاعلية وذكية للمستخدمين. يتكامل الشات بوت مع نماذج لغوية متقدمة لفهم الاستفسارات وتقديم إجابات دقيقة.

### 1.1. البنية

*   **الخادم (Backend):** `chatbot_service.py` (Flask application)
*   **الواجهة الأمامية (Frontend):** `website_project_v3/assets/js/chatbot-advanced.js`
*   **الاستجابات:** `website_project_v3/assets/data/chatbot-responses.json`
*   **الأنماط:** `website_project_v3/assets/css/chatbot-advanced.css`

### 1.2. الإعداد والتشغيل

1.  **تثبيت التبعيات:**
    ```bash
    pip3 install flask openai flask-cors
    ```
2.  **تشغيل الخدمة:**
    ```bash
    python3 chatbot_service.py
    ```
    ستعمل الخدمة على `http://localhost:5000`.

### 1.3. نقاط النهاية (API Endpoints)

*   `GET /health`: للتحقق من حالة الخدمة.
*   `POST /chat`: لإرسال رسالة إلى الشات بوت وتلقي الرد.
    *   **الطلب:** `{"message": "مرحباً"}`
    *   **الاستجابة:** `{"response": "أهلاً بك..."}`
*   `POST /chat/reset`: لإعادة تعيين سياق المحادثة.

### 1.4. التكامل مع الواجهة الأمامية

ملف `chatbot-advanced.js` مسؤول عن التعامل مع واجهة المستخدم، إرسال الرسائل إلى `chatbot_service.py`، وعرض الردود. يتم تضمينه في `index.html`.

## 2. نظام الإشعارات والتحديثات الحية (WebSockets Notifications)

تم دمج نظام إشعارات وتحديثات حية باستخدام WebSockets لتقديم معلومات فورية للمستخدمين حول تحديثات المشاريع، تنبيهات النظام، وغيرها.

### 2.1. البنية

*   **الخادم (Backend):** `websocket_service.py` (Flask-SocketIO application)
*   **الواجهة الأمامية (Frontend):** `website_project_v3/assets/js/websocket-client.js`
*   **الأنماط:** `website_project_v3/assets/css/websocket-notifications.css`

### 2.2. الإعداد والتشغيل

1.  **تثبيت التبعيات:**
    ```bash
    pip3 install flask flask-socketio eventlet
    ```
2.  **تشغيل الخدمة:**
    ```bash
    python3 websocket_service.py
    ```
    ستعمل الخدمة على `http://localhost:3001`.

### 2.3. الأحداث (Events)

*   **`connect`:** عند اتصال العميل.
*   **`disconnect`:** عند قطع اتصال العميل.
*   **`join_room`:** للانضمام إلى غرفة إشعارات محددة (مثال: `admin`, `client`, `team`, `general`).
*   **`leave_room`:** للمغادرة من غرفة.
*   **`notification`:** لاستقبال إشعارات عامة.
*   **`live_update`:** لاستقبال تحديثات حية (مثل تحديثات المشاريع).
*   **`system_stats`:** لاستقبال إحصائيات النظام.

### 2.4. التكامل مع الواجهة الأمامية

ملف `websocket-client.js` يدير الاتصال بالـ WebSocket، الانضمام إلى الغرف، ومعالجة الإشعارات والتحديثات الواردة. يتم تضمينه في `index.html`.

## 3. تطبيق الويب التقدمي (PWA Functionality)

تم تحويل الموقع ولوحات التحكم إلى تطبيقات ويب تقدمية (PWA) لتقديم تجربة مستخدم محسنة، بما في ذلك إمكانية التثبيت على الأجهزة، العمل دون اتصال، وتحديثات التطبيق.

### 3.1. البنية

*   **Service Worker:** `website_project_v3/sw.js`
*   **Web App Manifest:** `website_project_v3/manifest.json`، `client_portal/pwa-manifest.json`، `team_management/pwa-manifest.json`
*   **صفحة عدم الاتصال:** `website_project_v3/offline.html`
*   **مدير PWA:** `website_project_v3/assets/js/pwa-manager.js`
*   **الأنماط:** `website_project_v3/assets/css/pwa-styles.css`

### 3.2. المكونات الرئيسية

*   **`sw.js` (Service Worker):** مسؤول عن التخزين المؤقت للملفات (Caching Strategy)، العمل دون اتصال (Offline-first)، ومزامنة الخلفية (Background Sync).
*   **`manifest.json`:** يحدد خصائص التطبيق مثل الاسم، الأيقونات، `start_url`، و `display` (standalone).
*   **`offline.html`:** صفحة مخصصة تظهر للمستخدمين عند عدم توفر اتصال بالإنترنت.
*   **`pwa-manager.js`:** يدير تسجيل Service Worker، يعالج أحداث التثبيت والتحديث، ويعرض إشعارات PWA للمستخدم.

### 3.3. الإعداد

1.  **تضمين Manifest:** تأكد من وجود `<link rel="manifest" href="/manifest.json">` في قسم `<head>` من ملفات HTML.
2.  **تسجيل Service Worker:** يتم تسجيله تلقائياً بواسطة `pwa-manager.js`.

## 4. تحديثات الوثائق

تم تحديث الوثائق التالية لتعكس التغييرات الجديدة:

*   **`achievements_and_development_plan.md`:** تم تحديثه ليشمل إنجازات المرحلة الثانية.
*   **`phase2_test_report.md`:** تقرير مفصل عن اختبار الميزات الجديدة.

## 5. رفع التغييرات إلى GitHub

تم تجميع جميع الملفات المحدثة في أرشيف مضغوط `improved_idea_system_phase2_updates.zip` وجاهزة للرفع إلى مستودع GitHub. يجب على المطورين التأكد من سحب أحدث التغييرات ودمجها في فروعهم المحلية.

## الخلاصة

تضيف هذه التحديثات تحسينات كبيرة لنظام IDEA من حيث التفاعل، الإشعارات الفورية، وتجربة المستخدم على الأجهزة المحمولة. يجب على المطورين مراجعة هذا الدليل بعناية لضمان الفهم الكامل للميزات الجديدة وكيفية صيانتها وتطويرها مستقبلاً.
