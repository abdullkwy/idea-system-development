/**
 * مدير الإشعارات
 * يتعامل مع الإشعارات في الوقت الفعلي وإدارة العرض
 */

class NotificationsManager {
    constructor() {
        this.apiClient = apiClient;
        this.notifications = [];
        this.unreadCount = 0;
        this.isDropdownOpen = false;
        this.refreshInterval = null;
        this.init();
    }

    /**
     * تهيئة مدير الإشعارات
     */
    init() {
        this.setupNotificationElements();
        this.loadNotifications();
        this.startAutoRefresh();
        this.setupEventListeners();
    }

    /**
     * إعداد عناصر الإشعارات في DOM
     */
    setupNotificationElements() {
        this.notificationBell = document.getElementById('notificationsDropdown');
        this.notificationBadge = document.getElementById('notificationCount');
        this.notificationsList = document.getElementById('notificationsList');
        this.markAllReadBtn = document.querySelector('.mark-all-read');
        
        if (!this.notificationBell) {
            console.warn('Notification elements not found in DOM');
            return;
        }
    }

    /**
     * إعداد مستمعي الأحداث
     */
    setupEventListeners() {
        // فتح/إغلاق قائمة الإشعارات
        if (this.notificationBell) {
            this.notificationBell.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleNotificationsDropdown();
            });
        }

        // تحديد جميع الإشعارات كمقروءة
        if (this.markAllReadBtn) {
            this.markAllReadBtn.addEventListener('click', () => {
                this.markAllNotificationsRead();
            });
        }

        // إغلاق القائمة عند النقر خارجها
        document.addEventListener('click', (e) => {
            if (this.isDropdownOpen && !this.notificationBell?.contains(e.target)) {
                this.closeNotificationsDropdown();
            }
        });

        // تحديث الإشعارات عند التركيز على النافذة
        window.addEventListener('focus', () => {
            this.loadNotifications();
        });
    }

    /**
     * تحميل الإشعارات من الخادم
     */
    async loadNotifications() {
        if (!this.apiClient.isAuthenticated()) {
            return;
        }

        try {
            const response = await this.apiClient.getNotifications();
            if (response.success) {
                this.notifications = response.results || [];
                this.updateNotificationUI();
            }
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    /**
     * تحديث واجهة الإشعارات
     */
    updateNotificationUI() {
        this.updateNotificationBadge();
        this.renderNotificationsList();
    }

    /**
     * تحديث شارة عدد الإشعارات
     */
    updateNotificationBadge() {
        this.unreadCount = this.notifications.filter(n => !n.is_read).length;
        
        if (this.notificationBadge) {
            if (this.unreadCount > 0) {
                this.notificationBadge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                this.notificationBadge.style.display = 'block';
                this.notificationBadge.classList.add('pulse');
            } else {
                this.notificationBadge.style.display = 'none';
                this.notificationBadge.classList.remove('pulse');
            }
        }
    }

    /**
     * عرض قائمة الإشعارات
     */
    renderNotificationsList() {
        if (!this.notificationsList) {
            return;
        }

        if (this.notifications.length === 0) {
            this.notificationsList.innerHTML = `
                <div class="no-notifications">
                    <i class="fas fa-bell-slash"></i>
                    <p>لا توجد إشعارات</p>
                </div>
            `;
            return;
        }

        const notificationsHTML = this.notifications.slice(0, 10).map(notification => {
            return this.createNotificationHTML(notification);
        }).join('');

        this.notificationsList.innerHTML = notificationsHTML;

        // إضافة مستمعي الأحداث للإشعارات
        this.setupNotificationItemListeners();
    }

    /**
     * إنشاء HTML لإشعار واحد
     */
    createNotificationHTML(notification) {
        const timeAgo = this.getTimeAgo(notification.created_at);
        const isUnread = !notification.is_read;
        
        return `
            <div class="notification-item ${isUnread ? 'unread' : ''}" 
                 data-notification-id="${notification.id}">
                <div class="notification-icon">
                    ${this.getNotificationIcon(notification.notification_type)}
                </div>
                <div class="notification-content">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.message}</div>
                    <div class="notification-meta">
                        <span class="notification-time">${timeAgo}</span>
                        ${notification.sender_name ? `<span class="notification-sender">من: ${notification.sender_name}</span>` : ''}
                    </div>
                </div>
                <div class="notification-actions">
                    ${isUnread ? '<button class="mark-read-btn" title="تحديد كمقروء"><i class="fas fa-check"></i></button>' : ''}
                    <button class="delete-notification-btn" title="حذف"><i class="fas fa-times"></i></button>
                </div>
            </div>
        `;
    }

    /**
     * الحصول على أيقونة الإشعار حسب النوع
     */
    getNotificationIcon(type) {
        const icons = {
            'task_assigned': '<i class="fas fa-tasks text-blue"></i>',
            'task_completed': '<i class="fas fa-check-circle text-green"></i>',
            'project_update': '<i class="fas fa-project-diagram text-purple"></i>',
            'deadline_reminder': '<i class="fas fa-clock text-orange"></i>',
            'system_alert': '<i class="fas fa-exclamation-triangle text-red"></i>',
            'message_received': '<i class="fas fa-envelope text-blue"></i>'
        };
        
        return icons[type] || '<i class="fas fa-bell text-gray"></i>';
    }

    /**
     * حساب الوقت المنقضي
     */
    getTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) {
            return 'الآن';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `منذ ${minutes} دقيقة`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `منذ ${hours} ساعة`;
        } else {
            const days = Math.floor(diffInSeconds / 86400);
            return `منذ ${days} يوم`;
        }
    }

    /**
     * إعداد مستمعي الأحداث لعناصر الإشعارات
     */
    setupNotificationItemListeners() {
        // أزرار تحديد كمقروء
        const markReadButtons = this.notificationsList.querySelectorAll('.mark-read-btn');
        markReadButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const notificationId = btn.closest('.notification-item').dataset.notificationId;
                this.markNotificationRead(notificationId);
            });
        });

        // أزرار الحذف
        const deleteButtons = this.notificationsList.querySelectorAll('.delete-notification-btn');
        deleteButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const notificationId = btn.closest('.notification-item').dataset.notificationId;
                this.deleteNotification(notificationId);
            });
        });

        // النقر على الإشعار نفسه
        const notificationItems = this.notificationsList.querySelectorAll('.notification-item');
        notificationItems.forEach(item => {
            item.addEventListener('click', () => {
                const notificationId = item.dataset.notificationId;
                this.handleNotificationClick(notificationId);
            });
        });
    }

    /**
     * فتح/إغلاق قائمة الإشعارات
     */
    toggleNotificationsDropdown() {
        if (this.isDropdownOpen) {
            this.closeNotificationsDropdown();
        } else {
            this.openNotificationsDropdown();
        }
    }

    /**
     * فتح قائمة الإشعارات
     */
    openNotificationsDropdown() {
        if (!this.notificationBell) return;
        
        const dropdown = this.notificationBell.querySelector('.dropdown-menu');
        if (dropdown) {
            dropdown.classList.add('show');
            this.isDropdownOpen = true;
            
            // تحميل الإشعارات الجديدة
            this.loadNotifications();
        }
    }

    /**
     * إغلاق قائمة الإشعارات
     */
    closeNotificationsDropdown() {
        if (!this.notificationBell) return;
        
        const dropdown = this.notificationBell.querySelector('.dropdown-menu');
        if (dropdown) {
            dropdown.classList.remove('show');
            this.isDropdownOpen = false;
        }
    }

    /**
     * تحديد إشعار كمقروء
     */
    async markNotificationRead(notificationId) {
        try {
            const response = await this.apiClient.markNotificationRead(notificationId);
            if (response.success) {
                // تحديث الإشعار محلياً
                const notification = this.notifications.find(n => n.id == notificationId);
                if (notification) {
                    notification.is_read = true;
                }
                this.updateNotificationUI();
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    /**
     * تحديد جميع الإشعارات كمقروءة
     */
    async markAllNotificationsRead() {
        try {
            const response = await this.apiClient.markAllNotificationsRead();
            if (response.success) {
                // تحديث جميع الإشعارات محلياً
                this.notifications.forEach(notification => {
                    notification.is_read = true;
                });
                this.updateNotificationUI();
                
                // إظهار رسالة نجاح
                this.showNotificationMessage('تم تحديد جميع الإشعارات كمقروءة', 'success');
            }
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
            this.showNotificationMessage('خطأ في تحديث الإشعارات', 'error');
        }
    }

    /**
     * حذف إشعار
     */
    async deleteNotification(notificationId) {
        if (!confirm('هل أنت متأكد من حذف هذا الإشعار؟')) {
            return;
        }

        try {
            // حذف الإشعار محلياً (يمكن إضافة API للحذف لاحقاً)
            this.notifications = this.notifications.filter(n => n.id != notificationId);
            this.updateNotificationUI();
            
            this.showNotificationMessage('تم حذف الإشعار', 'success');
        } catch (error) {
            console.error('Error deleting notification:', error);
            this.showNotificationMessage('خطأ في حذف الإشعار', 'error');
        }
    }

    /**
     * معالجة النقر على إشعار
     */
    async handleNotificationClick(notificationId) {
        const notification = this.notifications.find(n => n.id == notificationId);
        if (!notification) return;

        // تحديد الإشعار كمقروء إذا لم يكن مقروءاً
        if (!notification.is_read) {
            await this.markNotificationRead(notificationId);
        }

        // التنقل إلى الصفحة المرتبطة
        if (notification.related_project) {
            window.location.href = `/admin-panel/pages/projects/project-detail.html?id=${notification.related_project}`;
        } else if (notification.related_task) {
            window.location.href = `/admin-panel/pages/tasks/task-detail.html?id=${notification.related_task}`;
        }

        // إغلاق القائمة
        this.closeNotificationsDropdown();
    }

    /**
     * بدء التحديث التلقائي
     */
    startAutoRefresh() {
        // تحديث كل 30 ثانية
        this.refreshInterval = setInterval(() => {
            if (this.apiClient.isAuthenticated()) {
                this.loadNotifications();
            }
        }, 30000);
    }

    /**
     * إيقاف التحديث التلقائي
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    /**
     * إضافة إشعار جديد (للاستخدام مع WebSocket لاحقاً)
     */
    addNewNotification(notification) {
        this.notifications.unshift(notification);
        this.updateNotificationUI();
        
        // إظهار إشعار منبثق
        this.showPopupNotification(notification);
        
        // تشغيل صوت الإشعار
        this.playNotificationSound();
    }

    /**
     * إظهار إشعار منبثق
     */
    showPopupNotification(notification) {
        // إنشاء عنصر الإشعار المنبثق
        const popup = document.createElement('div');
        popup.className = 'notification-popup';
        popup.innerHTML = `
            <div class="popup-content">
                <div class="popup-icon">
                    ${this.getNotificationIcon(notification.notification_type)}
                </div>
                <div class="popup-text">
                    <div class="popup-title">${notification.title}</div>
                    <div class="popup-message">${notification.message}</div>
                </div>
                <button class="popup-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // إضافة إلى الصفحة
        document.body.appendChild(popup);

        // إضافة مستمع لإغلاق الإشعار
        const closeBtn = popup.querySelector('.popup-close');
        closeBtn.addEventListener('click', () => {
            popup.remove();
        });

        // إزالة تلقائية بعد 5 ثوان
        setTimeout(() => {
            if (popup.parentNode) {
                popup.remove();
            }
        }, 5000);

        // إضافة تأثير الظهور
        setTimeout(() => {
            popup.classList.add('show');
        }, 100);
    }

    /**
     * تشغيل صوت الإشعار
     */
    playNotificationSound() {
        try {
            const audio = new Audio('/admin-panel/assets/sounds/notification.mp3');
            audio.volume = 0.3;
            audio.play().catch(e => {
                // تجاهل أخطاء تشغيل الصوت
                console.log('Could not play notification sound:', e);
            });
        } catch (error) {
            // تجاهل أخطاء إنشاء الصوت
        }
    }

    /**
     * إظهار رسالة إشعار
     */
    showNotificationMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `notification-message ${type}`;
        messageDiv.textContent = message;
        
        document.body.appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }

    /**
     * تنظيف الموارد
     */
    destroy() {
        this.stopAutoRefresh();
        // إزالة مستمعي الأحداث إذا لزم الأمر
    }
}

// تهيئة مدير الإشعارات عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    if (typeof apiClient !== 'undefined') {
        window.notificationsManager = new NotificationsManager();
    }
});

// تصدير للاستخدام في ملفات أخرى
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationsManager;
}

