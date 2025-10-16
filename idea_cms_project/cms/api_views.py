from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    CustomUser, Project, Task, Notification, Message, Analytics,
    BlogPost, FormSubmission, ContactMessage, DynamicForm,
    VisitorTracking, IntegrationSettings, PlatformReport
)
from .serializers import (
    LoginSerializer, UserSerializer, CustomUserProfileSerializer,
    ProjectSerializer, TaskSerializer, NotificationSerializer,
    MessageSerializer, AnalyticsSerializer, DashboardStatsSerializer,
    ProjectProgressSerializer, TaskSummarySerializer, UserActivitySerializer,
    SearchResultSerializer, BlogPostSerializer, FormSubmissionSerializer,
    ContactMessageSerializer, DynamicFormSerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    """تقسيم النتائج إلى صفحات"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# Authentication Views

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_api(request):
    """API تسجيل الدخول"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        # إنشاء أو الحصول على token
        token, created = Token.objects.get_or_create(user=user)
        
        # تسجيل عملية تسجيل الدخول في التحليلات
        Analytics.objects.create(
            user=user,
            metric_type='user_login',
            value={'login_time': timezone.now().isoformat()},
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # الحصول على ملف المستخدم
        try:
            profile = CustomUser.objects.get(user=user)
            profile_data = CustomUserProfileSerializer(profile).data
        except CustomUser.DoesNotExist:
            profile_data = None
        
        return Response({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'token': token.key,
            'user': UserSerializer(user).data,
            'profile': profile_data
        })
    
    return Response({
        'success': False,
        'message': 'بيانات تسجيل الدخول غير صحيحة',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_api(request):
    """API تسجيل الخروج"""
    try:
        # حذف token المستخدم
        request.user.auth_token.delete()
    except:
        pass
    
    logout(request)
    return Response({
        'success': True,
        'message': 'تم تسجيل الخروج بنجاح'
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile_api(request):
    """API الحصول على ملف المستخدم"""
    try:
        profile = CustomUser.objects.get(user=request.user)
        serializer = CustomUserProfileSerializer(profile)
        return Response({
            'success': True,
            'profile': serializer.data
        })
    except CustomUser.DoesNotExist:
        return Response({
            'success': False,
            'message': 'ملف المستخدم غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)

# Dashboard API Views

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats_api(request):
    """API إحصائيات لوحة القيادة"""
    user = request.user
    
    # إحصائيات المشاريع
    if hasattr(user, 'profile') and user.profile.user_type == 'client':
        # إحصائيات العميل
        total_projects = Project.objects.filter(client=user).count()
        active_projects = Project.objects.filter(client=user, status__in=['planning', 'in_progress']).count()
        completed_projects = Project.objects.filter(client=user, status='completed').count()
        total_tasks = Task.objects.filter(project__client=user).count()
        pending_tasks = Task.objects.filter(project__client=user, status__in=['todo', 'in_progress']).count()
        completed_tasks = Task.objects.filter(project__client=user, status='done').count()
    else:
        # إحصائيات عامة للإدارة والفريق
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(status__in=['planning', 'in_progress']).count()
        completed_projects = Project.objects.filter(status='completed').count()
        total_tasks = Task.objects.count()
        pending_tasks = Task.objects.filter(status__in=['todo', 'in_progress']).count()
        completed_tasks = Task.objects.filter(status='done').count()
    
    # إحصائيات المستخدمين (للإدارة فقط)
    if user.is_staff:
        total_users = User.objects.count()
        active_users = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=30)).count()
        total_form_submissions = FormSubmission.objects.count()
    else:
        total_users = 0
        active_users = 0
        total_form_submissions = 0
    
    # الإشعارات غير المقروءة
    unread_notifications = Notification.objects.filter(recipient=user, is_read=False).count()
    
    stats = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'total_users': total_users,
        'active_users': active_users,
        'total_form_submissions': total_form_submissions,
        'unread_notifications': unread_notifications
    }
    
    serializer = DashboardStatsSerializer(stats)
    return Response({
        'success': True,
        'stats': serializer.data
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def project_progress_api(request):
    """API تقدم المشاريع"""
    user = request.user
    
    if hasattr(user, 'profile') and user.profile.user_type == 'client':
        projects = Project.objects.filter(client=user)
    else:
        projects = Project.objects.all()
    
    progress_data = []
    for project in projects:
        days_remaining = (project.end_date - timezone.now().date()).days if project.end_date else 0
        progress_data.append({
            'project_id': project.id,
            'project_title': project.title,
            'progress': project.progress,
            'status': project.status,
            'start_date': project.start_date,
            'end_date': project.end_date,
            'days_remaining': max(0, days_remaining)
        })
    
    serializer = ProjectProgressSerializer(progress_data, many=True)
    return Response({
        'success': True,
        'projects': serializer.data
    })

# Projects API Views

class ProjectListCreateAPIView(generics.ListCreateAPIView):
    """API قائمة وإنشاء المشاريع"""
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.user_type == 'client':
            return Project.objects.filter(client=user)
        return Project.objects.all()
    
    def perform_create(self, serializer):
        # تسجيل إنشاء المشروع في التحليلات
        Analytics.objects.create(
            user=self.request.user,
            metric_type='project_created',
            value={'project_title': serializer.validated_data['title']},
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        serializer.save()

class ProjectDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API تفاصيل المشروع"""
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.user_type == 'client':
            return Project.objects.filter(client=user)
        return Project.objects.all()

# Tasks API Views

class TaskListCreateAPIView(generics.ListCreateAPIView):
    """API قائمة وإنشاء المهام"""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project_id')
        
        queryset = Task.objects.all()
        
        if hasattr(user, 'profile') and user.profile.user_type == 'client':
            queryset = queryset.filter(project__client=user)
        elif hasattr(user, 'profile') and user.profile.user_type == 'team_member':
            queryset = queryset.filter(Q(assigned_to=user) | Q(project__team_members=user))
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class TaskDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API تفاصيل المهمة"""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.user_type == 'client':
            return Task.objects.filter(project__client=user)
        return Task.objects.all()
    
    def perform_update(self, serializer):
        # إنشاء إشعار عند تحديث حالة المهمة
        old_status = self.get_object().status
        new_status = serializer.validated_data.get('status', old_status)
        
        if old_status != new_status and new_status == 'done':
            # إشعار إكمال المهمة
            task = serializer.save()
            Notification.objects.create(
                recipient=task.project.client,
                sender=self.request.user,
                title=f'تم إكمال المهمة: {task.title}',
                message=f'تم إكمال المهمة "{task.title}" في المشروع "{task.project.title}"',
                notification_type='task_completed',
                related_project=task.project,
                related_task=task
            )
            
            # تسجيل في التحليلات
            Analytics.objects.create(
                user=self.request.user,
                metric_type='task_completed',
                value={'task_title': task.title, 'project_title': task.project.title},
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')
            )
        else:
            serializer.save()

# Notifications API Views

class NotificationListAPIView(generics.ListAPIView):
    """API قائمة الإشعارات"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read_api(request, notification_id):
    """API تحديد الإشعار كمقروء"""
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({
            'success': True,
            'message': 'تم تحديد الإشعار كمقروء'
        })
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'message': 'الإشعار غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read_api(request):
    """API تحديد جميع الإشعارات كمقروءة"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response({
        'success': True,
        'message': 'تم تحديد جميع الإشعارات كمقروءة'
    })

# Search API

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_api(request):
    """API البحث العام في النظام"""
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({
            'success': False,
            'message': 'يجب إدخال كلمة البحث'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    results = []
    user = request.user
    
    # البحث في المشاريع
    projects = Project.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )
    if hasattr(user, 'profile') and user.profile.user_type == 'client':
        projects = projects.filter(client=user)
    
    for project in projects[:5]:
        results.append({
            'type': 'project',
            'id': project.id,
            'title': project.title,
            'description': project.description[:100] + '...' if len(project.description) > 100 else project.description,
            'url': f'/projects/{project.id}/',
            'relevance_score': 1.0
        })
    
    # البحث في المهام
    tasks = Task.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )
    if hasattr(user, 'profile') and user.profile.user_type == 'client':
        tasks = tasks.filter(project__client=user)
    
    for task in tasks[:5]:
        results.append({
            'type': 'task',
            'id': task.id,
            'title': task.title,
            'description': task.description[:100] + '...' if len(task.description) > 100 else task.description,
            'url': f'/tasks/{task.id}/',
            'relevance_score': 0.8
        })
    
    # البحث في المستخدمين (للإدارة فقط)
    if user.is_staff:
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
        
        for user_obj in users[:5]:
            results.append({
                'type': 'user',
                'id': user_obj.id,
                'title': user_obj.get_full_name() or user_obj.username,
                'description': user_obj.email,
                'url': f'/users/{user_obj.id}/',
                'relevance_score': 0.6
            })
    
    # ترتيب النتائج حسب الصلة
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    serializer = SearchResultSerializer(results, many=True)
    return Response({
        'success': True,
        'query': query,
        'results': serializer.data,
        'total_results': len(results)
    })

# Analytics API Views

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def task_summary_api(request):
    """API ملخص المهام"""
    user = request.user
    
    if hasattr(user, 'profile') and user.profile.user_type == 'client':
        tasks = Task.objects.filter(project__client=user)
    else:
        tasks = Task.objects.all()
    
    total_tasks = tasks.count()
    if total_tasks == 0:
        return Response({
            'success': True,
            'summary': []
        })
    
    summary = []
    for status_choice in Task.STATUS_CHOICES:
        status_code = status_choice[0]
        status_name = status_choice[1]
        count = tasks.filter(status=status_code).count()
        percentage = (count / total_tasks) * 100
        
        summary.append({
            'status': status_name,
            'count': count,
            'percentage': round(percentage, 2)
        })
    
    serializer = TaskSummarySerializer(summary, many=True)
    return Response({
        'success': True,
        'summary': serializer.data
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_activity_api(request):
    """API نشاط المستخدمين"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': 'غير مصرح لك بالوصول لهذه البيانات'
        }, status=status.HTTP_403_FORBIDDEN)
    
    users = User.objects.filter(is_active=True)
    activity_data = []
    
    for user in users:
        tasks_assigned = Task.objects.filter(assigned_to=user).count()
        tasks_completed = Task.objects.filter(assigned_to=user, status='done').count()
        projects_involved = Project.objects.filter(
            Q(client=user) | Q(manager=user) | Q(team_members=user)
        ).distinct().count()
        
        activity_data.append({
            'user_id': user.id,
            'username': user.username,
            'full_name': user.get_full_name() or user.username,
            'last_login': user.last_login,
            'tasks_assigned': tasks_assigned,
            'tasks_completed': tasks_completed,
            'projects_involved': projects_involved
        })
    
    # ترتيب حسب آخر تسجيل دخول
    activity_data.sort(key=lambda x: x['last_login'] or timezone.now() - timedelta(days=365), reverse=True)
    
    serializer = UserActivitySerializer(activity_data, many=True)
    return Response({
        'success': True,
        'activity': serializer.data
    })

# Form Submissions API

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def submit_form_api(request):
    """API إرسال النماذج من الموقع"""
    form_type = request.data.get('form_type')
    form_data = request.data.get('form_data', {})
    
    # إنشاء إرسال نموذج جديد
    submission = FormSubmission.objects.create(
        form_type=form_type,
        name=form_data.get('name', ''),
        email=form_data.get('email', ''),
        phone=form_data.get('phone', ''),
        company=form_data.get('company', ''),
        message=form_data.get('message', ''),
        form_data=form_data,
        ip_address=request.META.get('REMOTE_ADDR'),
    )
    
    # تسجيل في التحليلات
    Analytics.objects.create(
        metric_type='form_submission',
        value={'form_type': form_type, 'submission_id': str(submission.id)},
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return Response({
        'success': True,
        'message': 'تم إرسال النموذج بنجاح',
        'submission_id': str(submission.id)
    })

# Contact Messages API

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def contact_message_api(request):
    """API إرسال رسائل التواصل"""
    serializer = ContactMessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'تم إرسال رسالتك بنجاح. سنتواصل معك قريباً.'
        })
    
    return Response({
        'success': False,
        'message': 'خطأ في البيانات المرسلة',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

