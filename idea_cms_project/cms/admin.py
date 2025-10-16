from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import HttpResponseRedirect
import json
from .models import (
    Category, Tag, Media, Page, BlogPost, SiteSettings, ContactMessage,
    DynamicForm, FormSubmission, VisitorTracking, IntegrationSettings,
    PlatformReport, AdCampaign, AnalyticsReport
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['title', 'media_type', 'file_size_display', 'uploaded_by', 'uploaded_at']
    list_filter = ['media_type', 'uploaded_at', 'uploaded_by']
    search_fields = ['title', 'description']
    readonly_fields = ['file_size', 'uploaded_at']
    ordering = ['-uploaded_at']

    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "غير محدد"
    file_size_display.short_description = "حجم الملف"

    def save_model(self, request, obj, form, change):
        if not change:  # إذا كان إنشاء جديد
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'show_in_menu', 'order', 'author', 'created_at', 'published_at']
    list_filter = ['status', 'show_in_menu', 'created_at', 'published_at', 'author']
    search_fields = ['title', 'content', 'meta_title']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order', 'title']
    
    fieldsets = (
        ('المحتوى الأساسي', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        ('إعدادات النشر', {
            'fields': ('status', 'show_in_menu', 'order', 'published_at')
        }),
        ('تحسين محركات البحث', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('معلومات إضافية', {
            'fields': ('author', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # إذا كان إنشاء جديد
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'is_featured', 'views_count', 'author', 'created_at', 'published_at']
    list_filter = ['status', 'is_featured', 'category', 'tags', 'created_at', 'published_at', 'author']
    search_fields = ['title', 'content', 'meta_title']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'views_count']
    ordering = ['-published_at', '-created_at']
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('المحتوى الأساسي', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        ('التصنيف والوسوم', {
            'fields': ('category', 'tags')
        }),
        ('إعدادات النشر', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('تحسين محركات البحث', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('إحصائيات ومعلومات', {
            'fields': ('views_count', 'author', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # إذا كان إنشاء جديد
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('معلومات الموقع الأساسية', {
            'fields': ('site_title', 'site_description', 'site_logo')
        }),
        ('معلومات التواصل', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('وسائل التواصل الاجتماعي', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url')
        }),
        ('إعدادات التتبع', {
            'fields': ('google_analytics_id',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['updated_at']

    def has_add_permission(self, request):
        # منع إنشاء أكثر من سجل واحد
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # منع حذف إعدادات الموقع
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        # منع إضافة رسائل من لوحة الإدارة
        return False

    def has_delete_permission(self, request, obj=None):
        # السماح بحذف الرسائل
        return True

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"تم تحديد {queryset.count()} رسالة كمقروءة.")
    mark_as_read.short_description = "تحديد كمقروءة"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"تم تحديد {queryset.count()} رسالة كغير مقروءة.")
    mark_as_unread.short_description = "تحديد كغير مقروءة"


# النماذج الجديدة للميزات المتقدمة

@admin.register(DynamicForm)
class DynamicFormAdmin(admin.ModelAdmin):
    list_display = ['name', 'form_type', 'is_active', 'created_by', 'created_at']
    list_filter = ['form_type', 'is_active', 'created_at', 'created_by']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('معلومات النموذج', {
            'fields': ('name', 'form_type', 'description', 'is_active')
        }),
        ('هيكل النموذج (JSON)', {
            'fields': ('form_schema',),
            'description': 'يجب أن يكون الهيكل بصيغة JSON صحيحة'
        }),
        ('معلومات إضافية', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # إذا كان إنشاء جديد
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['form', 'status', 'submitted_at', 'processed_by', 'get_submitter_info']
    list_filter = ['status', 'form', 'submitted_at', 'processed_by']
    search_fields = ['submission_data', 'notes']
    readonly_fields = ['form', 'submission_data', 'ip_address', 'user_agent', 'submitted_at']
    ordering = ['-submitted_at']

    fieldsets = (
        ('معلومات الإرسال', {
            'fields': ('form', 'status', 'submitted_at', 'ip_address')
        }),
        ('بيانات الإرسال', {
            'fields': ('submission_data_display',),
            'classes': ('wide',)
        }),
        ('المعالجة', {
            'fields': ('notes', 'processed_by', 'processed_at')
        }),
        ('معلومات تقنية', {
            'fields': ('user_agent',),
            'classes': ('collapse',)
        }),
    )

    def get_submitter_info(self, obj):
        data = obj.submission_data
        name = data.get('name', data.get('full_name', 'غير محدد'))
        email = data.get('email', 'غير محدد')
        return f"{name} ({email})"
    get_submitter_info.short_description = "معلومات المرسل"

    def submission_data_display(self, obj):
        """عرض بيانات الإرسال بشكل منسق"""
        if obj.submission_data:
            formatted_data = ""
            for key, value in obj.submission_data.items():
                formatted_data += f"<strong>{key}:</strong> {value}<br>"
            return mark_safe(formatted_data)
        return "لا توجد بيانات"
    submission_data_display.short_description = "بيانات الإرسال"

    def has_add_permission(self, request):
        # منع إضافة إرسالات من لوحة الإدارة
        return False

    actions = ['mark_as_processed', 'mark_as_in_progress']

    def mark_as_processed(self, request, queryset):
        queryset.update(status='completed', processed_by=request.user)
        self.message_user(request, f"تم تحديد {queryset.count()} إرسال كمعالج.")
    mark_as_processed.short_description = "تحديد كمعالج"

    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress', processed_by=request.user)
        self.message_user(request, f"تم تحديد {queryset.count()} إرسال كقيد المعالجة.")
    mark_as_in_progress.short_description = "تحديد كقيد المعالجة"


@admin.register(VisitorTracking)
class VisitorTrackingAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'page_title', 'device_type', 'browser', 'country', 'visit_duration', 'visited_at']
    list_filter = ['device_type', 'browser', 'operating_system', 'country', 'is_bounce', 'visited_at']
    search_fields = ['ip_address', 'page_title', 'page_url', 'referrer']
    readonly_fields = ['session_key', 'ip_address', 'user_agent', 'referrer', 'page_url', 
                      'page_title', 'visit_duration', 'is_bounce', 'device_type', 
                      'browser', 'operating_system', 'country', 'city', 'visited_at']
    ordering = ['-visited_at']

    def has_add_permission(self, request):
        # منع إضافة تتبع من لوحة الإدارة
        return False

    def has_change_permission(self, request, obj=None):
        # منع تعديل بيانات التتبع
        return False


@admin.register(IntegrationSettings)
class IntegrationSettingsAdmin(admin.ModelAdmin):
    list_display = ['platform', 'is_active', 'is_configured_display', 'last_sync', 'updated_at']
    list_filter = ['platform', 'is_active', 'last_sync']
    readonly_fields = ['last_sync', 'created_at', 'updated_at']
    ordering = ['platform']

    fieldsets = (
        ('إعدادات المنصة', {
            'fields': ('platform', 'is_active')
        }),
        ('مفاتيح API', {
            'fields': ('api_key', 'api_secret', 'access_token', 'refresh_token'),
            'description': 'احرص على عدم مشاركة هذه المفاتيح مع أي شخص'
        }),
        ('إعدادات إضافية', {
            'fields': ('additional_settings',),
            'classes': ('collapse',)
        }),
        ('معلومات المزامنة', {
            'fields': ('last_sync', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_configured_display(self, obj):
        if obj.is_configured():
            return format_html('<span style="color: green;">✓ مكون</span>')
        else:
            return format_html('<span style="color: red;">✗ غير مكون</span>')
    is_configured_display.short_description = "حالة التكوين"


@admin.register(PlatformReport)
class PlatformReportAdmin(admin.ModelAdmin):
    list_display = ['integration', 'report_type', 'date_from', 'date_to', 'generated_at']
    list_filter = ['integration__platform', 'report_type', 'date_from', 'generated_at']
    search_fields = ['integration__platform']
    readonly_fields = ['generated_at']
    ordering = ['-generated_at']

    def has_add_permission(self, request):
        # منع إضافة تقارير من لوحة الإدارة (يتم إنشاؤها تلقائياً)
        return False


@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'status', 'account_id', 'created_date', 'created_by']
    list_filter = ['platform', 'status', 'created_date', 'created_by']
    search_fields = ['name', 'objective', 'external_id']
    readonly_fields = ['created_date', 'updated_at']
    ordering = ['-created_date']

    fieldsets = (
        ('معلومات الحملة', {
            'fields': ('name', 'platform', 'external_id', 'objective', 'status', 'account_id')
        }),
        ('التواريخ والبيانات', {
            'fields': ('created_date', 'data')
        }),
        ('معلومات إضافية', {
            'fields': ('created_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

