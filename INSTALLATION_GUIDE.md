# دليل التثبيت السريع - نظام آيديا المتكامل

## التثبيت في 5 دقائق ⚡

### المتطلبات الأساسية
- Python 3.8+ 
- Node.js 14+ (اختياري)
- Git

### خطوات التثبيت

#### 1. تحميل المشروع
```bash
# إذا كان لديك Git
git clone [repository-url]
cd website_project_v3

# أو فك ضغط الملف المضغوط
unzip website_project_v3_final.zip
cd website_project_v3
```

#### 2. إعداد البيئة الافتراضية
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. تثبيت المتطلبات
```bash
cd idea_cms_project
pip install -r requirements.txt
```

#### 4. إعداد قاعدة البيانات
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
# أدخل: admin / admin@example.com / admin123
```

#### 5. إضافة البيانات التجريبية (اختياري)
```bash
python add_sample_data_advanced.py
```

#### 6. تشغيل النظام
```bash
# Terminal 1: Django CMS
python manage.py runserver 8000

# Terminal 2: الموقع الرئيسي
cd ../website_project_v3
python -m http.server 3000

# Terminal 3: لوحة التحكم
cd ../admin_panel
python -m http.server 3001
```

### الوصول للنظام
- **الموقع الرئيسي**: http://localhost:3000
- **لوحة التحكم**: http://localhost:3001
- **Django Admin**: http://localhost:8000/admin

### بيانات الدخول
- **المستخدم**: admin
- **كلمة المرور**: admin123

---

## التثبيت للإنتاج 🚀

### 1. إعداد الخادم
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات
sudo apt install python3 python3-pip python3-venv nginx postgresql -y
```

### 2. إعداد قاعدة البيانات
```bash
sudo -u postgres psql
CREATE DATABASE idea_cms;
CREATE USER idea_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE idea_cms TO idea_user;
\q
```

### 3. إعداد المشروع
```bash
cd /var/www/
sudo git clone [repository-url] idea_website
sudo chown -R www-data:www-data idea_website
cd idea_website

# إعداد البيئة الافتراضية
python3 -m venv venv
source venv/bin/activate
pip install -r idea_cms_project/requirements.txt
```

### 4. إعداد Django للإنتاج
```bash
cd idea_cms_project

# تحديث إعدادات الإنتاج
export DEBUG=False
export ALLOWED_HOSTS=your-domain.com
export DATABASE_URL=postgresql://idea_user:strong_password@localhost/idea_cms

# تطبيق التغييرات
python manage.py collectstatic --noinput
python manage.py migrate
```

### 5. إعداد Nginx
```bash
sudo nano /etc/nginx/sites-available/idea_website
```

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # الموقع الرئيسي
    location / {
        root /var/www/idea_website/website_project_v3;
        index index.html;
        try_files $uri $uri/ =404;
    }
    
    # لوحة التحكم
    location /admin-panel/ {
        alias /var/www/idea_website/admin_panel/;
        index index.html;
    }
    
    # Django API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # الملفات الثابتة
    location /static/ {
        alias /var/www/idea_website/idea_cms_project/static/;
    }
    
    location /media/ {
        alias /var/www/idea_website/idea_cms_project/media/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/idea_website /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. إعداد Gunicorn
```bash
# إنشاء ملف الخدمة
sudo nano /etc/systemd/system/idea_cms.service
```

```ini
[Unit]
Description=Idea CMS Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/idea_website/idea_cms_project
Environment="PATH=/var/www/idea_website/venv/bin"
ExecStart=/var/www/idea_website/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 idea_cms.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start idea_cms
sudo systemctl enable idea_cms
```

### 7. إعداد SSL (اختياري)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## استكشاف الأخطاء الشائعة 🔧

### خطأ في تثبيت المتطلبات
```bash
# تحديث pip
pip install --upgrade pip

# تثبيت المتطلبات واحداً تلو الآخر
pip install Django==4.2.7
pip install djangorestframework==3.14.0
```

### خطأ في قاعدة البيانات
```bash
# حذف قاعدة البيانات وإعادة إنشائها
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
```

### خطأ في الصلاحيات (Linux)
```bash
sudo chown -R $USER:$USER .
chmod -R 755 .
```

### خطأ في المنافذ
```bash
# التحقق من المنافذ المستخدمة
netstat -tlnp | grep :3000
netstat -tlnp | grep :8000

# استخدام منافذ أخرى
python -m http.server 3002
python manage.py runserver 8001
```

---

## الدعم والمساعدة 📞

### المشاكل الشائعة
1. **الموقع لا يتحمل**: تحقق من تشغيل الخوادم
2. **خطأ 404**: تأكد من صحة المسارات
3. **خطأ في قاعدة البيانات**: راجع إعدادات الاتصال
4. **مشاكل الصلاحيات**: تحقق من صلاحيات الملفات

### التواصل للدعم
- **البريد الإلكتروني**: info@ideateeam.com
- **الهاتف**: 773171477
- **الموقع**: www.ideateeam.com

### الموارد المفيدة
- [Django Documentation](https://docs.djangoproject.com/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PostgreSQL Guide](https://www.postgresql.org/docs/)

---

**نصائح مهمة**:
- احتفظ بنسخة احتياطية قبل أي تحديث
- غيّر كلمات المرور الافتراضية
- استخدم HTTPS في الإنتاج
- راقب سجلات النظام بانتظام

✅ **النظام جاهز للاستخدام!**

