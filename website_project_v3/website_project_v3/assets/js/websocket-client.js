/**
 * عميل WebSocket للإشعارات والتحديثات الحية
 * يوفر اتصال مباشر مع خدمة WebSocket لتلقي التحديثات الفورية
 */

class IdeaWebSocketClient {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.notifications = [];
        this.eventHandlers = {};
        
        this.init();
    }

    init() {
        this.createNotificationUI();
        this.connect();
        this.bindEvents();
    }

    connect() {
        try {
            // تحميل مكتبة Socket.IO
            if (typeof io === 'undefined') {
                this.loadSocketIO(() => this.establishConnection());
            } else {
                this.establishConnection();
            }
        } catch (error) {
            console.error('خطأ في الاتصال بـ WebSocket:', error);
            this.scheduleReconnect();
        }
    }

    loadSocketIO(callback) {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js';
        script.onload = callback;
        script.onerror = () => {
            console.error('فشل في تحميل مكتبة Socket.IO');
            this.showConnectionError();
        };
        document.head.appendChild(script);
    }

    establishConnection() {
        this.socket = io('http://localhost:3001', {
            transports: ['websocket', 'polling'],
            timeout: 10000,
            reconnection: true,
            reconnectionAttempts: this.maxReconnectAttempts,
            reconnectionDelay: this.reconnectDelay
        });

        this.setupSocketEvents();
    }

    setupSocketEvents() {
        // اتصال ناجح
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.reconnectAttempts = 0;
            console.log('✅ تم الاتصال بخدمة الإشعارات');
            this.updateConnectionStatus(true);
            this.joinDefaultRooms();
        });

        // قطع الاتصال
        this.socket.on('disconnect', (reason) => {
            this.isConnected = false;
            console.log('❌ انقطع الاتصال:', reason);
            this.updateConnectionStatus(false);
            
            if (reason === 'io server disconnect') {
                this.socket.connect();
            }
        });

        // خطأ في الاتصال
        this.socket.on('connect_error', (error) => {
            console.error('خطأ في الاتصال:', error);
            this.scheduleReconnect();
        });

        // تأكيد الاتصال
        this.socket.on('connected', (data) => {
            console.log('تأكيد الاتصال:', data);
            this.sessionId = data.session_id;
        });

        // استقبال الإشعارات
        this.socket.on('notification', (notification) => {
            this.handleNotification(notification);
        });

        // استقبال التحديثات الحية
        this.socket.on('live_update', (update) => {
            this.handleLiveUpdate(update);
        });

        // إحصائيات النظام
        this.socket.on('system_stats', (data) => {
            this.handleSystemStats(data);
        });

        // تأكيد الانضمام للغرفة
        this.socket.on('room_joined', (data) => {
            console.log('تم الانضمام للغرفة:', data.room);
        });
    }

    joinDefaultRooms() {
        // تحديد الغرف بناءً على نوع المستخدم
        const userType = this.detectUserType();
        const rooms = this.getRoomsForUserType(userType);
        
        rooms.forEach(room => {
            this.joinRoom(room);
        });
    }

    detectUserType() {
        // تحديد نوع المستخدم بناءً على الصفحة الحالية
        const path = window.location.pathname;
        
        if (path.includes('admin')) return 'admin';
        if (path.includes('client')) return 'client';
        if (path.includes('team')) return 'team';
        
        return 'visitor';
    }

    getRoomsForUserType(userType) {
        const roomMap = {
            'admin': ['admin', 'general'],
            'client': ['client', 'general'],
            'team': ['team', 'general'],
            'visitor': ['general']
        };
        
        return roomMap[userType] || ['general'];
    }

    joinRoom(room) {
        if (this.isConnected) {
            this.socket.emit('join_room', { room });
        }
    }

    leaveRoom(room) {
        if (this.isConnected) {
            this.socket.emit('leave_room', { room });
        }
    }

    handleNotification(notification) {
        console.log('إشعار جديد:', notification);
        
        // إضافة للقائمة
        this.notifications.unshift(notification);
        
        // الاحتفاظ بآخر 50 إشعار فقط
        if (this.notifications.length > 50) {
            this.notifications = this.notifications.slice(0, 50);
        }
        
        // عرض الإشعار
        this.displayNotification(notification);
        
        // تحديث العداد
        this.updateNotificationCounter();
        
        // تشغيل معالجات الأحداث المخصصة
        this.triggerEvent('notification', notification);
    }

    handleLiveUpdate(update) {
        console.log('تحديث حي:', update);
        
        // معالجة أنواع التحديثات المختلفة
        switch (update.update_type) {
            case 'project_update':
                this.handleProjectUpdate(update.data);
                break;
            case 'system_stats':
                this.handleSystemStats(update.data);
                break;
            case 'user_activity':
                this.handleUserActivity(update.data);
                break;
            default:
                console.log('نوع تحديث غير معروف:', update.update_type);
        }
        
        // تشغيل معالجات الأحداث المخصصة
        this.triggerEvent('live_update', update);
    }

    handleProjectUpdate(data) {
        // تحديث واجهة المشاريع إذا كانت موجودة
        const projectElements = document.querySelectorAll('[data-project-id]');
        projectElements.forEach(element => {
            if (element.dataset.projectId === data.project_id) {
                this.updateProjectElement(element, data);
            }
        });
    }

    handleSystemStats(data) {
        // تحديث إحصائيات النظام في لوحة التحكم
        const statsElements = document.querySelectorAll('[data-stat-type]');
        statsElements.forEach(element => {
            const statType = element.dataset.statType;
            if (data.stats && data.stats[statType]) {
                element.textContent = data.stats[statType];
            }
        });
    }

    handleUserActivity(data) {
        // تحديث نشاط المستخدمين
        console.log('نشاط المستخدم:', data);
    }

    displayNotification(notification) {
        // إنشاء عنصر الإشعار
        const notificationElement = this.createNotificationElement(notification);
        
        // إضافة للحاوية
        const container = document.getElementById('notifications-container');
        if (container) {
            container.insertBefore(notificationElement, container.firstChild);
        }
        
        // عرض الإشعار المنبثق
        this.showNotificationPopup(notification);
        
        // إزالة الإشعارات القديمة
        this.cleanupOldNotifications();
    }

    createNotificationElement(notification) {
        const element = document.createElement('div');
        element.className = `notification-item priority-${notification.priority || 'medium'}`;
        element.innerHTML = `
            <div class="notification-icon">
                <i class="fas ${this.getNotificationIcon(notification.type)}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${notification.title || 'إشعار'}</div>
                <div class="notification-message">${notification.message}</div>
                <div class="notification-time">${this.formatTime(notification.timestamp)}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        return element;
    }

    showNotificationPopup(notification) {
        // إنشاء إشعار منبثق
        const popup = document.createElement('div');
        popup.className = `notification-popup priority-${notification.priority || 'medium'}`;
        popup.innerHTML = `
            <div class="popup-content">
                <div class="popup-icon">
                    <i class="fas ${this.getNotificationIcon(notification.type)}"></i>
                </div>
                <div class="popup-text">
                    <div class="popup-title">${notification.title || 'إشعار'}</div>
                    <div class="popup-message">${notification.message}</div>
                </div>
                <button class="popup-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // إضافة للصفحة
        document.body.appendChild(popup);
        
        // تأثير الظهور
        setTimeout(() => popup.classList.add('show'), 100);
        
        // إزالة تلقائية
        setTimeout(() => {
            popup.classList.remove('show');
            setTimeout(() => popup.remove(), 300);
        }, 5000);
        
        // إزالة عند النقر
        popup.querySelector('.popup-close').addEventListener('click', () => {
            popup.classList.remove('show');
            setTimeout(() => popup.remove(), 300);
        });
    }

    getNotificationIcon(type) {
        const iconMap = {
            'welcome': 'fa-hand-wave',
            'project_update': 'fa-project-diagram',
            'system_alert': 'fa-exclamation-triangle',
            'new_message': 'fa-envelope',
            'system_update': 'fa-cog',
            'user_activity': 'fa-user',
            'default': 'fa-bell'
        };
        
        return iconMap[type] || iconMap['default'];
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('ar-SA', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    updateNotificationCounter() {
        const counter = document.getElementById('notification-counter');
        if (counter) {
            const unreadCount = this.notifications.filter(n => !n.read).length;
            counter.textContent = unreadCount;
            counter.style.display = unreadCount > 0 ? 'block' : 'none';
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
            statusElement.innerHTML = `
                <i class="fas ${connected ? 'fa-wifi' : 'fa-wifi-slash'}"></i>
                <span>${connected ? 'متصل' : 'غير متصل'}</span>
            `;
        }
    }

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`محاولة إعادة الاتصال ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('فشل في إعادة الاتصال بعد عدة محاولات');
            this.showConnectionError();
        }
    }

    showConnectionError() {
        const errorElement = document.createElement('div');
        errorElement.className = 'connection-error';
        errorElement.innerHTML = `
            <div class="error-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>فشل في الاتصال بخدمة الإشعارات</span>
                <button onclick="window.ideaWebSocket.connect()">إعادة المحاولة</button>
            </div>
        `;
        
        document.body.appendChild(errorElement);
        
        setTimeout(() => errorElement.remove(), 10000);
    }

    createNotificationUI() {
        // إنشاء حاوية الإشعارات إذا لم تكن موجودة
        if (!document.getElementById('notifications-container')) {
            const container = document.createElement('div');
            container.id = 'notifications-container';
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }
        
        // إنشاء مؤشر حالة الاتصال
        if (!document.getElementById('connection-status')) {
            const status = document.createElement('div');
            status.id = 'connection-status';
            status.className = 'connection-status disconnected';
            status.innerHTML = `
                <i class="fas fa-wifi-slash"></i>
                <span>غير متصل</span>
            `;
            document.body.appendChild(status);
        }
    }

    cleanupOldNotifications() {
        const container = document.getElementById('notifications-container');
        if (container && container.children.length > 10) {
            // الاحتفاظ بآخر 10 إشعارات فقط في الواجهة
            while (container.children.length > 10) {
                container.removeChild(container.lastChild);
            }
        }
    }

    // API للمطورين
    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    off(event, handler) {
        if (this.eventHandlers[event]) {
            const index = this.eventHandlers[event].indexOf(handler);
            if (index > -1) {
                this.eventHandlers[event].splice(index, 1);
            }
        }
    }

    triggerEvent(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`خطأ في معالج الحدث ${event}:`, error);
                }
            });
        }
    }

    // إرسال إشعار (للمشرفين)
    sendNotification(notification, target = 'broadcast') {
        if (this.isConnected) {
            this.socket.emit('send_notification', {
                notification,
                target
            });
        }
    }

    // طلب إحصائيات النظام
    requestStats() {
        if (this.isConnected) {
            this.socket.emit('request_stats');
        }
    }
}

// تهيئة العميل عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    // التحقق من توفر الخدمة
    fetch('http://localhost:3001/api/health')
        .then(response => response.json())
        .then(data => {
            console.log('✅ خدمة WebSocket متاحة:', data);
            window.ideaWebSocket = new IdeaWebSocketClient();
        })
        .catch(error => {
            console.warn('⚠️ خدمة WebSocket غير متاحة:', error);
            // يمكن إضافة نظام بديل هنا
        });
});
