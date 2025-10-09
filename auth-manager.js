/**
 * مدير المصادقة
 * يتعامل مع تسجيل الدخول والخروج وإدارة الجلسات
 */

class AuthManager {
    constructor() {
        this.apiClient = apiClient;
        this.loginForm = null;
        this.init();
    }

    /**
     * تهيئة مدير المصادقة
     */
    init() {
        this.setupLoginForm();
        this.checkAuthStatus();
        this.setupLogoutHandlers();
    }

    /**
     * إعداد نموذج تسجيل الدخول
     */
    setupLoginForm() {
        this.loginForm = document.getElementById('loginForm');
        if (this.loginForm) {
            this.loginForm.addEventListener('submit', this.handleLogin.bind(this));
        }
    }

    /**
     * معالجة تسجيل الدخول
     */
    async handleLogin(event) {
        event.preventDefault();
        
        const formData = new FormData(this.loginForm);
        const username = formData.get('username');
        const password = formData.get('password');
        const rememberMe = formData.get('remember_me');

        // إظهار مؤشر التحميل
        this.showLoginLoading(true);
        this.clearLoginErrors();

        try {
            const response = await this.apiClient.login(username, password);
            
            if (response.success) {
                // حفظ خيار "تذكرني"
                if (rememberMe) {
                    localStorage.setItem('remember_me', 'true');
                } else {
                    localStorage.removeItem('remember_me');
                }

                // إظهار رسالة نجاح
                this.showLoginSuccess('تم تسجيل الدخول بنجاح');
                
                // إعادة توجيه إلى لوحة القيادة
                setTimeout(() => {
                    window.location.href = '/admin-panel/pages/dashboard/dashboard.html';
                }, 1500);
            }
        } catch (error) {
            this.showLoginError(error.message || 'خطأ في تسجيل الدخول');
        } finally {
            this.showLoginLoading(false);
        }
    }

    /**
     * إظهار/إخفاء مؤشر التحميل
     */
    showLoginLoading(show) {
        const submitBtn = this.loginForm?.querySelector('button[type="submit"]');
        const loadingSpinner = this.loginForm?.querySelector('.loading-spinner');
        
        if (submitBtn) {
            submitBtn.disabled = show;
            submitBtn.textContent = show ? 'جاري تسجيل الدخول...' : 'تسجيل الدخول';
        }
        
        if (loadingSpinner) {
            loadingSpinner.style.display = show ? 'block' : 'none';
        }
    }

    /**
     * إظهار رسالة خطأ
     */
    showLoginError(message) {
        this.clearLoginMessages();
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
        `;
        
        const form = this.loginForm || document.querySelector('.login-form');
        if (form) {
            form.insertBefore(errorDiv, form.firstChild);
        }
    }

    /**
     * إظهار رسالة نجاح
     */
    showLoginSuccess(message) {
        this.clearLoginMessages();
        
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success';
        successDiv.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        
        const form = this.loginForm || document.querySelector('.login-form');
        if (form) {
            form.insertBefore(successDiv, form.firstChild);
        }
    }

    /**
     * مسح رسائل الخطأ والنجاح
     */
    clearLoginMessages() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => alert.remove());
    }

    /**
     * مسح أخطاء تسجيل الدخول
     */
    clearLoginErrors() {
        const errorAlerts = document.querySelectorAll('.alert-error');
        errorAlerts.forEach(alert => alert.remove());
    }

    /**
     * التحقق من حالة المصادقة
     */
    checkAuthStatus() {
        if (this.apiClient.isAuthenticated()) {
            // المستخدم مسجل دخول
            this.handleAuthenticatedUser();
        } else {
            // المستخدم غير مسجل دخول
            this.handleUnauthenticatedUser();
        }
    }

    /**
     * معالجة المستخدم المصادق
     */
    handleAuthenticatedUser() {
        // إذا كان في صفحة تسجيل الدخول، إعادة توجيه إلى لوحة القيادة
        if (window.location.pathname.includes('index.html') || 
            window.location.pathname.endsWith('/admin-panel/')) {
            window.location.href = '/admin-panel/pages/dashboard/dashboard.html';
            return;
        }

        // تحديث واجهة المستخدم
        this.updateUserInterface();
        this.loadUserData();
    }

    /**
     * معالجة المستخدم غير المصادق
     */
    handleUnauthenticatedUser() {
        // إذا لم يكن في صفحة تسجيل الدخول، إعادة توجيه إليها
        if (!window.location.pathname.includes('index.html') && 
            !window.location.pathname.endsWith('/admin-panel/')) {
            window.location.href = '/admin-panel/index.html';
            return;
        }
    }

    /**
     * تحديث واجهة المستخدم للمستخدم المصادق
     */
    updateUserInterface() {
        const user = this.apiClient.user;
        const profile = this.apiClient.profile;
        
        // تحديث اسم المستخدم في الهيدر
        const userNameElements = document.querySelectorAll('.user-name');
        userNameElements.forEach(element => {
            element.textContent = user?.first_name && user?.last_name 
                ? `${user.first_name} ${user.last_name}`
                : user?.username || 'مستخدم';
        });

        // تحديث البريد الإلكتروني
        const userEmailElements = document.querySelectorAll('.user-email');
        userEmailElements.forEach(element => {
            element.textContent = user?.email || '';
        });

        // تحديث الصورة الشخصية
        const userAvatarElements = document.querySelectorAll('.user-avatar');
        userAvatarElements.forEach(element => {
            if (profile?.avatar) {
                element.src = profile.avatar;
            } else {
                element.src = '/admin-panel/assets/images/default-avatar.png';
            }
        });

        // تحديث نوع المستخدم
        const userTypeElements = document.querySelectorAll('.user-type');
        userTypeElements.forEach(element => {
            element.textContent = profile?.user_type || 'مستخدم';
        });
    }

    /**
     * تحميل بيانات المستخدم من الخادم
     */
    async loadUserData() {
        try {
            const response = await this.apiClient.request('/auth/profile/');
            if (response.success) {
                this.apiClient.profile = response.profile;
                localStorage.setItem('user_profile', JSON.stringify(response.profile));
                this.updateUserInterface();
            }
        } catch (error) {
            console.error('Error loading user data:', error);
        }
    }

    /**
     * إعداد معالجات تسجيل الخروج
     */
    setupLogoutHandlers() {
        const logoutButtons = document.querySelectorAll('.logout-btn, [data-action="logout"]');
        logoutButtons.forEach(button => {
            button.addEventListener('click', this.handleLogout.bind(this));
        });
    }

    /**
     * معالجة تسجيل الخروج
     */
    async handleLogout(event) {
        event.preventDefault();
        
        // إظهار تأكيد
        if (!confirm('هل أنت متأكد من تسجيل الخروج؟')) {
            return;
        }

        try {
            await this.apiClient.logout();
            
            // إظهار رسالة نجاح
            this.showLogoutMessage('تم تسجيل الخروج بنجاح');
            
            // إعادة توجيه إلى صفحة تسجيل الدخول
            setTimeout(() => {
                window.location.href = '/admin-panel/index.html';
            }, 1500);
        } catch (error) {
            console.error('Logout error:', error);
            // حتى لو فشل الطلب، قم بتسجيل الخروج محلياً
            this.apiClient.logout();
            window.location.href = '/admin-panel/index.html';
        }
    }

    /**
     * إظهار رسالة تسجيل الخروج
     */
    showLogoutMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'logout-message';
        messageDiv.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(messageDiv);
        
        // إزالة الرسالة بعد 3 ثوان
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }

    /**
     * التحقق من انتهاء صلاحية الجلسة
     */
    checkSessionExpiry() {
        // يمكن تطوير هذه الوظيفة لاحقاً للتحقق من انتهاء صلاحية token
        setInterval(async () => {
            if (this.apiClient.isAuthenticated()) {
                try {
                    await this.apiClient.request('/auth/profile/');
                } catch (error) {
                    if (error.message.includes('401') || error.message.includes('403')) {
                        // انتهت صلاحية الجلسة
                        this.handleSessionExpiry();
                    }
                }
            }
        }, 300000); // كل 5 دقائق
    }

    /**
     * معالجة انتهاء صلاحية الجلسة
     */
    handleSessionExpiry() {
        alert('انتهت صلاحية جلستك. يرجى تسجيل الدخول مرة أخرى.');
        this.apiClient.logout();
        window.location.href = '/admin-panel/index.html';
    }
}

// تهيئة مدير المصادقة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    window.authManager = new AuthManager();
});

// تصدير للاستخدام في ملفات أخرى
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthManager;
}

