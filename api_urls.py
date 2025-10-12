from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# إعداد الـ router للـ ViewSets
router = DefaultRouter()

# URLs للواجهات البرمجية
urlpatterns = [
    # Authentication APIs
    path('auth/login/', api_views.login_api, name='api_login'),
    path('auth/logout/', api_views.logout_api, name='api_logout'),
    path('auth/profile/', api_views.user_profile_api, name='api_user_profile'),
    
    # Dashboard APIs
    path('dashboard/stats/', api_views.dashboard_stats_api, name='api_dashboard_stats'),
    path('dashboard/project-progress/', api_views.project_progress_api, name='api_project_progress'),
    path('dashboard/task-summary/', api_views.task_summary_api, name='api_task_summary'),
    path('dashboard/user-activity/', api_views.user_activity_api, name='api_user_activity'),
    
    # Projects APIs
    path('projects/', api_views.ProjectListCreateAPIView.as_view(), name='api_projects_list'),
    path('projects/<int:pk>/', api_views.ProjectDetailAPIView.as_view(), name='api_project_detail'),
    
    # Tasks APIs
    path('tasks/', api_views.TaskListCreateAPIView.as_view(), name='api_tasks_list'),
    path('tasks/<int:pk>/', api_views.TaskDetailAPIView.as_view(), name='api_task_detail'),
    
    # Notifications APIs
    path('notifications/', api_views.NotificationListAPIView.as_view(), name='api_notifications_list'),
    path('notifications/<int:notification_id>/mark-read/', api_views.mark_notification_read_api, name='api_mark_notification_read'),
    path('notifications/mark-all-read/', api_views.mark_all_notifications_read_api, name='api_mark_all_notifications_read'),
    
    # Search API
    path('search/', api_views.search_api, name='api_search'),
    
    # Form Submissions APIs
    path('forms/submit/', api_views.submit_form_api, name='api_submit_form'),
    path('contact/submit/', api_views.contact_message_api, name='api_contact_message'),
    
    # Include router URLs
    path('', include(router.urls)),
]

