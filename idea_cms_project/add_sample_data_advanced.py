#!/usr/bin/env python3
import os
import sys
import django
from datetime import datetime, timedelta
import json

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idea_cms.settings')
django.setup()

from django.contrib.auth.models import User
from cms.models import (
    DynamicForm, FormSubmission, VisitorTracking, IntegrationSettings,
    PlatformReport, AdCampaign, AnalyticsReport
)

def create_sample_dynamic_forms():
    """إنشاء نماذج ديناميكية تجريبية"""
    print("إنشاء النماذج الديناميكية...")
    
    # الحصول على المستخدم الإداري
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("لا يوجد مستخدم إداري. يرجى إنشاء مستخدم إداري أولاً.")
        return

    # نموذج طلب الاستشارة
    consultation_schema = {
        "fields": [
            {
                "name": "full_name",
                "type": "text",
                "label": "الاسم الكامل",
                "required": True,
                "placeholder": "أدخل اسمك الكامل"
            },
            {
                "name": "email",
                "type": "email",
                "label": "البريد الإلكتروني",
                "required": True,
                "placeholder": "example@domain.com"
            },
            {
                "name": "phone",
                "type": "tel",
                "label": "رقم الهاتف",
                "required": True,
                "placeholder": "+966xxxxxxxxx"
            },
            {
                "name": "company",
                "type": "text",
                "label": "اسم الشركة",
                "required": False,
                "placeholder": "اسم شركتك (اختياري)"
            },
            {
                "name": "consultation_type",
                "type": "select",
                "label": "نوع الاستشارة",
                "required": True,
                "options": [
                    {"value": "marketing", "label": "استشارة تسويقية"},
                    {"value": "branding", "label": "استشارة هوية تجارية"},
                    {"value": "digital", "label": "استشارة تسويق رقمي"},
                    {"value": "strategy", "label": "استشارة استراتيجية"}
                ]
            },
            {
                "name": "budget",
                "type": "select",
                "label": "الميزانية المتوقعة",
                "required": True,
                "options": [
                    {"value": "5000-10000", "label": "5,000 - 10,000 ريال"},
                    {"value": "10000-25000", "label": "10,000 - 25,000 ريال"},
                    {"value": "25000-50000", "label": "25,000 - 50,000 ريال"},
                    {"value": "50000+", "label": "أكثر من 50,000 ريال"}
                ]
            },
            {
                "name": "message",
                "type": "textarea",
                "label": "تفاصيل المشروع",
                "required": True,
                "placeholder": "اشرح لنا تفاصيل مشروعك واحتياجاتك"
            }
        ],
        "settings": {
            "submit_button_text": "طلب الاستشارة",
            "success_message": "تم إرسال طلبك بنجاح. سنتواصل معك قريباً.",
            "email_notifications": True,
            "redirect_url": ""
        }
    }

    consultation_form, created = DynamicForm.objects.get_or_create(
        name="نموذج طلب الاستشارة المجانية",
        form_type="consultation",
        defaults={
            "description": "نموذج لطلب استشارة مجانية من فريق آيديا",
            "form_schema": consultation_schema,
            "is_active": True,
            "created_by": admin_user
        }
    )
    if created:
        print("✓ تم إنشاء نموذج طلب الاستشارة")

    # نموذج الحلول التسويقية
    marketing_schema = {
        "fields": [
            {
                "name": "full_name",
                "type": "text",
                "label": "الاسم الكامل",
                "required": True
            },
            {
                "name": "email",
                "type": "email",
                "label": "البريد الإلكتروني",
                "required": True
            },
            {
                "name": "phone",
                "type": "tel",
                "label": "رقم الهاتف",
                "required": True
            },
            {
                "name": "company",
                "type": "text",
                "label": "اسم الشركة",
                "required": True
            },
            {
                "name": "industry",
                "type": "select",
                "label": "القطاع",
                "required": True,
                "options": [
                    {"value": "retail", "label": "التجارة والبيع بالتجزئة"},
                    {"value": "healthcare", "label": "الرعاية الصحية"},
                    {"value": "education", "label": "التعليم"},
                    {"value": "technology", "label": "التكنولوجيا"},
                    {"value": "food", "label": "الأغذية والمشروبات"},
                    {"value": "real_estate", "label": "العقارات"},
                    {"value": "other", "label": "أخرى"}
                ]
            },
            {
                "name": "services",
                "type": "checkbox",
                "label": "الخدمات المطلوبة",
                "required": True,
                "options": [
                    {"value": "social_media", "label": "إدارة وسائل التواصل الاجتماعي"},
                    {"value": "content_creation", "label": "إنتاج المحتوى"},
                    {"value": "paid_ads", "label": "الإعلانات المدفوعة"},
                    {"value": "seo", "label": "تحسين محركات البحث"},
                    {"value": "email_marketing", "label": "التسويق عبر البريد الإلكتروني"},
                    {"value": "influencer", "label": "التسويق عبر المؤثرين"}
                ]
            },
            {
                "name": "timeline",
                "type": "select",
                "label": "الإطار الزمني المطلوب",
                "required": True,
                "options": [
                    {"value": "asap", "label": "في أقرب وقت ممكن"},
                    {"value": "1_month", "label": "خلال شهر"},
                    {"value": "3_months", "label": "خلال 3 أشهر"},
                    {"value": "6_months", "label": "خلال 6 أشهر"}
                ]
            },
            {
                "name": "goals",
                "type": "textarea",
                "label": "أهداف التسويق",
                "required": True,
                "placeholder": "ما هي أهدافك من الحملة التسويقية؟"
            }
        ],
        "settings": {
            "submit_button_text": "طلب الحلول التسويقية",
            "success_message": "تم إرسال طلبك بنجاح. سيتواصل معك فريق المبيعات قريباً.",
            "email_notifications": True
        }
    }

    marketing_form, created = DynamicForm.objects.get_or_create(
        name="نموذج طلب الحلول التسويقية",
        form_type="marketing_solutions",
        defaults={
            "description": "نموذج لطلب الحلول التسويقية المتكاملة",
            "form_schema": marketing_schema,
            "is_active": True,
            "created_by": admin_user
        }
    )
    if created:
        print("✓ تم إنشاء نموذج الحلول التسويقية")

    # نموذج الحلول الشاملة
    comprehensive_schema = {
        "fields": [
            {
                "name": "full_name",
                "type": "text",
                "label": "الاسم الكامل",
                "required": True
            },
            {
                "name": "email",
                "type": "email",
                "label": "البريد الإلكتروني",
                "required": True
            },
            {
                "name": "phone",
                "type": "tel",
                "label": "رقم الهاتف",
                "required": True
            },
            {
                "name": "company",
                "type": "text",
                "label": "اسم الشركة",
                "required": True
            },
            {
                "name": "company_size",
                "type": "select",
                "label": "حجم الشركة",
                "required": True,
                "options": [
                    {"value": "startup", "label": "شركة ناشئة (1-10 موظفين)"},
                    {"value": "small", "label": "شركة صغيرة (11-50 موظف)"},
                    {"value": "medium", "label": "شركة متوسطة (51-200 موظف)"},
                    {"value": "large", "label": "شركة كبيرة (200+ موظف)"}
                ]
            },
            {
                "name": "current_challenges",
                "type": "checkbox",
                "label": "التحديات الحالية",
                "required": True,
                "options": [
                    {"value": "brand_awareness", "label": "ضعف الوعي بالعلامة التجارية"},
                    {"value": "lead_generation", "label": "صعوبة في توليد العملاء المحتملين"},
                    {"value": "customer_retention", "label": "صعوبة في الاحتفاظ بالعملاء"},
                    {"value": "digital_presence", "label": "ضعف الحضور الرقمي"},
                    {"value": "competition", "label": "المنافسة الشديدة"},
                    {"value": "roi", "label": "ضعف عائد الاستثمار التسويقي"}
                ]
            },
            {
                "name": "budget_range",
                "type": "select",
                "label": "الميزانية الشهرية",
                "required": True,
                "options": [
                    {"value": "10000-25000", "label": "10,000 - 25,000 ريال"},
                    {"value": "25000-50000", "label": "25,000 - 50,000 ريال"},
                    {"value": "50000-100000", "label": "50,000 - 100,000 ريال"},
                    {"value": "100000+", "label": "أكثر من 100,000 ريال"}
                ]
            },
            {
                "name": "project_description",
                "type": "textarea",
                "label": "وصف المشروع والأهداف",
                "required": True,
                "placeholder": "اشرح لنا مشروعك بالتفصيل وما تريد تحقيقه"
            },
            {
                "name": "preferred_contact_time",
                "type": "select",
                "label": "الوقت المفضل للتواصل",
                "required": False,
                "options": [
                    {"value": "morning", "label": "صباحاً (9-12)"},
                    {"value": "afternoon", "label": "بعد الظهر (12-5)"},
                    {"value": "evening", "label": "مساءً (5-8)"}
                ]
            }
        ],
        "settings": {
            "submit_button_text": "طلب حلول آيديا الشاملة",
            "success_message": "تم إرسال طلبك بنجاح. سيتواصل معك مدير الحساب المخصص خلال 24 ساعة.",
            "email_notifications": True,
            "priority": "high"
        }
    }

    comprehensive_form, created = DynamicForm.objects.get_or_create(
        name="نموذج طلب حلول آيديا الشاملة",
        form_type="comprehensive_solutions",
        defaults={
            "description": "نموذج لطلب الحلول الشاملة والمتكاملة من آيديا",
            "form_schema": comprehensive_schema,
            "is_active": True,
            "created_by": admin_user
        }
    )
    if created:
        print("✓ تم إنشاء نموذج الحلول الشاملة")


def create_sample_form_submissions():
    """إنشاء إرسالات نماذج تجريبية"""
    print("إنشاء إرسالات النماذج التجريبية...")
    
    forms = DynamicForm.objects.all()
    if not forms.exists():
        print("لا توجد نماذج ديناميكية. يرجى إنشاؤها أولاً.")
        return

    # إرسالات تجريبية لنموذج الاستشارة
    consultation_form = forms.filter(form_type='consultation').first()
    if consultation_form:
        sample_submissions = [
            {
                "full_name": "أحمد محمد السعيد",
                "email": "ahmed@example.com",
                "phone": "+966501234567",
                "company": "شركة النجاح للتجارة",
                "consultation_type": "marketing",
                "budget": "25000-50000",
                "message": "نحتاج إلى استشارة تسويقية لإطلاق منتج جديد في السوق السعودي"
            },
            {
                "full_name": "فاطمة علي الزهراني",
                "email": "fatima@startup.com",
                "phone": "+966509876543",
                "company": "ستارت أب تك",
                "consultation_type": "digital",
                "budget": "10000-25000",
                "message": "شركة ناشئة في مجال التكنولوجيا تحتاج استراتيجية تسويق رقمي"
            }
        ]

        for submission_data in sample_submissions:
            FormSubmission.objects.get_or_create(
                form=consultation_form,
                submission_data=submission_data,
                defaults={
                    "status": "new",
                    "ip_address": "192.168.1.100"
                }
            )
        print("✓ تم إنشاء إرسالات نموذج الاستشارة")


def create_sample_integration_settings():
    """إنشاء إعدادات التكامل التجريبية"""
    print("إنشاء إعدادات التكامل...")
    
    integrations = [
        {
            "platform": "meta_business",
            "additional_settings": {
                "app_id": "your_app_id",
                "app_secret": "your_app_secret",
                "ad_account_id": "act_xxxxxxxxx"
            }
        },
        {
            "platform": "twitter",
            "additional_settings": {
                "consumer_key": "your_consumer_key",
                "consumer_secret": "your_consumer_secret"
            }
        },
        {
            "platform": "google_analytics",
            "additional_settings": {
                "property_id": "GA4_PROPERTY_ID",
                "measurement_id": "G-XXXXXXXXXX"
            }
        }
    ]

    for integration_data in integrations:
        IntegrationSettings.objects.get_or_create(
            platform=integration_data["platform"],
            defaults={
                "additional_settings": integration_data["additional_settings"],
                "is_active": False  # يتم تفعيلها عند إدخال المفاتيح الصحيحة
            }
        )
    print("✓ تم إنشاء إعدادات التكامل")


def create_sample_visitor_tracking():
    """إنشاء بيانات تتبع زوار تجريبية"""
    print("إنشاء بيانات تتبع الزوار...")
    
    # بيانات تجريبية للزوار
    sample_visits = [
        {
            "session_key": "session_001",
            "ip_address": "192.168.1.10",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "page_url": "https://ideateeam.com/",
            "page_title": "الصفحة الرئيسية - آيديا",
            "visit_duration": 120,
            "device_type": "desktop",
            "browser": "Chrome",
            "operating_system": "Windows",
            "country": "Saudi Arabia",
            "city": "Riyadh"
        },
        {
            "session_key": "session_002",
            "ip_address": "192.168.1.20",
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
            "page_url": "https://ideateeam.com/services",
            "page_title": "خدماتنا - آيديا",
            "visit_duration": 85,
            "device_type": "mobile",
            "browser": "Safari",
            "operating_system": "iOS",
            "country": "Saudi Arabia",
            "city": "Jeddah"
        }
    ]

    for visit_data in sample_visits:
        VisitorTracking.objects.get_or_create(
            session_key=visit_data["session_key"],
            defaults=visit_data
        )
    print("✓ تم إنشاء بيانات تتبع الزوار")


def main():
    print("بدء إنشاء البيانات التجريبية للميزات المتقدمة...")
    print("=" * 50)
    
    try:
        create_sample_dynamic_forms()
        create_sample_form_submissions()
        create_sample_integration_settings()
        create_sample_visitor_tracking()
        
        print("=" * 50)
        print("✅ تم إنشاء جميع البيانات التجريبية بنجاح!")
        print("\nيمكنك الآن:")
        print("1. تسجيل الدخول إلى لوحة الإدارة")
        print("2. استعراض النماذج الديناميكية")
        print("3. مراجعة إرسالات النماذج")
        print("4. تكوين إعدادات التكامل")
        print("5. مراجعة بيانات تتبع الزوار")
        
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

