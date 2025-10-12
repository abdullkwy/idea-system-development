/**
 * مدير تطبيق الويب التقدمي (PWA) لآيديا
 * يدير Service Worker والتثبيت والتحديثات
 */

class IdeaPWAManager {
    constructor() {
        this.swRegistration = null;
        this.isUpdateAvailable = false;
        this.deferredPrompt = null;
        this.isInstalled = false;
        this.isStandalone = false;
        
        this.init();
    }

    async init() {
        this.checkStandaloneMode();
        this.checkInstallation();
        await this.registerServiceWorker();
        this.setupInstallPrompt();
        this.setupUpdateHandling();
        this.setupOfflineHandling();
        this.createPWAUI();
    }

    checkStandaloneMode() {
        // التحقق من وضع التطبيق المستقل
        this.isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                           window.navigator.standalone ||
                           document.referrer.includes('android-app://');
        
        if (this.isStandalone) {
            document.body.classList.add('pwa-standalone');
            console.log('🎯 التطبيق يعمل في الوضع المستقل');
        }
    }

    checkInstallation() {
        // التحقق من حالة التثبيت
        this.isInstalled = this.isStandalone || 
                          localStorage.getItem('pwa-installed') === 'true';
        
        if (this.isInstalled) {
            document.body.classList.add('pwa-installed');
        }
    }

    async registerServiceWorker() {
        if (!('serviceWorker' in navigator)) {
            console.warn('Service Worker غير مدعوم في هذا المتصفح');
            return;
        }

        try {
            this.swRegistration = await navigator.serviceWorker.register('/sw.js', {
                scope: '/'
            });

            console.log('✅ تم تسجيل Service Worker بنجاح');

            // التحقق من التحديثات
            this.swRegistration.addEventListener('updatefound', () => {
                this.handleUpdateFound();
            });

            // التحقق من Service Worker النشط
            if (this.swRegistration.active) {
                this.setupMessageChannel();
            }

            // التحقق من التحديثات عند التحميل
            this.swRegistration.update();

        } catch (error) {
            console.error('❌ فشل في تسجيل Service Worker:', error);
        }
    }

    handleUpdateFound() {
        const newWorker = this.swRegistration.installing;
        
        newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed') {
                if (navigator.serviceWorker.controller) {
                    // تحديث متاح
                    this.isUpdateAvailable = true;
                    this.showUpdateNotification();
                } else {
                    // تثبيت أولي
                    console.log('✅ تم تثبيت Service Worker للمرة الأولى');
                }
            }
        });
    }

    setupMessageChannel() {
        // إعداد قناة التواصل مع Service Worker
        navigator.serviceWorker.addEventListener('message', event => {
            const { type, payload } = event.data;
            
            switch (type) {
                case 'SW_UPDATE_AVAILABLE':
                    this.showUpdateNotification();
                    break;
                case 'SW_CACHE_UPDATED':
                    this.showCacheUpdateNotification();
                    break;
                default:
                    console.log('رسالة من Service Worker:', event.data);
            }
        });
    }

    setupInstallPrompt() {
        // معالجة حدث التثبيت
        window.addEventListener('beforeinstallprompt', event => {
            event.preventDefault();
            this.deferredPrompt = event;
            this.showInstallButton();
            console.log('💾 يمكن تثبيت التطبيق');
        });

        // معالجة التثبيت الناجح
        window.addEventListener('appinstalled', () => {
            this.isInstalled = true;
            localStorage.setItem('pwa-installed', 'true');
            document.body.classList.add('pwa-installed');
            this.hideInstallButton();
            this.showInstallSuccessMessage();
            console.log('🎉 تم تثبيت التطبيق بنجاح');
        });
    }

    setupUpdateHandling() {
        // معالجة تحديثات التطبيق
        let refreshing = false;
        
        navigator.serviceWorker.addEventListener('controllerchange', () => {
            if (refreshing) return;
            refreshing = true;
            window.location.reload();
        });
    }

    setupOfflineHandling() {
        // معالجة حالة الاتصال
        window.addEventListener('online', () => {
            this.showConnectionStatus(true);
            this.syncWhenOnline();
        });

        window.addEventListener('offline', () => {
            this.showConnectionStatus(false);
        });

        // فحص الحالة الأولية
        if (!navigator.onLine) {
            this.showConnectionStatus(false);
        }
    }

    createPWAUI() {
        // إنشاء واجهة PWA
        const pwaContainer = document.createElement('div');
        pwaContainer.id = 'pwa-container';
        pwaContainer.className = 'pwa-container';
        pwaContainer.innerHTML = `
            <div id="pwa-install-banner" class="pwa-banner install-banner" style="display: none;">
                <div class="banner-content">
                    <div class="banner-icon">📱</div>
                    <div class="banner-text">
                        <div class="banner-title">تثبيت تطبيق آيديا</div>
                        <div class="banner-message">احصل على تجربة أفضل مع التطبيق</div>
                    </div>
                    <div class="banner-actions">
                        <button id="pwa-install-btn" class="pwa-btn primary">تثبيت</button>
                        <button id="pwa-install-dismiss" class="pwa-btn secondary">لاحقاً</button>
                    </div>
                </div>
            </div>

            <div id="pwa-update-banner" class="pwa-banner update-banner" style="display: none;">
                <div class="banner-content">
                    <div class="banner-icon">🔄</div>
                    <div class="banner-text">
                        <div class="banner-title">تحديث متاح</div>
                        <div class="banner-message">إصدار جديد من التطبيق متاح</div>
                    </div>
                    <div class="banner-actions">
                        <button id="pwa-update-btn" class="pwa-btn primary">تحديث</button>
                        <button id="pwa-update-dismiss" class="pwa-btn secondary">تجاهل</button>
                    </div>
                </div>
            </div>

            <div id="pwa-connection-status" class="pwa-status" style="display: none;">
                <div class="status-content">
                    <div class="status-icon">📡</div>
                    <div class="status-text">غير متصل</div>
                </div>
            </div>
        `;

        document.body.appendChild(pwaContainer);
        this.bindPWAEvents();
    }

    bindPWAEvents() {
        // ربط أحداث واجهة PWA
        const installBtn = document.getElementById('pwa-install-btn');
        const installDismiss = document.getElementById('pwa-install-dismiss');
        const updateBtn = document.getElementById('pwa-update-btn');
        const updateDismiss = document.getElementById('pwa-update-dismiss');

        if (installBtn) {
            installBtn.addEventListener('click', () => this.installApp());
        }

        if (installDismiss) {
            installDismiss.addEventListener('click', () => this.hideInstallButton());
        }

        if (updateBtn) {
            updateBtn.addEventListener('click', () => this.updateApp());
        }

        if (updateDismiss) {
            updateDismiss.addEventListener('click', () => this.hideUpdateNotification());
        }
    }

    showInstallButton() {
        const banner = document.getElementById('pwa-install-banner');
        if (banner && !this.isInstalled) {
            banner.style.display = 'block';
            setTimeout(() => banner.classList.add('show'), 100);
        }
    }

    hideInstallButton() {
        const banner = document.getElementById('pwa-install-banner');
        if (banner) {
            banner.classList.remove('show');
            setTimeout(() => banner.style.display = 'none', 300);
        }
    }

    async installApp() {
        if (!this.deferredPrompt) {
            console.warn('لا يمكن تثبيت التطبيق حالياً');
            return;
        }

        try {
            this.deferredPrompt.prompt();
            const { outcome } = await this.deferredPrompt.userChoice;
            
            if (outcome === 'accepted') {
                console.log('✅ المستخدم وافق على التثبيت');
            } else {
                console.log('❌ المستخدم رفض التثبيت');
            }
            
            this.deferredPrompt = null;
            this.hideInstallButton();
            
        } catch (error) {
            console.error('خطأ في تثبيت التطبيق:', error);
        }
    }

    showUpdateNotification() {
        const banner = document.getElementById('pwa-update-banner');
        if (banner) {
            banner.style.display = 'block';
            setTimeout(() => banner.classList.add('show'), 100);
        }
    }

    hideUpdateNotification() {
        const banner = document.getElementById('pwa-update-banner');
        if (banner) {
            banner.classList.remove('show');
            setTimeout(() => banner.style.display = 'none', 300);
        }
    }

    async updateApp() {
        if (!this.swRegistration || !this.swRegistration.waiting) {
            console.warn('لا يوجد تحديث متاح');
            return;
        }

        try {
            // إرسال رسالة للـ Service Worker الجديد للتفعيل
            this.swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
            this.hideUpdateNotification();
            
            // إظهار رسالة التحديث
            this.showUpdateInProgressMessage();
            
        } catch (error) {
            console.error('خطأ في تحديث التطبيق:', error);
        }
    }

    showConnectionStatus(isOnline) {
        const status = document.getElementById('pwa-connection-status');
        if (!status) return;

        if (isOnline) {
            status.style.display = 'none';
        } else {
            status.style.display = 'block';
            setTimeout(() => status.classList.add('show'), 100);
        }
    }

    showInstallSuccessMessage() {
        this.showToast('🎉 تم تثبيت التطبيق بنجاح!', 'success');
    }

    showCacheUpdateNotification() {
        this.showToast('📦 تم تحديث المحتوى', 'info');
    }

    showUpdateInProgressMessage() {
        this.showToast('🔄 جاري تحديث التطبيق...', 'info');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `pwa-toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    async syncWhenOnline() {
        // مزامنة البيانات عند العودة للاتصال
        if ('serviceWorker' in navigator && this.swRegistration) {
            try {
                // إرسال رسالة للـ Service Worker للمزامنة
                navigator.serviceWorker.ready.then(registration => {
                    return registration.sync.register('background-sync');
                });
                
                console.log('🔄 تم طلب المزامنة');
                
            } catch (error) {
                console.warn('فشل في طلب المزامنة:', error);
            }
        }
    }

    // API للمطورين
    async clearCache() {
        if (this.swRegistration) {
            const messageChannel = new MessageChannel();
            
            return new Promise((resolve) => {
                messageChannel.port1.onmessage = (event) => {
                    resolve(event.data);
                };
                
                navigator.serviceWorker.controller.postMessage(
                    { type: 'CLEAR_CACHE' },
                    [messageChannel.port2]
                );
            });
        }
    }

    async getVersion() {
        if (this.swRegistration) {
            const messageChannel = new MessageChannel();
            
            return new Promise((resolve) => {
                messageChannel.port1.onmessage = (event) => {
                    resolve(event.data);
                };
                
                navigator.serviceWorker.controller.postMessage(
                    { type: 'GET_VERSION' },
                    [messageChannel.port2]
                );
            });
        }
    }

    async cacheUrls(urls) {
        if (this.swRegistration) {
            const messageChannel = new MessageChannel();
            
            return new Promise((resolve) => {
                messageChannel.port1.onmessage = (event) => {
                    resolve(event.data);
                };
                
                navigator.serviceWorker.controller.postMessage(
                    { type: 'CACHE_URLS', payload: { urls } },
                    [messageChannel.port2]
                );
            });
        }
    }

    // معلومات التطبيق
    getAppInfo() {
        return {
            isInstalled: this.isInstalled,
            isStandalone: this.isStandalone,
            isUpdateAvailable: this.isUpdateAvailable,
            isOnline: navigator.onLine,
            hasServiceWorker: !!this.swRegistration
        };
    }
}

// تهيئة مدير PWA عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    window.ideaPWA = new IdeaPWAManager();
    
    // إضافة معلومات PWA للكونسول
    console.log('🎯 مدير PWA لآيديا جاهز');
    console.log('📱 للتحكم في PWA استخدم: window.ideaPWA');
});
