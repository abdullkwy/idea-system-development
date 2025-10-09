from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from PIL import Image
import os
import json


class Category(models.Model):
    """نموذج التصنيفات"""
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم التصنيف")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="الرابط المختصر")
    description = models.TextField(blank=True, verbose_name="الوصف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """نموذج الوسوم"""
    name = models.CharField(max_length=50, unique=True, verbose_name="اسم الوسم")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="الرابط المختصر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "وسم"
        verbose_name_plural = "الوسوم"
        ordering = ['name']

    def __str__(self):
        return self.name


class Media(models.Model):
    """نموذج مكتبة الوسائط"""
    MEDIA_TYPES = [
        ('image', 'صورة'),
        ('video', 'فيديو'),
        ('document', 'مستند'),
        ('other', 'أخرى'),
    ]

    title = models.CharField(max_length=200, verbose_name="العنوان")
    file = models.FileField(upload_to='uploads/%Y/%m/', verbose_name="الملف")
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, verbose_name="نوع الوسائط")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="النص البديل")
    description = models.TextField(blank=True, verbose_name="الوصف")
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name="حجم الملف")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="رفع بواسطة")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرفع")

    class Meta:
        verbose_name = "وسائط"
        verbose_name_plural = "مكتبة الوسائط"
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            # تحديد نوع الوسائط تلقائياً
            file_extension = os.path.splitext(self.file.name)[1].lower()
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                self.media_type = 'image'
            elif file_extension in ['.mp4', '.avi', '.mov', '.wmv']:
                self.media_type = 'video'
            elif file_extension in ['.pdf', '.doc', '.docx', '.txt']:
                self.media_type = 'document'
            else:
                self.media_type = 'other'
        super().save(*args, **kwargs)


class Page(models.Model):
    """نموذج الصفحات"""
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('published', 'منشور'),
        ('archived', 'مؤرشف'),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان الصفحة")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="الرابط المختصر")
    content = models.TextField(verbose_name="المحتوى")
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="المقتطف")
    featured_image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='featured_pages', verbose_name="الصورة المميزة")
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="عنوان SEO")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="وصف SEO")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="الحالة")
    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    show_in_menu = models.BooleanField(default=True, verbose_name="إظهار في القائمة")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المؤلف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ النشر")

    class Meta:
        verbose_name = "صفحة"
        verbose_name_plural = "الصفحات"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('page_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    """نموذج مقالات المدونة"""
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('published', 'منشور'),
        ('archived', 'مؤرشف'),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان المقال")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="الرابط المختصر")
    content = models.TextField(verbose_name="المحتوى")
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="المقتطف")
    featured_image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='featured_posts', verbose_name="الصورة المميزة")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="التصنيف")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="الوسوم")
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="عنوان SEO")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="وصف SEO")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="الحالة")
    is_featured = models.BooleanField(default=False, verbose_name="مقال مميز")
    views_count = models.PositiveIntegerField(default=0, verbose_name="عدد المشاهدات")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المؤلف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ النشر")

    class Meta:
        verbose_name = "مقال"
        verbose_name_plural = "مقالات المدونة"
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class SiteSettings(models.Model):
    """نموذج إعدادات الموقع"""
    site_title = models.CharField(max_length=200, default="آيديا للاستشارات والحلول التسويقية", 
                                 verbose_name="عنوان الموقع")
    site_description = models.TextField(default="خبراء التسويق والإبداع", verbose_name="وصف الموقع")
    site_logo = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='site_logo', verbose_name="شعار الموقع")
    contact_email = models.EmailField(default="info@ideateeam.com", verbose_name="البريد الإلكتروني")
    contact_phone = models.CharField(max_length=20, default="773171477", verbose_name="رقم الهاتف")
    address = models.TextField(blank=True, verbose_name="العنوان")
    facebook_url = models.URLField(blank=True, verbose_name="رابط فيسبوك")
    twitter_url = models.URLField(blank=True, verbose_name="رابط تويتر")
    instagram_url = models.URLField(blank=True, verbose_name="رابط إنستغرام")
    linkedin_url = models.URLField(blank=True, verbose_name="رابط لينكد إن")
    google_analytics_id = models.CharField(max_length=50, blank=True, verbose_name="معرف Google Analytics")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "إعدادات الموقع"
        verbose_name_plural = "إعدادات الموقع"

    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        # التأكد من وجود سجل واحد فقط
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('يمكن إنشاء سجل واحد فقط من إعدادات الموقع')
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    """نموذج رسائل التواصل"""
    name = models.CharField(max_length=100, verbose_name="الاسم")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=20, blank=True, verbose_name="رقم الهاتف")
    subject = models.CharField(max_length=200, verbose_name="الموضوع")
    message = models.TextField(verbose_name="الرسالة")
    is_read = models.BooleanField(default=False, verbose_name="مقروءة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")

    class Meta:
        verbose_name = "رسالة تواصل"
        verbose_name_plural = "رسائل التواصل"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


# النماذج الجديدة للميزات المتقدمة

class DynamicForm(models.Model):
    """نموذج النماذج الديناميكية"""
    FORM_TYPES = [
        ('consultation', 'طلب استشارة'),
        ('marketing_solutions', 'الحلول التسويقية'),
        ('creative_solutions', 'الحلول الإبداعية'),
        ('technical_solutions', 'الحلول التقنية'),
        ('comprehensive_solutions', 'حلول آيديا الشاملة'),
        ('contact', 'تواصل معنا'),
        ('custom', 'نموذج مخصص'),
    ]

    name = models.CharField(max_length=200, verbose_name="اسم النموذج")
    form_type = models.CharField(max_length=50, choices=FORM_TYPES, verbose_name="نوع النموذج")
    description = models.TextField(blank=True, verbose_name="وصف النموذج")
    form_schema = models.JSONField(default=dict, verbose_name="هيكل النموذج")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="أنشئ بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "نموذج ديناميكي"
        verbose_name_plural = "النماذج الديناميكية"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_form_fields(self):
        """إرجاع حقول النموذج من JSON Schema"""
        return self.form_schema.get('fields', [])

    def get_form_settings(self):
        """إرجاع إعدادات النموذج من JSON Schema"""
        return self.form_schema.get('settings', {})


class FormSubmission(models.Model):
    """نموذج إرسالات النماذج"""
    STATUS_CHOICES = [
        ('new', 'جديد'),
        ('in_progress', 'قيد المعالجة'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]

    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, verbose_name="النموذج")
    submission_data = models.JSONField(verbose_name="بيانات الإرسال")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ المعالجة")
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   verbose_name="معالج بواسطة")

    class Meta:
        verbose_name = "إرسال نموذج"
        verbose_name_plural = "إرسالات النماذج"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.form.name} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"

    def get_field_value(self, field_name):
        """الحصول على قيمة حقل معين من بيانات الإرسال"""
        return self.submission_data.get(field_name, '')

    def mark_as_processed(self, user=None):
        """تحديد الإرسال كمعالج"""
        self.status = 'completed'
        self.processed_at = timezone.now()
        if user:
            self.processed_by = user
        self.save()


class VisitorTracking(models.Model):
    """نموذج تتبع الزوار"""
    session_key = models.CharField(max_length=40, verbose_name="مفتاح الجلسة")
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(verbose_name="User Agent")
    referrer = models.URLField(blank=True, verbose_name="المصدر")
    page_url = models.URLField(verbose_name="رابط الصفحة")
    page_title = models.CharField(max_length=200, blank=True, verbose_name="عنوان الصفحة")
    visit_duration = models.PositiveIntegerField(default=0, verbose_name="مدة الزيارة (ثانية)")
    is_bounce = models.BooleanField(default=True, verbose_name="زيارة ارتداد")
    device_type = models.CharField(max_length=20, blank=True, verbose_name="نوع الجهاز")
    browser = models.CharField(max_length=50, blank=True, verbose_name="المتصفح")
    operating_system = models.CharField(max_length=50, blank=True, verbose_name="نظام التشغيل")
    country = models.CharField(max_length=100, blank=True, verbose_name="البلد")
    city = models.CharField(max_length=100, blank=True, verbose_name="المدينة")
    visited_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الزيارة")

    class Meta:
        verbose_name = "تتبع زائر"
        verbose_name_plural = "تتبع الزوار"
        ordering = ['-visited_at']

    def __str__(self):
        return f"{self.ip_address} - {self.page_title} - {self.visited_at.strftime('%Y-%m-%d %H:%M')}"


class IntegrationSettings(models.Model):
    """نموذج إعدادات التكامل مع المنصات الخارجية"""
    PLATFORM_CHOICES = [
        ('meta_business', 'Meta Business'),
        ('twitter', 'X (Twitter)'),
        ('google_analytics', 'Google Analytics'),
        ('google_ads', 'Google Ads'),
        ('linkedin', 'LinkedIn'),
    ]

    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, unique=True, verbose_name="المنصة")
    api_key = models.CharField(max_length=500, blank=True, verbose_name="مفتاح API")
    api_secret = models.CharField(max_length=500, blank=True, verbose_name="سر API")
    access_token = models.TextField(blank=True, verbose_name="رمز الوصول")
    refresh_token = models.TextField(blank=True, verbose_name="رمز التحديث")
    additional_settings = models.JSONField(default=dict, verbose_name="إعدادات إضافية")
    is_active = models.BooleanField(default=False, verbose_name="نشط")
    last_sync = models.DateTimeField(null=True, blank=True, verbose_name="آخر مزامنة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "إعدادات التكامل"
        verbose_name_plural = "إعدادات التكامل"

    def __str__(self):
        return f"{self.get_platform_display()}"

    def is_configured(self):
        """التحقق من تكوين المنصة بشكل صحيح"""
        return bool(self.api_key and self.is_active)


class PlatformReport(models.Model):
    """نموذج تقارير المنصات الخارجية"""
    REPORT_TYPES = [
        ('analytics', 'تحليلات'),
        ('ads_performance', 'أداء الإعلانات'),
        ('social_insights', 'رؤى اجتماعية'),
        ('engagement', 'التفاعل'),
        ('reach', 'الوصول'),
    ]

    integration = models.ForeignKey(IntegrationSettings, on_delete=models.CASCADE, verbose_name="التكامل")
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES, verbose_name="نوع التقرير")
    report_data = models.JSONField(verbose_name="بيانات التقرير")
    date_from = models.DateField(verbose_name="من تاريخ")
    date_to = models.DateField(verbose_name="إلى تاريخ")
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "تقرير منصة"
        verbose_name_plural = "تقارير المنصات"
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.integration.get_platform_display()} - {self.get_report_type_display()} - {self.date_from}"


class AdCampaign(models.Model):
    """نموذج الحملات الإعلانية"""
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('active', 'نشطة'),
        ('paused', 'متوقفة'),
        ('completed', 'مكتملة'),
        ('cancelled', 'ملغية'),
    ]

    PLATFORM_CHOICES = [
        ('meta', 'Meta (Facebook/Instagram)'),
        ('google', 'Google Ads'),
        ('twitter', 'X (Twitter)'),
        ('linkedin', 'LinkedIn'),
    ]

    name = models.CharField(max_length=200, verbose_name="اسم الحملة")
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, verbose_name="المنصة")
    campaign_id = models.CharField(max_length=100, blank=True, verbose_name="معرف الحملة في المنصة")
    objective = models.CharField(max_length=100, verbose_name="هدف الحملة")
    budget = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الميزانية")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="الحالة")
    start_date = models.DateTimeField(verbose_name="تاريخ البداية")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ النهاية")
    target_audience = models.JSONField(default=dict, verbose_name="الجمهور المستهدف")
    campaign_settings = models.JSONField(default=dict, verbose_name="إعدادات الحملة")
    performance_data = models.JSONField(default=dict, verbose_name="بيانات الأداء")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="أنشئ بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "حملة إعلانية"
        verbose_name_plural = "الحملات الإعلانية"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_platform_display()}"

    def get_performance_metric(self, metric_name):
        """الحصول على مقياس أداء معين"""
        return self.performance_data.get(metric_name, 0)

    def update_performance_data(self, new_data):
        """تحديث بيانات الأداء"""
        self.performance_data.update(new_data)
        self.save()


class AnalyticsReport(models.Model):
    """نموذج تقارير التحليلات الشاملة"""
    REPORT_TYPES = [
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري'),
        ('quarterly', 'ربع سنوي'),
        ('yearly', 'سنوي'),
        ('custom', 'مخصص'),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان التقرير")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="نوع التقرير")
    date_from = models.DateField(verbose_name="من تاريخ")
    date_to = models.DateField(verbose_name="إلى تاريخ")
    website_analytics = models.JSONField(default=dict, verbose_name="تحليلات الموقع")
    form_submissions = models.JSONField(default=dict, verbose_name="إرسالات النماذج")
    visitor_insights = models.JSONField(default=dict, verbose_name="رؤى الزوار")
    platform_performance = models.JSONField(default=dict, verbose_name="أداء المنصات")
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="أنشئ بواسطة")
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "تقرير تحليلات"
        verbose_name_plural = "تقارير التحليلات"
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.title} - {self.date_from} إلى {self.date_to}"




class AdCampaign(models.Model):
    """نموذج الحملات الإعلانية الموحدة"""
    PLATFORM_CHOICES = [
        ("meta_business", "Meta Business"),
        ("twitter", "X (Twitter)"),
        ("google_ads", "Google Ads"),
    ]

    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, verbose_name="المنصة")
    external_id = models.CharField(max_length=255, unique=True, verbose_name="المعرف الخارجي للحملة")
    name = models.CharField(max_length=255, verbose_name="اسم الحملة")
    status = models.CharField(max_length=50, verbose_name="الحالة")
    objective = models.CharField(max_length=255, blank=True, verbose_name="الهدف")
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="الميزانية")
    start_date = models.DateField(null=True, blank=True, verbose_name="تاريخ البدء")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    account_id = models.CharField(max_length=255, blank=True, verbose_name="معرف الحساب الإعلاني")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="أنشئ بواسطة")
    created_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الإنشاء")
    data = models.JSONField(default=dict, verbose_name="البيانات الخام للحملة")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "حملة إعلانية"
        verbose_name_plural = "الحملات الإعلانية"
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.name} ({self.platform})"




# النماذج الجديدة للمصادقة وإدارة المهام

class CustomUser(models.Model):
    """نموذج المستخدم المخصص - إضافة معلومات للمستخدمين الحاليين"""
    USER_TYPES = (
        ('admin', 'مدير النظام'),
        ('client', 'عميل'),
        ('team_member', 'عضو فريق'),
        ('manager', 'مدير مشروع'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='client')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"

class Project(models.Model):
    """نموذج المشاريع"""
    STATUS_CHOICES = (
        ('planning', 'تخطيط'),
        ('in_progress', 'قيد التنفيذ'),
        ('review', 'مراجعة'),
        ('completed', 'مكتمل'),
        ('on_hold', 'متوقف'),
        ('cancelled', 'ملغي'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'منخفضة'),
        ('medium', 'متوسطة'),
        ('high', 'عالية'),
        ('urgent', 'عاجلة'),
    )
    
    title = models.CharField(max_length=200, verbose_name="عنوان المشروع")
    description = models.TextField(verbose_name="وصف المشروع")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_projects', verbose_name="العميل")
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_projects', verbose_name="مدير المشروع")
    team_members = models.ManyToManyField(User, related_name='team_projects', blank=True, verbose_name="أعضاء الفريق")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning', verbose_name="الحالة")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="الأولوية")
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(verbose_name="تاريخ النهاية")
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="الميزانية")
    progress = models.IntegerField(default=0, verbose_name="نسبة الإنجاز")  # من 0 إلى 100
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "مشروع"
        verbose_name_plural = "المشاريع"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Task(models.Model):
    """نموذج المهام"""
    STATUS_CHOICES = (
        ('todo', 'قائمة المهام'),
        ('in_progress', 'قيد التنفيذ'),
        ('review', 'مراجعة'),
        ('done', 'مكتملة'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'منخفضة'),
        ('medium', 'متوسطة'),
        ('high', 'عالية'),
        ('urgent', 'عاجلة'),
    )
    
    title = models.CharField(max_length=200, verbose_name="عنوان المهمة")
    description = models.TextField(blank=True, verbose_name="وصف المهمة")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name="المشروع")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks', verbose_name="مُعين إلى")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name="أنشئ بواسطة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo', verbose_name="الحالة")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="الأولوية")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاستحقاق")
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="الساعات المقدرة")
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="الساعات الفعلية")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "مهمة"
        verbose_name_plural = "المهام"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.project.title}"

class Notification(models.Model):
    """نموذج الإشعارات"""
    NOTIFICATION_TYPES = (
        ('task_assigned', 'تم تعيين مهمة'),
        ('task_completed', 'تم إكمال مهمة'),
        ('project_update', 'تحديث مشروع'),
        ('deadline_reminder', 'تذكير موعد نهائي'),
        ('system_alert', 'تنبيه النظام'),
        ('message_received', 'رسالة جديدة'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="المستلم")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_notifications', verbose_name="المرسل")
    title = models.CharField(max_length=200, verbose_name="العنوان")
    message = models.TextField(verbose_name="الرسالة")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name="نوع الإشعار")
    is_read = models.BooleanField(default=False, verbose_name="مقروء")
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, verbose_name="المشروع المرتبط")
    related_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, verbose_name="المهمة المرتبطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "إشعار"
        verbose_name_plural = "الإشعارات"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

class Message(models.Model):
    """نموذج الرسائل"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="المرسل")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name="المستلم")
    subject = models.CharField(max_length=200, verbose_name="الموضوع")
    content = models.TextField(verbose_name="المحتوى")
    is_read = models.BooleanField(default=False, verbose_name="مقروء")
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المشروع المرتبط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "رسالة"
        verbose_name_plural = "الرسائل"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - من {self.sender.username} إلى {self.recipient.username}"

class Analytics(models.Model):
    """نموذج التحليلات المتقدمة"""
    METRIC_TYPES = (
        ('page_view', 'مشاهدة صفحة'),
        ('user_login', 'تسجيل دخول'),
        ('project_created', 'إنشاء مشروع'),
        ('task_completed', 'إكمال مهمة'),
        ('form_submission', 'إرسال نموذج'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المستخدم")
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES, verbose_name="نوع المقياس")
    value = models.JSONField(default=dict, verbose_name="القيمة")  # بيانات إضافية مرنة
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "تحليل"
        verbose_name_plural = "التحليلات"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_metric_type_display()} - {self.created_at}"

class SystemSettings(models.Model):
    """نموذج إعدادات النظام المتقدمة"""
    key = models.CharField(max_length=100, unique=True, verbose_name="المفتاح")
    value = models.TextField(verbose_name="القيمة")
    description = models.TextField(blank=True, verbose_name="الوصف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "إعداد النظام"
        verbose_name_plural = "إعدادات النظام"

    def __str__(self):
        return self.key

