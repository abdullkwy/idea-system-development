// Client Dashboard JavaScript
// جافاسكريبت لوحة تحكم العملاء

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initializeDashboard();
    loadClientData();
    setupEventListeners();
    initializeCharts();
    loadDashboardData();
});

// Client data and state
let clientData = null;
let currentSection = 'dashboard';

// Initialize dashboard
function initializeDashboard() {
    // Get client data from session
    const storedClientData = sessionStorage.getItem('clientData');
    if (storedClientData) {
        clientData = JSON.parse(storedClientData);
        updateClientInfo();
    } else {
        // Redirect to login if no client data
        window.location.href = 'index.html';
        return;
    }
    
    // Setup sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });
}

// Load client data
function loadClientData() {
    // Demo client projects data
    const projectsData = [
        {
            id: 'PRJ001',
            title: 'حملة التسويق الرقمي - المرحلة الأولى',
            description: 'إنشاء وإدارة حملة تسويقية شاملة عبر منصات التواصل الاجتماعي',
            status: 'active',
            progress: 75,
            startDate: '2024-01-15',
            endDate: '2024-03-15',
            type: 'تسويق رقمي'
        },
        {
            id: 'PRJ002',
            title: 'تصميم الهوية البصرية',
            description: 'تطوير شعار وهوية بصرية متكاملة للعلامة التجارية',
            status: 'completed',
            progress: 100,
            startDate: '2023-12-01',
            endDate: '2024-01-10',
            type: 'تصميم إبداعي'
        },
        {
            id: 'PRJ003',
            title: 'تطوير موقع إلكتروني',
            description: 'تصميم وتطوير موقع إلكتروني متجاوب مع لوحة تحكم',
            status: 'active',
            progress: 45,
            startDate: '2024-02-01',
            endDate: '2024-04-30',
            type: 'تطوير تقني'
        },
        {
            id: 'PRJ004',
            title: 'استشارة تسويقية',
            description: 'وضع استراتيجية تسويقية شاملة للعام القادم',
            status: 'pending',
            progress: 20,
            startDate: '2024-03-01',
            endDate: '2024-03-31',
            type: 'استشارات'
        }
    ];
    
    // Store projects data
    window.clientProjects = projectsData;
    
    // Demo activities data
    const activitiesData = [
        {
            type: 'success',
            title: 'تم إكمال مرحلة التصميم',
            description: 'تم الانتهاء من تصميم الصفحة الرئيسية للموقع',
            time: 'منذ ساعتين',
            project: 'PRJ003'
        },
        {
            type: 'info',
            title: 'تحديث تقرير الأداء',
            description: 'تم رفع تقرير أداء الحملة الإعلانية لهذا الأسبوع',
            time: 'منذ 4 ساعات',
            project: 'PRJ001'
        },
        {
            type: 'warning',
            title: 'مطلوب مراجعة المحتوى',
            description: 'يرجى مراجعة المحتوى المقترح للحملة الجديدة',
            time: 'منذ يوم واحد',
            project: 'PRJ004'
        }
    ];
    
    window.clientActivities = activitiesData;
}

// Update client information in UI
function updateClientInfo() {
    if (clientData) {
        document.getElementById('welcomeText').textContent = `مرحباً ${clientData.name}`;
        document.getElementById('clientName').textContent = clientData.name;
    }
}

// Setup event listeners
function setupEventListeners() {
    // Logout functionality
    document.getElementById('logoutBtn').addEventListener('click', function(e) {
        e.preventDefault();
        if (confirm('هل أنت متأكد من تسجيل الخروج؟')) {
            sessionStorage.removeItem('clientData');
            window.location.href = 'index.html';
        }
    });
    
    // Dropdown toggles
    setupDropdowns();
}

// Setup dropdown menus
function setupDropdowns() {
    const dropdowns = document.querySelectorAll('.nav-item');
    
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Close other dropdowns
            dropdowns.forEach(other => {
                if (other !== dropdown) {
                    other.classList.remove('active');
                }
            });
            
            // Toggle current dropdown
            this.classList.toggle('active');
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', () => {
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('active');
        });
    });
}

// Initialize charts
function initializeCharts() {
    // Campaign performance chart
    const campaignCtx = document.getElementById('campaignChart');
    if (campaignCtx) {
        new Chart(campaignCtx, {
            type: 'line',
            data: {
                labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'],
                datasets: [{
                    label: 'المشاهدات',
                    data: [12000, 19000, 15000, 25000, 22000, 30000],
                    borderColor: '#2B5741',
                    backgroundColor: 'rgba(43, 87, 65, 0.1)',
                    tension: 0.4
                }, {
                    label: 'التفاعلات',
                    data: [800, 1200, 900, 1500, 1300, 1800],
                    borderColor: '#C9A769',
                    backgroundColor: 'rgba(201, 167, 105, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Projects distribution chart
    const projectsCtx = document.getElementById('projectsChart');
    if (projectsCtx) {
        new Chart(projectsCtx, {
            type: 'doughnut',
            data: {
                labels: ['نشط', 'مكتمل', 'في الانتظار'],
                datasets: [{
                    data: [3, 12, 1],
                    backgroundColor: [
                        '#2B5741',
                        '#28A745',
                        '#FFC107'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }
}

// Load dashboard data
function loadDashboardData() {
    loadCurrentProjects();
    loadRecentActivities();
    loadNotifications();
}

// Load current projects
function loadCurrentProjects() {
    const container = document.getElementById('currentProjects');
    if (!container || !window.clientProjects) return;
    
    const activeProjects = window.clientProjects.filter(project => project.status === 'active');
    
    container.innerHTML = activeProjects.map(project => `
        <div class="project-card">
            <div class="project-header">
                <h4 class="project-title">${project.title}</h4>
                <span class="project-status status-${project.status}">
                    ${getStatusText(project.status)}
                </span>
            </div>
            <p class="project-description">${project.description}</p>
            <div class="project-progress">
                <div class="progress-label">
                    <span>التقدم</span>
                    <span>${project.progress}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${project.progress}%"></div>
                </div>
            </div>
            <div class="project-meta">
                <span><i class="fas fa-calendar"></i> ${formatDate(project.endDate)}</span>
                <span><i class="fas fa-tag"></i> ${project.type}</span>
            </div>
        </div>
    `).join('');
}

// Load recent activities
function loadRecentActivities() {
    const container = document.getElementById('recentActivities');
    if (!container || !window.clientActivities) return;
    
    container.innerHTML = window.clientActivities.map(activity => `
        <div class="activity-item">
            <div class="activity-icon ${activity.type}">
                <i class="fas ${getActivityIcon(activity.type)}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">${activity.title}</div>
                <div class="activity-description">${activity.description}</div>
                <div class="activity-time">${activity.time}</div>
            </div>
        </div>
    `).join('');
}

// Load notifications
function loadNotifications() {
    const container = document.getElementById('notificationsList');
    if (!container) return;
    
    const notifications = [
        {
            title: 'تحديث في المشروع',
            message: 'تم رفع ملفات التصميم الجديدة',
            time: 'منذ ساعة',
            read: false
        },
        {
            title: 'موعد اجتماع',
            message: 'اجتماع مراجعة المشروع غداً الساعة 2 ظهراً',
            time: 'منذ 3 ساعات',
            read: false
        }
    ];
    
    container.innerHTML = notifications.map(notification => `
        <div class="notification-item ${notification.read ? 'read' : 'unread'}">
            <div class="notification-content">
                <div class="notification-title">${notification.title}</div>
                <div class="notification-message">${notification.message}</div>
                <div class="notification-time">${notification.time}</div>
            </div>
        </div>
    `).join('');
}

// Navigation functions
function showDashboard() {
    showSection('dashboardSection');
    setActiveMenuItem(0);
}

function showProjects() {
    showSection('projectsSection');
    setActiveMenuItem(2);
    loadAllProjects();
}

function showCompletedWorks() {
    showSection('projectsSection');
    setActiveMenuItem(3);
    loadCompletedProjects();
}

function showSchedule() {
    alert('قريباً... صفحة المواعيد المستقبلية');
}

function showReports() {
    showSection('reportsSection');
    setActiveMenuItem(5);
}

function showPlatformReports() {
    alert('قريباً... تقارير المنصات');
}

function showMessages() {
    alert('قريباً... صفحة الرسائل');
}

function showSupport() {
    alert('قريباً... صفحة الدعم الفني');
}

function showProfile() {
    alert('قريباً... الملف الشخصي');
}

function showSettings() {
    alert('قريباً... الإعدادات');
}

// Show specific section
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }
}

// Set active menu item
function setActiveMenuItem(index) {
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const menuItems = document.querySelectorAll('.menu-item');
    if (menuItems[index]) {
        menuItems[index].classList.add('active');
    }
}

// Load all projects
function loadAllProjects() {
    const container = document.getElementById('allProjects');
    if (!container || !window.clientProjects) return;
    
    container.innerHTML = window.clientProjects.map(project => `
        <div class="project-item">
            <div class="project-header">
                <h4 class="project-title">${project.title}</h4>
                <span class="project-status status-${project.status}">
                    ${getStatusText(project.status)}
                </span>
            </div>
            <p class="project-description">${project.description}</p>
            <div class="project-progress">
                <div class="progress-label">
                    <span>التقدم</span>
                    <span>${project.progress}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${project.progress}%"></div>
                </div>
            </div>
            <div class="project-meta">
                <span><i class="fas fa-calendar"></i> ${formatDate(project.startDate)} - ${formatDate(project.endDate)}</span>
                <span><i class="fas fa-tag"></i> ${project.type}</span>
                <span><i class="fas fa-id-badge"></i> ${project.id}</span>
            </div>
        </div>
    `).join('');
}

// Load completed projects
function loadCompletedProjects() {
    const container = document.getElementById('allProjects');
    if (!container || !window.clientProjects) return;
    
    const completedProjects = window.clientProjects.filter(project => project.status === 'completed');
    
    container.innerHTML = completedProjects.map(project => `
        <div class="project-item">
            <div class="project-header">
                <h4 class="project-title">${project.title}</h4>
                <span class="project-status status-${project.status}">
                    ${getStatusText(project.status)}
                </span>
            </div>
            <p class="project-description">${project.description}</p>
            <div class="project-progress">
                <div class="progress-label">
                    <span>التقدم</span>
                    <span>${project.progress}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${project.progress}%"></div>
                </div>
            </div>
            <div class="project-meta">
                <span><i class="fas fa-calendar"></i> ${formatDate(project.startDate)} - ${formatDate(project.endDate)}</span>
                <span><i class="fas fa-tag"></i> ${project.type}</span>
                <span><i class="fas fa-id-badge"></i> ${project.id}</span>
            </div>
        </div>
    `).join('');
}

// Request new project
function requestNewProject() {
    alert('قريباً... نموذج طلب مشروع جديد');
}

// Utility functions
function getStatusText(status) {
    const statusMap = {
        'active': 'نشط',
        'completed': 'مكتمل',
        'pending': 'في الانتظار'
    };
    return statusMap[status] || status;
}

function getActivityIcon(type) {
    const iconMap = {
        'success': 'fa-check-circle',
        'info': 'fa-info-circle',
        'warning': 'fa-exclamation-triangle'
    };
    return iconMap[type] || 'fa-circle';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-SA');
}

