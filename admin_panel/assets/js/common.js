// ملف JavaScript الرئيسي للوحة التحكم
// Common JavaScript functions for Admin Panel

// إعدادات API
const API_BASE_URL = 'http://localhost:8000/api';
const CSRF_TOKEN = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

// إعدادات الطلبات
const defaultHeaders = {
    'Content-Type': 'application/json',
    'X-CSRFToken': CSRF_TOKEN || '',
};

// دالة لإرسال طلبات API
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: defaultHeaders,
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        showNotification('حدث خطأ في الاتصال بالخادم', 'error');
        throw error;
    }
}

// دالة لعرض الإشعارات
function showNotification(message, type = 'info', duration = 5000) {
    // إنشاء عنصر الإشعار
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;

    // إضافة الإشعار إلى الصفحة
    const container = document.getElementById('notifications-container') || createNotificationsContainer();
    container.appendChild(notification);

    // إزالة الإشعار تلقائياً
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, duration);
}

// إنشاء حاوية الإشعارات
function createNotificationsContainer() {
    const container = document.createElement('div');
    container.id = 'notifications-container';
    container.className = 'notifications-container';
    document.body.appendChild(container);
    return container;
}

// دالة لتحديث الإحصائيات في لوحة القيادة
async function updateDashboardStats() {
    try {
        // جلب إحصائيات الصفحات
        const pagesData = await apiRequest('/pages/');
        document.getElementById('total-pages').textContent = pagesData.count || pagesData.length || 0;

        // جلب إحصائيات المقالات
        const postsData = await apiRequest('/blog-posts/');
        document.getElementById('total-posts').textContent = postsData.count || postsData.length || 0;

        // جلب إحصائيات الرسائل
        const messagesData = await apiRequest('/contact-messages/');
        document.getElementById('total-messages').textContent = messagesData.count || messagesData.length || 0;

        // جلب إحصائيات الزوار (إذا كانت متوفرة)
        try {
            const visitorsData = await apiRequest('/visitor-analytics/');
            document.getElementById('total-visitors').textContent = visitorsData.count || visitorsData.length || 0;
        } catch (error) {
            document.getElementById('total-visitors').textContent = '0';
        }

    } catch (error) {
        console.error('Error updating dashboard stats:', error);
    }
}

// دالة لتحديث الرسم البياني
function updateChart(chartId, data, labels) {
    const ctx = document.getElementById(chartId);
    if (!ctx) return;

    // إنشاء رسم بياني بسيط باستخدام Canvas
    const canvas = ctx.getContext('2d');
    const width = ctx.width;
    const height = ctx.height;

    // مسح الرسم السابق
    canvas.clearRect(0, 0, width, height);

    // رسم الخلفية
    canvas.fillStyle = '#f8f9fa';
    canvas.fillRect(0, 0, width, height);

    // رسم البيانات
    if (data && data.length > 0) {
        const maxValue = Math.max(...data);
        const barWidth = width / data.length;
        
        data.forEach((value, index) => {
            const barHeight = (value / maxValue) * (height - 40);
            const x = index * barWidth;
            const y = height - barHeight - 20;

            // رسم العمود
            canvas.fillStyle = '#007bff';
            canvas.fillRect(x + 5, y, barWidth - 10, barHeight);

            // رسم القيمة
            canvas.fillStyle = '#333';
            canvas.font = '12px Arial';
            canvas.textAlign = 'center';
            canvas.fillText(value, x + barWidth / 2, y - 5);
        });
    }
}

// دالة لتحديث قائمة الأنشطة الأخيرة
async function updateRecentActivities() {
    try {
        const activities = [];

        // جلب آخر الصفحات المحدثة
        const pagesData = await apiRequest('/pages/?ordering=-updated_at&limit=3');
        const pages = pagesData.results || pagesData.slice(0, 3) || [];
        pages.forEach(page => {
            activities.push({
                type: 'page',
                title: `تم تحديث صفحة: ${page.title}`,
                time: formatDate(page.updated_at),
                icon: '📄'
            });
        });

        // جلب آخر المقالات
        const postsData = await apiRequest('/blog-posts/?ordering=-created_at&limit=3');
        const posts = postsData.results || postsData.slice(0, 3) || [];
        posts.forEach(post => {
            activities.push({
                type: 'post',
                title: `تم إنشاء مقال: ${post.title}`,
                time: formatDate(post.created_at),
                icon: '📝'
            });
        });

        // ترتيب الأنشطة حسب التاريخ
        activities.sort((a, b) => new Date(b.time) - new Date(a.time));

        // عرض الأنشطة
        const activitiesContainer = document.getElementById('recent-activities');
        if (activitiesContainer) {
            activitiesContainer.innerHTML = activities.slice(0, 5).map(activity => `
                <div class="activity-item">
                    <span class="activity-icon">${activity.icon}</span>
                    <div class="activity-content">
                        <div class="activity-title">${activity.title}</div>
                        <div class="activity-time">${activity.time}</div>
                    </div>
                </div>
            `).join('');
        }

    } catch (error) {
        console.error('Error updating recent activities:', error);
    }
}

// دالة لتنسيق التاريخ
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) {
        return 'أمس';
    } else if (diffDays < 7) {
        return `منذ ${diffDays} أيام`;
    } else {
        return date.toLocaleDateString('ar-SA');
    }
}

// دالة لتبديل الشريط الجانبي
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    
    if (sidebar && mainContent) {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
    }
}

// دالة لتسجيل الخروج
function logout() {
    if (confirm('هل أنت متأكد من تسجيل الخروج؟')) {
        localStorage.removeItem('admin_token');
        sessionStorage.clear();
        window.location.href = '/admin_panel/index.html';
    }
}

// دالة لتحديث الملف الشخصي
function updateProfile() {
    // يمكن تطوير هذه الدالة لاحقاً
    showNotification('سيتم إضافة هذه الميزة قريباً', 'info');
}

// دالة لتحديث كلمة المرور
function changePassword() {
    const newPassword = prompt('أدخل كلمة المرور الجديدة:');
    if (newPassword && newPassword.length >= 6) {
        // حفظ كلمة المرور الجديدة في التخزين المحلي
        localStorage.setItem('admin_password', newPassword);
        showNotification('تم تحديث كلمة المرور بنجاح', 'success');
    } else if (newPassword) {
        showNotification('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error');
    }
}

// دالة لتحديث إعدادات الموقع
async function updateSiteSettings() {
    try {
        const settingsData = await apiRequest('/site-settings/');
        const settings = settingsData.results?.[0] || settingsData[0];
        
        if (settings) {
            // عرض نموذج تحديث الإعدادات
            const modal = createSettingsModal(settings);
            document.body.appendChild(modal);
        }
    } catch (error) {
        console.error('Error loading site settings:', error);
    }
}

// دالة لإنشاء نموذج إعدادات الموقع
function createSettingsModal(settings) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>إعدادات الموقع</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
            </div>
            <div class="modal-body">
                <form id="settings-form">
                    <div class="form-group">
                        <label>اسم الموقع</label>
                        <input type="text" name="site_name" value="${settings.site_name || ''}" required>
                    </div>
                    <div class="form-group">
                        <label>وصف الموقع</label>
                        <textarea name="site_description" rows="3">${settings.site_description || ''}</textarea>
                    </div>
                    <div class="form-group">
                        <label>البريد الإلكتروني</label>
                        <input type="email" name="contact_email" value="${settings.contact_email || ''}">
                    </div>
                    <div class="form-group">
                        <label>رقم الهاتف</label>
                        <input type="tel" name="contact_phone" value="${settings.contact_phone || ''}">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">إلغاء</button>
                <button type="button" class="btn btn-primary" onclick="saveSettings(${settings.id})">حفظ</button>
            </div>
        </div>
    `;
    return modal;
}

// دالة لحفظ إعدادات الموقع
async function saveSettings(settingsId) {
    const form = document.getElementById('settings-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        await apiRequest(`/site-settings/${settingsId}/`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
        
        showNotification('تم حفظ الإعدادات بنجاح', 'success');
        document.querySelector('.modal').remove();
    } catch (error) {
        showNotification('حدث خطأ في حفظ الإعدادات', 'error');
    }
}

// دالة لتحديث البيانات عند تحميل الصفحة
function initializeDashboard() {
    // تحديث الإحصائيات
    updateDashboardStats();
    
    // تحديث الأنشطة الأخيرة
    updateRecentActivities();
    
    // تحديث الرسوم البيانية
    const sampleData = [12, 19, 3, 5, 2, 3, 7];
    updateChart('visitors-chart', sampleData);
    
    // تحديث البيانات كل 5 دقائق
    setInterval(() => {
        updateDashboardStats();
        updateRecentActivities();
    }, 300000);
}

// تشغيل الدوال عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // التحقق من تسجيل الدخول
    const isLoggedIn = localStorage.getItem('admin_token') || sessionStorage.getItem('admin_logged_in');
    
    if (!isLoggedIn && !window.location.pathname.includes('index.html')) {
        window.location.href = '/admin_panel/index.html';
        return;
    }
    
    // تهيئة لوحة القيادة إذا كانت الصفحة الحالية هي لوحة القيادة
    if (window.location.pathname.includes('dashboard.html')) {
        initializeDashboard();
    }
    
    // إضافة مستمعي الأحداث للقائمة الجانبية
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    // إضافة مستمعي الأحداث للقوائم المنسدلة
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const dropdown = this.nextElementSibling;
            if (dropdown) {
                dropdown.classList.toggle('show');
            }
        });
    });
    
    // إغلاق القوائم المنسدلة عند النقر خارجها
    document.addEventListener('click', function(e) {
        if (!e.target.matches('.dropdown-toggle')) {
            const dropdowns = document.querySelectorAll('.dropdown-menu.show');
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    });
});

// دوال مساعدة للتحقق من صحة البيانات
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[\+]?[1-9][\d]{0,15}$/;
    return re.test(phone);
}

function validateRequired(value) {
    return value && value.trim().length > 0;
}

// دالة لتنسيق الأرقام
function formatNumber(num) {
    return new Intl.NumberFormat('ar-SA').format(num);
}

// دالة لتحويل النص إلى slug
function slugify(text) {
    return text
        .toString()
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '-')
        .replace(/[^\w\-]+/g, '')
        .replace(/\-\-+/g, '-')
        .replace(/^-+/, '')
        .replace(/-+$/, '');
}

// تصدير الدوال للاستخدام في ملفات أخرى
window.adminPanel = {
    apiRequest,
    showNotification,
    updateDashboardStats,
    updateChart,
    updateRecentActivities,
    toggleSidebar,
    logout,
    updateProfile,
    changePassword,
    updateSiteSettings,
    validateEmail,
    validatePhone,
    validateRequired,
    formatNumber,
    slugify
};

