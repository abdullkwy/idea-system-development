from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from .models import (
    Category, Tag, Media, Page, BlogPost, SiteSettings, ContactMessage,
    DynamicForm, FormSubmission, VisitorTracking, IntegrationSettings,
    PlatformReport, AdCampaign, AnalyticsReport
)
from .serializers import (
    CategorySerializer, TagSerializer, MediaSerializer, PageSerializer,
    BlogPostSerializer, BlogPostListSerializer, SiteSettingsSerializer,
    ContactMessageSerializer, ContactMessageCreateSerializer,
    DynamicFormSerializer, FormSubmissionSerializer, FormSubmissionCreateSerializer,
    VisitorTrackingSerializer, VisitorTrackingCreateSerializer,
    IntegrationSettingsSerializer, IntegrationSettingsUpdateSerializer,
    PlatformReportSerializer, AdCampaignSerializer, AnalyticsReportSerializer,
    AnalyticsStatsSerializer, FormSubmissionStatsSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet للتصنيفات"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Category.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        return queryset.order_by('name')


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet للوسوم"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Tag.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by('name')


class MediaViewSet(viewsets.ModelViewSet):
    """ViewSet للوسائط"""
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Media.objects.all()
        media_type = self.request.query_params.get('type', None)
        search = self.request.query_params.get('search', None)
        
        if media_type:
            queryset = queryset.filter(media_type=media_type)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('-uploaded_at')
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class PageViewSet(viewsets.ModelViewSet):
    """ViewSet للصفحات"""
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Page.objects.all()
        
        # للمستخدمين غير المصادق عليهم، عرض الصفحات المنشورة فقط
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        return queryset.order_by('order', '-created_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BlogPostViewSet(viewsets.ModelViewSet):
    """ViewSet لمقالات المدونة"""
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BlogPostListSerializer
        return BlogPostSerializer
    
    def get_queryset(self):
        queryset = BlogPost.objects.all()
        
        # للمستخدمين غير المصادق عليهم، عرض المقالات المنشورة فقط
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        
        # فلترة حسب التصنيف
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # فلترة حسب الوسم
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        # فلترة المقالات المميزة
        featured = self.request.query_params.get('featured', None)
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # البحث
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) | 
                Q(excerpt__icontains=search)
            )
        
        return queryset.order_by('-published_at', '-created_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """زيادة عدد المشاهدات عند عرض المقال"""
        instance = self.get_object()
        if not request.user.is_authenticated or request.user != instance.author:
            instance.views_count += 1
            instance.save(update_fields=['views_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class SiteSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet لإعدادات الموقع"""
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        # إرجاع إعدادات واحدة فقط (أول إعداد)
        return SiteSettings.objects.all()[:1]
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public(self, request):
        """إعدادات الموقع العامة (للواجهة الأمامية)"""
        settings = SiteSettings.objects.first()
        if settings:
            data = {
                'site_title': settings.site_title,
                'site_description': settings.site_description,
                'site_logo': settings.site_logo.file.url if settings.site_logo else None,
                'contact_email': settings.contact_email,
                'contact_phone': settings.contact_phone,
                'address': settings.address,
                'social_links': {
                    'facebook': settings.facebook_url,
                    'twitter': settings.twitter_url,
                    'instagram': settings.instagram_url,
                    'linkedin': settings.linkedin_url
                }
            }
            return Response(data)
        return Response({})


class ContactMessageViewSet(viewsets.ModelViewSet):
    """ViewSet لرسائل التواصل"""
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ContactMessageCreateSerializer
        return ContactMessageSerializer
    
    def get_permissions(self):
        """السماح للجميع بإنشاء رسائل تواصل"""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = ContactMessage.objects.all()
        
        # فلترة حسب حالة القراءة
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # البحث
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(email__icontains=search) | 
                Q(subject__icontains=search) | 
                Q(message__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """تحديد الرسالة كمقروءة"""
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({'status': 'تم تحديد الرسالة كمقروءة'})
    
    @action(detail=True, methods=['post'])
    def mark_unread(self, request, pk=None):
        """تحديد الرسالة كغير مقروءة"""
        message = self.get_object()
        message.is_read = False
        message.save()
        return Response({'status': 'تم تحديد الرسالة كغير مقروءة'})


# ViewSets للميزات الجديدة

class DynamicFormViewSet(viewsets.ModelViewSet):
    """ViewSet للنماذج الديناميكية"""
    queryset = DynamicForm.objects.all()
    serializer_class = DynamicFormSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """السماح للجميع بعرض النماذج النشطة"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = DynamicForm.objects.all()
        
        # للمستخدمين غير المصادق عليهم، عرض النماذج النشطة فقط
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_active=True)
        
        # فلترة حسب نوع النموذج
        form_type = self.request.query_params.get('type', None)
        if form_type:
            queryset = queryset.filter(form_type=form_type)
        
        # البحث
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def schema(self, request, pk=None):
        """الحصول على هيكل النموذج فقط"""
        form = self.get_object()
        return Response({
            'id': form.id,
            'name': form.name,
            'form_type': form.form_type,
            'description': form.description,
            'form_schema': form.form_schema
        })
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """تفعيل/إلغاء تفعيل النموذج"""
        form = self.get_object()
        form.is_active = not form.is_active
        form.save()
        status_text = 'مفعل' if form.is_active else 'معطل'
        return Response({'status': f'النموذج الآن {status_text}'})


class FormSubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet لإرسالات النماذج"""
    queryset = FormSubmission.objects.all()
    serializer_class = FormSubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FormSubmissionCreateSerializer
        return FormSubmissionSerializer
    
    def get_permissions(self):
        """السماح للجميع بإنشاء إرسالات"""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = FormSubmission.objects.all()
        
        # فلترة حسب النموذج
        form_id = self.request.query_params.get('form', None)
        if form_id:
            queryset = queryset.filter(form_id=form_id)
        
        # فلترة حسب الحالة
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # فلترة حسب التاريخ
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if date_from:
            queryset = queryset.filter(submitted_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(submitted_at__lte=date_to)
        
        # البحث في بيانات الإرسال
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(submission_data__icontains=search) |
                Q(notes__icontains=search)
            )
        
        return queryset.order_by('-submitted_at')
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """تحديث حالة الإرسال"""
        submission = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if new_status in ['new', 'in_progress', 'completed', 'rejected']:
            submission.status = new_status
            if notes:
                submission.notes = notes
            if new_status != 'new':
                submission.processed_at = timezone.now()
                submission.processed_by = request.user
            submission.save()
            
            return Response({
                'status': 'تم تحديث الحالة بنجاح',
                'new_status': new_status
            })
        
        return Response(
            {'error': 'حالة غير صحيحة'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """إحصائيات إرسالات النماذج"""
        queryset = self.get_queryset()
        
        # إحصائيات عامة
        total_submissions = queryset.count()
        submissions_by_status = queryset.values('status').annotate(count=Count('id'))
        submissions_by_form = queryset.values('form__name').annotate(count=Count('id'))
        
        # إحصائيات حسب التاريخ (آخر 30 يوم)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_submissions = queryset.filter(submitted_at__gte=thirty_days_ago)
        submissions_by_date = {}
        
        for i in range(30):
            date = (timezone.now() - timedelta(days=i)).date()
            count = recent_submissions.filter(submitted_at__date=date).count()
            submissions_by_date[str(date)] = count
        
        # معدل التحويل (نسبة الإرسالات المكتملة)
        completed_submissions = queryset.filter(status='completed').count()
        conversion_rate = (completed_submissions / total_submissions * 100) if total_submissions > 0 else 0
        
        # متوسط وقت المعالجة
        processed_submissions = queryset.filter(processed_at__isnull=False)
        avg_processing_time = 0
        if processed_submissions.exists():
            total_time = sum([
                (sub.processed_at - sub.submitted_at).total_seconds() / 3600  # بالساعات
                for sub in processed_submissions
            ])
            avg_processing_time = total_time / processed_submissions.count()
        
        stats_data = {
            'total_submissions': total_submissions,
            'submissions_by_form': {item['form__name']: item['count'] for item in submissions_by_form},
            'submissions_by_status': {item['status']: item['count'] for item in submissions_by_status},
            'submissions_by_date': submissions_by_date,
            'conversion_rate': round(conversion_rate, 2),
            'avg_processing_time': round(avg_processing_time, 2)
        }
        
        serializer = FormSubmissionStatsSerializer(stats_data)
        return Response(serializer.data)


class VisitorTrackingViewSet(viewsets.ModelViewSet):
    """ViewSet لتتبع الزوار"""
    queryset = VisitorTracking.objects.all()
    serializer_class = VisitorTrackingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VisitorTrackingCreateSerializer
        return VisitorTrackingSerializer
    
    def get_permissions(self):
        """السماح للجميع بإنشاء تتبع زوار"""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = VisitorTracking.objects.all()
        
        # فلترة حسب التاريخ
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if date_from:
            queryset = queryset.filter(visited_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(visited_at__lte=date_to)
        
        # فلترة حسب نوع الجهاز
        device_type = self.request.query_params.get('device_type', None)
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        
        # فلترة حسب المتصفح
        browser = self.request.query_params.get('browser', None)
        if browser:
            queryset = queryset.filter(browser=browser)
        
        return queryset.order_by('-visited_at')
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """تحليلات الزوار"""
        queryset = self.get_queryset()
        
        # إحصائيات عامة
        total_visitors = queryset.values('session_key').distinct().count()
        total_page_views = queryset.count()
        bounce_visits = queryset.filter(is_bounce=True).count()
        bounce_rate = (bounce_visits / total_page_views * 100) if total_page_views > 0 else 0
        
        # متوسط مدة الجلسة
        avg_session_duration = queryset.aggregate(
            avg_duration=Avg('visit_duration')
        )['avg_duration'] or 0
        
        # أهم الصفحات
        top_pages = list(queryset.values('page_url', 'page_title')
                        .annotate(views=Count('id'))
                        .order_by('-views')[:10])
        
        # أهم المصادر
        top_referrers = list(queryset.exclude(referrer__isnull=True)
                           .exclude(referrer='')
                           .values('referrer')
                           .annotate(visits=Count('id'))
                           .order_by('-visits')[:10])
        
        # توزيع الأجهزة
        device_breakdown = dict(queryset.values('device_type')
                              .annotate(count=Count('id'))
                              .values_list('device_type', 'count'))
        
        # توزيع المتصفحات
        browser_breakdown = dict(queryset.values('browser')
                               .annotate(count=Count('id'))
                               .values_list('browser', 'count'))
        
        # توزيع البلدان
        country_breakdown = dict(queryset.values('country')
                               .annotate(count=Count('id'))
                               .values_list('country', 'count'))
        
        analytics_data = {
            'total_visitors': total_visitors,
            'total_page_views': total_page_views,
            'total_form_submissions': FormSubmission.objects.count(),
            'bounce_rate': round(bounce_rate, 2),
            'avg_session_duration': round(avg_session_duration, 2),
            'top_pages': top_pages,
            'top_referrers': top_referrers,
            'device_breakdown': device_breakdown,
            'browser_breakdown': browser_breakdown,
            'country_breakdown': country_breakdown
        }
        
        serializer = AnalyticsStatsSerializer(analytics_data)
        return Response(serializer.data)


class IntegrationSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet لإعدادات التكامل"""
    queryset = IntegrationSettings.objects.all()
    serializer_class = IntegrationSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return IntegrationSettingsUpdateSerializer
        return IntegrationSettingsSerializer
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """اختبار الاتصال مع المنصة"""
        integration = self.get_object()
        
        # هنا يمكن إضافة منطق اختبار الاتصال حسب كل منصة
        if integration.platform == 'meta_business':
            # اختبار اتصال Meta Business
            success = self._test_meta_connection(integration)
        elif integration.platform == 'twitter':
            # اختبار اتصال Twitter
            success = self._test_twitter_connection(integration)
        elif integration.platform == 'google_analytics':
            # اختبار اتصال Google Analytics
            success = self._test_google_analytics_connection(integration)
        else:
            success = False
        
        if success:
            integration.last_sync = timezone.now()
            integration.save()
            return Response({'status': 'الاتصال ناجح'})
        else:
            return Response(
                {'error': 'فشل في الاتصال. تحقق من المفاتيح والإعدادات.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _test_meta_connection(self, integration):
        """اختبار اتصال Meta Business"""
        # منطق اختبار Meta Business API
        return True  # مؤقت
    
    def _test_twitter_connection(self, integration):
        """اختبار اتصال Twitter"""
        # منطق اختبار Twitter API
        return True  # مؤقت
    
    def _test_google_analytics_connection(self, integration):
        """اختبار اتصال Google Analytics"""
        # منطق اختبار Google Analytics API
        return True  # مؤقت


class PlatformReportViewSet(viewsets.ModelViewSet):
    """ViewSet لتقارير المنصات"""
    queryset = PlatformReport.objects.all()
    serializer_class = PlatformReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PlatformReport.objects.all()
        
        # فلترة حسب المنصة
        platform = self.request.query_params.get('platform', None)
        if platform:
            queryset = queryset.filter(integration__platform=platform)
        
        # فلترة حسب نوع التقرير
        report_type = self.request.query_params.get('type', None)
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        return queryset.order_by('-generated_at')


class AdCampaignViewSet(viewsets.ModelViewSet):
    """ViewSet للحملات الإعلانية"""
    queryset = AdCampaign.objects.all()
    serializer_class = AdCampaignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AdCampaign.objects.all()
        
        # فلترة حسب المنصة
        platform = self.request.query_params.get('platform', None)
        if platform:
            queryset = queryset.filter(platform=platform)
        
        # فلترة حسب الحالة
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_performance(self, request, pk=None):
        """تحديث بيانات أداء الحملة"""
        campaign = self.get_object()
        performance_data = request.data.get('performance_data', {})
        
        if performance_data:
            campaign.performance_data.update(performance_data)
            campaign.save()
            return Response({'status': 'تم تحديث بيانات الأداء'})
        
        return Response(
            {'error': 'لم يتم تقديم بيانات أداء'},
            status=status.HTTP_400_BAD_REQUEST
        )


class AnalyticsReportViewSet(viewsets.ModelViewSet):
    """ViewSet لتقارير التحليلات"""
    queryset = AnalyticsReport.objects.all()
    serializer_class = AnalyticsReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AnalyticsReport.objects.all()
        
        # فلترة حسب نوع التقرير
        report_type = self.request.query_params.get('type', None)
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        return queryset.order_by('-generated_at')
    
    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """إنشاء تقرير جديد"""
        report_type = request.data.get('report_type', 'comprehensive')
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to')
        title = request.data.get('title', f'تقرير {report_type}')
        
        if not date_from or not date_to:
            return Response(
                {'error': 'يجب تحديد تاريخ البداية والنهاية'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # جمع بيانات التقرير
        report_data = self._generate_report_data(report_type, date_from, date_to)
        
        # إنشاء التقرير
        report = AnalyticsReport.objects.create(
            title=title,
            report_type=report_type,
            date_from=date_from,
            date_to=date_to,
            generated_by=request.user,
            **report_data
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def _generate_report_data(self, report_type, date_from, date_to):
        """إنشاء بيانات التقرير"""
        # تحليلات الموقع
        visitor_queryset = VisitorTracking.objects.filter(
            visited_at__range=[date_from, date_to]
        )
        
        website_analytics = {
            'total_visitors': visitor_queryset.values('session_key').distinct().count(),
            'total_page_views': visitor_queryset.count(),
            'bounce_rate': visitor_queryset.filter(is_bounce=True).count() / visitor_queryset.count() * 100 if visitor_queryset.count() > 0 else 0,
            'avg_session_duration': visitor_queryset.aggregate(avg=Avg('visit_duration'))['avg'] or 0
        }
        
        # إرسالات النماذج
        submission_queryset = FormSubmission.objects.filter(
            submitted_at__range=[date_from, date_to]
        )
        
        form_submissions = {
            'total_submissions': submission_queryset.count(),
            'submissions_by_form': dict(submission_queryset.values('form__name').annotate(count=Count('id')).values_list('form__name', 'count')),
            'submissions_by_status': dict(submission_queryset.values('status').annotate(count=Count('id')).values_list('status', 'count'))
        }
        
        # رؤى الزوار
        visitor_insights = {
            'total_visitors': website_analytics['total_visitors'],
            'total_page_views': website_analytics['total_page_views'],
            'bounce_rate': website_analytics['bounce_rate'],
            'avg_session_duration': website_analytics['avg_session_duration'],
            'device_breakdown': dict(visitor_queryset.values('device_type').annotate(count=Count('id')).values_list('device_type', 'count')),
            'browser_breakdown': dict(visitor_queryset.values('browser').annotate(count=Count('id')).values_list('browser', 'count'))
        }
        
        # أداء المنصات (يمكن توسيعه لاحقاً)
        platform_performance = {
            'meta_business': {},
            'twitter': {},
            'google_analytics': {}
        }
        
        return {
            'website_analytics': website_analytics,
            'form_submissions': form_submissions,
            'visitor_insights': visitor_insights,
            'platform_performance': platform_performance
        }




# ViewSets للتكاملات والمنصات الخارجية
from .integrations import IntegrationManager, get_integration_manager


class IntegrationSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet لإعدادات التكامل مع المنصات الخارجية"""
    queryset = IntegrationSettings.objects.all()
    serializer_class = IntegrationSettingsSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'platform'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return IntegrationSettingsUpdateSerializer
        return IntegrationSettingsSerializer
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, platform=None):
        """اختبار الاتصال مع المنصة"""
        try:
            integration_manager = get_integration_manager()
            
            if platform == 'meta_business':
                result = integration_manager.meta_business.test_connection()
            elif platform == 'x_twitter':
                result = integration_manager.x_twitter.test_connection()
            else:
                return Response({
                    'success': False,
                    'error': 'Unsupported platform'
                }, status=400)
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def test_all_connections(self, request):
        """اختبار جميع الاتصالات"""
        try:
            integration_manager = get_integration_manager()
            results = integration_manager.test_all_connections()
            return Response(results)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)


class PlatformReportViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet لتقارير المنصات الخارجية"""
    queryset = PlatformReport.objects.all()
    serializer_class = PlatformReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PlatformReport.objects.all()
        
        # فلترة حسب المنصة
        platform = self.request.query_params.get('platform', None)
        if platform:
            queryset = queryset.filter(platform=platform)
        
        # فلترة حسب التاريخ
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if date_from:
            queryset = queryset.filter(report_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(report_date__lte=date_to)
        
        return queryset.order_by('-report_date')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """ملخص تقارير جميع المنصات"""
        try:
            # تحديد نطاق التاريخ
            days = int(request.query_params.get('days', 7))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            # جلب التقارير
            reports = PlatformReport.objects.filter(
                report_date__gte=start_date,
                report_date__lte=end_date
            )
            
            # تجميع البيانات حسب المنصة
            summary = {}
            for platform in ['meta_business', 'x_twitter']:
                platform_reports = reports.filter(platform=platform)
                
                summary[platform] = {
                    'total_impressions': platform_reports.aggregate(
                        total=Sum('impressions')
                    )['total'] or 0,
                    'total_clicks': platform_reports.aggregate(
                        total=Sum('clicks')
                    )['total'] or 0,
                    'total_spend': float(platform_reports.aggregate(
                        total=Sum('spend')
                    )['total'] or 0),
                    'total_reach': platform_reports.aggregate(
                        total=Sum('reach')
                    )['total'] or 0,
                    'avg_ctr': platform_reports.aggregate(
                        avg=Avg('ctr')
                    )['avg'] or 0,
                    'avg_cpc': platform_reports.aggregate(
                        avg=Avg('cpc')
                    )['avg'] or 0,
                    'campaigns_count': platform_reports.values('campaign_id').distinct().count()
                }
            
            # حساب الإجماليات
            total_summary = {
                'total_impressions': sum(p['total_impressions'] for p in summary.values()),
                'total_clicks': sum(p['total_clicks'] for p in summary.values()),
                'total_spend': sum(p['total_spend'] for p in summary.values()),
                'total_reach': sum(p['total_reach'] for p in summary.values()),
                'total_campaigns': sum(p['campaigns_count'] for p in summary.values()),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            }
            
            # حساب المعدلات الإجمالية
            if total_summary['total_impressions'] > 0:
                total_summary['overall_ctr'] = (
                    total_summary['total_clicks'] / total_summary['total_impressions']
                ) * 100
            else:
                total_summary['overall_ctr'] = 0
            
            if total_summary['total_clicks'] > 0:
                total_summary['overall_cpc'] = (
                    total_summary['total_spend'] / total_summary['total_clicks']
                )
            else:
                total_summary['overall_cpc'] = 0
            
            return Response({
                'success': True,
                'summary': total_summary,
                'platforms': summary
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def sync_data(self, request):
        """مزامنة البيانات من المنصات الخارجية"""
        try:
            platform = request.data.get('platform', 'all')
            integration_manager = get_integration_manager()
            
            if platform == 'all':
                results = integration_manager.sync_all_data()
            elif platform == 'meta_business':
                results = {'meta_business': integration_manager.meta_business.sync_campaigns_data()}
            elif platform == 'x_twitter':
                results = {'x_twitter': integration_manager.x_twitter.sync_content_data()}
            else:
                return Response({
                    'success': False,
                    'error': 'Unsupported platform'
                }, status=400)
            
            return Response({
                'success': True,
                'results': results
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)


class AdCampaignViewSet(viewsets.ModelViewSet):
    """ViewSet للحملات الإعلانية"""
    queryset = AdCampaign.objects.all()
    serializer_class = AdCampaignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AdCampaign.objects.all()
        
        # فلترة حسب المنصة
        platform = self.request.query_params.get('platform', None)
        if platform:
            queryset = queryset.filter(platform=platform)
        
        # فلترة حسب الحالة
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # البحث
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(objective__icontains=search)
            )
        
        return queryset.order_by('-created_date')
    
    @action(detail=True, methods=['post'])
    def update_performance(self, request, pk=None):
        """تحديث أداء الحملة"""
        try:
            campaign = self.get_object()
            integration_manager = get_integration_manager()
            
            if campaign.platform == 'meta_business':
                insights = integration_manager.meta_business.get_campaign_insights(
                    campaign.external_id
                )
                
                if insights:
                    # تحديث أو إنشاء تقرير جديد
                    PlatformReport.objects.update_or_create(
                        platform=campaign.platform,
                        campaign_id=campaign.external_id,
                        report_date=timezone.now().date(),
                        defaults={
                            'impressions': int(insights.get('impressions', 0)),
                            'clicks': int(insights.get('clicks', 0)),
                            'spend': float(insights.get('spend', 0)),
                            'reach': int(insights.get('reach', 0)),
                            'ctr': float(insights.get('ctr', 0)),
                            'cpc': float(insights.get('cpc', 0)),
                            'cpm': float(insights.get('cpm', 0)),
                            'data': insights
                        }
                    )
                    
                    return Response({
                        'success': True,
                        'message': 'Performance updated successfully',
                        'data': insights
                    })
                else:
                    return Response({
                        'success': False,
                        'error': 'No performance data available'
                    }, status=404)
            
            elif campaign.platform == 'x_twitter':
                analytics = integration_manager.x_twitter.get_tweet_analytics(
                    campaign.external_id
                )
                
                if analytics:
                    # تحديث أو إنشاء تقرير جديد
                    PlatformReport.objects.update_or_create(
                        platform=campaign.platform,
                        campaign_id=campaign.external_id,
                        report_date=timezone.now().date(),
                        defaults={
                            'impressions': analytics.get('impression_count', 0),
                            'clicks': analytics.get('url_link_clicks', 0),
                            'reach': analytics.get('impression_count', 0),
                            'engagement_rate': (
                                analytics.get('like_count', 0) + 
                                analytics.get('retweet_count', 0)
                            ),
                            'data': analytics
                        }
                    )
                    
                    return Response({
                        'success': True,
                        'message': 'Performance updated successfully',
                        'data': analytics
                    })
                else:
                    return Response({
                        'success': False,
                        'error': 'No analytics data available'
                    }, status=404)
            
            else:
                return Response({
                    'success': False,
                    'error': 'Unsupported platform'
                }, status=400)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def performance_summary(self, request):
        """ملخص أداء جميع الحملات"""
        try:
            # تحديد نطاق التاريخ
            days = int(request.query_params.get('days', 7))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            # جلب الحملات
            campaigns = self.get_queryset()
            
            # جلب التقارير المرتبطة
            campaign_ids = campaigns.values_list('external_id', flat=True)
            reports = PlatformReport.objects.filter(
                campaign_id__in=campaign_ids,
                report_date__gte=start_date,
                report_date__lte=end_date
            )
            
            # تجميع البيانات
            summary = {
                'total_campaigns': campaigns.count(),
                'active_campaigns': campaigns.filter(status='active').count(),
                'paused_campaigns': campaigns.filter(status='paused').count(),
                'total_impressions': reports.aggregate(total=Sum('impressions'))['total'] or 0,
                'total_clicks': reports.aggregate(total=Sum('clicks'))['total'] or 0,
                'total_spend': float(reports.aggregate(total=Sum('spend'))['total'] or 0),
                'total_reach': reports.aggregate(total=Sum('reach'))['total'] or 0,
                'avg_ctr': reports.aggregate(avg=Avg('ctr'))['avg'] or 0,
                'avg_cpc': reports.aggregate(avg=Avg('cpc'))['avg'] or 0,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            }
            
            # تجميع حسب المنصة
            platforms_summary = {}
            for platform in ['meta_business', 'x_twitter']:
                platform_campaigns = campaigns.filter(platform=platform)
                platform_reports = reports.filter(platform=platform)
                
                platforms_summary[platform] = {
                    'campaigns_count': platform_campaigns.count(),
                    'active_campaigns': platform_campaigns.filter(status='active').count(),
                    'total_impressions': platform_reports.aggregate(
                        total=Sum('impressions')
                    )['total'] or 0,
                    'total_clicks': platform_reports.aggregate(
                        total=Sum('clicks')
                    )['total'] or 0,
                    'total_spend': float(platform_reports.aggregate(
                        total=Sum('spend')
                    )['total'] or 0),
                    'avg_ctr': platform_reports.aggregate(avg=Avg('ctr'))['avg'] or 0,
                    'avg_cpc': platform_reports.aggregate(avg=Avg('cpc'))['avg'] or 0
                }
            
            return Response({
                'success': True,
                'summary': summary,
                'platforms': platforms_summary
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)


class SocialMediaViewSet(viewsets.ViewSet):
    """ViewSet لإدارة المحتوى على وسائل التواصل الاجتماعي"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def post_tweet(self, request):
        """نشر تغريدة على X"""
        try:
            text = request.data.get('text', '')
            media_ids = request.data.get('media_ids', [])
            
            if not text:
                return Response({
                    'success': False,
                    'error': 'Tweet text is required'
                }, status=400)
            
            integration_manager = get_integration_manager()
            result = integration_manager.x_twitter.post_tweet(text, media_ids)
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def get_tweets(self, request):
        """جلب التغريدات الأخيرة"""
        try:
            max_results = int(request.query_params.get('max_results', 10))
            
            integration_manager = get_integration_manager()
            tweets = integration_manager.x_twitter.get_user_tweets(max_results=max_results)
            
            return Response({
                'success': True,
                'data': tweets
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def get_meta_accounts(self, request):
        """جلب حسابات Meta Business"""
        try:
            integration_manager = get_integration_manager()
            accounts = integration_manager.meta_business.get_ad_accounts()
            
            return Response({
                'success': True,
                'data': accounts
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def get_meta_campaigns(self, request):
        """جلب حملات Meta Business"""
        try:
            ad_account_id = request.query_params.get('ad_account_id')
            
            if not ad_account_id:
                return Response({
                    'success': False,
                    'error': 'ad_account_id is required'
                }, status=400)
            
            integration_manager = get_integration_manager()
            campaigns = integration_manager.meta_business.get_campaigns(ad_account_id)
            
            return Response({
                'success': True,
                'data': campaigns
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def create_meta_campaign(self, request):
        """إنشاء حملة إعلانية على Meta Business"""
        try:
            ad_account_id = request.data.get('ad_account_id')
            campaign_data = request.data.get('campaign_data', {})
            
            if not ad_account_id or not campaign_data:
                return Response({
                    'success': False,
                    'error': 'ad_account_id and campaign_data are required'
                }, status=400)
            
            integration_manager = get_integration_manager()
            result = integration_manager.meta_business.create_campaign(
                ad_account_id, campaign_data
            )
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)


class UnifiedReportViewSet(viewsets.ViewSet):
    """ViewSet للتقارير الموحدة من جميع المنصات"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def generate_report(self, request):
        """إنشاء تقرير موحد"""
        try:
            days = int(request.query_params.get('days', 7))
            
            integration_manager = get_integration_manager()
            result = integration_manager.get_unified_report(days)
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """إحصائيات لوحة القيادة"""
        try:
            # تحديد نطاق التاريخ
            days = int(request.query_params.get('days', 7))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            # إحصائيات المنصات
            platform_reports = PlatformReport.objects.filter(
                report_date__gte=start_date,
                report_date__lte=end_date
            )
            
            # إحصائيات الحملات
            campaigns = AdCampaign.objects.all()
            
            # إحصائيات الزوار
            visitors = VisitorTracking.objects.filter(
                visit_date__gte=start_date,
                visit_date__lte=end_date
            )
            
            # إحصائيات النماذج
            form_submissions = FormSubmission.objects.filter(
                submitted_at__gte=timezone.make_aware(
                    datetime.combine(start_date, datetime.min.time())
                ),
                submitted_at__lte=timezone.make_aware(
                    datetime.combine(end_date, datetime.max.time())
                )
            )
            
            stats = {
                'platforms': {
                    'total_impressions': platform_reports.aggregate(
                        total=Sum('impressions')
                    )['total'] or 0,
                    'total_clicks': platform_reports.aggregate(
                        total=Sum('clicks')
                    )['total'] or 0,
                    'total_spend': float(platform_reports.aggregate(
                        total=Sum('spend')
                    )['total'] or 0),
                    'total_reach': platform_reports.aggregate(
                        total=Sum('reach')
                    )['total'] or 0
                },
                'campaigns': {
                    'total_campaigns': campaigns.count(),
                    'active_campaigns': campaigns.filter(status='active').count(),
                    'paused_campaigns': campaigns.filter(status='paused').count(),
                    'meta_business_campaigns': campaigns.filter(platform='meta_business').count(),
                    'x_twitter_campaigns': campaigns.filter(platform='x_twitter').count()
                },
                'visitors': {
                    'total_visits': visitors.count(),
                    'unique_visitors': visitors.values('ip_address').distinct().count(),
                    'avg_session_duration': visitors.aggregate(
                        avg=Avg('session_duration')
                    )['avg'] or 0,
                    'bounce_rate': 0  # يمكن حسابها لاحقاً
                },
                'forms': {
                    'total_submissions': form_submissions.count(),
                    'pending_submissions': form_submissions.filter(status='pending').count(),
                    'processed_submissions': form_submissions.filter(status='processed').count(),
                    'forms_count': DynamicForm.objects.filter(is_active=True).count()
                },
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            }
            
            return Response({
                'success': True,
                'stats': stats
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)

