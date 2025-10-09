// Team Management Dashboard JavaScript
// جافاسكريبت لوحة تحكم نظام إدارة المهام

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initializeDashboard();
    loadTeamMemberData();
    setupEventListeners();
    initializeCharts();
    loadDashboardData();
    initializeKanban();
});

// Team member data and state
let teamMemberData = null;
let currentSection = 'dashboard';
let tasks = [];
let projects = [];

// Initialize dashboard
function initializeDashboard() {
    // Get team member data from session
    const storedMemberData = sessionStorage.getItem('teamMemberData');
    if (storedMemberData) {
        teamMemberData = JSON.parse(storedMemberData);
        updateMemberInfo();
    } else {
        // Redirect to login if no member data
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

// Load team member data
function loadTeamMemberData() {
    // Demo tasks data
    const tasksData = [
        {
            id: 'TSK001',
            title: 'تصميم واجهة الصفحة الرئيسية',
            description: 'إنشاء تصميم متجاوب وجذاب للصفحة الرئيسية للموقع الجديد',
            status: 'in-progress',
            priority: 'high',
            assignee: 'TM002',
            assigneeName: 'فاطمة علي',
            project: 'project2',
            projectName: 'تطوير الموقع',
            dueDate: '2024-02-15',
            createdDate: '2024-02-01',
            progress: 65
        },
        {
            id: 'TSK002',
            title: 'كتابة محتوى الحملة الإعلانية',
            description: 'إعداد النصوص والمحتوى للحملة الإعلانية الجديدة على منصات التواصل',
            status: 'todo',
            priority: 'medium',
            assignee: 'TM004',
            assigneeName: 'سارة أحمد',
            project: 'project1',
            projectName: 'مشروع التسويق الرقمي',
            dueDate: '2024-02-20',
            createdDate: '2024-02-05',
            progress: 0
        },
        {
            id: 'TSK003',
            title: 'تطوير نظام تسجيل الدخول',
            description: 'برمجة وتطوير نظام آمن لتسجيل دخول المستخدمين',
            status: 'review',
            priority: 'high',
            assignee: 'TM003',
            assigneeName: 'محمد سالم',
            project: 'project2',
            projectName: 'تطوير الموقع',
            dueDate: '2024-02-12',
            createdDate: '2024-01-25',
            progress: 90
        },
        {
            id: 'TSK004',
            title: 'تصميم شعار العلامة التجارية',
            description: 'إنشاء شعار احترافي يعكس هوية العلامة التجارية',
            status: 'done',
            priority: 'medium',
            assignee: 'TM002',
            assigneeName: 'فاطمة علي',
            project: 'project3',
            projectName: 'تصميم الهوية',
            dueDate: '2024-01-30',
            createdDate: '2024-01-15',
            progress: 100
        },
        {
            id: 'TSK005',
            title: 'إعداد خطة المشروع',
            description: 'وضع خطة زمنية مفصلة لتنفيذ المشروع مع تحديد المهام والمسؤوليات',
            status: 'done',
            priority: 'high',
            assignee: 'TM001',
            assigneeName: 'أحمد محمد',
            project: 'project1',
            projectName: 'مشروع التسويق الرقمي',
            dueDate: '2024-01-20',
            createdDate: '2024-01-10',
            progress: 100
        },
        {
            id: 'TSK006',
            title: 'تحليل المنافسين',
            description: 'دراسة وتحليل استراتيجيات المنافسين في السوق',
            status: 'in-progress',
            priority: 'medium',
            assignee: 'TM004',
            assigneeName: 'سارة أحمد',
            project: 'project1',
            projectName: 'مشروع التسويق الرقمي',
            dueDate: '2024-02-25',
            createdDate: '2024-02-08',
            progress: 40
        },
        {
            id: 'TSK007',
            title: 'اختبار الموقع على الأجهزة المختلفة',
            description: 'التأكد من توافق الموقع مع جميع الأجهزة والمتصفحات',
            status: 'todo',
            priority: 'low',
            assignee: 'TM003',
            assigneeName: 'محمد سالم',
            project: 'project2',
            projectName: 'تطوير الموقع',
            dueDate: '2024-03-01',
            createdDate: '2024-02-10',
            progress: 0
        },
        {
            id: 'TSK008',
            title: 'إنشاء دليل الهوية البصرية',
            description: 'توثيق جميع عناصر الهوية البصرية في دليل شامل',
            status: 'review',
            priority: 'medium',
            assignee: 'TM002',
            assigneeName: 'فاطمة علي',
            project: 'project3',
            projectName: 'تصميم الهوية',
            dueDate: '2024-02-18',
            createdDate: '2024-02-01',
            progress: 85
        }
    ];
    
    // Store tasks data
    window.teamTasks = tasksData;
    
    // Demo team activities data
    const activitiesData = [
        {
            type: 'task',
            title: 'تم إكمال مهمة جديدة',
            description: 'أكملت فاطمة علي مهمة "تصميم شعار العلامة التجارية"',
            time: 'منذ ساعة واحدة',
            user: 'فاطمة علي'
        },
        {
            type: 'project',
            title: 'تحديث في المشروع',
            description: 'تم رفع ملفات جديدة لمشروع تطوير الموقع',
            time: 'منذ 3 ساعات',
            user: 'محمد سالم'
        },
        {
            type: 'comment',
            title: 'تعليق جديد',
            description: 'أضاف أحمد محمد تعليقاً على مهمة "تحليل المنافسين"',
            time: 'منذ 5 ساعات',
            user: 'أحمد محمد'
        },
        {
            type: 'task',
            title: 'مهمة جديدة',
            description: 'تم إنشاء مهمة جديدة "اختبار الموقع على الأجهزة المختلفة"',
            time: 'منذ يوم واحد',
            user: 'أحمد محمد'
        }
    ];
    
    window.teamActivities = activitiesData;
}

// Update member information in UI
function updateMemberInfo() {
    if (teamMemberData) {
        document.getElementById('memberName').textContent = teamMemberData.name;
        
        // Update my tasks count based on member's tasks
        const myTasks = window.teamTasks ? window.teamTasks.filter(task => task.assignee === teamMemberData.id) : [];
        const myTasksCount = myTasks.filter(task => task.status !== 'done').length;
        document.getElementById('myTasksCount').textContent = myTasksCount;
    }
}

// Setup event listeners
function setupEventListeners() {
    // Logout functionality
    document.getElementById('logoutBtn').addEventListener('click', function(e) {
        e.preventDefault();
        if (confirm('هل أنت متأكد من تسجيل الخروج؟')) {
            sessionStorage.removeItem('teamMemberData');
            window.location.href = 'index.html';
        }
    });
    
    // Task search functionality
    const taskSearch = document.getElementById('taskSearch');
    if (taskSearch) {
        taskSearch.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            filterTasks(searchTerm);
        });
    }
    
    // Create task form
    const createTaskForm = document.getElementById('createTaskForm');
    if (createTaskForm) {
        createTaskForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createNewTask();
        });
    }
    
    // Setup dropdowns
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
    // Weekly progress chart
    const weeklyCtx = document.getElementById('weeklyProgressChart');
    if (weeklyCtx) {
        new Chart(weeklyCtx, {
            type: 'line',
            data: {
                labels: ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'],
                datasets: [{
                    label: 'المهام المكتملة',
                    data: [2, 3, 1, 4, 2, 3, 1],
                    borderColor: '#2B5741',
                    backgroundColor: 'rgba(43, 87, 65, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'المهام الجديدة',
                    data: [1, 2, 3, 1, 3, 2, 2],
                    borderColor: '#C9A769',
                    backgroundColor: 'rgba(201, 167, 105, 0.1)',
                    tension: 0.4,
                    fill: true
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
    
    // Task status chart
    const statusCtx = document.getElementById('taskStatusChart');
    if (statusCtx) {
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: ['قائمة المهام', 'قيد التنفيذ', 'قيد المراجعة', 'مكتملة'],
                datasets: [{
                    data: [5, 3, 2, 8],
                    backgroundColor: [
                        '#6C757D',
                        '#17A2B8',
                        '#FFC107',
                        '#28A745'
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
    loadTodayTasks();
    loadTeamActivity();
    loadNotifications();
}

// Load today's tasks
function loadTodayTasks() {
    const container = document.getElementById('todayTasks');
    if (!container || !window.teamTasks) return;
    
    // Filter tasks for current user that are not done
    const myTasks = window.teamTasks.filter(task => 
        task.assignee === teamMemberData.id && task.status !== 'done'
    ).slice(0, 5); // Show only first 5 tasks
    
    container.innerHTML = myTasks.map(task => `
        <div class="task-item priority-${task.priority}">
            <div class="task-header">
                <h4 class="task-title">${task.title}</h4>
                <span class="task-status status-${task.status}">
                    ${getStatusText(task.status)}
                </span>
            </div>
            <p class="task-description">${task.description}</p>
            <div class="task-meta">
                <div class="task-assignee">
                    <div class="assignee-avatar">${task.assigneeName.charAt(0)}</div>
                    <span>${task.assigneeName}</span>
                </div>
                <span><i class="fas fa-calendar"></i> ${formatDate(task.dueDate)}</span>
            </div>
        </div>
    `).join('');
}

// Load team activity
function loadTeamActivity() {
    const container = document.getElementById('teamActivity');
    if (!container || !window.teamActivities) return;
    
    container.innerHTML = window.teamActivities.map(activity => `
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
            title: 'مهمة جديدة',
            message: 'تم تعيين مهمة جديدة لك: "تحديث قاعدة البيانات"',
            time: 'منذ 30 دقيقة',
            read: false
        },
        {
            title: 'اقتراب موعد التسليم',
            message: 'موعد تسليم مهمة "تصميم واجهة الصفحة الرئيسية" غداً',
            time: 'منذ ساعة',
            read: false
        },
        {
            title: 'تعليق جديد',
            message: 'أضاف أحمد محمد تعليقاً على مهمتك',
            time: 'منذ 2 ساعة',
            read: true
        },
        {
            title: 'اجتماع الفريق',
            message: 'اجتماع الفريق الأسبوعي غداً الساعة 10 صباحاً',
            time: 'منذ 4 ساعات',
            read: true
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

// Initialize Kanban board
function initializeKanban() {
    loadKanbanTasks();
    setupKanbanDragDrop();
}

// Load Kanban tasks
function loadKanbanTasks() {
    if (!window.teamTasks) return;
    
    const todoColumn = document.getElementById('todoColumn');
    const inProgressColumn = document.getElementById('inProgressColumn');
    const reviewColumn = document.getElementById('reviewColumn');
    const doneColumn = document.getElementById('doneColumn');
    
    const columns = {
        'todo': todoColumn,
        'in-progress': inProgressColumn,
        'review': reviewColumn,
        'done': doneColumn
    };
    
    // Clear columns
    Object.values(columns).forEach(column => {
        if (column) column.innerHTML = '';
    });
    
    // Populate columns
    window.teamTasks.forEach(task => {
        const column = columns[task.status];
        if (column) {
            const taskElement = createKanbanTaskElement(task);
            column.appendChild(taskElement);
        }
    });
}

// Create Kanban task element
function createKanbanTaskElement(task) {
    const taskDiv = document.createElement('div');
    taskDiv.className = `kanban-task priority-${task.priority}`;
    taskDiv.draggable = true;
    taskDiv.dataset.taskId = task.id;
    
    taskDiv.innerHTML = `
        <div class="kanban-task-title">${task.title}</div>
        <div class="kanban-task-meta">
            <div class="kanban-task-assignee">
                <div class="assignee-avatar">${task.assigneeName.charAt(0)}</div>
                <span>${task.assigneeName}</span>
            </div>
            <span class="task-due-date">${formatDate(task.dueDate)}</span>
        </div>
    `;
    
    return taskDiv;
}

// Setup Kanban drag and drop
function setupKanbanDragDrop() {
    const columns = document.querySelectorAll('.column-content');
    
    columns.forEach(column => {
        new Sortable(column, {
            group: 'kanban',
            animation: 150,
            ghostClass: 'sortable-ghost',
            onEnd: function(evt) {
                const taskId = evt.item.dataset.taskId;
                const newStatus = evt.to.parentElement.dataset.status;
                updateTaskStatus(taskId, newStatus);
            }
        });
    });
}

// Update task status
function updateTaskStatus(taskId, newStatus) {
    const task = window.teamTasks.find(t => t.id === taskId);
    if (task) {
        task.status = newStatus;
        console.log(`Task ${taskId} moved to ${newStatus}`);
        // Here you would typically send an API request to update the task
    }
}

// Navigation functions
function showDashboard() {
    showSection('dashboardSection');
    setActiveMenuItem(0);
}

function showMyTasks() {
    showSection('tasksSection');
    setActiveMenuItem(2);
    loadMyTasks();
}

function showAllTasks() {
    showSection('tasksSection');
    setActiveMenuItem(3);
    loadAllTasks();
}

function showKanbanBoard() {
    showSection('kanbanSection');
    setActiveMenuItem(4);
    loadKanbanTasks();
}

function showProjects() {
    alert('قريباً... صفحة المشاريع');
}

function showCalendar() {
    alert('قريباً... التقويم');
}

function showTeamMembers() {
    alert('قريباً... أعضاء الفريق');
}

function showReports() {
    alert('قريباً... التقارير');
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

// Load my tasks
function loadMyTasks() {
    if (!window.teamTasks) return;
    
    const myTasks = window.teamTasks.filter(task => task.assignee === teamMemberData.id);
    displayTasksList(myTasks);
}

// Load all tasks
function loadAllTasks() {
    if (!window.teamTasks) return;
    
    displayTasksList(window.teamTasks);
}

// Display tasks list
function displayTasksList(tasks) {
    const container = document.querySelector('#tasksSection .tasks-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="tasks-list">
            ${tasks.map(task => `
                <div class="task-item priority-${task.priority}">
                    <div class="task-header">
                        <h4 class="task-title">${task.title}</h4>
                        <span class="task-status status-${task.status}">
                            ${getStatusText(task.status)}
                        </span>
                    </div>
                    <p class="task-description">${task.description}</p>
                    <div class="task-meta">
                        <div class="task-assignee">
                            <div class="assignee-avatar">${task.assigneeName.charAt(0)}</div>
                            <span>${task.assigneeName}</span>
                        </div>
                        <span><i class="fas fa-calendar"></i> ${formatDate(task.dueDate)}</span>
                        <span><i class="fas fa-folder"></i> ${task.projectName}</span>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Task creation functions
function showCreateTask() {
    const modal = document.getElementById('createTaskModal');
    if (modal) {
        modal.classList.add('active');
    }
}

function closeCreateTask() {
    const modal = document.getElementById('createTaskModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

function createNewTask() {
    const form = document.getElementById('createTaskForm');
    const formData = new FormData(form);
    
    const newTask = {
        id: 'TSK' + String(Date.now()).slice(-3),
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        status: 'todo',
        priority: document.getElementById('taskPriority').value,
        assignee: document.getElementById('taskAssignee').value,
        assigneeName: getAssigneeName(document.getElementById('taskAssignee').value),
        project: document.getElementById('taskProject').value,
        projectName: getProjectName(document.getElementById('taskProject').value),
        dueDate: document.getElementById('taskDueDate').value,
        createdDate: new Date().toISOString().split('T')[0],
        progress: 0
    };
    
    // Add to tasks array
    window.teamTasks.push(newTask);
    
    // Refresh current view
    if (currentSection === 'dashboard') {
        loadTodayTasks();
    } else if (currentSection === 'kanban') {
        loadKanbanTasks();
    }
    
    // Close modal and reset form
    closeCreateTask();
    form.reset();
    
    alert('تم إنشاء المهمة بنجاح!');
}

// Filter tasks
function filterTasks(searchTerm) {
    if (!window.teamTasks) return;
    
    const filteredTasks = window.teamTasks.filter(task =>
        task.title.toLowerCase().includes(searchTerm) ||
        task.description.toLowerCase().includes(searchTerm) ||
        task.assigneeName.toLowerCase().includes(searchTerm)
    );
    
    // Update current view with filtered tasks
    if (currentSection === 'tasks') {
        displayTasksList(filteredTasks);
    }
}

// Utility functions
function getStatusText(status) {
    const statusMap = {
        'todo': 'قائمة المهام',
        'in-progress': 'قيد التنفيذ',
        'review': 'قيد المراجعة',
        'done': 'مكتملة'
    };
    return statusMap[status] || status;
}

function getActivityIcon(type) {
    const iconMap = {
        'task': 'fa-tasks',
        'project': 'fa-project-diagram',
        'comment': 'fa-comment'
    };
    return iconMap[type] || 'fa-circle';
}

function getAssigneeName(assigneeId) {
    const assigneeMap = {
        'TM001': 'أحمد محمد',
        'TM002': 'فاطمة علي',
        'TM003': 'محمد سالم',
        'TM004': 'سارة أحمد'
    };
    return assigneeMap[assigneeId] || 'غير محدد';
}

function getProjectName(projectId) {
    const projectMap = {
        'project1': 'مشروع التسويق الرقمي',
        'project2': 'تطوير الموقع',
        'project3': 'تصميم الهوية'
    };
    return projectMap[projectId] || 'مشروع غير محدد';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-SA');
}

