/**
 * عميل API للتفاعل مع الخادم
 * يوفر وظائف للمصادقة وإدارة البيانات
 */

class APIClient {
    constructor() {
        this.baseURL = '/api';
        this.token = localStorage.getItem('auth_token');
        this.user = JSON.parse(localStorage.getItem('user_data') || 'null');
        this.profile = JSON.parse(localStorage.getItem('user_profile') || 'null');
    }

    /**
     * إعداد headers للطلبات
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (this.token) {
            headers['Authorization'] = `Token ${this.token}`;
        }

        // إضافة CSRF token إذا كان متوفراً
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken.value;
        }

        return headers;
    }

    /**
     * إرسال طلب HTTP
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    /**
     * تسجيل الدخول
     */
    async login(username, password) {
        try {
            const response = await this.request('/auth/login/', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });

            if (response.success) {
                this.token = response.token;
                this.user = response.user;
                this.profile = response.profile;

                // حفظ البيانات في localStorage
                localStorage.setItem('auth_token', this.token);
                localStorage.setItem('user_data', JSON.stringify(this.user));
                localStorage.setItem('user_profile', JSON.stringify(this.profile));

                return response;
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            console.error('Login Error:', error);
            throw error;
        }
    }

    /**
     * تسجيل الخروج
     */
    async logout() {
        try {
            await this.request('/auth/logout/', {
                method: 'POST'
            });
        } catch (error) {
            console.error('Logout Error:', error);
        } finally {
            // مسح البيانات المحلية
            this.token = null;
            this.user = null;
            this.profile = null;
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_data');
            localStorage.removeItem('user_profile');
        }
    }

    /**
     * التحقق من حالة تسجيل الدخول
     */
    isAuthenticated() {
        return !!this.token && !!this.user;
    }

    /**
     * الحصول على إحصائيات لوحة القيادة
     */
    async getDashboardStats() {
        return await this.request('/dashboard/stats/');
    }

    /**
     * الحصول على تقدم المشاريع
     */
    async getProjectProgress() {
        return await this.request('/dashboard/project-progress/');
    }

    /**
     * الحصول على ملخص المهام
     */
    async getTaskSummary() {
        return await this.request('/dashboard/task-summary/');
    }

    /**
     * الحصول على نشاط المستخدمين
     */
    async getUserActivity() {
        return await this.request('/dashboard/user-activity/');
    }

    /**
     * الحصول على قائمة المشاريع
     */
    async getProjects(page = 1, filters = {}) {
        const params = new URLSearchParams({ page, ...filters });
        return await this.request(`/projects/?${params}`);
    }

    /**
     * الحصول على تفاصيل مشروع
     */
    async getProject(projectId) {
        return await this.request(`/projects/${projectId}/`);
    }

    /**
     * إنشاء مشروع جديد
     */
    async createProject(projectData) {
        return await this.request('/projects/', {
            method: 'POST',
            body: JSON.stringify(projectData)
        });
    }

    /**
     * تحديث مشروع
     */
    async updateProject(projectId, projectData) {
        return await this.request(`/projects/${projectId}/`, {
            method: 'PUT',
            body: JSON.stringify(projectData)
        });
    }

    /**
     * حذف مشروع
     */
    async deleteProject(projectId) {
        return await this.request(`/projects/${projectId}/`, {
            method: 'DELETE'
        });
    }

    /**
     * الحصول على قائمة المهام
     */
    async getTasks(page = 1, filters = {}) {
        const params = new URLSearchParams({ page, ...filters });
        return await this.request(`/tasks/?${params}`);
    }

    /**
     * الحصول على تفاصيل مهمة
     */
    async getTask(taskId) {
        return await this.request(`/tasks/${taskId}/`);
    }

    /**
     * إنشاء مهمة جديدة
     */
    async createTask(taskData) {
        return await this.request('/tasks/', {
            method: 'POST',
            body: JSON.stringify(taskData)
        });
    }

    /**
     * تحديث مهمة
     */
    async updateTask(taskId, taskData) {
        return await this.request(`/tasks/${taskId}/`, {
            method: 'PUT',
            body: JSON.stringify(taskData)
        });
    }

    /**
     * حذف مهمة
     */
    async deleteTask(taskId) {
        return await this.request(`/tasks/${taskId}/`, {
            method: 'DELETE'
        });
    }

    /**
     * الحصول على الإشعارات
     */
    async getNotifications(page = 1) {
        return await this.request(`/notifications/?page=${page}`);
    }

    /**
     * تحديد إشعار كمقروء
     */
    async markNotificationRead(notificationId) {
        return await this.request(`/notifications/${notificationId}/mark-read/`, {
            method: 'POST'
        });
    }

    /**
     * تحديد جميع الإشعارات كمقروءة
     */
    async markAllNotificationsRead() {
        return await this.request('/notifications/mark-all-read/', {
            method: 'POST'
        });
    }

    /**
     * البحث في النظام
     */
    async search(query) {
        const params = new URLSearchParams({ q: query });
        return await this.request(`/search/?${params}`);
    }

    /**
     * إرسال نموذج من الموقع
     */
    async submitForm(formType, formData) {
        return await this.request('/forms/submit/', {
            method: 'POST',
            body: JSON.stringify({
                form_type: formType,
                form_data: formData
            })
        });
    }

    /**
     * إرسال رسالة تواصل
     */
    async submitContactMessage(messageData) {
        return await this.request('/contact/submit/', {
            method: 'POST',
            body: JSON.stringify(messageData)
        });
    }
}

// إنشاء instance عام من APIClient
const apiClient = new APIClient();

// تصدير للاستخدام في ملفات أخرى
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}

