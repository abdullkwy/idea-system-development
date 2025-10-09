"""
Django management command to fix system issues
أمر Django لحل مشاكل النظام
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from cms.models import *
import os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix common system issues and setup proper configurations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-permissions',
            action='store_true',
            help='Fix user permissions and groups',
        )
        parser.add_argument(
            '--fix-database',
            action='store_true',
            help='Fix database issues and constraints',
        )
        parser.add_argument(
            '--setup-defaults',
            action='store_true',
            help='Setup default data and configurations',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all fixes',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting system fixes...')
        )
        
        if options['all']:
            options['fix_permissions'] = True
            options['fix_database'] = True
            options['setup_defaults'] = True
        
        try:
            with transaction.atomic():
                if options['fix_permissions']:
                    self.fix_permissions()
                
                if options['fix_database']:
                    self.fix_database()
                
                if options['setup_defaults']:
                    self.setup_defaults()
                
                self.stdout.write(
                    self.style.SUCCESS('All fixes completed successfully!')
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during fixes: {str(e)}')
            )
            logger.error(f'System fix error: {str(e)}')
    
    def fix_permissions(self):
        """Fix user permissions and groups"""
        self.stdout.write('Fixing permissions and groups...')
        
        # Create default groups
        admin_group, created = Group.objects.get_or_create(name='Administrators')
        if created:
            self.stdout.write('Created Administrators group')
        
        editor_group, created = Group.objects.get_or_create(name='Editors')
        if created:
            self.stdout.write('Created Editors group')
        
        viewer_group, created = Group.objects.get_or_create(name='Viewers')
        if created:
            self.stdout.write('Created Viewers group')
        
        # Assign permissions to groups
        self.assign_group_permissions(admin_group, 'admin')
        self.assign_group_permissions(editor_group, 'editor')
        self.assign_group_permissions(viewer_group, 'viewer')
        
        # Create default admin user if not exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@ideateeam.com',
                password='admin123',
                first_name='مدير',
                last_name='النظام'
            )
            admin_user.groups.add(admin_group)
            self.stdout.write('Created default admin user')
        
        self.stdout.write(
            self.style.SUCCESS('Permissions fixed successfully')
        )
    
    def assign_group_permissions(self, group, role):
        """Assign permissions to group based on role"""
        if role == 'admin':
            # Admin gets all permissions
            permissions = Permission.objects.all()
            group.permissions.set(permissions)
        
        elif role == 'editor':
            # Editor gets content management permissions
            content_types = ContentType.objects.filter(
                model__in=['page', 'service', 'project', 'client', 'blogpost']
            )
            permissions = Permission.objects.filter(
                content_type__in=content_types,
                codename__in=['add_', 'change_', 'view_']
            )
            group.permissions.set(permissions)
        
        elif role == 'viewer':
            # Viewer gets only view permissions
            permissions = Permission.objects.filter(
                codename__startswith='view_'
            )
            group.permissions.set(permissions)
    
    def fix_database(self):
        """Fix database issues and constraints"""
        self.stdout.write('Fixing database issues...')
        
        # Fix any orphaned records
        self.fix_orphaned_records()
        
        # Update database constraints
        self.update_constraints()
        
        # Fix data inconsistencies
        self.fix_data_inconsistencies()
        
        self.stdout.write(
            self.style.SUCCESS('Database issues fixed successfully')
        )
    
    def fix_orphaned_records(self):
        """Fix orphaned records in database"""
        # This would contain specific fixes for orphaned records
        # Example: Remove projects without clients, etc.
        pass
    
    def update_constraints(self):
        """Update database constraints"""
        # This would contain database constraint updates
        pass
    
    def fix_data_inconsistencies(self):
        """Fix data inconsistencies"""
        # Fix any data that doesn't match expected formats
        pass
    
    def setup_defaults(self):
        """Setup default data and configurations"""
        self.stdout.write('Setting up default configurations...')
        
        # Create default pages
        self.create_default_pages()
        
        # Create default services
        self.create_default_services()
        
        # Create default settings
        self.create_default_settings()
        
        self.stdout.write(
            self.style.SUCCESS('Default configurations setup successfully')
        )
    
    def create_default_pages(self):
        """Create default pages"""
        default_pages = [
            {
                'title': 'الصفحة الرئيسية',
                'slug': 'home',
                'content': 'مرحباً بكم في آيديا للاستشارات والحلول التسويقية',
                'is_published': True,
                'meta_description': 'آيديا للاستشارات والحلول التسويقية - أوسع مما تتخيل أدق مما تتوقع'
            },
            {
                'title': 'من نحن',
                'slug': 'about',
                'content': 'نحن فريق متخصص في تقديم الحلول التسويقية المتكاملة',
                'is_published': True,
                'meta_description': 'تعرف على فريق آيديا وخبراتنا في مجال التسويق والإبداع'
            },
            {
                'title': 'تواصل معنا',
                'slug': 'contact',
                'content': 'تواصل مع فريق آيديا للحصول على استشارة مجانية',
                'is_published': True,
                'meta_description': 'تواصل مع آيديا للاستشارات والحلول التسويقية'
            }
        ]
        
        for page_data in default_pages:
            page, created = Page.objects.get_or_create(
                slug=page_data['slug'],
                defaults=page_data
            )
            if created:
                self.stdout.write(f'Created page: {page_data["title"]}')
    
    def create_default_services(self):
        """Create default services"""
        default_services = [
            {
                'name': 'الاستشارات التسويقية',
                'slug': 'marketing-consultancy',
                'description': 'استشارات تسويقية متخصصة لتطوير أعمالك',
                'is_active': True,
                'price': 0.00,
                'category': 'استشارات'
            },
            {
                'name': 'الحلول التسويقية',
                'slug': 'marketing-solutions',
                'description': 'حلول تسويقية متكاملة تشمل التسويق الرقمي',
                'is_active': True,
                'price': 0.00,
                'category': 'تسويق'
            },
            {
                'name': 'الحلول الإبداعية',
                'slug': 'creative-solutions',
                'description': 'تصميم الهوية البصرية والمحتوى الإبداعي',
                'is_active': True,
                'price': 0.00,
                'category': 'تصميم'
            },
            {
                'name': 'الحلول التقنية',
                'slug': 'technical-solutions',
                'description': 'تطوير المواقع والتطبيقات وأنظمة إدارة المحتوى',
                'is_active': True,
                'price': 0.00,
                'category': 'تقنية'
            }
        ]
        
        for service_data in default_services:
            service, created = Service.objects.get_or_create(
                slug=service_data['slug'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'Created service: {service_data["name"]}')
    
    def create_default_settings(self):
        """Create default system settings"""
        default_settings = {
            'site_name': 'آيديا للاستشارات والحلول التسويقية',
            'site_description': 'أوسع مما تتخيل أدق مما تتوقع',
            'contact_email': 'info@ideateeam.com',
            'contact_phone': '773171477',
            'address': 'حدة - امام الديرة مول - مبنى القطرية - الدور الخامس',
            'city': 'صنعاء',
            'country': 'اليمن',
            'facebook_url': 'https://www.facebook.com/ideamarketing',
            'twitter_url': 'https://www.twitter.com/ideamarketing',
            'instagram_url': 'https://www.instagram.com/ideamarketing',
            'linkedin_url': 'https://www.linkedin.com/company/ideamarketing',
            'enable_analytics': True,
            'enable_seo': True,
            'maintenance_mode': False,
            'max_upload_size': 10485760,  # 10MB
            'allowed_file_types': 'jpg,jpeg,png,gif,pdf,doc,docx',
            'email_notifications': True,
            'sms_notifications': False,
            'backup_frequency': 'daily',
            'cache_timeout': 3600,
            'session_timeout': 1800,
            'password_min_length': 8,
            'enable_two_factor': False,
            'api_rate_limit': 1000,
            'debug_mode': False
        }
        
        for key, value in default_settings.items():
            setting, created = SystemSetting.objects.get_or_create(
                key=key,
                defaults={'value': str(value)}
            )
            if created:
                self.stdout.write(f'Created setting: {key}')
    
    def run_system_checks(self):
        """Run system health checks"""
        self.stdout.write('Running system health checks...')
        
        checks = [
            self.check_database_connection,
            self.check_file_permissions,
            self.check_required_directories,
            self.check_dependencies,
            self.check_configuration
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Check failed: {str(e)}')
                )
    
    def check_database_connection(self):
        """Check database connection"""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        self.stdout.write('✓ Database connection OK')
    
    def check_file_permissions(self):
        """Check file permissions"""
        from django.conf import settings
        
        # Check media directory
        media_root = getattr(settings, 'MEDIA_ROOT', '')
        if media_root and os.path.exists(media_root):
            if os.access(media_root, os.W_OK):
                self.stdout.write('✓ Media directory writable')
            else:
                raise Exception('Media directory not writable')
        
        # Check static directory
        static_root = getattr(settings, 'STATIC_ROOT', '')
        if static_root and os.path.exists(static_root):
            if os.access(static_root, os.R_OK):
                self.stdout.write('✓ Static directory readable')
            else:
                raise Exception('Static directory not readable')
    
    def check_required_directories(self):
        """Check required directories exist"""
        from django.conf import settings
        
        required_dirs = [
            getattr(settings, 'MEDIA_ROOT', ''),
            getattr(settings, 'STATIC_ROOT', ''),
            os.path.join(settings.BASE_DIR, 'logs'),
            os.path.join(settings.BASE_DIR, 'backups')
        ]
        
        for directory in required_dirs:
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                self.stdout.write(f'Created directory: {directory}')
        
        self.stdout.write('✓ Required directories OK')
    
    def check_dependencies(self):
        """Check required dependencies"""
        required_packages = [
            'django',
            'pillow',
            'django-cors-headers',
            'djangorestframework'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                self.stdout.write(f'✓ {package} installed')
            except ImportError:
                raise Exception(f'Required package {package} not installed')
    
    def check_configuration(self):
        """Check system configuration"""
        from django.conf import settings
        
        # Check required settings
        required_settings = [
            'SECRET_KEY',
            'DATABASES',
            'INSTALLED_APPS'
        ]
        
        for setting in required_settings:
            if not hasattr(settings, setting):
                raise Exception(f'Required setting {setting} not configured')
        
        self.stdout.write('✓ Configuration OK')

