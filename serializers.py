from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Category, Tag, Media, Page, BlogPost, SiteSettings, ContactMessage,
    DynamicForm, FormSubmission, VisitorTracking, IntegrationSettings,
    PlatformReport, AdCampaign, AnalyticsReport
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer للمستخدمين"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer للتصنيفات"""
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at', 'posts_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_posts_count(self, obj):
        return obj.blogpost_set.filter(status='published').count()


class TagSerializer(serializers.ModelSerializer):
    """Serializer للوسوم"""
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at', 'posts_count']
        read_only_fields = ['id', 'created_at']
    
    def get_posts_count(self, obj):
        return obj.blogpost_set.filter(status='published').count()


class MediaSerializer(serializers.ModelSerializer):
    """Serializer للوسائط"""
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Media
        fields = ['id', 'title', 'file', 'file_url', 'media_type', 'alt_text', 
                 'description', 'file_size', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'file_size', 'uploaded_by', 'uploaded_at', 'media_type']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class PageSerializer(serializers.ModelSerializer):
    """Serializer للصفحات"""
    author = UserSerializer(read_only=True)
    featured_image = MediaSerializer(read_only=True)
    featured_image_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Page
        fields = ['id', 'title', 'slug', 'content', 'excerpt', 'featured_image', 
                 'featured_image_id', 'meta_title', 'meta_description', 'status', 
                 'order', 'show_in_menu', 'author', 'created_at', 'updated_at', 'published_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        featured_image_id = validated_data.pop('featured_image_id', None)
        page = Page.objects.create(**validated_data)
        if featured_image_id:
            try:
                featured_image = Media.objects.get(id=featured_image_id)
                page.featured_image = featured_image
                page.save()
            except Media.DoesNotExist:
                pass
        return page
    
    def update(self, instance, validated_data):
        featured_image_id = validated_data.pop('featured_image_id', None)
        if featured_image_id is not None:
            if featured_image_id:
                try:
                    featured_image = Media.objects.get(id=featured_image_id)
                    instance.featured_image = featured_image
                except Media.DoesNotExist:
                    pass
            else:
                instance.featured_image = None
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BlogPostSerializer(serializers.ModelSerializer):
    """Serializer لمقالات المدونة"""
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    featured_image = MediaSerializer(read_only=True)
    
    # حقول للكتابة
    category_id = serializers.IntegerField(write_only=True)
    tag_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    featured_image_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'excerpt', 'featured_image', 
                 'featured_image_id', 'category', 'category_id', 'tags', 'tag_ids',
                 'meta_title', 'meta_description', 'status', 'is_featured', 
                 'views_count', 'author', 'created_at', 'updated_at', 'published_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'views_count']
    
    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        tag_ids = validated_data.pop('tag_ids', [])
        featured_image_id = validated_data.pop('featured_image_id', None)
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise serializers.ValidationError({'category_id': 'التصنيف غير موجود'})
        
        post = BlogPost.objects.create(category=category, **validated_data)
        
        # إضافة الوسوم
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            post.tags.set(tags)
        
        # إضافة الصورة المميزة
        if featured_image_id:
            try:
                featured_image = Media.objects.get(id=featured_image_id)
                post.featured_image = featured_image
                post.save()
            except Media.DoesNotExist:
                pass
        
        return post
    
    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        tag_ids = validated_data.pop('tag_ids', None)
        featured_image_id = validated_data.pop('featured_image_id', None)
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                instance.category = category
            except Category.DoesNotExist:
                raise serializers.ValidationError({'category_id': 'التصنيف غير موجود'})
        
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            instance.tags.set(tags)
        
        if featured_image_id is not None:
            if featured_image_id:
                try:
                    featured_image = Media.objects.get(id=featured_image_id)
                    instance.featured_image = featured_image
                except Media.DoesNotExist:
                    pass
            else:
                instance.featured_image = None
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BlogPostListSerializer(serializers.ModelSerializer):
    """Serializer مبسط لقائمة المقالات"""
    author = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)
    featured_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'excerpt', 'featured_image_url', 
                 'category', 'tags', 'is_featured', 'views_count', 
                 'author', 'published_at']
    
    def get_featured_image_url(self, obj):
        if obj.featured_image and obj.featured_image.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.file.url)
            return obj.featured_image.file.url
        return None


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer لإعدادات الموقع"""
    site_logo = MediaSerializer(read_only=True)
    site_logo_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = SiteSettings
        fields = ['id', 'site_title', 'site_description', 'site_logo', 'site_logo_id',
                 'contact_email', 'contact_phone', 'address', 'facebook_url', 
                 'twitter_url', 'instagram_url', 'linkedin_url', 'google_analytics_id', 
                 'updated_at']
        read_only_fields = ['id', 'updated_at']
    
    def update(self, instance, validated_data):
        site_logo_id = validated_data.pop('site_logo_id', None)
        if site_logo_id is not None:
            if site_logo_id:
                try:
                    site_logo = Media.objects.get(id=site_logo_id)
                    instance.site_logo = site_logo
                except Media.DoesNotExist:
                    pass
            else:
                instance.site_logo = None
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer لرسائل التواصل"""
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message', 
                 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer لإنشاء رسائل التواصل (للموقع العام)"""
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
    
    def create(self, validated_data):
        return ContactMessage.objects.create(**validated_data)


# Serializers للميزات الجديدة

class DynamicFormSerializer(serializers.ModelSerializer):
    """Serializer للنماذج الديناميكية"""
    created_by = UserSerializer(read_only=True)
    submissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DynamicForm
        fields = ['id', 'name', 'form_type', 'description', 'form_schema', 
                 'is_active', 'created_by', 'created_at', 'updated_at', 'submissions_count']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_submissions_count(self, obj):
        return obj.formsubmission_set.count()
    
    def validate_form_schema(self, value):
        """التحقق من صحة هيكل النموذج"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("يجب أن يكون هيكل النموذج من نوع JSON object")
        
        if 'fields' not in value:
            raise serializers.ValidationError("يجب أن يحتوي هيكل النموذج على حقل 'fields'")
        
        if not isinstance(value['fields'], list):
            raise serializers.ValidationError("يجب أن يكون حقل 'fields' من نوع array")
        
        # التحقق من صحة كل حقل
        for field in value['fields']:
            if not isinstance(field, dict):
                raise serializers.ValidationError("كل حقل يجب أن يكون من نوع object")
            
            required_field_keys = ['name', 'type', 'label']
            for key in required_field_keys:
                if key not in field:
                    raise serializers.ValidationError(f"كل حقل يجب أن يحتوي على '{key}'")
        
        return value


class FormSubmissionSerializer(serializers.ModelSerializer):
    """Serializer لإرسالات النماذج"""
    form = DynamicFormSerializer(read_only=True)
    processed_by = UserSerializer(read_only=True)
    submitter_info = serializers.SerializerMethodField()
    
    class Meta:
        model = FormSubmission
        fields = ['id', 'form', 'submission_data', 'status', 'notes', 
                 'ip_address', 'user_agent', 'submitted_at', 'processed_at', 
                 'processed_by', 'submitter_info']
        read_only_fields = ['id', 'form', 'submission_data', 'ip_address', 
                           'user_agent', 'submitted_at', 'processed_by']
    
    def get_submitter_info(self, obj):
        """استخراج معلومات المرسل من بيانات الإرسال"""
        data = obj.submission_data
        return {
            'name': data.get('full_name', data.get('name', 'غير محدد')),
            'email': data.get('email', 'غير محدد'),
            'phone': data.get('phone', 'غير محدد'),
            'company': data.get('company', 'غير محدد')
        }


class FormSubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer لإنشاء إرسالات النماذج (للموقع العام)"""
    form_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FormSubmission
        fields = ['form_id', 'submission_data']
    
    def validate_form_id(self, value):
        """التحقق من وجود النموذج وأنه نشط"""
        try:
            form = DynamicForm.objects.get(id=value, is_active=True)
            return value
        except DynamicForm.DoesNotExist:
            raise serializers.ValidationError("النموذج غير موجود أو غير نشط")
    
    def validate_submission_data(self, value):
        """التحقق من صحة بيانات الإرسال"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("بيانات الإرسال يجب أن تكون من نوع JSON object")
        return value
    
    def create(self, validated_data):
        form_id = validated_data.pop('form_id')
        form = DynamicForm.objects.get(id=form_id)
        
        # الحصول على معلومات الطلب
        request = self.context.get('request')
        ip_address = None
        user_agent = ''
        
        if request:
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return FormSubmission.objects.create(
            form=form,
            ip_address=ip_address,
            user_agent=user_agent,
            **validated_data
        )


class VisitorTrackingSerializer(serializers.ModelSerializer):
    """Serializer لتتبع الزوار"""
    class Meta:
        model = VisitorTracking
        fields = ['id', 'session_key', 'ip_address', 'user_agent', 'referrer', 
                 'page_url', 'page_title', 'visit_duration', 'is_bounce', 
                 'device_type', 'browser', 'operating_system', 'country', 
                 'city', 'visited_at']
        read_only_fields = ['id', 'visited_at']


class VisitorTrackingCreateSerializer(serializers.ModelSerializer):
    """Serializer لإنشاء تتبع زائر جديد"""
    class Meta:
        model = VisitorTracking
        fields = ['page_url', 'page_title', 'referrer', 'visit_duration']
    
    def create(self, validated_data):
        request = self.context.get('request')
        
        # استخراج معلومات الطلب
        session_key = request.session.session_key if request and hasattr(request, 'session') else 'anonymous'
        ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1') if request else '127.0.0.1'
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        # تحليل User Agent لاستخراج معلومات الجهاز والمتصفح
        device_type = 'desktop'
        browser = 'unknown'
        operating_system = 'unknown'
        
        if user_agent:
            user_agent_lower = user_agent.lower()
            
            # تحديد نوع الجهاز
            if any(mobile in user_agent_lower for mobile in ['mobile', 'android', 'iphone', 'ipad']):
                device_type = 'mobile'
            elif 'tablet' in user_agent_lower:
                device_type = 'tablet'
            
            # تحديد المتصفح
            if 'chrome' in user_agent_lower:
                browser = 'Chrome'
            elif 'firefox' in user_agent_lower:
                browser = 'Firefox'
            elif 'safari' in user_agent_lower:
                browser = 'Safari'
            elif 'edge' in user_agent_lower:
                browser = 'Edge'
            
            # تحديد نظام التشغيل
            if 'windows' in user_agent_lower:
                operating_system = 'Windows'
            elif 'mac' in user_agent_lower:
                operating_system = 'macOS'
            elif 'linux' in user_agent_lower:
                operating_system = 'Linux'
            elif 'android' in user_agent_lower:
                operating_system = 'Android'
            elif 'ios' in user_agent_lower:
                operating_system = 'iOS'
        
        return VisitorTracking.objects.create(
            session_key=session_key,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type,
            browser=browser,
            operating_system=operating_system,
            country='Saudi Arabia',  # يمكن تحسينها باستخدام خدمة GeoIP
            city='Riyadh',
            **validated_data
        )


class IntegrationSettingsSerializer(serializers.ModelSerializer):
    """Serializer لإعدادات التكامل"""
    is_configured = serializers.SerializerMethodField()
    
    class Meta:
        model = IntegrationSettings
        fields = ['id', 'platform', 'is_active', 'is_configured', 'additional_settings', 
                 'last_sync', 'created_at', 'updated_at']
        read_only_fields = ['id', 'last_sync', 'created_at', 'updated_at']
    
    def get_is_configured(self, obj):
        return obj.is_configured()
    
    def to_representation(self, instance):
        """إخفاء المفاتيح الحساسة في الاستجابة"""
        data = super().to_representation(instance)
        # إخفاء المفاتيح الحساسة
        if 'additional_settings' in data and data['additional_settings']:
            sensitive_keys = ['api_key', 'api_secret', 'access_token', 'refresh_token']
            for key in sensitive_keys:
                if key in data['additional_settings']:
                    data['additional_settings'][key] = '***'
        return data


class IntegrationSettingsUpdateSerializer(serializers.ModelSerializer):
    """Serializer لتحديث إعدادات التكامل (مع المفاتيح الحساسة)"""
    class Meta:
        model = IntegrationSettings
        fields = ['platform', 'api_key', 'api_secret', 'access_token', 
                 'refresh_token', 'additional_settings', 'is_active']


class PlatformReportSerializer(serializers.ModelSerializer):
    """Serializer لتقارير المنصات"""
    integration = IntegrationSettingsSerializer(read_only=True)
    
    class Meta:
        model = PlatformReport
        fields = ['id', 'integration', 'report_type', 'report_data', 
                 'date_from', 'date_to', 'generated_at']
        read_only_fields = ['id', 'generated_at']


class AdCampaignSerializer(serializers.ModelSerializer):
    """Serializer للحملات الإعلانية"""
    created_by = UserSerializer(read_only=True)
    performance_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = AdCampaign
        fields = ['id', 'name', 'platform', 'campaign_id', 'objective', 
                 'budget', 'status', 'start_date', 'end_date', 'target_audience', 
                 'campaign_settings', 'performance_data', 'performance_summary',
                 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_performance_summary(self, obj):
        """ملخص أداء الحملة"""
        performance = obj.performance_data
        return {
            'impressions': performance.get('impressions', 0),
            'clicks': performance.get('clicks', 0),
            'conversions': performance.get('conversions', 0),
            'cost': performance.get('cost', 0),
            'ctr': performance.get('ctr', 0),  # Click Through Rate
            'cpc': performance.get('cpc', 0),  # Cost Per Click
            'roas': performance.get('roas', 0)  # Return on Ad Spend
        }


class AnalyticsReportSerializer(serializers.ModelSerializer):
    """Serializer لتقارير التحليلات"""
    generated_by = UserSerializer(read_only=True)
    summary = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsReport
        fields = ['id', 'title', 'report_type', 'date_from', 'date_to', 
                 'website_analytics', 'form_submissions', 'visitor_insights', 
                 'platform_performance', 'summary', 'generated_by', 'generated_at']
        read_only_fields = ['id', 'generated_by', 'generated_at']
    
    def get_summary(self, obj):
        """ملخص التقرير"""
        return {
            'total_visitors': obj.visitor_insights.get('total_visitors', 0),
            'total_page_views': obj.visitor_insights.get('total_page_views', 0),
            'total_form_submissions': obj.form_submissions.get('total_submissions', 0),
            'bounce_rate': obj.visitor_insights.get('bounce_rate', 0),
            'avg_session_duration': obj.visitor_insights.get('avg_session_duration', 0)
        }


# Serializers للإحصائيات والتحليلات

class AnalyticsStatsSerializer(serializers.Serializer):
    """Serializer لإحصائيات التحليلات"""
    total_visitors = serializers.IntegerField()
    total_page_views = serializers.IntegerField()
    total_form_submissions = serializers.IntegerField()
    bounce_rate = serializers.FloatField()
    avg_session_duration = serializers.FloatField()
    top_pages = serializers.ListField()
    top_referrers = serializers.ListField()
    device_breakdown = serializers.DictField()
    browser_breakdown = serializers.DictField()
    country_breakdown = serializers.DictField()


class FormSubmissionStatsSerializer(serializers.Serializer):
    """Serializer لإحصائيات إرسالات النماذج"""
    total_submissions = serializers.IntegerField()
    submissions_by_form = serializers.DictField()
    submissions_by_status = serializers.DictField()
    submissions_by_date = serializers.DictField()
    conversion_rate = serializers.FloatField()
    avg_processing_time = serializers.FloatField()



# Serializers جديدة للمصادقة وإدارة المهام

class LoginSerializer(serializers.Serializer):
    """مُسلسل تسجيل الدخول"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        from django.contrib.auth import authenticate
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('حساب المستخدم غير نشط.')
            else:
                raise serializers.ValidationError('بيانات تسجيل الدخول غير صحيحة.')
        else:
            raise serializers.ValidationError('يجب إدخال اسم المستخدم وكلمة المرور.')
        
        return data

class CustomUserProfileSerializer(serializers.ModelSerializer):
    """مُسلسل ملف المستخدم المخصص"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        from .models import CustomUser
        model = CustomUser
        fields = ['user', 'user_type', 'phone', 'avatar', 'company', 'position', 'is_verified', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ProjectSerializer(serializers.ModelSerializer):
    """مُسلسل المشاريع"""
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    team_members_names = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()
    completed_tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        from .models import Project
        model = Project
        fields = [
            'id', 'title', 'description', 'client', 'client_name', 'manager', 'manager_name',
            'team_members', 'team_members_names', 'status', 'priority', 'start_date', 'end_date',
            'budget', 'progress', 'tasks_count', 'completed_tasks_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_team_members_names(self, obj):
        return [member.get_full_name() or member.username for member in obj.team_members.all()]
    
    def get_tasks_count(self, obj):
        return obj.tasks.count()
    
    def get_completed_tasks_count(self, obj):
        return obj.tasks.filter(status='done').count()

class TaskSerializer(serializers.ModelSerializer):
    """مُسلسل المهام"""
    project_title = serializers.CharField(source='project.title', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        from .models import Task
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'project_title', 'assigned_to', 'assigned_to_name',
            'created_by', 'created_by_name', 'status', 'priority', 'due_date', 'estimated_hours',
            'actual_hours', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class NotificationSerializer(serializers.ModelSerializer):
    """مُسلسل الإشعارات"""
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    project_title = serializers.CharField(source='related_project.title', read_only=True)
    task_title = serializers.CharField(source='related_task.title', read_only=True)
    
    class Meta:
        from .models import Notification
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_name', 'title', 'message', 'notification_type',
            'is_read', 'related_project', 'project_title', 'related_task', 'task_title', 'created_at'
        ]
        read_only_fields = ['created_at']

class MessageSerializer(serializers.ModelSerializer):
    """مُسلسل الرسائل"""
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    project_title = serializers.CharField(source='related_project.title', read_only=True)
    
    class Meta:
        from .models import Message
        model = Message
        fields = [
            'id', 'sender', 'sender_name', 'recipient', 'recipient_name', 'subject', 'content',
            'is_read', 'related_project', 'project_title', 'created_at'
        ]
        read_only_fields = ['created_at']

class AnalyticsSerializer(serializers.ModelSerializer):
    """مُسلسل التحليلات"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        from .models import Analytics
        model = Analytics
        fields = ['id', 'user', 'user_name', 'metric_type', 'value', 'ip_address', 'user_agent', 'created_at']
        read_only_fields = ['created_at']

# مُسلسلات إضافية للإحصائيات والتقارير

class DashboardStatsSerializer(serializers.Serializer):
    """مُسلسل إحصائيات لوحة القيادة"""
    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_form_submissions = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()

class ProjectProgressSerializer(serializers.Serializer):
    """مُسلسل تقدم المشاريع"""
    project_id = serializers.IntegerField()
    project_title = serializers.CharField()
    progress = serializers.IntegerField()
    status = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    days_remaining = serializers.IntegerField()

class TaskSummarySerializer(serializers.Serializer):
    """مُسلسل ملخص المهام"""
    status = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()

class UserActivitySerializer(serializers.Serializer):
    """مُسلسل نشاط المستخدمين"""
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    last_login = serializers.DateTimeField()
    tasks_assigned = serializers.IntegerField()
    tasks_completed = serializers.IntegerField()
    projects_involved = serializers.IntegerField()

class SearchResultSerializer(serializers.Serializer):
    """مُسلسل نتائج البحث"""
    type = serializers.CharField()  # project, task, user, etc.
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    url = serializers.CharField()
    relevance_score = serializers.FloatField()

