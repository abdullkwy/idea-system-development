from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# إنشاء router للـ API
router = DefaultRouter()

# APIs الأساسية
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'media', views.MediaViewSet)
router.register(r'pages', views.PageViewSet)
router.register(r'posts', views.BlogPostViewSet)
router.register(r'settings', views.SiteSettingsViewSet)
router.register(r'contact-messages', views.ContactMessageViewSet)

# APIs الجديدة للميزات المتقدمة
router.register(r'dynamic-forms', views.DynamicFormViewSet)
router.register(r'form-submissions', views.FormSubmissionViewSet)
router.register(r'visitor-tracking', views.VisitorTrackingViewSet)
router.register(r'integrations', views.IntegrationSettingsViewSet)
router.register(r'platform-reports', views.PlatformReportViewSet)
router.register(r'ad-campaigns', views.AdCampaignViewSet)
router.register(r'analytics-reports', views.AnalyticsReportViewSet)

# APIs التكاملات والمنصات الخارجية
router.register(r'social-media', views.SocialMediaViewSet, basename='social-media')
router.register(r'unified-reports', views.UnifiedReportViewSet, basename='unified-reports')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]

