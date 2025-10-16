#!/usr/bin/env python3
"""
سكريبت لإضافة بيانات تجريبية لنظام إدارة المحتوى
"""

import os
import sys
import django
from django.utils import timezone
from django.utils.text import slugify

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idea_cms.settings')
django.setup()

from django.contrib.auth.models import User
from cms.models import Category, Tag, Page, BlogPost, SiteSettings


def create_sample_data():
    """إنشاء بيانات تجريبية"""
    
    print("إنشاء بيانات تجريبية...")
    
    # الحصول على المستخدم الإداري
    admin_user = User.objects.get(username='admin')
    
    # إنشاء التصنيفات
    categories_data = [
        {'name': 'التسويق الرقمي', 'description': 'مقالات حول التسويق الرقمي والإلكتروني'},
        {'name': 'التصميم الإبداعي', 'description': 'مقالات حول التصميم والإبداع'},
        {'name': 'التطوير التقني', 'description': 'مقالات حول التطوير والتقنية'},
        {'name': 'الاستشارات التسويقية', 'description': 'مقالات حول الاستشارات والاستراتيجيات'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'slug': slugify(cat_data['name']),
                'description': cat_data['description']
            }
        )
        categories.append(category)
        if created:
            print(f"تم إنشاء التصنيف: {category.name}")
    
    # إنشاء الوسوم
    tags_data = [
        'SEO', 'وسائل التواصل الاجتماعي', 'التسويق بالمحتوى', 'التصميم الجرافيكي',
        'تطوير المواقع', 'التجارة الإلكترونية', 'الذكاء الاصطناعي', 'التحليلات'
    ]
    
    tags = []
    for tag_name in tags_data:
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'slug': slugify(tag_name)}
        )
        tags.append(tag)
        if created:
            print(f"تم إنشاء الوسم: {tag.name}")
    
    # إنشاء الصفحات
    pages_data = [
        {
            'title': 'من نحن',
            'content': '''
            <h2>مرحباً بكم في آيديا للاستشارات والحلول التسويقية</h2>
            <p>نحن فريق من الخبراء المتخصصين في مجال التسويق والإبداع، نقدم حلولاً متكاملة لتطوير أعمالكم ونموها.</p>
            
            <h3>رؤيتنا</h3>
            <p>أن نكون الشريك الأول والموثوق في تقديم الحلول التسويقية والإبداعية المبتكرة.</p>
            
            <h3>مهمتنا</h3>
            <p>نساعد الشركات والمؤسسات على تحقيق أهدافها التسويقية من خلال استراتيجيات مدروسة وحلول إبداعية.</p>
            
            <h3>المدير العام: عبدالقوي سامي</h3>
            <p>يقود فريقنا المدير العام عبدالقوي سامي، الذي يتمتع بخبرة واسعة في مجال التسويق والإدارة.</p>
            ''',
            'excerpt': 'تعرف على آيديا للاستشارات والحلول التسويقية وفريق العمل المتخصص',
            'show_in_menu': True,
            'order': 1
        },
        {
            'title': 'حلولنا التسويقية',
            'content': '''
            <h2>حلول تسويقية متكاملة</h2>
            <p>نقدم مجموعة شاملة من الحلول التسويقية المصممة خصيصاً لتلبية احتياجاتكم.</p>
            
            <h3>التسويق الرقمي</h3>
            <ul>
                <li>إدارة وسائل التواصل الاجتماعي</li>
                <li>تحسين محركات البحث (SEO)</li>
                <li>الحملات الإعلانية المدفوعة</li>
                <li>التسويق بالمحتوى</li>
            </ul>
            
            <h3>الحلول الإبداعية</h3>
            <ul>
                <li>تصميم الهوية البصرية</li>
                <li>التصميم الجرافيكي</li>
                <li>إنتاج الفيديو</li>
                <li>التصوير الفوتوغرافي</li>
            </ul>
            ''',
            'excerpt': 'اكتشف مجموعة حلولنا التسويقية والإبداعية المتكاملة',
            'show_in_menu': True,
            'order': 2
        },
        {
            'title': 'تواصل معنا',
            'content': '''
            <h2>تواصل معنا</h2>
            <p>نحن هنا لمساعدتكم في تحقيق أهدافكم التسويقية. تواصلوا معنا اليوم!</p>
            
            <h3>معلومات التواصل</h3>
            <ul>
                <li><strong>الهاتف:</strong> 773171477</li>
                <li><strong>البريد الإلكتروني:</strong> info@ideateeam.com</li>
            </ul>
            
            <h3>ساعات العمل</h3>
            <p>السبت - الخميس: 9:00 صباحاً - 6:00 مساءً</p>
            ''',
            'excerpt': 'تواصل مع فريق آيديا للحصول على استشارة مجانية',
            'show_in_menu': True,
            'order': 3
        }
    ]
    
    for page_data in pages_data:
        page, created = Page.objects.get_or_create(
            title=page_data['title'],
            defaults={
                'slug': slugify(page_data['title']),
                'content': page_data['content'],
                'excerpt': page_data['excerpt'],
                'status': 'published',
                'show_in_menu': page_data['show_in_menu'],
                'order': page_data['order'],
                'author': admin_user,
                'published_at': timezone.now()
            }
        )
        if created:
            print(f"تم إنشاء الصفحة: {page.title}")
    
    # إنشاء مقالات المدونة
    blog_posts_data = [
        {
            'title': 'أهمية التسويق الرقمي في عصر التكنولوجيا',
            'content': '''
            <p>في عالم اليوم المتسارع، أصبح التسويق الرقمي ضرورة حتمية لأي عمل تجاري يسعى للنجاح والنمو.</p>
            
            <h3>ما هو التسويق الرقمي؟</h3>
            <p>التسويق الرقمي هو استخدام القنوات الرقمية للوصول إلى العملاء المحتملين وبناء علاقات قوية معهم.</p>
            
            <h3>فوائد التسويق الرقمي</h3>
            <ul>
                <li>وصول أوسع للجمهور المستهدف</li>
                <li>تكلفة أقل مقارنة بالتسويق التقليدي</li>
                <li>قياس النتائج بدقة</li>
                <li>التفاعل المباشر مع العملاء</li>
            </ul>
            ''',
            'excerpt': 'اكتشف أهمية التسويق الرقمي وكيف يمكن أن يساعد في نمو أعمالك',
            'category': categories[0],  # التسويق الرقمي
            'tags': [tags[0], tags[1], tags[2]],  # SEO, وسائل التواصل, التسويق بالمحتوى
            'is_featured': True
        },
        {
            'title': 'دليل شامل لتصميم الهوية البصرية',
            'content': '''
            <p>الهوية البصرية هي الوجه الذي يعكس شخصية علامتكم التجارية ويميزها عن المنافسين.</p>
            
            <h3>عناصر الهوية البصرية</h3>
            <ul>
                <li>الشعار (Logo)</li>
                <li>الألوان الأساسية</li>
                <li>الخطوط المستخدمة</li>
                <li>الأشكال والرموز</li>
            </ul>
            
            <h3>خطوات تصميم الهوية البصرية</h3>
            <ol>
                <li>دراسة السوق والمنافسين</li>
                <li>تحديد شخصية العلامة التجارية</li>
                <li>تصميم الشعار</li>
                <li>اختيار الألوان والخطوط</li>
                <li>إنشاء دليل الهوية البصرية</li>
            </ol>
            ''',
            'excerpt': 'تعلم كيفية تصميم هوية بصرية قوية ومميزة لعلامتك التجارية',
            'category': categories[1],  # التصميم الإبداعي
            'tags': [tags[3]],  # التصميم الجرافيكي
            'is_featured': False
        },
        {
            'title': 'مستقبل التجارة الإلكترونية في المنطقة العربية',
            'content': '''
            <p>تشهد التجارة الإلكترونية نمواً متسارعاً في المنطقة العربية، مما يفتح آفاقاً جديدة للأعمال.</p>
            
            <h3>إحصائيات مهمة</h3>
            <ul>
                <li>نمو التجارة الإلكترونية بنسبة 35% سنوياً</li>
                <li>زيادة عدد المتسوقين الرقميين</li>
                <li>تطور وسائل الدفع الإلكتروني</li>
            </ul>
            
            <h3>التحديات والفرص</h3>
            <p>رغم النمو السريع، تواجه التجارة الإلكترونية تحديات مثل الثقة الرقمية وأمان المعاملات.</p>
            ''',
            'excerpt': 'استكشف مستقبل التجارة الإلكترونية والفرص المتاحة في السوق العربي',
            'category': categories[2],  # التطوير التقني
            'tags': [tags[4], tags[5]],  # تطوير المواقع, التجارة الإلكترونية
            'is_featured': True
        }
    ]
    
    for post_data in blog_posts_data:
        post, created = BlogPost.objects.get_or_create(
            title=post_data['title'],
            defaults={
                'slug': slugify(post_data['title']),
                'content': post_data['content'],
                'excerpt': post_data['excerpt'],
                'category': post_data['category'],
                'status': 'published',
                'is_featured': post_data['is_featured'],
                'author': admin_user,
                'published_at': timezone.now()
            }
        )
        if created:
            # إضافة الوسوم
            post.tags.set(post_data['tags'])
            print(f"تم إنشاء المقال: {post.title}")
    
    # إنشاء إعدادات الموقع
    site_settings, created = SiteSettings.objects.get_or_create(
        id=1,
        defaults={
            'site_title': 'آيديا للاستشارات والحلول التسويقية',
            'site_description': 'خبراء التسويق والإبداع - نقدم حلولاً متكاملة لتطوير أعمالكم',
            'contact_email': 'info@ideateeam.com',
            'contact_phone': '773171477',
            'address': 'المملكة العربية السعودية',
        }
    )
    if created:
        print("تم إنشاء إعدادات الموقع")
    
    print("\nتم إنشاء جميع البيانات التجريبية بنجاح!")
    print("يمكنك الآن الدخول إلى لوحة الإدارة باستخدام:")
    print("اسم المستخدم: admin")
    print("كلمة المرور: admin123")


if __name__ == '__main__':
    create_sample_data()

